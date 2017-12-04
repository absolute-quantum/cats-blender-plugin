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
import math
import numpy as np
import time

from mathutils import Quaternion

import tools.common
import tools.armature


class CreateEyesButton(bpy.types.Operator):
    bl_idname = 'create.eyes'
    bl_label = 'Create Eye Tracking'
    bl_description = 'This will let you track someone when they come close to you and it enables blinking.\n' \
                     "You should check the eye movement in pose mode after this operation to check the validity of the automatic eye tracking creation."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene.mesh_name_eye == "" \
                or context.scene.head == "" \
                or context.scene.eye_left == "" \
                or context.scene.eye_right == "" \
                or context.scene.wink_left == "" \
                or context.scene.wink_right == "" \
                or context.scene.lowerlid_left == "" \
                or context.scene.lowerlid_right == "":
            return False

        if not context.scene.disable_eye_blinking:
            if context.scene.wink_left == 'Basis' or context.scene.wink_right == 'Basis':
                return False

        if context.scene.disable_eye_blinking and context.scene.disable_eye_movement:
            return False

        return True

    def vertex_group_exists_old(self, mesh_name, bone_name):
        mesh = bpy.data.objects[mesh_name]

        group_lookup = {g.index: g.name for g in mesh.vertex_groups}
        verts = {name: [] for name in group_lookup.values()}

        for v in mesh.data.vertices:
            for g in v.groups:
                vert = verts.get(group_lookup.get(g.group)).append(v)

        try:
            verts.get(bone_name)
        except:
            return False

        return len(verts[bone_name]) >= 1

    def vertex_group_exists(self, mesh_name, bone_name):
        mesh = bpy.data.objects[mesh_name]
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

    def copy_vertex_group(self, mesh, vertex_group, rename_to):
        # iterate through the vertex group
        vertex_group_index = 0
        for group in bpy.data.objects[mesh].vertex_groups:
            # Find the vertex group
            if group.name == vertex_group:
                # Copy the group and rename
                bpy.data.objects[mesh].vertex_groups.active_index = vertex_group_index
                bpy.ops.object.vertex_group_copy()
                bpy.data.objects[mesh].vertex_groups[vertex_group + '_copy'].name = rename_to
                break

            vertex_group_index += 1

    def copy_shape_key(self, context, from_shape, new_name, new_index):
        mesh = bpy.data.objects[context.scene.mesh_name_eye]
        blinking = not context.scene.disable_eye_blinking

        # rename shapekey if it already exists and set all values to 0
        for shapekey in mesh.data.shape_keys.key_blocks:
            shapekey.value = 0
            if shapekey.name == new_name:
                shapekey.name = shapekey.name + '_old'
                if from_shape == new_name:
                    from_shape = shapekey.name

        # create new shape key
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if from_shape == shapekey.name:
                mesh.active_shape_key_index = index
                shapekey.value = 1
                mesh.shape_key_add(name=new_name, from_mix=blinking)
                break

        # Select the created shapekey
        mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1

        # Re-adjust index position
        position_correct = False
        bpy.ops.object.shape_key_move(type='TOP')
        while position_correct is False:
            if mesh.active_shape_key_index != new_index:
                bpy.ops.object.shape_key_move(type='DOWN')
            else:
                position_correct = True

        # reset shape values back to 0
        for shapekey in mesh.data.shape_keys.key_blocks:
            shapekey.value = 0

        mesh.active_shape_key_index = 0
        return from_shape

    def fix_eye_position(self, context, old_eye, new_eye, head):
        # Verify that the new eye bone is in the correct position
        # by comparing the old eye vertex group average vector location
        mesh_name = context.scene.mesh_name_eye
        scale = -context.scene.eye_distance + 1

        coords_eye = tools.common.find_center_vector_of_vertex_group(mesh_name, old_eye.name)

        if coords_eye is False:
            return

        mesh = bpy.data.objects[mesh_name]
        p1 = mesh.matrix_world * head.head
        p2 = mesh.matrix_world * coords_eye
        length = (p1 - p2).length
        print(length)  # TODO calculate scale if bone is too close to center of the eye

        # dist = math.sqrt((coords_eye[0] - head.head[0]) ** 2 + (coords_eye[1] - head.head[1]) ** 2 + (coords_eye[2] - head.head[2]) ** 2)
        # dist2 = np.linalg.norm(coords_eye - head.head)
        # dist3 = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)
        #dist4 = np.linalg.norm(p1 - p2)
        # print(dist)
        # print(dist2)
        # print(2 ** 2)
        #print(dist4)

        if context.scene.disable_eye_movement:
            new_eye.head[0] = head.head[0]
            new_eye.head[1] = head.head[1]
            new_eye.head[2] = head.head[2]
        else:
            new_eye.head[0] = old_eye.head[0] + scale * (coords_eye[0] - old_eye.head[0])
            new_eye.head[1] = old_eye.head[1] + scale * (coords_eye[1] - old_eye.head[1])
            new_eye.head[2] = old_eye.head[2] + scale * (coords_eye[2] - old_eye.head[2])

        new_eye.tail[0] = new_eye.head[0]
        new_eye.tail[1] = new_eye.head[1]
        new_eye.tail[2] = new_eye.head[2] + 0.2

    def execute(self, context):
        # PreserveState = tools.common.PreserveState()
        # PreserveState.save()

        start_time_unit = time.time()
        print(time.time() - start_time_unit)

        # Set the stage
        armature = tools.common.set_default_stage()
        tools.common.switch('EDIT')

        # Set up old bones
        head = armature.data.edit_bones.get(context.scene.head)
        old_eye_left = armature.data.edit_bones.get(context.scene.eye_left)
        old_eye_right = armature.data.edit_bones.get(context.scene.eye_right)

        # Check for errors
        if head is None:
            self.report({'ERROR'}, 'The bone "' + context.scene.head + '" does not exist.')
            return {'CANCELLED'}

        if old_eye_left is None:
            self.report({'ERROR'}, 'The bone "' + context.scene.eye_left + '" does not exist.')
            return {'CANCELLED'}

        if old_eye_right is None:
            self.report({'ERROR'}, 'The bone "' + context.scene.eye_right + '" does not exist.')
            return {'CANCELLED'}

        # Find the existing vertex group of the left eye bone
        if self.vertex_group_exists(context.scene.mesh_name_eye, old_eye_left.name) is False:
            self.report({'ERROR'}, 'The bone "' + context.scene.eye_left + '" has no existing vertex group or no vertices assigned to it, this is probably the wrong eye bone')
            return {'CANCELLED'}

        # Find the existing vertex group of the right eye bone
        if self.vertex_group_exists(context.scene.mesh_name_eye, old_eye_right.name) is False:
            self.report({'ERROR'}, 'The bone "' + context.scene.eye_right + '" has no existing vertex group or no vertices assigned to it, this is probably the wrong eye bone')
            return {'CANCELLED'}

        # Find existing LeftEye/RightEye and rename or delete
        if 'LeftEye' in armature.data.edit_bones:
            if old_eye_left.name == 'LeftEye':
                old_eye_left.name = 'OldLeftEye'
            else:
                armature.data.edit_bones.remove(armature.data.edit_bones.get('LeftEye'))

        if 'RightEye' in armature.data.edit_bones:
            if old_eye_right.name == 'RightEye':
                old_eye_right.name = 'OldRightEye'
            else:
                armature.data.edit_bones.remove(armature.data.edit_bones.get('RightEye'))

        # Set head roll to 0 degrees
        bpy.context.object.data.edit_bones[context.scene.head].roll = 0

        # Create the new eye bones
        new_left_eye = bpy.context.object.data.edit_bones.new('LeftEye')
        new_right_eye = bpy.context.object.data.edit_bones.new('RightEye')

        # Parent them correctly
        new_left_eye.parent = bpy.context.object.data.edit_bones[context.scene.head]
        new_right_eye.parent = bpy.context.object.data.edit_bones[context.scene.head]

        # Calculate their new positions
        self.fix_eye_position(context, old_eye_left, new_left_eye, head)
        self.fix_eye_position(context, old_eye_right, new_right_eye, head)

        # Switch to mesh
        bpy.context.scene.objects.active = bpy.data.objects[context.scene.mesh_name_eye]
        tools.common.switch('OBJECT')

        # Copy the existing eye vertex group to the new one if eye movement is activated
        if not context.scene.disable_eye_movement:
            self.copy_vertex_group(context.scene.mesh_name_eye, old_eye_left.name, 'LeftEye')
            self.copy_vertex_group(context.scene.mesh_name_eye, old_eye_right.name, 'RightEye')

        # Store shape keys to ignore changes during copying
        shapes = [context.scene.wink_left, context.scene.wink_right, context.scene.lowerlid_left, context.scene.lowerlid_right]

        # Copy shape key mixes from user defined shape keys and rename them to the correct liking of VRC
        shapes[0] = self.copy_shape_key(context, shapes[0], 'vrc.blink_left', 1)
        shapes[1] = self.copy_shape_key(context, shapes[1], 'vrc.blink_right', 2)
        shapes[2] = self.copy_shape_key(context, shapes[2], 'vrc.lowerlid_left', 3)
        shapes[3] = self.copy_shape_key(context, shapes[3], 'vrc.lowerlid_right', 4)

        # Reset the scenes in case they were changed
        context.scene.head = head.name
        context.scene.eye_left = old_eye_left.name
        context.scene.eye_right = old_eye_right.name
        context.scene.wink_left = shapes[0]
        context.scene.wink_right = shapes[1]
        context.scene.lowerlid_left = shapes[2]
        context.scene.lowerlid_right = shapes[3]

        # Remove empty objects
        tools.common.remove_empty()

        # Fix armature name
        tools.common.fix_armature_name()

        # Check for correct bone hierarchy
        is_correct = tools.armature.check_hierarchy([['Hips', 'Spine', 'Chest', 'Neck', 'Head']])

        print(time.time() - start_time_unit)
        if context.scene.disable_eye_movement:
            repair_shapekeys_mouth(context.scene.mesh_name_eye, context.scene.wink_left)
        else:
            repair_shapekeys(context.scene.mesh_name_eye, new_right_eye.name)

        print(time.time() - start_time_unit)

        # PreserveState.load()  # TODO

        # deleted = []
        # # deleted = checkshapekeys()
        #
        # if len(deleted) > 0:
        #     text = 'Following shape keys get deleted: '
        #     for key in deleted:
        #         text += key + ', '
        #     self.report({'WARNING'}, text)
        if not is_correct['result']:
            self.report({'ERROR'}, is_correct['message'])
            self.report({'ERROR'}, 'Eye tracking will not work unless the bone hierarchy is exactly as following: Hips > Spine > Chest > Neck > Head')
        else:
            self.report({'INFO'}, 'Created eye tracking!')

        return {'FINISHED'}


