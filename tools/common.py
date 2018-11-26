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

from datetime import datetime

import bpy
import bmesh
import numpy as np
import tools.supporter
import tools.decimation
import tools.translate
import tools.armature_bones as Bones
from mathutils import Vector
from math import degrees
from collections import OrderedDict
from tools.register import register_wrap

from googletrans import Translator
from mmd_tools_local import utils

from html.parser import HTMLParser
from html.entities import name2codepoint
import re

# TODO
# - Add check if hips bone really needs to be rotated
# - Reset Pivot
# - Manual bone selection button for root bones
# - Checkbox for eye blinking/moving
# - Translate progress bar
# - Eye tracking should remove vertex group from eye if there is one already bound to it and "No Movement" is checked
# - Eye tracking test add reset blink
# - Eye tracking test set subcol like in updater


shapekey_order = None
version_str = ''


def get_armature(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE' and obj.name == armature_name:
            return obj
    return None


def get_armature_objects():
    armatures = []
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armatures.append(obj)
    return armatures


def get_top_parent(child):
    if child.parent:
        return get_top_parent(child.parent)
    return child


def unhide_all(everything=False, obj_to_unhide=None):
    if not obj_to_unhide:
        obj_to_unhide = get_armature()

    if version_2_79_or_older():
        if everything or not obj_to_unhide:
            for obj in bpy.data.objects:
                obj.hide = False
        else:
            def unhide_children(parent):
                for child in parent.children:
                    child.hide = False
                    unhide_children(child)

            top_parent = get_top_parent(obj_to_unhide)
            top_parent.hide = False
            unhide_children(top_parent)
    else:
        for obj in bpy.data.collections:
            obj.hide_viewport = False


def unselect_all():
    for obj in bpy.data.objects:
        select(obj, False)


def set_active(obj):
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
    if version_2_79_or_older():
        obj.hide = val
    else:
        obj.hide_viewport = val


def is_hidden(obj):
    if version_2_79_or_older():
        return obj.hide
    return obj.hide_viewport


def switch(new_mode):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=new_mode, toggle=False)


def set_default_stage_old():
    switch('OBJECT')
    unhide_all()
    unselect_all()
    armature = get_armature()
    set_active(armature)
    return armature


def set_default_stage(everything=False):
    unhide_all(everything=everything)
    unselect_all()

    for obj in bpy.data.objects:
        set_active(obj)
        switch('OBJECT')
        if obj.type == 'ARMATURE':
            obj.data.pose_position = 'REST'

        select(obj, False)

    armature = get_armature()
    if armature:
        set_active(armature)
    return armature


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
    unselect_all()
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            ob.update_from_editmode()

            vgroup_used = {i: False for i, k in enumerate(ob.vertex_groups)}

            for v in ob.data.vertices:
                for g in v.groups:
                    if g.weight > 0.0:
                        vgroup_used[g.group] = True

            for i, used in sorted(vgroup_used.items(), reverse=True):
                if not used:
                    if ignore_main_bones and ob.vertex_groups[i].name in Bones.dont_delete_these_main_bones:
                        continue
                    ob.vertex_groups.remove(ob.vertex_groups[i])


def find_center_vector_of_vertex_group(mesh_name, vertex_group):
    mesh = bpy.data.objects[mesh_name]

    data = mesh.data
    verts = data.vertices
    verts_in_group = []

    for vert in verts:
        i = vert.index
        try:
            mesh.vertex_groups[vertex_group].weight(i)
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


