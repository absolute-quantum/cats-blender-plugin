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

import bpy
import bmesh
import numpy as np
from mathutils import Vector
from math import degrees
from collections import OrderedDict
import time


# TODO
# - Add check if hips bone really needs to be rotated
# - Error: https://i.imgur.com/kBnSx0I.png with model Kanna O: https://goo.gl/sJj2xL
# - Reset Pivot
# - Manual bone selection button for root bones
# - Checkbox for eye blinking/moving
# - Translate progress bar
# - Add error dialog: At the bottom here: https://wiki.blender.org/index.php/Dev:Py/Scripts/Cookbook/Code_snippets/Interface
# - Eye tracking should remove vertex group from eye if there is one already bound to it and "No Movement" is checked


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


class PreserveState():
    state_data = {}

    def save(self):
        hidden = {}
        for object in bpy.data.objects:
            hidden[object.name] = object.hide

        selected = {}
        for object in bpy.data.objects:
            selected[object.name] = object.select

        self.state_data = {
            'object_mode': bpy.context.active_object.mode,
            'selection': selected,
            'hidden': hidden,
        }

        return self.state_data

    def load(self):
        switch(self.state_data['object_mode'])
        for object in bpy.data.objects:
            try:
                self.state_data['hidden'][object.name]
            except KeyError:
                object.hide = False
                continue

            object.hide = self.state_data['hidden'][object.name]

        for object in bpy.data.objects:
            try:
                self.state_data['selection'][object.name]
            except KeyError:
                object.select = False
                continue

            object.select = self.state_data['selection'][object.name]

        return self.state_data


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


def get_bones_head(self, context):
    return get_bones(['Head'])


def get_bones_eye_l(self, context):
    return get_bones(['Eye_L', 'EyeReturn_L'])


def get_bones_eye_r(self, context):
    return get_bones(['Eye_R', 'EyeReturn_R'])


# names - The first object will be the first one in the list. So the first one has to be the one that exists in the most models
def get_bones(names):
    choices = []

    armature = get_armature().data
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
    return get_shapekeys(context, ['Ah', 'Wow'], False)


def get_shapekeys_mouth_oh(self, context):
    return get_shapekeys(context, ['Your'], False)


def get_shapekeys_mouth_ch(self, context):
    return get_shapekeys(context, ['Glue', 'There'], False)


def get_shapekeys_eye_blink_l(self, context):
    return get_shapekeys(context, ['Wink 2', 'Wink'], True)


def get_shapekeys_eye_blink_r(self, context):
    return get_shapekeys(context, ['Wink 2 right', 'Wink right 2', 'Wink right'], True)


def get_shapekeys_eye_low_l(self, context):
    return get_shapekeys(context, ['Basis'], False)


def get_shapekeys_eye_low_r(self, context):
    return get_shapekeys(context, ['Basis'], False)


# names - The first object will be the first one in the list. So the first one has to be the one that exists in the most models
# no_basis - If this is true the Basis will not be available in the list
def get_shapekeys(context, names, no_basis):
    choices = []

    if hasattr(bpy.data.objects[context.scene.mesh_name_eye].data, 'shape_keys'):
        if hasattr(bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys, 'key_blocks'):
            for shapekey in bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys.key_blocks:
                if no_basis and shapekey.name == 'Basis':
                    continue
                choices.append((shapekey.name, shapekey.name, shapekey.name))

    choices.sort(key=lambda x: tuple(x[0].lower()))

    choices2 = []
    for name in names:
        if hasattr(bpy.data.objects[context.scene.mesh_name_eye].data, 'shape_keys'):
            if hasattr(bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys, 'key_blocks'):
                if name in bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys.key_blocks and choices[0][0] != name:
                    choices2.append((name, name, name))

    for choice in choices:
        choices2.append(choice)

    bpy.types.Object.Enum = choices2

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


# Repair vrc shape keys
def repair_shapekeys():
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            mesh = ob
            bm = bmesh.new()
            bm.from_mesh(mesh.data)
            bm.verts.ensure_lookup_table()

            for key in bm.verts.layers.shape.keys():
                if not key.startswith('vrc'):
                    continue

                value = bm.verts.layers.shape.get(key)
                for vert in bm.verts:
                    shapekey = vert
                    shapekey_coords = mesh.matrix_world * shapekey[value]
                    shapekey_coords[2] -= 0.00001
                    shapekey[value] = mesh.matrix_world.inverted() * shapekey_coords
                    break

            bm.to_mesh(mesh.data)


def get_meshes_objects():
    meshes = []
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            if ob.parent is not None and ob.parent.type == 'ARMATURE':
                meshes.append(ob)
    return meshes


def join_meshes():
    # Combines Meshes
    set_default_stage()
    unselect_all()
    for mesh in get_meshes_objects():
        select(mesh)

    # Joins the meshes
    if bpy.ops.object.join.poll():
        bpy.ops.object.join()

    # Renames it to Body
    mesh = None
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            if ob.parent is not None and ob.parent.type == 'ARMATURE':
                ob.name = 'Body'
                mesh = ob
                break

    return mesh


def repair_viseme_order(mesh_name):
    mesh = bpy.data.objects[mesh_name]
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

    for name in order.keys():
        if mesh.data.shape_keys is not None:
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


def LLHtoECEF(lat, lon, alt):
    # see http://www.mathworks.de/help/toolbox/aeroblks/llatoecefposition.html

    rad = np.float64(6378137.0)  # Radius of the Earth (in meters)
    f = np.float64(1.0 / 298.257223563)  # Flattening factor WGS84 Model
    cosLat = np.cos(lat)
    sinLat = np.sin(lat)
    FF = (1.0 - f) ** 2
    C = 1 / np.sqrt(cosLat ** 2 + FF * sinLat ** 2)
    S = C * FF

    x = (rad * C + alt) * cosLat * np.cos(lon)
    y = (rad * C + alt) * cosLat * np.sin(lon)
    z = (rad * S + alt) * sinLat

    return [x, y, z]

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

# === THIS CODE COULD BE USEFUL ===
