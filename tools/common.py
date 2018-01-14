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
from mathutils import Vector
from math import degrees
from collections import OrderedDict
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


def get_armature():
    # NOTE: what if there are two armatures?
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            return obj


def unhide_all():
    for obj in bpy.data.objects:
        obj.hide = False


def unselect_all():
    for obj in bpy.data.objects:
        obj.select = False


def select(obj):
    bpy.context.scene.objects.active = obj
    obj.select = True


def switch(new_mode):
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode=new_mode, toggle=False)


def set_default_stage():
    switch('OBJECT')
    unhide_all()
    unselect_all()
    armature = get_armature()
    select(armature)
    return armature


def remove_bone(find_bone):
    armature = get_armature()
    switch('EDIT')
    for bone in armature.data.edit_bones:
        if bone.name == find_bone:
            armature.data.edit_bones.remove(bone)


def remove_empty():
    switch('EDIT')  # This fixes an error apparently
    set_default_stage()
    unselect_all()
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY':
            bpy.context.scene.objects.active = bpy.data.objects[obj.name]
            obj.select = True
            bpy.ops.object.delete(use_global=False)

        unselect_all()


def get_bone_angle(p1, p2):
    try:
        ret = degrees((p1.head - p1.tail).angle(p2.head - p2.tail))
    except ValueError:
        ret = 0

    return ret


