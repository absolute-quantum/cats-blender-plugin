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
import tools.decimation
import tools.armature_bones as Bones
from mathutils import Vector
from math import degrees
from collections import OrderedDict

from googletrans import Translator
from mmd_tools_local import utils

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


def unhide_all():
    if bpy.app.version < (2, 79, 9):
        for obj in bpy.data.objects:
            obj.hide = False
    else:
        for obj in bpy.data.collections:
            obj.hide_viewport = False


def unselect_all():
    for obj in bpy.data.objects:
        obj.select = False


def select(obj):
    bpy.context.scene.objects.active = obj
    obj.select = True


def switch(new_mode):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=new_mode, toggle=False)


def set_default_stage_old():
    switch('OBJECT')
    unhide_all()
    unselect_all()
    armature = get_armature()
    select(armature)
    return armature


def set_default_stage():
    unhide_all()
    unselect_all()

    for obj in bpy.data.objects:
        select(obj)
        switch('OBJECT')
        if obj.type == 'ARMATURE':
            obj.data.pose_position = 'REST'

        obj.select = False

    armature = get_armature()
    if armature:
        select(armature)
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
        tools.common.unselect_all()
        tools.common.select(armature.parent)
        bpy.ops.object.delete(use_global=False)
        tools.common.unselect_all()


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
    return get_shapekeys(context, ['Ah', 'Wow', 'A'], True, False, False, False)


def get_shapekeys_mouth_oh(self, context):
    return get_shapekeys(context, ['Your', 'O'], True, False, False, False)


def get_shapekeys_mouth_ch(self, context):
    return get_shapekeys(context, ['Glue', 'There', 'I'], True, False, False, False)


def get_shapekeys_eye_blink_l(self, context):
    return get_shapekeys(context, ['Wink 2', 'Wink', 'Blink (Left)', 'Blink', 'Basis'], False, False, False, False)


def get_shapekeys_eye_blink_r(self, context):
    return get_shapekeys(context, ['Wink 2 right', 'Wink right 2', 'Wink right', 'Blink (Right)', 'Basis'], False,
                         False, False, False)


def get_shapekeys_eye_low_l(self, context):
    return get_shapekeys(context, ['Basis'], False, False, False, False)


def get_shapekeys_eye_low_r(self, context):
    return get_shapekeys(context, ['Basis'], False, False, False, False)


def get_shapekeys_decimation(self, context):
    return get_shapekeys(context,
                         ['Ah', 'Wow', 'Your', 'Glue', 'There', 'Wink 2', 'Wink', 'Wink 2 right', 'Wink right 2',
                          'Wink right'], False, True, True, False)


def get_shapekeys_decimation_list(self, context):
    return get_shapekeys(context,
                         ['Ah', 'Wow', 'Your', 'Glue', 'There', 'Wink 2', 'Wink', 'Wink 2 right', 'Wink right 2',
                          'Wink right'], False, True, True, True)


# names - The first object will be the first one in the list. So the first one has to be the one that exists in the most models
# no_basis - If this is true the Basis will not be available in the list
def get_shapekeys(context, names, is_mouth, no_basis, decimation, return_list):
    choices = []
    choices_simple = []

    if is_mouth:
        meshes = [bpy.data.objects.get(context.scene.mesh_name_viseme)]
    else:
        meshes = [bpy.data.objects.get(context.scene.mesh_name_eye)]

    if decimation:
        meshes = get_meshes_objects()

    for mesh in meshes:
        if mesh is None or not hasattr(mesh.data, 'shape_keys') or not hasattr(mesh.data.shape_keys, 'key_blocks'):
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
        try:
            armature.data.name = 'Armature (' + Translator().translate(armature.data.name).text + ')'
        except:
            armature.data.name = 'Armature'

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

    meshes = []
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            if mode == 0:
                if not armature_name:
                    armature_name = bpy.context.scene.armature
                if ob.parent and ob.parent.type == 'ARMATURE' and ob.parent.name == armature_name:
                    meshes.append(ob)

            elif mode == 1:
                if not ob.parent:
                    meshes.append(ob)

            elif mode == 2:
                meshes.append(ob)
    return meshes