# Repair vrc shape keys
def repair_shapekeys(mesh_name, vertex_group):
    mesh = bpy.data.objects[mesh_name]
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()

    # Get a vertex from the eye vertex group # TODO https://i.imgur.com/tWi8lk6.png after many times resetting the eyes
    group = mesh.vertex_groups.get(vertex_group)
    if group is None:
        repair_shapekeys_mouth(mesh_name)
        return
    gi = group.index
    for v in mesh.data.vertices:
        for g in v.groups:
            if g.group == gi:
                vcoords = v.co.xyz

    if vcoords is None:
        return

    # Move that vertex by a tiny amount
    i = 0
    for key in bm.verts.layers.shape.keys():
        if not key.startswith('vrc'):
            continue
        value = bm.verts.layers.shape.get(key)
        for vert in bm.verts:
            if vert.co.xyz == vcoords:
                shapekey = vert
                shapekey_coords = mesh.matrix_world * shapekey[value]
                shapekey_coords[2] -= 0.00001
                shapekey[value] = mesh.matrix_world.inverted() * shapekey_coords
                i += 1
                break

    bm.to_mesh(mesh.data)

    if i == 0:
        print('Error: Shapekey repairing failed for some reason! Using random shapekey method now.')
        repair_shapekeys_mouth(mesh_name)


