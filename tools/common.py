# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: GiveMeAllYourCats
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: GiveMeAllYourCats, Hotox

import re
import bpy
import time
import bmesh
import platform

from math import degrees
from mathutils import Vector
from datetime import datetime
from html.parser import HTMLParser
from html.entities import name2codepoint

from . import common as Common
from . import supporter as Supporter
from . import decimation as Decimation
from . import translate as Translate
from . import armature_bones as Bones
from . import settings as Settings
from .register import register_wrap
from .translations import t

from mmd_tools_local import utils
from mmd_tools_local.panels import tool as mmd_tool
from mmd_tools_local.panels import util_tools as mmd_util_tools
from mmd_tools_local.panels import view_prop as mmd_view_prop

# TODO:
#  - Add check if hips bone really needs to be rotated
#  - Reset Pivot
#  - Manual bone selection button for root bones
#  - Checkbox for eye blinking/moving
#  - Translate progress bar


def version_2_79_or_older():
    return bpy.app.version < (2, 80)


def get_objects():
    return bpy.context.scene.objects if version_2_79_or_older() else bpy.context.view_layer.objects


class SavedData:
    __object_properties = {}
    __active_object = None

    def __init__(self):
        # initialize as instance attributes rather than class attributes
        self.__object_properties = {}
        self.__active_object = None

        for obj in get_objects():
            mode = obj.mode
            selected = is_selected(obj)
            hidden = is_hidden(obj)
            pose = None
            if obj.type == 'ARMATURE':
                pose = obj.data.pose_position
            self.__object_properties[obj.name] = [mode, selected, hidden, pose]

            active = get_active()
            if active:
                self.__active_object = active.name

    def load(self, ignore=None, load_mode=True, load_select=True, load_hide=True, load_active=True, hide_only=False):
        if not ignore:
            ignore = []
        if hide_only:
            load_mode = False
            load_select = False
            load_active = False

        for obj_name, values in self.__object_properties.items():
            # print(obj_name, ignore)
            if obj_name in ignore:
                continue

            obj = get_objects().get(obj_name)
            if not obj:
                continue

            mode, selected, hidden, pose = values
            # print(obj_name, mode, selected, hidden)
            print(obj_name, pose)

            if load_mode and obj.mode != mode:
                set_active(obj, skip_sel=True)
                switch(mode, check_mode=False)
                if pose:
                    obj.data.pose_position = pose

            if load_select:
                select(obj, selected)
            if load_hide:
                hide(obj, hidden)

        # Set the active object
        if load_active and self.__active_object and get_objects().get(self.__active_object):
            if self.__active_object not in ignore and self.__active_object != get_active():
                set_active(get_objects().get(self.__active_object), skip_sel=True)


def get_armature(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature
    for obj in get_objects():
        if obj.type == 'ARMATURE':
            if (armature_name and obj.name == armature_name) or not armature_name:
                return obj
    return None


def get_armature_objects():
    armatures = []
    for obj in get_objects():
        if obj.type == 'ARMATURE':
            armatures.append(obj)
    return armatures


def get_top_parent(child):
    if child.parent:
        return get_top_parent(child.parent)
    return child


def unhide_all_unnecessary():
    # TODO: Documentation? What does "unnecessary" mean?
    try:
        bpy.ops.object.hide_view_clear()
    except RuntimeError:
        pass

    for collection in bpy.data.collections:
        collection.hide_select = False
        collection.hide_viewport = False


def unhide_all():
    for obj in get_objects():
        hide(obj, False)
        set_unselectable(obj, False)

    if not version_2_79_or_older():
        unhide_all_unnecessary()


def unhide_children(parent):
    for child in parent.children:
        hide(child, False)
        set_unselectable(child, False)
        unhide_children(child)


def unhide_all_of(obj_to_unhide=None):
    if not obj_to_unhide:
        return

    top_parent = get_top_parent(obj_to_unhide)
    hide(top_parent, False)
    set_unselectable(top_parent, False)
    unhide_children(top_parent)


def unselect_all():
    for obj in get_objects():
        select(obj, False)


def set_active(obj, skip_sel=False):
    if not skip_sel:
        select(obj)
    if version_2_79_or_older():
        bpy.context.scene.objects.active = obj
    else:
        bpy.context.view_layer.objects.active = obj


def get_active():
    if version_2_79_or_older():
        return bpy.context.scene.objects.active
    return bpy.context.view_layer.objects.active


def select(obj, sel=True):
    if sel:
        hide(obj, False)
    if version_2_79_or_older():
        obj.select = sel
    else:
        obj.select_set(sel)


def is_selected(obj):
    if version_2_79_or_older():
        return obj.select
    return obj.select_get()


def hide(obj, val=True):
    if hasattr(obj, 'hide'):
        obj.hide = val
    if not version_2_79_or_older():
        obj.hide_set(val)


def is_hidden(obj):
    if version_2_79_or_older():
        return obj.hide
    return obj.hide_get()


def set_unselectable(obj, val=True):
    obj.hide_select = val


def switch(new_mode, check_mode=True):
    if check_mode and get_active() and get_active().mode == new_mode:
        return
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=new_mode, toggle=False)


def set_default_stage_old():
    switch('OBJECT')
    unhide_all()
    unselect_all()
    armature = get_armature()
    set_active(armature)
    return armature


def set_default_stage():
    """

    Selects the armature, unhides everything and sets the modes of every object to object mode

    :return: the armature
    """

    # Remove rigidbody collections, as they cause issues if they are not in the view_layer
    if not version_2_79_or_older() and bpy.context.scene.remove_rigidbodies_joints:
        print('Collections:')
        for collection in bpy.data.collections:
            print(' ' + collection.name, collection.name.lower())
            if 'rigidbody' in collection.name.lower():
                print('DELETE')
                for obj in collection.objects:
                    delete(obj)
                bpy.data.collections.remove(collection)

    unhide_all()
    unselect_all()

    for obj in get_objects():
        set_active(obj)
        switch('OBJECT')
        if obj.type == 'ARMATURE':
            # obj.data.pose_position = 'REST'
            pass

        select(obj, False)

    armature = get_armature()
    if armature:
        set_active(armature)
        if version_2_79_or_older():
            armature.layers[0] = True

    # Fix broken armatures
    if not bpy.context.scene.armature:
        bpy.context.scene.armature = armature.name

    return armature


def apply_modifier(mod, as_shapekey=False):
    if bpy.app.version < (2, 90):
        bpy.ops.object.modifier_apply(apply_as='SHAPE' if as_shapekey else 'DATA', modifier=mod.name)
        return

    if as_shapekey:
        bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=mod.name)
    else:
        bpy.ops.object.modifier_apply(modifier=mod.name)


def remove_bone(find_bone):
    armature = get_armature()
    switch('EDIT')
    for bone in armature.data.edit_bones:
        if bone.name == find_bone:
            armature.data.edit_bones.remove(bone)


def remove_empty():
    armature = set_default_stage()
    if armature.parent and armature.parent.type == 'EMPTY':
        unselect_all()
        set_active(armature.parent)
        bpy.ops.object.delete(use_global=False)
        unselect_all()


def get_bone_angle(p1, p2):
    try:
        ret = degrees((p1.head - p1.tail).angle(p2.head - p2.tail))
    except ValueError:
        ret = 0

    return ret


def remove_unused_vertex_groups(ignore_main_bones=False):
    remove_count = 0
    unselect_all()
    for mesh in get_meshes_objects(mode=2):
        mesh.update_from_editmode()

        vgroup_used = {i: False for i, k in enumerate(mesh.vertex_groups)}

        for v in mesh.data.vertices:
            for g in v.groups:
                if g.weight > 0.0:
                    vgroup_used[g.group] = True

        for i, used in sorted(vgroup_used.items(), reverse=True):
            if not used:
                if ignore_main_bones and mesh.vertex_groups[i].name in Bones.dont_delete_these_main_bones:
                    continue
                mesh.vertex_groups.remove(mesh.vertex_groups[i])
                remove_count += 1
    return remove_count


def remove_unused_vertex_groups_of_mesh(mesh):
    remove_count = 0
    unselect_all()
    mesh.update_from_editmode()

    vgroup_used = {i: False for i, k in enumerate(mesh.vertex_groups)}

    for v in mesh.data.vertices:
        for g in v.groups:
            if g.weight > 0.0:
                vgroup_used[g.group] = True

    for i, used in sorted(vgroup_used.items(), reverse=True):
        if not used:
            mesh.vertex_groups.remove(mesh.vertex_groups[i])
            remove_count += 1
    return remove_count