def remove_unused_vertex_groups():
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
    choices = []

    for object in bpy.context.scene.objects:
        if object.type == 'MESH':
            if object.parent is not None and object.parent.type == 'ARMATURE':
                choices.append((object.name, object.name, object.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_meshes_decimation(self, context):
    choices = []

    for object in bpy.context.scene.objects:
        if object.type == 'MESH':
            if object.parent is not None and object.parent.type == 'ARMATURE':
                if object.name in tools.decimation.ignore_meshes:
                    continue
                choices.append((object.name, object.name, object.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: tuple(x[0].lower()))
    return bpy.types.Object.Enum


def get_bones_head(self, context):
    return get_bones(['Head'])


def get_bones_eye_l(self, context):
    return get_bones(['Eye_L', 'EyeReturn_L'])


def get_bones_eye_r(self, context):
    return get_bones(['Eye_R', 'EyeReturn_R'])


# names - The first object will be the first one in the list. So the first one has to be the one that exists in the most models
def get_bones(names):
    choices = []
    armature = get_armature()

    if armature is None:
        bpy.types.Object.Enum = choices
        return bpy.types.Object.Enum

    armature = armature.data
    for bone in armature.bones:
        choices.append((bone.name, bone.name, bone.name))

    choices.sort(key=lambda x: tuple(x[0].lower()))

    choices2 = []
    for name in names:
        if name in armature.bones and choices[0][0] != name:
            choices2.append((name, name, name))

    for choice in choices:
        choices2.append(choice)

    bpy.types.Object.Enum = choices2

    return bpy.types.Object.Enum


def get_shapekeys_mouth_ah(self, context):
    return get_shapekeys(context, ['Ah', 'Wow', 'A'], False, False, False)


def get_shapekeys_mouth_oh(self, context):
    return get_shapekeys(context, ['Your', 'O'], False, False, False)


def get_shapekeys_mouth_ch(self, context):
    return get_shapekeys(context, ['Glue', 'There', 'I'], False, False, False)


def get_shapekeys_eye_blink_l(self, context):
    return get_shapekeys(context, ['Wink 2', 'Wink', 'Blink (Left)', 'Blink', 'Basis'], False, False, False)


def get_shapekeys_eye_blink_r(self, context):
    return get_shapekeys(context, ['Wink 2 right', 'Wink right 2', 'Wink right', 'Blink (Right)', 'Basis'], False, False, False)


def get_shapekeys_eye_low_l(self, context):
    return get_shapekeys(context, ['Basis'], False, False, False)


def get_shapekeys_eye_low_r(self, context):
    return get_shapekeys(context, ['Basis'], False, False, False)


def get_shapekeys_decimation(self, context):
    return get_shapekeys(context, ['Ah', 'Wow', 'Your', 'Glue', 'There', 'Wink 2', 'Wink', 'Wink 2 right', 'Wink right 2', 'Wink right'], True, True, False)


def get_shapekeys_decimation_list(self, context):
    return get_shapekeys(context, ['Ah', 'Wow', 'Your', 'Glue', 'There', 'Wink 2', 'Wink', 'Wink 2 right', 'Wink right 2', 'Wink right'], True, True, True)


# names - The first object will be the first one in the list. So the first one has to be the one that exists in the most models
# no_basis - If this is true the Basis will not be available in the list
def get_shapekeys(context, names, no_basis, decimation, return_list):
    choices = []
    choices_simple = []
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


def fix_armature_name():
    get_armature().name = 'Armature'
    get_armature().data.name = 'Armature'


def get_texture_sizes(self, context):
    bpy.types.Object.Enum = [
        ("1024", "1024 (low)", "1024"),
        ("2048", "2048 (medium)", "2048"),
        ("4096", "4096 (high)", "4096")
    ]

    return bpy.types.Object.Enum


def get_meshes_objects():
    meshes = []
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            if ob.parent is not None and ob.parent.type == 'ARMATURE':
                meshes.append(ob)
    return meshes


def join_meshes(context):
    set_default_stage()
    unselect_all()

    # Apply existing decimation modifiers
    for mesh in get_meshes_objects():
        select(mesh)
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
        unselect_all()

    # Select all meshes
    for mesh in get_meshes_objects():
        select(mesh)

    # Join the meshes
    if bpy.ops.object.join.poll():
        bpy.ops.object.join()

    # Rename result to Body
    mesh = None
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            if ob.parent is not None and ob.parent.type == 'ARMATURE':
                mesh = ob
                mesh.name = 'Body'
                for mod in mesh.modifiers:
                    mod.show_expanded = False
                ShapekeyOrder.repair(mesh.name)
                break

    reset_context_scenes(context)

    return mesh


def separate_by_materials(context, mesh):
    set_default_stage()

    # Remove Rigidbodies and joints
    for obj in bpy.data.objects:
        if 'rigidbodies' in obj.name or 'joints' in obj.name:
            tools.common.delete_hierarchy(obj)

    select(mesh)
    ShapekeyOrder.save(mesh.name)

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


def can_remove(key_block):
    if 'mmd_' in key_block.name:
        return True
    if key_block.relative_key == key_block:
        return False  # Basis
    for v0, v1 in zip(key_block.relative_key.data, key_block.data):
        if v0.co != v1.co:
            return False
    return True


def separate_by_verts(context):
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


def reset_context_scenes(context):
    context.scene.head = get_bones_head(None, context)[0][0]
    context.scene.eye_left = get_bones_eye_l(None, context)[0][0]
    context.scene.eye_right = get_bones_eye_r(None, context)[0][0]

    mesh = get_meshes(None, context)[0][0]
    context.scene.mesh_name_eye = mesh
    context.scene.mesh_name_viseme = mesh
    context.scene.mesh_name_atlas = mesh
    context.scene.merge_mesh = mesh


def repair_viseme_order(mesh_name):
    order = OrderedDict()
    order['Basis'] = 0
    order['vrc.blink_left'] = 1
    order['vrc.blink_right'] = 2
    order['vrc.lowerlid_left'] = 3
    order['vrc.lowerlid_right'] = 4
    order['vrc.v_aa'] = 5
    order['vrc.v_ch'] = 6
    order['vrc.v_dd'] = 7
    order['vrc.v_e'] = 8
    order['vrc.v_ff'] = 9
    order['vrc.v_ih'] = 10
    order['vrc.v_kk'] = 11
    order['vrc.v_nn'] = 12
    order['vrc.v_oh'] = 13
    order['vrc.v_ou'] = 14
    order['vrc.v_pp'] = 15
    order['vrc.v_rr'] = 16
    order['vrc.v_sil'] = 17
    order['vrc.v_ss'] = 18
    order['vrc.v_th'] = 19

    repair_shape_order(mesh_name, order)


def repair_shape_order(mesh_name, order):
    mesh = bpy.data.objects[mesh_name]
    if not mesh.data.shape_keys:
        return

    wm = bpy.context.window_manager
    current_step = 0
    wm.progress_begin(current_step, len(order.items()))

    for name in order.keys():
        if hasattr(mesh.data.shape_keys, 'key_blocks'):
            for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                if shapekey.name == name:

                    mesh.active_shape_key_index = index
                    new_index = order.get(shapekey.name)
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
                    break
        current_step += 1
        wm.progress_update(current_step)

    mesh.active_shape_key_index = 0

    wm.progress_end()


class ShapekeyOrder:

    @staticmethod
    def save(mesh_name):
        global shapekey_order
        if shapekey_order:
            print('SAVE ABORTED!')
            return
        print('SAVE ORDER')
        shapekey_order = OrderedDict()
        mesh = bpy.data.objects[mesh_name]
        if mesh.data.shape_keys is not None and hasattr(mesh.data.shape_keys, 'key_blocks'):
            for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                shapekey_order[shapekey.name] = index

    @staticmethod
    def repair(mesh_name):
        global shapekey_order
        print('REPAIR ORDER')
        if not shapekey_order:
            print('REPAIR EMTPY')
            return

        repair_shape_order(mesh_name, shapekey_order)
        shapekey_order = None


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
        if obj_temp is not None:
            setattr(obj_temp, 'select', True)
            obj_temp.animation_data_clear()

    result = bpy.ops.object.delete()
    bpy.data.scenes['Scene'].objects.unlink(obj)
    bpy.data.objects.remove(obj)
    if result == {'FINISHED'}:
        print("Successfully deleted object")
    else:
        print("Could not delete object")


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)

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