def join_meshes(armature_name=None, mode=0):
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
        elif mode == 1 and mesh.select:
            meshes_to_join.append(mesh.name)

    set_default_stage()
    unselect_all()

    # Apply existing decimation modifiers and select the meshes for joining
    for mesh in meshes:
        if mesh.name in meshes_to_join:
            mesh.select = True
            bpy.context.scene.objects.active = mesh

            for mod in mesh.modifiers:
                if mod.type == 'DECIMATE':
                    if mod.decimate_type == 'COLLAPSE' and mod.ratio == 1:
                        mesh.modifiers.remove(mod)
                        continue
                    if mod.decimate_type == 'UNSUBDIV' and mod.iterations == 0:
                        mesh.modifiers.remove(mod)
                        continue

                    if mesh.data.shape_keys is not None:
                        bpy.ops.object.shape_key_remove(all=True)
                    bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

    # Join the meshes
    if bpy.ops.object.join.poll():
        bpy.ops.object.join()
    else:
        return None

    # Rename result to Body and correct modifiers
    mesh = bpy.context.scene.objects.active
    if mesh:
        mesh.name = 'Body'
        mesh.parent_type = 'OBJECT'

        mod_count = 0
        for mod in mesh.modifiers:
            mod.show_expanded = False
            if mod.type == 'ARMATURE':
                if mod_count > 0:
                    bpy.ops.object.modifier_remove(modifier=mod.name)
                    continue
                mod.object = get_armature(armature_name=armature_name)
                mod_count += 1

        repair_shapekey_order(mesh.name)

    reset_context_scenes()

    return mesh


def separate_by_materials(context, mesh):
    set_default_stage()

    # Remove Rigidbodies and joints
    for obj in bpy.data.objects:
        if 'rigidbodies' in obj.name or 'joints' in obj.name:
            tools.common.delete_hierarchy(obj)

    save_shapekey_order(mesh.name)
    select(mesh)

    for mod in mesh.modifiers:
        if mod.type == 'DECIMATE':
            mesh.modifiers.remove(mod)
        else:
            mod.show_expanded = False

    utils.separateByMaterials(mesh)

    for ob in context.selected_objects:
        if ob.type == 'MESH' and ob.data.shape_keys:
            for kb in ob.data.shape_keys.key_blocks:
                if can_remove(kb):
                    ob.shape_key_remove(kb)

    utils.clearUnusedMeshes()


def separate_by_loose_parts(context, mesh):
    set_default_stage()

    # Remove Rigidbodies and joints
    for obj in bpy.data.objects:
        if 'rigidbodies' in obj.name or 'joints' in obj.name:
            tools.common.delete_hierarchy(obj)

    save_shapekey_order(mesh.name)
    select(mesh)

    for mod in mesh.modifiers:
        if mod.type == 'DECIMATE':
            mesh.modifiers.remove(mod)
        else:
            mod.show_expanded = False

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
        select(mesh)
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
            if mesh2 and mesh2.data.shape_keys:
                for kb in mesh2.data.shape_keys.key_blocks:
                    if can_remove(kb):
                        mesh2.shape_key_remove(kb)

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


def can_remove(key_block):
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
            bpy.context.scene.objects.active = obj
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
        bpy.context.scene.mesh_name_atlas = mesh
        bpy.context.scene.merge_mesh = mesh