# Repair vrc shape keys with random vertex
def repair_shapekeys_mouth(mesh_name, shapekey_name):  # TODO Add vertex repairing!
    mesh = bpy.data.objects[mesh_name]
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()

    # Move that vertex by a tiny amount
    i = 0
    for key in bm.verts.layers.shape.keys():
        if not key.startswith('vrc'):
            continue
        value = bm.verts.layers.shape.get(key)
        for vert in bm.verts:
            shapekey = vert
            shapekey_coords = mesh.matrix_world * shapekey[value]
            shapekey_coords[2] -= 0.00001
            shapekey[value] = mesh.matrix_world.inverted() * shapekey_coords
            i += 1
            break

    bm.to_mesh(mesh.data)

    if i == 0:
        print('Error: Random shapekey repairing failed for some reason! Canceling!')


class StartTestingButton(bpy.types.Operator):
    bl_idname = 'eyes.test'
    bl_label = 'Start eye testing'
    bl_description = 'Starts the testing process.\n' \
                     'Bones "EyeLeft" and "EyeRight" are required.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        armature = tools.common.get_armature()
        if 'LeftEye' in armature.pose.bones:
            if 'RightEye' in armature.pose.bones:
                return True
        return False

    def execute(self, context):
        armature = tools.common.set_default_stage()
        tools.common.switch('POSE')
        armature.data.pose_position = 'POSE'

        eye_left = armature.data.bones.get('LeftEye')
        eye_right = armature.data.bones.get('RightEye')

        if eye_left is None or eye_right is None:
            return

        eye_left.select = True
        eye_right.select = True

        return {'FINISHED'}