def get_meshes(self, context):
    # Modes:
    # 0 = With Armature only
    # 1 = Without armature only
    # 2 = All meshes

    choices = []

    for mesh in get_meshes_objects(mode=0):
        choices.append((mesh.name, mesh.name, mesh.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_top_meshes(self, context):
    choices = []

    for mesh in get_meshes_objects(mode=1):
        choices.append((mesh.name, mesh.name, mesh.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_all_meshes(self, context):
    choices = []

    for mesh in get_meshes_objects(mode=2):
        choices.append((mesh.name, mesh.name, mesh.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_armature_list(self, context):
    choices = []

    for object in context.scene.objects:
        if object.type == 'ARMATURE':
            # 1. Will be returned by context.scene
            # 2. Will be shown in lists
            # 3. will be shown in the hover description (below description)

            # Set name displayed in list
            name = object.data.name
            if name.startswith('Armature ('):
                name = object.name + ' (' + name.replace('Armature (', '')[:-1] + ')'

            choices.append((object.name, name, object.name))

    if len(choices) == 0:
        choices.append(('None', 'None', 'None'))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_armature_merge_list(self, context):
    choices = []
    current_armature = context.scene.merge_armature_into

    for obj in context.scene.objects:
        if obj.type == 'ARMATURE' and obj.name != current_armature:
            # 1. Will be returned by context.scene
            # 2. Will be shown in lists
            # 3. will be shown in the hover description (below description)

            # Set name displayed in list
            name = obj.data.name
            if name.startswith('Armature ('):
                name = obj.name + ' (' + name.replace('Armature (', '')[:-1] + ')'

            choices.append((obj.name, name, obj.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_meshes_decimation(self, context):
    choices = []

    for object in bpy.context.scene.objects:
        if object.type == 'MESH':
            if object.parent is not None and object.parent.type == 'ARMATURE' and object.parent.name == bpy.context.scene.armature:
                if object.name in tools.decimation.ignore_meshes:
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
def get_bones(names=None, armature_name=None):
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

    for choice in choices:
        choices2.append(choice)

    bpy.types.Object.Enum = choices2

    return bpy.types.Object.Enum


def get_shapekeys_mouth_ah(self, context):
    return get_shapekeys(context, ['Ah', 'A'], True, False, False, False)


def get_shapekeys_mouth_oh(self, context):
    return get_shapekeys(context, ['Oh', 'O', 'Your'], True, False, False, False)


def get_shapekeys_mouth_ch(self, context):
    return get_shapekeys(context, ['Glue', 'Ch', 'I', 'There'], True, False, False, False)


def get_shapekeys_eye_blink_l(self, context):
    return get_shapekeys(context, ['Wink 2', 'Wink', 'Wink left', 'Wink Left', 'Blink (Left)', 'Blink', 'Basis'], False, False, False, False)


def get_shapekeys_eye_blink_r(self, context):
    return get_shapekeys(context, ['Wink 2 right', 'Wink 2 Right', 'Wink right 2', 'Wink Right 2', 'Wink right', 'Wink Right', 'Blink (Right)', 'Basis'], False, False, False, False)


def get_shapekeys_eye_low_l(self, context):
    return get_shapekeys(context, ['Basis'], False, False, False, False)


def get_shapekeys_eye_low_r(self, context):
    return get_shapekeys(context, ['Basis'], False, False, False, False)


def get_shapekeys_decimation(self, context):
    return get_shapekeys(context,
                         ['Ah', 'A', 'Oh', 'O', 'Your', 'Glue', 'Ch', 'I', 'There', 'Wink 2', 'Wink', 'Wink left', 'Wink Left', 'Blink (Left)', 'Wink 2 right',
                          'Wink 2 Right', 'Wink right 2', 'Wink Right 2', 'Wink right', 'Wink Right', 'Blink (Right)', 'Blink'], False, True, True, False)


def get_shapekeys_decimation_list(self, context):
    return get_shapekeys(context,
                         ['Ah', 'A', 'Oh', 'O', 'Your', 'Glue', 'Ch', 'I', 'There', 'Wink 2', 'Wink', 'Wink left', 'Wink Left', 'Blink (Left)', 'Wink 2 right',
                          'Wink 2 Right', 'Wink right 2', 'Wink Right 2', 'Wink right', 'Wink Right', 'Blink (Right)', 'Blink'], False, True, True, True)


# names - The first object will be the first one in the list. So the first one has to be the one that exists in the most models
# no_basis - If this is true the Basis will not be available in the list
def get_shapekeys(context, names, is_mouth, no_basis, decimation, return_list):
    choices = []
    choices_simple = []
    meshes_list = get_meshes_objects()

    if decimation:
        meshes = meshes_list
    elif meshes_list:
        if is_mouth:
            meshes = [bpy.data.objects.get(context.scene.mesh_name_viseme)]
        else:
            meshes = [bpy.data.objects.get(context.scene.mesh_name_eye)]
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
            if decimation and name in tools.decimation.ignore_shapes:
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
            if decimation and name in tools.decimation.ignore_shapes:
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
        tools.translate.update_dictionary(armature.data.name)
        armature.data.name = 'Armature (' + tools.translate.translate(armature.data.name, add_space=True)[0] + ')'

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


def get_meshes_objects(armature_name=None, mode=0):
    # Modes:
    # 0 = With armatures only
    # 1 = Top level only
    # 2 = All meshes
    # 3 = Selected only

    meshes = []
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            if mode == 0:
                if not armature_name:
                    armature_name = bpy.context.scene.armature
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
    return meshes


def join_meshes(armature_name=None, mode=0, apply_transformations=True, repair_shape_keys=True):
    # Modes:
    # 0 - Join all meshes
    # 1 - Join selected only

    if not armature_name:
        armature_name = bpy.context.scene.armature

    meshes = get_meshes_objects(armature_name=armature_name)

    # Find out which meshes to join
    meshes_to_join = []
    for mesh in meshes:
        if mode == 0:
            meshes_to_join.append(mesh.name)
        elif mode == 1 and is_selected(mesh):
            meshes_to_join.append(mesh.name)

    if not meshes_to_join:
        return None

    set_default_stage()
    unselect_all()

    if apply_transformations:
        apply_transforms(armature_name=armature_name)

    unselect_all()

    # Apply existing decimation modifiers and select the meshes for joining
    for mesh in meshes:
        if mesh.name in meshes_to_join:
            tools.common.set_active(mesh)

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
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

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

    # Join the meshes
    if bpy.ops.object.join.poll():
        bpy.ops.object.join()
    else:
        return None

    # Rename result to Body and correct modifiers
    mesh = tools.common.get_active()
    if mesh:
        mesh.name = 'Body'
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

        # Add armature mod if there is none
        if mod_count == 0:
            mod = mesh.modifiers.new("Armature", 'ARMATURE')
            mod.object = get_armature(armature_name=armature_name)

        if repair_shape_keys:
            repair_shapekey_order(mesh.name)

    reset_context_scenes()

    return mesh


def apply_transforms(armature_name=None):
    if not armature_name:
        armature_name = bpy.context.scene.armature

    unselect_all()
    set_active(get_armature(armature_name=armature_name))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    for mesh in get_meshes_objects(armature_name=armature_name):
        unselect_all()
        set_active(mesh)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def separate_by_materials(context, mesh):
    set_default_stage()

    # Remove Rigidbodies and joints
    for obj in bpy.data.objects:
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

    # Correctly put mesh together. This is done to prevent extremely small pieces.
    # This essentially does nothing but merges the extremely small parts together.
    switch('EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.remove_doubles(threshold=0)
    switch('OBJECT')

    utils.separateByMaterials(mesh)

    for ob in context.selected_objects:
        if ob.type == 'MESH':
            clean_shapekeys(ob)

    utils.clearUnusedMeshes()


def separate_by_loose_parts(context, mesh):
    set_default_stage()

    # Remove Rigidbodies and joints
    for obj in bpy.data.objects:
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

    # Correctly put mesh together. This is done to prevent extremely small pieces.
    # This essentially does nothing but merges the extremely small parts together.
    remove_doubles(mesh, 0)

    utils.separateByMaterials(mesh)

    meshes = []
    for ob in context.selected_objects:
        if ob.type == 'MESH':
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

    ## Old separate method
    # print("DEBUG3")
    # bpy.ops.mesh.separate(type='LOOSE')
    # print("DEBUG4")
    #
    # for ob in context.selected_objects:
    #     print(ob.name)
    #     if ob.type == 'MESH':
    #         if ob.data.shape_keys:
    #             for kb in ob.data.shape_keys.key_blocks:
    #                 if can_remove(kb):
    #                     ob.shape_key_remove(kb)
    #
    #         mesh = ob.data
    #         materials = mesh.materials
    #         if len(mesh.polygons) > 0:
    #             if len(materials) > 1:
    #                 mat_index = mesh.polygons[0].material_index
    #                 for x in reversed(range(len(materials))):
    #                     if x != mat_index:
    #                         materials.pop(index=x, update_data=True)
    #         ob.name = getattr(materials[0], 'name', 'None') if len(materials) else 'None'
    #
    #         if '. 001' in ob.name:
    #             ob.name = ob.name.replace('. 001', '')
    #         if '.000' in ob.name:
    #             ob.name = ob.name.replace('.000', '')

    utils.clearUnusedMeshes()


def clean_shapekeys(mesh):
    if has_shapekeys(mesh):
        for kb in mesh.data.shape_keys.key_blocks:
            if can_remove_shapekey(kb):
                mesh.shape_key_remove(kb)


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
            tools.common.set_active(obj)
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
        bpy.context.scene.mesh_name_eye = mesh
        bpy.context.scene.mesh_name_viseme = mesh
        # bpy.context.scene.mesh_name_atlas = mesh # TODO remove this
        bpy.context.scene.merge_mesh = mesh


def save_shapekey_order(mesh_name):
    mesh = bpy.data.objects[mesh_name]
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

        if len(shape_key_order) <= len(custom_data.get('shape_key_order')):
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
    custom_data = get_armature().get('CUSTOM')
    if not custom_data:
        custom_data = {}

    # Extract shape keys from string
    shape_key_order = custom_data.get('shape_key_order')
    if not shape_key_order:
        shape_key_order = []

    sort_shape_keys(mesh_name, shape_key_order)


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

        # Get shape keys and translate them
        for shape_name in order:
            shape_key_order_translated.append(tools.translate.translate(shape_name, add_space=True, translating_shapes=True)[0])

        # print(armature.name, shape_key_order_translated)
        custom_data['shape_key_order'] = shape_key_order_translated
        armature['CUSTOM'] = custom_data


def sort_shape_keys(mesh_name, shape_key_order=None):
    mesh = bpy.data.objects[mesh_name]
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
    mesh = bpy.data.objects.get('Body')
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

    for obj in to_delete:
        obj.animation_data_clear()
        bpy.data.objects.remove(obj)


def delete(obj):
    if obj.parent:
        for child in obj.children:
            child.parent = obj.parent

    obj.animation_data_clear()
    bpy.data.objects.remove(obj)


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
    for objects in armature.children:
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
    for obj in bpy.data.objects:
        if (obj.type == 'CAMERA' and obj.name == 'Camera') \
                or (obj.type in ['LAMP', 'LIGHT'] and obj.name == 'Lamp') \
                or (obj.type == 'MESH' and obj.name == 'Cube'):
            delete_hierarchy(obj)


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

    chest = armature.data.edit_bones.get('Chest')
    neck = armature.data.edit_bones.get('Neck')
    head = armature.data.edit_bones.get('Head')
    if chest and neck:
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
                leg.tail = knee.head
                knee.tail = ankle.head

    if 'Right leg' in armature.data.edit_bones:
        if 'Right knee' in armature.data.edit_bones:
            if 'Right ankle' in armature.data.edit_bones:
                leg = armature.data.edit_bones.get('Right leg')
                knee = armature.data.edit_bones.get('Right knee')
                ankle = armature.data.edit_bones.get('Right ankle')
                leg.tail = knee.head
                knee.tail = ankle.head


dpi_scale = 3
error = []
override = False


def show_error(scale, error_list, override_header=False):
    global override, dpi_scale, error
    override = override_header
    dpi_scale = scale
    error = error_list

    header = 'Report: Error'
    if override:
        header = error_list[0]

    ShowError.bl_label = header
    try:
        bpy.utils.register_class(ShowError)
    except ValueError:
        bpy.utils.unregister_class(ShowError)
        bpy.utils.register_class(ShowError)

    bpy.ops.error.show('INVOKE_DEFAULT')


@register_wrap
class ShowError(bpy.types.Operator):
    bl_idname = 'error.show'
    bl_label = 'Report: Error'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * dpi_scale)

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
                    row.label(text=line, icon_value=tools.supporter.preview_collections["custom_icons"]["empty"].icon_id)

        print('')
        print('Report: Error')
        for line in error:
            print('    ' + line)


def remove_doubles(mesh, threshold):
    if not mesh:
        return 0

    pre_tris = len(mesh.data.polygons)

    set_active(mesh)
    switch('EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=threshold)
    switch('OBJECT')

    return pre_tris - len(mesh.data.polygons)


def get_bone_orientations():
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
            if mat.name.endswith('. 001') or mat.name.endswith(' .001'):
                mesh.active_material_index = j
                mesh.active_material.name = mat.name[:-5]


def mix_weights(mesh, vg_from, vg_to, delete_old_vg=True):
    mesh.active_shape_key_index = 0
    mod = mesh.modifiers.new("VertexWeightMix", 'VERTEX_WEIGHT_MIX')
    mod.vertex_group_a = vg_to
    mod.vertex_group_b = vg_from
    mod.mix_mode = 'ADD'
    mod.mix_set = 'B'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    if delete_old_vg:
        mesh.vertex_groups.remove(mesh.vertex_groups.get(vg_from))


def version_2_79_or_older():
    return bpy.app.version < (2, 79, 9)


def has_shapekeys(mesh):
    if not hasattr(mesh.data, 'shape_keys'):
        return False
    return hasattr(mesh.data.shape_keys, 'key_blocks')


def matmul(a, b):
    if version_2_79_or_older():
        return a*b
    return a.__matmul__(b)


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
    except:  #HTMLParseError: No good replacement?
        pass
    return parser.get_text()


# === THIS CODE COULD BE USEFUL ===

# def addvertex(meshname, shapekey_name):
#     mesh = bpy.data.objects[meshname].data
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
#     for ob in bpy.data.objects:
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
#     for ob in bpy.data.objects:
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