def save_shapekey_order(mesh_name):
    mesh = bpy.data.objects[mesh_name]
    armature = get_armature()

    if not armature:
        return

    # Get current custom data
    custom_data = armature.get('CUSTOM')
    if not custom_data:
        print('NEW DATA!')
        custom_data = {}

    # Create shape key list for description
    shape_key_order = ''
    if mesh.data.shape_keys and mesh.data.shape_keys.key_blocks:
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if index > 0:
                shape_key_order += ',,,'
            shape_key_order += shapekey.name

    # Check if there is already a shapekey order
    if custom_data.get('shape_key_order'):
        print('CUSTOM PROP ALREADY EXISTS!')
        print(custom_data['shape_key_order'])

        if len(custom_data.get('shape_key_order')) > len(shape_key_order):
            print('ABORT')
            return

    # Save order to custom data
    print('CREATE NEW CUSTOM PROP!')
    custom_data['shape_key_order'] = shape_key_order

    # Save custom data in armature
    armature['CUSTOM'] = custom_data

    print(armature.get('CUSTOM')['shape_key_order'])


def repair_shapekey_order(mesh_name):
    armature = get_armature()
    shape_key_order = []

    # Get current custom data
    custom_data = armature.get('CUSTOM')
    if not custom_data:
        custom_data = {}

    # Extract shape keys from string
    order_string = custom_data.get('shape_key_order')
    if order_string:
        for shape_name in order_string.split(',,,'):
            shape_key_order.append(shape_name)

    sort_shape_keys(mesh_name, shape_key_order)


def update_shapekey_orders(translations):
    for armature in get_armature_objects():
        shape_key_order = []

        # Get current custom data
        custom_data = armature.get('CUSTOM')
        if not custom_data or not custom_data.get('shape_key_order'):
            continue

        # Create shape key list for description
        order_string = custom_data.get('shape_key_order')
        for shape_name in order_string.split(',,,'):
            if translations.get(shape_name):
                shape_key_order.append(translations.get(shape_name))
            else:
                shape_key_order.append(shape_name)
        print(order_string)

        # Create shape key list for properties
        order_string = ''
        for i, shapekey in enumerate(shape_key_order):
            if i > 0:
                order_string += ',,,'
            order_string += shapekey

        print(order_string)

        custom_data['shape_key_order'] = order_string


def sort_shape_keys(mesh_name, shape_key_order=None):
    mesh = bpy.data.objects[mesh_name]
    if not mesh.data.shape_keys or not mesh.data.shape_keys.key_blocks:
        return

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


def delete_hierarchy(obj):
    unselect_all()
    obj.animation_data_clear()
    names = set()

    def get_child_names(obj):
        for child in obj.children:
            if child.type != 'ARMATURE':
                names.add(child.name)
                if child.children:
                    get_child_names(child)

    get_child_names(obj)

    objects = bpy.data.objects
    for n in names:
        obj_temp = objects.get(n)
        if obj_temp:
            obj_temp.select = True
            obj_temp.animation_data_clear()

    result = bpy.ops.object.delete()

    bpy.context.scene.objects.unlink(obj)
    bpy.data.objects.remove(obj)

    if result == {'FINISHED'}:
        print("Successfully deleted object")
    else:
        print("Could not delete object")


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
                or (obj.type == 'LAMP' and obj.name == 'Lamp') \
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
    armature = tools.common.get_armature(armature_name=armature_name)

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
error = None


def show_error(scale, error_list):
    global error, dpi_scale
    error = error_list
    dpi_scale = scale

    # if len(error_list) == 1:
    #     ShowError.bl_label = error_list[0]
    #     try:
    #         bpy.utils.register_class(ShowError)
    #     except ValueError:
    #         bpy.utils.unregister_class(ShowError)
    #         bpy.utils.register_class(ShowError)

    bpy.ops.error.show('INVOKE_DEFAULT')


class ShowError(bpy.types.Operator):
    bl_idname = 'error.show'
    bl_label = 'Error'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * dpi_scale)

    def draw(self, context):
        if not error:
            return

        # if not error or len(error) == 1:
        #     return

        layout = self.layout
        col = layout.column(align=True)

        for line in error:
            if line == '':
                col.separator()
            else:
                row = col.row(align=True)
                row.scale_y = 0.85
                row.label(line)


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