def find_center_vector_of_vertex_group(mesh, vertex_group):
    data = mesh.data
    verts = data.vertices
    verts_in_group = []

    for vert in verts:
        i = vert.index
        try:
            if mesh.vertex_groups[vertex_group].weight(i) > 0:
                verts_in_group.append(vert)
        except RuntimeError:
            # vertex is not in the group
            pass

    # Find the average vector point of the vertex cluster
    divide_by = len(verts_in_group)
    total = Vector()

    if divide_by == 0:
        return False

    for vert in verts_in_group:
        total += vert.co

    average = total / divide_by

    return average


def vertex_group_exists(mesh_name, bone_name):
    mesh = get_objects()[mesh_name]
    data = mesh.data
    verts = data.vertices

    for vert in verts:
        i = vert.index
        try:
            mesh.vertex_groups[bone_name].weight(i)
            return True
        except:
            pass

    return False


def get_meshes(self, context):
    # Modes:
    # 0 = With Armature only
    # 1 = Without armature only
    # 2 = All meshes

    choices = []

    for mesh in get_meshes_objects(mode=0, check=False):
        choices.append((mesh.name, mesh.name, mesh.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_top_meshes(self, context):
    choices = []

    for mesh in get_meshes_objects(mode=1, check=False):
        choices.append((mesh.name, mesh.name, mesh.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_all_meshes(self, context):
    choices = []

    for mesh in get_meshes_objects(mode=2, check=False):
        choices.append((mesh.name, mesh.name, mesh.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_armature_list(self, context):
    choices = []

    for armature in get_armature_objects():
        # Set name displayed in list
        name = armature.data.name
        if name.startswith('Armature ('):
            name = armature.name + ' (' + name.replace('Armature (', '')[:-1] + ')'

        # 1. Will be returned by context.scene
        # 2. Will be shown in lists
        # 3. will be shown in the hover description (below description)
        choices.append((armature.name, name, armature.name))

    if len(choices) == 0:
        choices.append(('None', 'None', 'None'))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_armature_merge_list(self, context):
    choices = []
    current_armature = context.scene.merge_armature_into

    for armature in get_armature_objects():
        if armature.name != current_armature:
            # Set name displayed in list
            name = armature.data.name
            if name.startswith('Armature ('):
                name = armature.name + ' (' + name.replace('Armature (', '')[:-1] + ')'

            # 1. Will be returned by context.scene
            # 2. Will be shown in lists
            # 3. will be shown in the hover description (below description)
            choices.append((armature.name, name, armature.name))

    if len(choices) == 0:
        choices.append(('None', 'None', 'None'))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_meshes_decimation(self, context):
    choices = []

    for object in bpy.context.scene.objects:
        if object.type == 'MESH':
            if object.parent and object.parent.type == 'ARMATURE' and object.parent.name == bpy.context.scene.armature:
                if object.name in Decimation.ignore_meshes:
                    continue
                # 1. Will be returned by context.scene
                # 2. Will be shown in lists
                # 3. will be shown in the hover description (below description)
                choices.append((object.name, object.name, object.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_bones_head(self, context):
    return get_bones(names=['Head'])


def get_bones_eye_l(self, context):
    return get_bones(names=['Eye_L', 'EyeReturn_L'])


def get_bones_eye_r(self, context):
    return get_bones(names=['Eye_R', 'EyeReturn_R'])


def get_bones_merge(self, context):
    return get_bones(armature_name=bpy.context.scene.merge_armature_into)


# names - The first object will be the first one in the list. So the first one has to be the one that exists in the most models
def get_bones(names=None, armature_name=None, check_list=False):
    if not names:
        names = []
    if not armature_name:
        armature_name = bpy.context.scene.armature

    choices = []
    armature = get_armature(armature_name=armature_name)

    if not armature:
        bpy.types.Object.Enum = choices
        return bpy.types.Object.Enum

    # print("")
    # print("START DEBUG UNICODE")
    # print("")
    for bone in armature.data.bones:
        # print(bone.name)
        try:
            # 1. Will be returned by context.scene
            # 2. Will be shown in lists
            # 3. will be shown in the hover description (below description)
            choices.append((bone.name, bone.name, bone.name))
        except UnicodeDecodeError:
            print("ERROR", bone.name)

    choices.sort(key=lambda x: tuple(x[0].lower()))

    choices2 = []
    for name in names:
        if name in armature.data.bones and choices[0][0] != name:
            choices2.append((name, name, name))

    if not check_list:
        for choice in choices:
            choices2.append(choice)

    bpy.types.Object.Enum = choices2

    return bpy.types.Object.Enum


def get_shapekeys_mouth_ah(self, context):
    return get_shapekeys(context, ['MTH A', 'Ah', 'A'], True, False, False, False)


def get_shapekeys_mouth_oh(self, context):
    return get_shapekeys(context, ['MTH U', 'Oh', 'O', 'Your'], True, False, False, False)


def get_shapekeys_mouth_ch(self, context):
    return get_shapekeys(context, ['MTH I', 'Glue', 'Ch', 'I', 'There'], True, False, False, False)


def get_shapekeys_eye_blink_l(self, context):
    return get_shapekeys(context, ['EYE Close L', 'Wink 2', 'Wink', 'Wink left', 'Wink Left', 'Blink (Left)', 'Blink', 'Basis'], False, False, False, False)


def get_shapekeys_eye_blink_r(self, context):
    return get_shapekeys(context, ['EYE Close R', 'Wink 2 right', 'Wink 2 Right', 'Wink right 2', 'Wink Right 2', 'Wink right', 'Wink Right', 'Blink (Right)', 'Basis'], False, False, False, False)


def get_shapekeys_eye_low_l(self, context):
    return get_shapekeys(context, ['Basis'], False, False, False, False)


def get_shapekeys_eye_low_r(self, context):
    return get_shapekeys(context, ['Basis'], False, False, False, False)


def get_shapekeys_decimation(self, context):
    return get_shapekeys(context,
                         ['MTH A', 'Ah', 'A', 'MTH U', 'Oh', 'O', 'Your', 'MTH I', 'Glue', 'Ch', 'I', 'There', 'Wink 2', 'Wink', 'Wink left', 'Wink Left', 'Blink (Left)', 'Wink 2 right',
                          'EYE Close R', 'EYE Close L', 'Wink 2 Right', 'Wink right 2', 'Wink Right 2', 'Wink right', 'Wink Right', 'Blink (Right)', 'Blink'], False, True, True, False)


def get_shapekeys_decimation_list(self, context):
    return get_shapekeys(context,
                         ['MTH A', 'Ah', 'A', 'MTH U', 'Oh', 'O', 'Your', 'MTH I', 'Glue', 'Ch', 'I', 'There', 'Wink 2', 'Wink', 'Wink left', 'Wink Left', 'Blink (Left)', 'Wink 2 right',
                          'EYE Close R', 'EYE Close L', 'Wink 2 Right', 'Wink right 2', 'Wink Right 2', 'Wink right', 'Wink Right', 'Blink (Right)', 'Blink'], False, True, True, True)


# names - The first object will be the first one in the list. So the first one has to be the one that exists in the most models
# no_basis - If this is true the Basis will not be available in the list
def get_shapekeys(context, names, is_mouth, no_basis, decimation, return_list):
    choices = []
    choices_simple = []
    meshes_list = get_meshes_objects(check=False)

    if decimation:
        meshes = meshes_list
    elif meshes_list:
        if is_mouth:
            meshes = [get_objects().get(context.scene.mesh_name_viseme)]
        else:
            meshes = [get_objects().get(context.scene.mesh_name_eye)]
    else:
        bpy.types.Object.Enum = choices
        return bpy.types.Object.Enum

    for mesh in meshes:
        if not mesh or not has_shapekeys(mesh):
            bpy.types.Object.Enum = choices
            return bpy.types.Object.Enum

        for shapekey in mesh.data.shape_keys.key_blocks:
            name = shapekey.name
            if name in choices_simple:
                continue
            if no_basis and name == 'Basis':
                continue
            if decimation and name in Decimation.ignore_shapes:
                continue
            # 1. Will be returned by context.scene
            # 2. Will be shown in lists
            # 3. will be shown in the hover description (below description)
            choices.append((name, name, name))
            choices_simple.append(name)

    choices.sort(key=lambda x: tuple(x[0].lower()))

    choices2 = []
    for name in names:
        if name in choices_simple and len(choices) > 1 and choices[0][0] != name:
            if decimation and name in Decimation.ignore_shapes:
                continue
            choices2.append((name, name, name))

    for choice in choices:
        choices2.append(choice)

    bpy.types.Object.Enum = choices2

    if return_list:
        shape_list = []
        for choice in choices2:
            shape_list.append(choice[0])
        return shape_list

    return bpy.types.Object.Enum


def fix_armature_names(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature
    base_armature = get_armature(armature_name=bpy.context.scene.merge_armature_into)
    merge_armature = get_armature(armature_name=bpy.context.scene.merge_armature)

    # Armature should be named correctly (has to be at the end because of multiple armatures)
    armature = get_armature(armature_name=armature_name)
    armature.name = 'Armature'
    if not armature.data.name.startswith('Armature'):
        Translate.update_dictionary(armature.data.name)
        armature.data.name = 'Armature (' + Translate.translate(armature.data.name, add_space=True)[0] + ')'

    # Reset the armature lists
    try:
        bpy.context.scene.armature = armature.name
    except TypeError:
        pass

    try:
        if base_armature:
            bpy.context.scene.merge_armature_into = base_armature.name
    except TypeError:
        pass

    try:
        if merge_armature:
            bpy.context.scene.merge_armature = merge_armature.name
    except TypeError:
        pass


def get_texture_sizes(self, context):
    bpy.types.Object.Enum = [
        ("1024", "1024 (low)", "1024"),
        ("2048", "2048 (medium)", "2048"),
        ("4096", "4096 (high)", "4096")
    ]

    return bpy.types.Object.Enum


def get_meshes_objects(armature_name=None, mode=0, check=True, visible_only=False):
    # Modes:
    # 0 = With armatures only
    # 1 = Top level only
    # 2 = All meshes
    # 3 = Selected only

    if not armature_name:
        armature = get_armature()
        if armature:
            armature_name = armature.name

    meshes = []
    for ob in get_objects():
        if ob.type == 'MESH':
            if mode == 0 or mode == 5:
                if ob.parent:
                    if ob.parent.type == 'ARMATURE' and ob.parent.name == armature_name:
                        meshes.append(ob)
                    elif ob.parent.parent and ob.parent.parent.type == 'ARMATURE' and ob.parent.parent.name == armature_name:
                        meshes.append(ob)

            elif mode == 1:
                if not ob.parent:
                    meshes.append(ob)

            elif mode == 2:
                meshes.append(ob)

            elif mode == 3:
                if is_selected(ob):
                    meshes.append(ob)

    if visible_only:
        for mesh in meshes:
            if is_hidden(mesh):
                meshes.remove(mesh)

    # Check for broken meshes and delete them
    if check:
        current_active = get_active()
        to_remove = []
        for mesh in meshes:
            selected = is_selected(mesh)
            # print(mesh.name, mesh.users)
            set_active(mesh)

            if not get_active():
                to_remove.append(mesh)

            if not selected:
                select(mesh, False)

        for mesh in to_remove:
            print('DELETED CORRUPTED MESH:', mesh.name, mesh.users)
            meshes.remove(mesh)
            delete(mesh)

        if current_active:
            set_active(current_active)

    return meshes


def join_meshes(armature_name=None, mode=0, apply_transformations=True, repair_shape_keys=True):
    # Modes:
    # 0 - Join all meshes
    # 1 - Join selected only

    if not armature_name:
        armature_name = bpy.context.scene.armature

    # Get meshes to join
    meshes_to_join = get_meshes_objects(armature_name=armature_name, mode=3 if mode == 1 else 0)
    if not meshes_to_join:
        reset_context_scenes()
        return None

    set_default_stage()
    unselect_all()

    if apply_transformations:
        apply_transforms(armature_name=armature_name)

    unselect_all()

    # Apply existing decimation modifiers and select the meshes for joining
    for mesh in meshes_to_join:
        set_active(mesh)

        # Apply decimation modifiers
        for mod in mesh.modifiers:
            if mod.type == 'DECIMATE':
                if mod.decimate_type == 'COLLAPSE' and mod.ratio == 1:
                    mesh.modifiers.remove(mod)
                    continue
                if mod.decimate_type == 'UNSUBDIV' and mod.iterations == 0:
                    mesh.modifiers.remove(mod)
                    continue

                if has_shapekeys(mesh):
                    bpy.ops.object.shape_key_remove(all=True)
                apply_modifier(mod)
            elif mod.type == 'SUBSURF':
                mesh.modifiers.remove(mod)
            elif mod.type == 'MIRROR':
                if not has_shapekeys(mesh):
                    apply_modifier(mod)

        # Standardize UV maps name
        if version_2_79_or_older():
            if mesh.data.uv_textures:
                mesh.data.uv_textures[0].name = 'UVMap'
            for mat_slot in mesh.material_slots:
                if mat_slot and mat_slot.material:
                    for tex_slot in mat_slot.material.texture_slots:
                        if tex_slot and tex_slot.texture and tex_slot.texture_coords == 'UV':
                            tex_slot.uv_layer = 'UVMap'
        else:
            if mesh.data.uv_layers:
                mesh.data.uv_layers[0].name = 'UVMap'

    # Get the name of the active mesh in order to check if it was deleted later
    active_mesh_name = get_active().name

    # Join the meshes
    if bpy.ops.object.join.poll():
        bpy.ops.object.join()
    else:
        print('NO MESH COMBINED!')

    # Delete meshes that somehow weren't deleted. Both pre and post join mesh deletion methods are needed!
    for mesh in get_meshes_objects(armature_name=armature_name):
        if mesh.name == active_mesh_name:
            set_active(mesh)
        elif mesh.name in meshes_to_join:
            delete(mesh)
            print('DELETED', mesh.name, mesh.users)

    # Rename result to Body and correct modifiers
    mesh = get_active()
    if mesh:
        # If its the only mesh in the armature left, rename it to Body
        if len(get_meshes_objects(armature_name=armature_name)) == 1:
            mesh.name = 'Body'
        mesh.parent_type = 'OBJECT'

        repair_mesh(mesh, armature_name)

        if repair_shape_keys:
            repair_shapekey_order(mesh.name)

    reset_context_scenes()

    # Update the material list of the Material Combiner
    update_material_list()

    return mesh


def repair_mesh(mesh, armature_name):
    mesh.parent_type = 'OBJECT'

    # Remove duplicate armature modifiers
    mod_count = 0
    for mod in mesh.modifiers:
        mod.show_expanded = False
        if mod.type == 'ARMATURE':
            mod_count += 1
            if mod_count > 1:
                bpy.ops.object.modifier_remove(modifier=mod.name)
                continue
            mod.object = get_armature(armature_name=armature_name)
            mod.show_viewport = True

    # Add armature mod if there is none
    if mod_count == 0:
        mod = mesh.modifiers.new("Armature", 'ARMATURE')
        mod.object = get_armature(armature_name=armature_name)


def apply_transforms(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature
    armature = get_armature(armature_name=armature_name)

    # Apply transforms on armature
    unselect_all()
    set_active(armature)
    switch('OBJECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Apply transforms of meshes
    for mesh in get_meshes_objects(armature_name=armature_name):
        unselect_all()
        set_active(mesh)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def apply_all_transforms():

    def apply_transforms_with_children(parent):
        unselect_all()
        set_active(parent)
        switch('OBJECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        for child in parent.children:
            apply_transforms_with_children(child)

    for obj in get_objects():
        if not obj.parent:
            apply_transforms_with_children(obj)


def reset_transforms(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature
    armature = get_armature(armature_name=armature_name)

    # Reset transforms on armature
    for i in range(0, 3):
        armature.location[i] = 0
        armature.rotation_euler[i] = 0
        armature.scale[i] = 1

    # Apply transforms of meshes
    for mesh in get_meshes_objects(armature_name=armature_name):
        for i in range(0, 3):
            mesh.location[i] = 0
            mesh.rotation_euler[i] = 0
            mesh.scale[i] = 1


def separate_by_materials(context, mesh):
    prepare_separation(mesh)

    utils.separateByMaterials(mesh)

    for ob in context.selected_objects:
        if ob.type == 'MESH':
            hide(ob, False)
            clean_shapekeys(ob)

    utils.clearUnusedMeshes()

    # Update the material list of the Material Combiner
    update_material_list()


def separate_by_loose_parts(context, mesh):
    prepare_separation(mesh)

    # Correctly put mesh together. This is done to prevent extremely small pieces.
    # This essentially does nothing but merges the extremely small parts together.
    remove_doubles(mesh, 0, save_shapes=True)

    utils.separateByMaterials(mesh)

    meshes = []
    for ob in context.selected_objects:
        if ob.type == 'MESH':
            hide(ob, False)
            meshes.append(ob)

    wm = bpy.context.window_manager
    current_step = 0
    wm.progress_begin(current_step, len(meshes))

    for mesh in meshes:
        unselect_all()
        set_active(mesh)
        bpy.ops.mesh.separate(type='LOOSE')

        meshes2 = []
        for ob in context.selected_objects:
            if ob.type == 'MESH':
                meshes2.append(ob)

        ## This crashes blender, but would be better
        # unselect_all()
        # for mesh2 in meshes2:
        #     if len(mesh2.data.vertices) <= 3:
        #         select(mesh2)
        #     elif bpy.ops.object.join.poll():
        #         bpy.ops.object.join()
        #         unselect_all()

        for mesh2 in meshes2:
            clean_shapekeys(mesh2)

        current_step += 1
        wm.progress_update(current_step)

    wm.progress_end()

    utils.clearUnusedMeshes()

    # Update the material list of the Material Combiner
    update_material_list()


def separate_by_shape_keys(context, mesh):
    prepare_separation(mesh)

    switch('EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')

    switch('OBJECT')
    selected_count = 0
    max_count = 0
    if has_shapekeys(mesh):
        for kb in mesh.data.shape_keys.key_blocks:
            for i, (v0, v1) in enumerate(zip(kb.relative_key.data, kb.data)):
                max_count += 1
                if v0.co != v1.co:
                    mesh.data.vertices[i].select = True
                    selected_count += 1

    if not selected_count or selected_count == max_count:
        return False

    switch('EDIT')
    bpy.ops.mesh.select_all(action='INVERT')

    bpy.ops.mesh.separate(type='SELECTED')

    for ob in context.selected_objects:
        if ob.type == 'MESH':
            if ob != get_active():
                print('not active', ob.name)
                active_tmp = get_active()
                ob.name = ob.name.replace('.001', '') + '.no_shapes'
                set_active(ob)
                bpy.ops.object.shape_key_remove(all=True)
                set_active(active_tmp)
                select(ob, False)
            else:
                print('active', ob.name)
                clean_shapekeys(ob)
                switch('OBJECT')

    utils.clearUnusedMeshes()

    # Update the material list of the Material Combiner
    update_material_list()
    return True


def separate_by_cats_protection(context, mesh):
    prepare_separation(mesh)

    switch('EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')

    switch('OBJECT')
    selected_count = 0
    max_count = 0
    if has_shapekeys(mesh):
        for kb in mesh.data.shape_keys.key_blocks:
            if kb.name == 'Basis Original':
                for i, (v0, v1) in enumerate(zip(kb.relative_key.data, kb.data)):
                    max_count += 1
                    if v0.co != v1.co:
                        mesh.data.vertices[i].select = True
                        selected_count += 1

    if not selected_count or selected_count == max_count:
        return False

    switch('EDIT')
    bpy.ops.mesh.select_all(action='INVERT')

    bpy.ops.mesh.separate(type='SELECTED')

    for ob in context.selected_objects:
        if ob.type == 'MESH':
            if ob != get_active():
                print('not active', ob.name)
                active_tmp = get_active()
                ob.name = ob.name.replace('.001', '') + '.no_shapes'
                set_active(ob)
                bpy.ops.object.shape_key_remove(all=True)
                set_active(active_tmp)
                select(ob, False)
            else:
                print('active', ob.name)
                clean_shapekeys(ob)
                switch('OBJECT')

    utils.clearUnusedMeshes()

    # Update the material list of the Material Combiner
    update_material_list()
    return True


def prepare_separation(mesh):
    set_default_stage()
    unselect_all()

    # Remove Rigidbodies and joints
    if bpy.context.scene.remove_rigidbodies_joints:
        for obj in get_objects():
            if 'rigidbodies' in obj.name or 'joints' in obj.name:
                delete_hierarchy(obj)

    save_shapekey_order(mesh.name)
    set_active(mesh)

    for mod in mesh.modifiers:
        if mod.type == 'DECIMATE':
            mesh.modifiers.remove(mod)
        else:
            mod.show_expanded = False

    clean_material_names(mesh)


def clean_shapekeys(mesh):
    # Remove empty shapekeys
    if has_shapekeys(mesh):
        for kb in mesh.data.shape_keys.key_blocks:
            if can_remove_shapekey(kb):
                mesh.shape_key_remove(kb)
        if len(mesh.data.shape_keys.key_blocks) == 1:
            mesh.shape_key_remove(mesh.data.shape_keys.key_blocks[0])


def can_remove_shapekey(key_block):
    if 'mmd_' in key_block.name:
        return True
    if key_block.relative_key == key_block:
        return False  # Basis
    for v0, v1 in zip(key_block.relative_key.data, key_block.data):
        if v0.co != v1.co:
            return False
    return True


def separate_by_verts():
    for obj in bpy.context.selected_objects:
        if obj.type == 'MESH' and len(obj.vertex_groups) > 0:
            Common.set_active(obj)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        for vgroup in obj.vertex_groups:
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.vertex_group_set_active(group=vgroup.name)
            bpy.ops.object.vertex_group_select()
            bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')


def reset_context_scenes():
    head_bones = get_bones_head(None, bpy.context)
    if len(head_bones) > 0:
        bpy.context.scene.head = head_bones[0][0]
        bpy.context.scene.eye_left = get_bones_eye_l(None, bpy.context)[0][0]
        bpy.context.scene.eye_right = get_bones_eye_r(None, bpy.context)[0][0]

    meshes = get_meshes(None, bpy.context)
    if len(meshes) > 0:
        mesh = meshes[0][0]
        if not bpy.context.scene.mesh_name_eye:
            bpy.context.scene.mesh_name_eye = mesh
        if not bpy.context.scene.mesh_name_viseme:
            bpy.context.scene.mesh_name_viseme = mesh
        if not bpy.context.scene.merge_mesh:
            bpy.context.scene.merge_mesh = mesh


def save_shapekey_order(mesh_name):
    mesh = get_objects()[mesh_name]
    armature = get_armature()

    if not armature:
        return

    # Get current custom data
    custom_data = armature.get('CUSTOM')
    if not custom_data:
        # print('NEW DATA!')
        custom_data = {}

    # Create shapekey order
    shape_key_order = []
    if has_shapekeys(mesh):
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            shape_key_order.append(shapekey.name)

    # Check if there is already a shapekey order
    if custom_data.get('shape_key_order'):
        # print('SHAPEKEY ORDER ALREADY EXISTS!')
        # print(custom_data['shape_key_order'])
        old_len = len(custom_data.get('shape_key_order'))

        if type(shape_key_order) is str:
            old_len = len(shape_key_order.split(',,,'))

        if len(shape_key_order) <= old_len:
            # print('ABORT')
            return

    # Save order to custom data
    # print('SAVE NEW ORDER')
    custom_data['shape_key_order'] = shape_key_order

    # Save custom data in armature
    armature['CUSTOM'] = custom_data

    # print(armature.get('CUSTOM').get('shape_key_order'))


def repair_shapekey_order(mesh_name):
    # Get current custom data
    armature = get_armature()
    custom_data = armature.get('CUSTOM')
    if not custom_data:
        custom_data = {}

    # Extract shape keys from string
    shape_key_order = custom_data.get('shape_key_order')
    if not shape_key_order:
        custom_data['shape_key_order'] = []
        armature['CUSTOM'] = custom_data

    if type(shape_key_order) is str:
        shape_key_order_temp = []
        for shape_name in shape_key_order.split(',,,'):
            shape_key_order_temp.append(shape_name)
        custom_data['shape_key_order'] = shape_key_order_temp
        armature['CUSTOM'] = custom_data

    sort_shape_keys(mesh_name, custom_data['shape_key_order'])


def update_shapekey_orders():
    for armature in get_armature_objects():
        shape_key_order_translated = []

        # Get current custom data
        custom_data = armature.get('CUSTOM')
        if not custom_data:
            continue
        order = custom_data.get('shape_key_order')
        if not order:
            continue

        if type(order) is str:
            shape_key_order_temp = order.split(',,,')
            order = []
            for shape_name in shape_key_order_temp:
                order.append(shape_name)

        # Get shape keys and translate them
        for shape_name in order:
            shape_key_order_translated.append(Translate.translate(shape_name, add_space=True, translating_shapes=True)[0])

        # print(armature.name, shape_key_order_translated)
        custom_data['shape_key_order'] = shape_key_order_translated
        armature['CUSTOM'] = custom_data


def sort_shape_keys(mesh_name, shape_key_order=None):
    mesh = get_objects()[mesh_name]
    if not has_shapekeys(mesh):
        return
    set_active(mesh)

    if not shape_key_order:
        shape_key_order = []

    order = [
        'Basis',
        'vrc.blink_left',
        'vrc.blink_right',
        'vrc.lowerlid_left',
        'vrc.lowerlid_right',
        'vrc.v_aa',
        'vrc.v_ch',
        'vrc.v_dd',
        'vrc.v_e',
        'vrc.v_ff',
        'vrc.v_ih',
        'vrc.v_kk',
        'vrc.v_nn',
        'vrc.v_oh',
        'vrc.v_ou',
        'vrc.v_pp',
        'vrc.v_rr',
        'vrc.v_sil',
        'vrc.v_ss',
        'vrc.v_th',
        'Basis Original'
    ]

    for shape in shape_key_order:
        if shape not in order:
            order.append(shape)

    wm = bpy.context.window_manager
    current_step = 0
    wm.progress_begin(current_step, len(order))

    i = 0
    for name in order:
        if name == 'Basis' and 'Basis' not in mesh.data.shape_keys.key_blocks:
            i += 1
            current_step += 1
            wm.progress_update(current_step)
            continue

        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if shapekey.name == name:

                mesh.active_shape_key_index = index
                new_index = i
                index_diff = (index - new_index)

                if new_index >= len(mesh.data.shape_keys.key_blocks):
                    bpy.ops.object.shape_key_move(type='BOTTOM')
                    break

                position_correct = False
                if 0 <= index_diff <= (new_index - 1):
                    while position_correct is False:
                        if mesh.active_shape_key_index != new_index:
                            bpy.ops.object.shape_key_move(type='UP')
                        else:
                            position_correct = True
                else:
                    if mesh.active_shape_key_index > new_index:
                        bpy.ops.object.shape_key_move(type='TOP')

                    position_correct = False
                    while position_correct is False:
                        if mesh.active_shape_key_index != new_index:
                            bpy.ops.object.shape_key_move(type='DOWN')
                        else:
                            position_correct = True

                i += 1
                break

        current_step += 1
        wm.progress_update(current_step)

    mesh.active_shape_key_index = 0

    wm.progress_end()


def isEmptyGroup(group_name):
    mesh = get_objects().get('Body')
    if mesh is None:
        return True
    vgroup = mesh.vertex_groups.get(group_name)
    if vgroup is None:
        return True

    for vert in mesh.data.vertices:
        for group in vert.groups:
            if group.group == vgroup.index:
                if group.weight > 0:
                    return False

    return True


def removeEmptyGroups(obj, thres=0):
    z = []
    for v in obj.data.vertices:
        for g in v.groups:
            if g.weight > thres:
                if g not in z:
                    z.append(obj.vertex_groups[g.group])
    for r in obj.vertex_groups:
        if r not in z:
            obj.vertex_groups.remove(r)


def removeZeroVerts(obj, thres=0):
    for v in obj.data.vertices:
        z = []
        for g in v.groups:
            if not g.weight > thres:
                z.append(g)
        for r in z:
            obj.vertex_groups[g.group].remove([v.index])


def delete_hierarchy(parent):
    unselect_all()
    to_delete = []

    def get_child_names(obj):
        for child in obj.children:
            to_delete.append(child)
            if child.children:
                get_child_names(child)

    get_child_names(parent)
    to_delete.append(parent)

    objs = bpy.data.objects
    for obj in to_delete:
        objs.remove(objs[obj.name], do_unlink=True)


def delete(obj):
    if obj.parent:
        for child in obj.children:
            child.parent = obj.parent

    objs = bpy.data.objects
    objs.remove(objs[obj.name], do_unlink=True)


def days_between(d1, d2, time_format):
    d1 = datetime.strptime(d1, time_format)
    d2 = datetime.strptime(d2, time_format)
    return abs((d2 - d1).days)


def delete_bone_constraints(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature

    armature = get_armature(armature_name=armature_name)
    switch('POSE')

    for bone in armature.pose.bones:
        if len(bone.constraints) > 0:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)

    switch('EDIT')


def delete_zero_weight(armature_name=None, ignore=''):
    if not armature_name:
        armature_name = bpy.context.scene.armature

    armature = get_armature(armature_name=armature_name)
    switch('EDIT')

    bone_names_to_work_on = set([bone.name for bone in armature.data.edit_bones])

    bone_name_to_edit_bone = dict()
    for edit_bone in armature.data.edit_bones:
        bone_name_to_edit_bone[edit_bone.name] = edit_bone

    vertex_group_names_used = set()
    vertex_group_name_to_objects_having_same_named_vertex_group = dict()
    for objects in get_meshes_objects(armature_name=armature_name):
        vertex_group_id_to_vertex_group_name = dict()
        for vertex_group in objects.vertex_groups:
            vertex_group_id_to_vertex_group_name[vertex_group.index] = vertex_group.name
            if vertex_group.name not in vertex_group_name_to_objects_having_same_named_vertex_group:
                vertex_group_name_to_objects_having_same_named_vertex_group[vertex_group.name] = set()
            vertex_group_name_to_objects_having_same_named_vertex_group[vertex_group.name].add(objects)
        for vertex in objects.data.vertices:
            for group in vertex.groups:
                if group.weight > 0:
                    vertex_group_names_used.add(vertex_group_id_to_vertex_group_name.get(group.group))

    not_used_bone_names = bone_names_to_work_on - vertex_group_names_used

    count = 0
    for bone_name in not_used_bone_names:
        if not bpy.context.scene.keep_end_bones or not is_end_bone(bone_name, armature_name):
            if bone_name not in Bones.dont_delete_these_bones and 'Root_' not in bone_name and bone_name != ignore:
                armature.data.edit_bones.remove(bone_name_to_edit_bone[bone_name])  # delete bone
                count += 1
                if bone_name in vertex_group_name_to_objects_having_same_named_vertex_group:
                    for objects in vertex_group_name_to_objects_having_same_named_vertex_group[bone_name]:  # delete vertex groups
                        vertex_group = objects.vertex_groups.get(bone_name)
                        if vertex_group is not None:
                            objects.vertex_groups.remove(vertex_group)

    return count


def remove_unused_objects():
    default_scene_objects = []
    for obj in get_objects():
        if (obj.type == 'CAMERA' and obj.name == 'Camera') \
                or (obj.type == 'LAMP' and obj.name == 'Lamp') \
                or (obj.type == 'LIGHT' and obj.name == 'Light') \
                or (obj.type == 'MESH' and obj.name == 'Cube'):
            default_scene_objects.append(obj)

    if len(default_scene_objects) == 3:
        for obj in default_scene_objects:
            delete_hierarchy(obj)


def remove_no_user_objects():
    # print('\nREMOVE OBJECTS')
    for block in get_objects():
        # print(block.name, block.users)
        if block.users == 0:
            print('Removing obj ', block.name)
            delete(block)
    # print('\nREMOVE MESHES')
    for block in bpy.data.meshes:
        # print(block.name, block.users)
        if block.users == 0:
            print('Removing mesh ', block.name)
            bpy.data.meshes.remove(block)
    # print('\nREMOVE MATERIALS')
    for block in bpy.data.materials:
        # print(block.name, block.users)
        if block.users == 0:
            print('Removing material ', block.name)
            bpy.data.materials.remove(block)

    # print('\nREMOVE MATS')
    # for block in bpy.data.materials:
    #     print(block.name, block.users)
    #     if block.users == 0:
    #         bpy.data.materials.remove(block)


def is_end_bone(name, armature_name):
    armature = get_armature(armature_name=armature_name)
    end_bone = armature.data.edit_bones.get(name)
    if end_bone and end_bone.parent and len(end_bone.parent.children) == 1:
        return True
    return False


def correct_bone_positions(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature
    armature = get_armature(armature_name=armature_name)

    upper_chest = armature.data.edit_bones.get('Upper Chest')
    chest = armature.data.edit_bones.get('Chest')
    neck = armature.data.edit_bones.get('Neck')
    head = armature.data.edit_bones.get('Head')
    if chest and neck:
        if upper_chest and bpy.context.scene.keep_upper_chest:
            chest.tail = upper_chest.head
            upper_chest.tail = neck.head
        else:
            chest.tail = neck.head
    if neck and head:
        neck.tail = head.head

    if 'Left shoulder' in armature.data.edit_bones:
        if 'Left arm' in armature.data.edit_bones:
            if 'Left elbow' in armature.data.edit_bones:
                if 'Left wrist' in armature.data.edit_bones:
                    shoulder = armature.data.edit_bones.get('Left shoulder')
                    arm = armature.data.edit_bones.get('Left arm')
                    elbow = armature.data.edit_bones.get('Left elbow')
                    wrist = armature.data.edit_bones.get('Left wrist')
                    shoulder.tail = arm.head
                    arm.tail = elbow.head
                    elbow.tail = wrist.head

    if 'Right shoulder' in armature.data.edit_bones:
        if 'Right arm' in armature.data.edit_bones:
            if 'Right elbow' in armature.data.edit_bones:
                if 'Right wrist' in armature.data.edit_bones:
                    shoulder = armature.data.edit_bones.get('Right shoulder')
                    arm = armature.data.edit_bones.get('Right arm')
                    elbow = armature.data.edit_bones.get('Right elbow')
                    wrist = armature.data.edit_bones.get('Right wrist')
                    shoulder.tail = arm.head
                    arm.tail = elbow.head
                    elbow.tail = wrist.head

    if 'Left leg' in armature.data.edit_bones:
        if 'Left knee' in armature.data.edit_bones:
            if 'Left ankle' in armature.data.edit_bones:
                leg = armature.data.edit_bones.get('Left leg')
                knee = armature.data.edit_bones.get('Left knee')
                ankle = armature.data.edit_bones.get('Left ankle')

                if 'Left leg 2' in armature.data.edit_bones:
                    leg = armature.data.edit_bones.get('Left leg 2')

                leg.tail = knee.head
                knee.tail = ankle.head

    if 'Right leg' in armature.data.edit_bones:
        if 'Right knee' in armature.data.edit_bones:
            if 'Right ankle' in armature.data.edit_bones:
                leg = armature.data.edit_bones.get('Right leg')
                knee = armature.data.edit_bones.get('Right knee')
                ankle = armature.data.edit_bones.get('Right ankle')

                if 'Right leg 2' in armature.data.edit_bones:
                    leg = armature.data.edit_bones.get('Right leg 2')

                leg.tail = knee.head
                knee.tail = ankle.head


dpi_scale = 3
error = []
override = False


def show_error(scale, error_list, override_header=False):
    global override, dpi_scale, error
    override = override_header
    dpi_scale = scale

    if type(error_list) is str:
        error_list = error_list.split('\n')

    error = error_list

    header = t('ShowError.label')
    if override:
        header = error_list[0]

    ShowError.bl_label = header
    try:
        bpy.utils.register_class(ShowError)
    except ValueError:
        bpy.utils.unregister_class(ShowError)
        bpy.utils.register_class(ShowError)

    bpy.ops.cats_common.show_error('INVOKE_DEFAULT')

    print('')
    print('Report: Error')
    for line in error:
        print('    ' + line)


@register_wrap
class ShowError(bpy.types.Operator):
    bl_idname = 'cats_common.show_error'
    bl_label = t('ShowError.label')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * dpi_scale))

    def draw(self, context):
        if not error or len(error) == 0:
            return

        if override and len(error) == 1:
            return

        layout = self.layout
        col = layout.column(align=True)

        first_line = False
        for i, line in enumerate(error):
            if i == 0 and override:
                continue
            if line == '':
                col.separator()
            else:
                row = col.row(align=True)
                row.scale_y = 0.85
                if not first_line:
                    row.label(text=line, icon='ERROR')
                    first_line = True
                else:
                    row.label(text=line, icon_value=Supporter.preview_collections["custom_icons"]["empty"].icon_id)


def remove_doubles(mesh, threshold, save_shapes=True):
    if not mesh:
        return 0

    # If the mesh has no shapekeys, don't remove doubles
    if not has_shapekeys(mesh) or len(mesh.data.shape_keys.key_blocks) == 1:
        return 0

    pre_tris = len(mesh.data.polygons)

    set_active(mesh)
    switch('EDIT')
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')

    if save_shapes and has_shapekeys(mesh):
        switch('OBJECT')
        for kb in mesh.data.shape_keys.key_blocks:
            i = 0
            for v0, v1 in zip(kb.relative_key.data, kb.data):
                if v0.co != v1.co:
                    mesh.data.vertices[i].select = True
                i += 1
        switch('EDIT')
        bpy.ops.mesh.select_all(action='INVERT')
    else:
        bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.mesh.remove_doubles(threshold=threshold)
    bpy.ops.mesh.select_all(action='DESELECT')
    switch('OBJECT')

    return pre_tris - len(mesh.data.polygons)


def get_tricount(obj):
    # Triangulates with Bmesh to avoid messing with the original geometry
    bmesh_mesh = bmesh.new()
    bmesh_mesh.from_mesh(obj.data)

    bmesh.ops.triangulate(bmesh_mesh, faces=bmesh_mesh.faces[:])
    return len(bmesh_mesh.faces)


def get_bone_orientations(armature):
    x_cord = 0
    y_cord = 1
    z_cord = 2
    fbx = False
    # armature = get_armature()
    #
    # for index, bone in enumerate(armature.pose.bones):
    #     if 'Head' in bone.name:
    #     #if index == 5:
    #         bone_pos = bone.matrix
    #         print(bone_pos)
    #         world_pos = armature.matrix_world * bone.matrix
    #         print(world_pos)
    #         print(bone_pos[0][0], world_pos[0][0])
    #         if round(abs(bone_pos[0][0]), 4) != round(abs(world_pos[0][0]), 4):
    #             z_cord = 1
    #             y_cord = 2
    #             fbx = True
    #             break

    return x_cord, y_cord, z_cord, fbx


def clean_material_names(mesh):
    for j, mat in enumerate(mesh.material_slots):
        if mat.name.endswith('.001'):
            mesh.active_material_index = j
            mesh.active_material.name = mat.name[:-4]
        if mat.name.endswith(('. 001', ' .001')):
            mesh.active_material_index = j
            mesh.active_material.name = mat.name[:-5]


def mix_weights(mesh, vg_from, vg_to, mix_strength=1.0, mix_mode='ADD', delete_old_vg=True):
    mesh.active_shape_key_index = 0
    mod = mesh.modifiers.new("VertexWeightMix", 'VERTEX_WEIGHT_MIX')
    mod.vertex_group_a = vg_to
    mod.vertex_group_b = vg_from
    mod.mix_mode = mix_mode
    mod.mix_set = 'B'
    mod.mask_constant = mix_strength
    apply_modifier(mod)
    if delete_old_vg:
        mesh.vertex_groups.remove(mesh.vertex_groups.get(vg_from))
    mesh.active_shape_key_index = 0  # This line fixes a visual bug in 2.80 which causes random weights to be stuck after being merged


def get_user_preferences():
    return bpy.context.user_preferences if hasattr(bpy.context, 'user_preferences') else bpy.context.preferences


def has_shapekeys(mesh):
    if not hasattr(mesh.data, 'shape_keys'):
        return False
    return hasattr(mesh.data.shape_keys, 'key_blocks')


def matmul(a, b):
    if version_2_79_or_older():
        return a * b
    return a @ b


def ui_refresh():
    # A way to refresh the ui
    refreshed = False
    while not refreshed:
        if hasattr(bpy.data, 'window_managers'):
            for windowManager in bpy.data.window_managers:
                for window in windowManager.windows:
                    for area in window.screen.areas:
                        area.tag_redraw()
            refreshed = True
            # print('Refreshed UI')
        else:
            time.sleep(0.5)


def fix_zero_length_bones(armature, x_cord, y_cord, z_cord):
    pre_mode = armature.mode
    set_active(armature)
    switch('EDIT')

    for bone in armature.data.edit_bones:
        if round(bone.head[x_cord], 4) == round(bone.tail[x_cord], 4) \
                and round(bone.head[y_cord], 4) == round(bone.tail[y_cord], 4) \
                and round(bone.head[z_cord], 4) == round(bone.tail[z_cord], 4):
            bone.tail[z_cord] += 0.1

    switch(pre_mode)


def fix_bone_orientations(armature):
    # Connect all bones with their children if they have exactly one
    for bone in armature.data.edit_bones:
        if len(bone.children) == 1 and bone.name not in ['LeftEye', 'RightEye', 'Head', 'Hips']:
            p1 = bone.head
            p2 = bone.children[0].head
            dist = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2) ** (1/2)

            # Only connect them if the other bone is a certain distance away, otherwise blender will delete them
            if dist > 0.005:
                bone.tail = bone.children[0].head
                if len(bone.parent.children) == 1:  # if the bone's parent bone only has one child, connect the bones (Don't connect them all because that would mess up hand/finger bones)
                    bone.use_connect = True


def update_material_list(self=None, context=None):
    try:
        if hasattr(bpy.context.scene, 'smc_ob_data') and bpy.context.scene.smc_ob_data:
            bpy.ops.smc.refresh_ob_data()
    except AttributeError:
        print('Material Combiner not found')


def unify_materials():
    textures = []  # TODO

    for ob in get_objects():
        if ob.type == "MESH":
            for mat_slot in ob.material_slots:
                if mat_slot.material:
                    mat_slot.material.blend_method = 'HASHED'
                    # mat_slot.material.blend_method = 'BLEND'  # Use this for transparent textures only
                    print('MAT: ', mat_slot.material.name)
                    if mat_slot.material.node_tree:
                        nodes = mat_slot.material.node_tree.nodes
                        image = None
                        for node in nodes:
                            # print(' ' + node.name + ', ' + node.type + ', ' + node.label)
                            if node.type == 'TEX_IMAGE' and 'toon' not in node.name and 'sphere' not in node.name:
                                image = node.image
                                # textures.append(node.image.name)
                            mat_slot.material.node_tree.nodes.remove(node)

                        # Create Image node
                        node_texture = nodes.new(type='ShaderNodeTexImage')
                        node_texture.location = 0, 0
                        node_texture.image = image
                        node_texture.label = 'Cats Texture'

                        # Create Principled BSDF node
                        node_prinipled = nodes.new(type='ShaderNodeBsdfPrincipled')
                        node_prinipled.location = 300, -220
                        node_prinipled.label = 'Cats Emission'
                        node_prinipled.inputs['Specular'].default_value = 0
                        node_prinipled.inputs['Roughness'].default_value = 0
                        node_prinipled.inputs['Sheen Tint'].default_value = 0
                        node_prinipled.inputs['Clearcoat Roughness'].default_value = 0
                        node_prinipled.inputs['IOR'].default_value = 0

                        # Create Transparency BSDF node
                        node_transparent = nodes.new(type='ShaderNodeBsdfTransparent')
                        node_transparent.location = 325, -100
                        node_transparent.label = 'Cats Transparency'

                        # Create Mix Shader node
                        node_mix = nodes.new(type='ShaderNodeMixShader')
                        node_mix.location = 600, 0
                        node_mix.label = 'Cats Mix'

                        # Create Output node
                        node_output = nodes.new(type='ShaderNodeOutputMaterial')
                        node_output.location = 800, 0
                        node_output.label = 'Cats Output'

                        # Create 2nd Output node
                        node_output2 = nodes.new(type='ShaderNodeOutputMaterial')
                        node_output2.location = 800, -200
                        node_output2.label = 'Cats Export'

                        # Link nodes together
                        mat_slot.material.node_tree.links.new(node_texture.outputs['Color'], node_prinipled.inputs['Base Color'])
                        mat_slot.material.node_tree.links.new(node_texture.outputs['Alpha'], node_mix.inputs['Fac'])

                        mat_slot.material.node_tree.links.new(node_prinipled.outputs['BSDF'], node_mix.inputs[2])
                        mat_slot.material.node_tree.links.new(node_transparent.outputs['BSDF'], node_mix.inputs[1])

                        mat_slot.material.node_tree.links.new(node_mix.outputs['Shader'], node_output.inputs['Surface'])

                        mat_slot.material.node_tree.links.new(node_prinipled.outputs['BSDF'], node_output2.inputs['Surface'])

                    # break

    print(textures, len(textures))
    return {'FINISHED'}


def add_principled_shader(mesh):
    # This adds a principled shader and material output node in order for
    # Unity to automatically detect exported materials
    principled_shader_pos = (501, -500)
    output_shader_pos = (801, -500)
    principled_shader_label = 'Cats Export Shader'
    output_shader_label = 'Cats Export'

    for mat_slot in mesh.material_slots:
        if mat_slot.material and mat_slot.material.node_tree:
            nodes = mat_slot.material.node_tree.nodes
            node_image = None
            node_image_count = 0

            # Check if the new nodes should be added and to which image node they should be attached to
            for node in nodes:
                # Cancel if the cats nodes are already found
                if node.type == 'BSDF_PRINCIPLED' and node.label == principled_shader_label:
                    node_image = None
                    break
                if node.type == 'OUTPUT_MATERIAL' and node.label == output_shader_label:
                    node_image = None
                    break

                # Skip if this node is not an image node
                if node.type != 'TEX_IMAGE':
                    continue
                node_image_count += 1

                # If an mmd_texture is found, link it to the principled shader later
                if node.name == 'mmd_base_tex' or node.label == 'MainTexture':
                    node_image = node
                    node_image_count = 0
                    break

                # This is an image node, so link it to the principled shader later
                node_image = node

            if not node_image or node_image_count > 1:
                continue

            # Create Principled BSDF node
            node_prinipled = nodes.new(type='ShaderNodeBsdfPrincipled')
            node_prinipled.label = 'Cats Export Shader'
            node_prinipled.location = principled_shader_pos
            node_prinipled.inputs['Specular'].default_value = 0
            node_prinipled.inputs['Roughness'].default_value = 0
            node_prinipled.inputs['Sheen Tint'].default_value = 0
            node_prinipled.inputs['Clearcoat Roughness'].default_value = 0
            node_prinipled.inputs['IOR'].default_value = 0

            # Create Output node for correct image exports
            node_output = nodes.new(type='ShaderNodeOutputMaterial')
            node_output.label = 'Cats Export'
            node_output.location = output_shader_pos

            # Link nodes together
            mat_slot.material.node_tree.links.new(node_image.outputs['Color'], node_prinipled.inputs['Base Color'])
            mat_slot.material.node_tree.links.new(node_prinipled.outputs['BSDF'], node_output.inputs['Surface'])


def remove_toon_shader(mesh):
    for mat_slot in mesh.material_slots:
        if mat_slot.material and mat_slot.material.node_tree:
            nodes = mat_slot.material.node_tree.nodes
            for node in nodes:
                if node.name == 'mmd_toon_tex':
                    print('Toon tex removed from material', mat_slot.material.name)
                    nodes.remove(node)
                    # if not node.image or not node.image.filepath:
                    #     print('Toon tex removed: Empty, from material', mat_slot.material.name)
                    #     nodes.remove(node)
                    #     continue
                    #
                    # image_filepath = bpy.path.abspath(node.image.filepath)
                    # if not os.path.isfile(image_filepath):
                    #     print('Toon tex removed:', node.image.name, 'from material', mat_slot.material.name)
                    #     nodes.remove(node)


def fix_mmd_shader(mesh):
    for mat_slot in mesh.material_slots:
        if mat_slot.material and mat_slot.material.node_tree:
            nodes = mat_slot.material.node_tree.nodes
            for node in nodes:
                if node.name == 'mmd_shader':
                    node.inputs['Reflect'].default_value = 1


def fix_vrm_shader(mesh):
    for mat_slot in mesh.material_slots:
        if mat_slot.material and mat_slot.material.node_tree:
            is_vrm_mat = False
            nodes = mat_slot.material.node_tree.nodes
            for node in nodes:
                if hasattr(node, 'node_tree') and 'MToon_unversioned' in node.node_tree.name:
                    node.location[0] = 200
                    node.inputs['ReceiveShadow_Texture_alpha'].default_value = -10000
                    node.inputs['ShadeTexture'].default_value = (1.0, 1.0, 1.0, 1.0)
                    node.inputs['Emission_Texture'].default_value = (0.0, 0.0, 0.0, 0.0)
                    node.inputs['SphereAddTexture'].default_value = (0.0, 0.0, 0.0, 0.0)

                    # Support typo in old vrm importer
                    node_input = node.inputs.get('NomalmapTexture')
                    if not node_input:
                        node_input = node.inputs.get('NormalmapTexture')
                    node_input.default_value = (1.0, 1.0, 1.0, 1.0)

                    is_vrm_mat = True
                    break
            if not is_vrm_mat:
                continue

            nodes_to_keep = ['DiffuseColor', 'MainTexture', 'Emission_Texture']
            if 'HAIR' in mat_slot.material.name:
                nodes_to_keep = ['DiffuseColor', 'MainTexture', 'Emission_Texture', 'SphereAddTexture']

            for node in nodes:
                # Delete all unneccessary nodes
                if 'RGB' in node.name \
                        or 'Value' in node.name \
                        or 'Image Texture' in node.name \
                        or 'UV Map' in node.name \
                        or 'Mapping' in node.name:
                    if node.label not in nodes_to_keep:
                        for output in node.outputs:
                            for link in output.links:
                                mat_slot.material.node_tree.links.remove(link)
                        continue

                # if hasattr(node, 'node_tree') and 'matcap_vector' in node.node_tree.name:
                #     for output in node.outputs:
                #         for link in output.links:
                #             mat_slot.material.node_tree.links.remove(link)
                #     continue


def fix_twist_bones(mesh, bones_to_delete):
    # This will fix MMD twist bones

    for bone_type in ['Hand', 'Arm']:
        for suffix in ['L', 'R']:
            prefix = 'Left' if suffix == 'L' else 'Right'
            bone_parent_name = prefix + ' ' + ('elbow' if bone_type == 'Hand' else 'arm')

            vg_twist = mesh.vertex_groups.get(bone_type + 'Twist_' + suffix)
            vg_parent = mesh.vertex_groups.get(bone_parent_name)

            if not vg_twist:
                print('1. no ' + bone_type + 'Twist_' + suffix)
                continue
            if not vg_parent:
                print('2. no ' + bone_parent_name)
                vg_parent = mesh.vertex_groups.new(name=bone_parent_name)

            vg_twist1 = mesh.vertex_groups.get(bone_type + 'Twist1_' + suffix)
            vg_twist2 = mesh.vertex_groups.get(bone_type + 'Twist2_' + suffix)
            vg_twist3 = mesh.vertex_groups.get(bone_type + 'Twist3_' + suffix)

            mix_weights(mesh, vg_twist.name, vg_parent.name, mix_strength=0.2, delete_old_vg=False)
            mix_weights(mesh, vg_twist.name, vg_twist.name, mix_strength=0.2, mix_mode='SUB', delete_old_vg=False)

            if vg_twist1:
                bones_to_delete.append(vg_twist1.name)
                mix_weights(mesh, vg_twist1.name, vg_twist.name, mix_strength=0.25, delete_old_vg=False)
                mix_weights(mesh, vg_twist1.name, vg_parent.name, mix_strength=0.75)

            if vg_twist2:
                bones_to_delete.append(vg_twist2.name)
                mix_weights(mesh, vg_twist2.name, vg_twist.name, mix_strength=0.5, delete_old_vg=False)
                mix_weights(mesh, vg_twist2.name, vg_parent.name, mix_strength=0.5)

            if vg_twist3:
                bones_to_delete.append(vg_twist3.name)
                mix_weights(mesh, vg_twist3.name, vg_twist.name, mix_strength=0.75, delete_old_vg=False)
                mix_weights(mesh, vg_twist3.name, vg_parent.name, mix_strength=0.25)


def fix_twist_bone_names(armature):
    # This will fix MMD twist bone names after the vertex groups have been fixed
    for bone_type in ['Hand', 'Arm']:
        for suffix in ['L', 'R']:
            bone_twist = armature.data.edit_bones.get(bone_type + 'Twist_' + suffix)
            if bone_twist:
                bone_twist.name = 'z' + bone_twist.name


def toggle_mmd_tabs_update(self, context):
    toggle_mmd_tabs()


def toggle_mmd_tabs(shutdown_plugin=False):
    mmd_cls = [
        mmd_tool.MMDToolsObjectPanel,
        mmd_tool.MMDDisplayItemsPanel,
        mmd_tool.MMDMorphToolsPanel,
        mmd_tool.MMDRigidbodySelectorPanel,
        mmd_tool.MMDJointSelectorPanel,
        mmd_util_tools.MMDMaterialSorter,
        mmd_util_tools.MMDMeshSorter,
    ]
    mmd_cls_shading = [
        mmd_view_prop.MMDViewPanel,
        mmd_view_prop.MMDSDEFPanel,
    ]

    if not version_2_79_or_older():
        mmd_cls = mmd_cls + mmd_cls_shading

    # If the plugin is shutting down, load the mmd_tools tabs before that, to avoid issues when unregistering mmd_tools
    if bpy.context.scene.show_mmd_tabs or shutdown_plugin:
        for cls in mmd_cls:
            try:
                bpy.utils.register_class(cls)
            except:
                pass
    else:
        for cls in reversed(mmd_cls):
            try:
                bpy.utils.unregister_class(cls)
            except:
                pass

    if not shutdown_plugin:
        Settings.update_settings(None, None)



"""
HTML <-> text conversions.
http://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
"""


class _HTMLToText(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._buf = []
        self.hide_output = False

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'br') and not self.hide_output:
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = True

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self._buf.append('\n')

    def handle_endtag(self, tag):
        if tag == 'p':
            self._buf.append('\n')
        elif tag in ('script', 'style'):
            self.hide_output = False

    def handle_data(self, text):
        if text and not self.hide_output:
            self._buf.append(re.sub(r'\s+', ' ', text))

    def handle_entityref(self, name):
        if name in name2codepoint and not self.hide_output:
            c = chr(name2codepoint[name])
            self._buf.append(c)

    def handle_charref(self, name):
        if not self.hide_output:
            n = int(name[1:], 16) if name.startswith('x') else int(name)
            self._buf.append(chr(n))

    def get_text(self):
        return re.sub(r' +', ' ', ''.join(self._buf))


def html_to_text(html):
    """
    Given a piece of HTML, return the plain text it contains.
    This handles entities and char refs, but not javascript and stylesheets.
    """
    parser = _HTMLToText()
    try:
        parser.feed(html)
        parser.close()
    except:  # HTMLParseError: No good replacement?
        pass
    return parser.get_text()


""" === THIS CODE COULD BE USEFUL === """

# def addvertex(meshname, shapekey_name):
#     mesh = get_objects()[meshname].data
#     bm = bmesh.new()
#     bm.from_mesh(mesh)
#     bm.verts.ensure_lookup_table()
#
#     print(" ")
#     if shapekey_name in bm.verts.layers.shape.keys():
#         val = bm.verts.layers.shape.get(shapekey_name)
#         print("%s = %s" % (shapekey_name, val))
#         sk = mesh.shape_keys.key_blocks[shapekey_name]
#         print("v=%f, f=%f" % (sk.value, sk.frame))
#         for i in range(len(bm.verts)):
#             v = bm.verts[i]
#             delta = v[val] - v.co
#             if (delta.length > 0):
#                 print("v[%d]+%s" % (i, delta))
#
#     print(" ")

# === THIS CODE COULD BE USEFUL ===

# Check which shape keys will be deleted on export by Blender
# def checkshapekeys():
#     for ob in get_objects():
#         if ob.type == 'MESH':
#             mesh = ob
#     bm = bmesh.new()
#     bm.from_mesh(mesh.data)
#     bm.verts.ensure_lookup_table()
#
#     deleted_shapes = []
#     for key in bm.verts.layers.shape.keys():
#         if key == 'Basis':
#             continue
#         val = bm.verts.layers.shape.get(key)
#         delete = True
#         for vert in bm.verts:
#             delta = vert[val] - vert.co
#             if delta.length > 0:
#                 delete = False
#                 break
#         if delete:
#             deleted_shapes.append(key)
#
#     return deleted_shapes

# # Repair vrc shape keys old
# def repair_shapekeys():
#     for ob in get_objects():
#         if ob.type == 'MESH':
#             mesh = ob
#             bm = bmesh.new()
#             bm.from_mesh(mesh.data)
#             bm.verts.ensure_lookup_table()
#
#             for key in bm.verts.layers.shape.keys():
#                 if not key.startswith('vrc'):
#                     continue
#
#                 value = bm.verts.layers.shape.get(key)
#                 for vert in bm.verts:
#                     shapekey = vert
#                     shapekey_coords = mesh.matrix_world * shapekey[value]
#                     shapekey_coords[2] -= 0.00001
#                     shapekey[value] = mesh.matrix_world.inverted() * shapekey_coords
#                     break
#
#             bm.to_mesh(mesh.data)

# === THIS CODE COULD BE USEFUL ===