class StopTestingButton(bpy.types.Operator):
    bl_idname = 'eyes.test_stop'
    bl_label = 'Stop eye testing'
    bl_description = 'Stops the testing process.'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for pb in tools.common.get_armature().data.bones:
            pb.select = True
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()
        for pb in tools.common.get_armature().data.bones:
            pb.select = False

        armature = tools.common.set_default_stage()
        armature.data.pose_position = 'REST'
        return {'FINISHED'}


class SetRotationButton(bpy.types.Operator):
    bl_idname = 'eyes.set_rotation'
    bl_label = 'Set Rotation'
    bl_description = 'Sets the roation.'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = tools.common.get_armature()
        eye_left = armature.pose.bones.get('LeftEye')
        eye_right = armature.pose.bones.get('RightEye')

        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()

        eye_left.rotation_mode = 'XYZ'
        eye_left.rotation_euler.rotate_axis('X', math.radians(context.scene.eye_rotation_x))
        eye_left.rotation_euler.rotate_axis('Y', math.radians(context.scene.eye_rotation_y))

        eye_right.rotation_mode = 'XYZ'
        eye_right.rotation_euler.rotate_axis('X', math.radians(context.scene.eye_rotation_x))
        eye_right.rotation_euler.rotate_axis('Y', math.radians(context.scene.eye_rotation_y))

        return {'FINISHED'}


# Update via slider
def update_bones(degrees):
    armature = tools.common.get_armature()
    eye_left = armature.pose.bones.get('LeftEye')
    eye_right = armature.pose.bones.get('RightEye')

    eye_left.rotation_mode = 'XYZ'
    eye_right.rotation_mode = 'XYZ'

    eye_left.rotation_euler.rotate_axis('Z', math.radians(degrees))
    eye_right.rotation_euler.rotate_axis('Z', math.radians(degrees))

    if eye_left is None or eye_right is None:
        return







