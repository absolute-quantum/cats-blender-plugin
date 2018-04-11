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
from collections import OrderedDict
from random import random

import tools.common
import tools.armature


iris_heights = None


class CreateEyesButton(bpy.types.Operator):
    bl_idname = 'create.eyes'
    bl_label = 'Create Eye Tracking'
    bl_description = 'This will let you track someone when they come close to you and it enables blinking.\n' \
                     "You should do decimation before this operation.\n" \
                     "Test the resulting eye movement in the 'Testing' tab."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if context.scene.mesh_name_eye == "" \
                or context.scene.head == "" \
                or context.scene.eye_left == "" \
                or context.scene.eye_right == "":
            return False

        # if not context.scene.disable_eye_blinking:
        #     if context.scene.wink_left == 'Basis' or context.scene.wink_right == 'Basis':
        #         return False

        if context.scene.disable_eye_blinking and context.scene.disable_eye_movement:
            return False

        return True

    def execute(self, context):
        wm = bpy.context.window_manager

        # Set the stage
        armature = tools.common.set_default_stage()
        tools.common.switch('EDIT')

        mesh_name = context.scene.mesh_name_eye

        # Set up old bones
        head = armature.data.edit_bones.get(context.scene.head)
        old_eye_left = armature.data.edit_bones.get(context.scene.eye_left)
        old_eye_right = armature.data.edit_bones.get(context.scene.eye_right)

        # Check for errors
        if not context.scene.disable_eye_blinking and (context.scene.wink_left == ""
                                                       or context.scene.wink_right == ""
                                                       or context.scene.lowerlid_left == ""
                                                       or context.scene.lowerlid_right == ""):
            self.report({'ERROR'}, 'You have no shape keys selected.'
                                   '\nPlease choose a mesh containing shape keys or check "Disable Eye Blinking".')
            return {'CANCELLED'}

        if head is None:
            self.report({'ERROR'}, 'The bone "' + context.scene.head + '" does not exist.')
            return {'CANCELLED'}

        if old_eye_left is None:
            self.report({'ERROR'}, 'The bone "' + context.scene.eye_left + '" does not exist.')
            return {'CANCELLED'}

        if old_eye_right is None:
            self.report({'ERROR'}, 'The bone "' + context.scene.eye_right + '" does not exist.')
            return {'CANCELLED'}

        if not context.scene.disable_eye_movement:
            # Find the existing vertex group of the left eye bone
            if self.vertex_group_exists(mesh_name, old_eye_left.name) is False:
                self.report({'ERROR'}, 'The bone "' + context.scene.eye_left + '" has no existing vertex group or no vertices assigned to it.'
                                       '\nThis might be because you selected the wrong mesh or the wrong bone.'
                                       '\nAlso make sure to join your meshes before creating eye tracking and make sure that the eye bones actually move the eyes in pose mode.')
                return {'CANCELLED'}

            # Find the existing vertex group of the right eye bone
            if self.vertex_group_exists(mesh_name, old_eye_right.name) is False:
                self.report({'ERROR'}, 'The bone "' + context.scene.eye_right + '" has no existing vertex group or no vertices assigned to it.'
                                       '\nThis might be because you selected the wrong mesh or the wrong bone.'
                                       '\nAlso make sure to join your meshes before creating eye tracking and make sure that the eye bones actually move the eyes in pose mode.')
                return {'CANCELLED'}

        # Find existing LeftEye/RightEye and rename or delete
        if 'LeftEye' in armature.data.edit_bones:
            if old_eye_left.name == 'LeftEye':
                self.report({'ERROR'}, 'Please do not use "LeftEye" as the input bone.'
                                       '\nIf you are sure that you want to use that bone please rename it to "Eye_L".')
                return {'CANCELLED'}
            else:
                armature.data.edit_bones.remove(armature.data.edit_bones.get('LeftEye'))

        if 'RightEye' in armature.data.edit_bones:
            if old_eye_right.name == 'RightEye':
                self.report({'ERROR'}, 'Please do not use "RightEye" as the input bone.'
                                       '\nIf you are sure that you want to use that bone please rename it to "Eye_R".')
                return {'CANCELLED'}
            else:
                armature.data.edit_bones.remove(armature.data.edit_bones.get('RightEye'))

        if not bpy.data.objects[mesh_name].data.shape_keys:
            bpy.data.objects[mesh_name].shape_key_add(name='Basis', from_mix=False)

        # Set head roll to 0 degrees
        bpy.context.object.data.edit_bones[context.scene.head].roll = 0

        # Create the new eye bones
        new_left_eye = bpy.context.object.data.edit_bones.new('LeftEye')
        new_right_eye = bpy.context.object.data.edit_bones.new('RightEye')

        # Parent them correctly
        new_left_eye.parent = bpy.context.object.data.edit_bones[context.scene.head]
        new_right_eye.parent = bpy.context.object.data.edit_bones[context.scene.head]

        # Calculate their new positions
        fix_eye_position(context, old_eye_left, new_left_eye, head, False)
        fix_eye_position(context, old_eye_right, new_right_eye, head, True)

        # Switch to mesh
        bpy.context.scene.objects.active = bpy.data.objects[mesh_name]
        tools.common.switch('OBJECT')

        # Fix a small bug
        bpy.context.object.show_only_shape_key = False

        # Copy the existing eye vertex group to the new one if eye movement is activated
        if not context.scene.disable_eye_movement:
            self.copy_vertex_group(mesh_name, old_eye_left.name, 'LeftEye')
            self.copy_vertex_group(mesh_name, old_eye_right.name, 'RightEye')
        else:
            # Remove the vertex groups if no blink is enabled
            mesh = bpy.data.objects[mesh_name]
            bones = ['LeftEye', 'RightEye']
            for bone in bones:
                group = mesh.vertex_groups.get(bone)
                if group is not None:
                    mesh.vertex_groups.remove(group)

        # Store shape keys to ignore changes during copying
        shapes = [context.scene.wink_left, context.scene.wink_right, context.scene.lowerlid_left, context.scene.lowerlid_right]
        new_shapes = ['vrc.blink_left', 'vrc.blink_right', 'vrc.lowerlid_left', 'vrc.lowerlid_right']

        # Remove existing shapekeys
        for new_shape in new_shapes:
            for index, shapekey in enumerate(bpy.data.objects[mesh_name].data.shape_keys.key_blocks):
                if shapekey.name == new_shape and new_shape not in shapes:
                    bpy.context.active_object.active_shape_key_index = index
                    bpy.ops.object.shape_key_remove()
                    break

        # Copy shape key mixes from user defined shape keys and rename them to the correct liking of VRC
        wm.progress_begin(0, 4)
        shapes[0] = self.copy_shape_key(context, shapes[0], new_shapes, 1)
        wm.progress_update(1)
        shapes[1] = self.copy_shape_key(context, shapes[1], new_shapes, 2)
        wm.progress_update(2)
        shapes[2] = self.copy_shape_key(context, shapes[2], new_shapes, 3)
        wm.progress_update(3)
        shapes[3] = self.copy_shape_key(context, shapes[3], new_shapes, 4)
        wm.progress_update(4)

        tools.common.repair_viseme_order(mesh_name)

        # Reset the scenes in case they were changed
        context.scene.head = head.name
        context.scene.eye_left = old_eye_left.name
        context.scene.eye_right = old_eye_right.name
        context.scene.wink_left = shapes[0]
        context.scene.wink_right = shapes[1]
        context.scene.lowerlid_left = shapes[2]
        context.scene.lowerlid_right = shapes[3]

        # Remove empty objects
        tools.common.set_default_stage()  # Fixes an error apparently
        tools.common.remove_empty()

        # Fix armature name
        tools.common.fix_armature_names()

        # Check for correct bone hierarchy
        is_correct = tools.armature.check_hierarchy(True, [['Hips', 'Spine', 'Chest', 'Neck', 'Head']])

        if context.scene.disable_eye_movement:
            # print('Repair with mouth.')
            repair_shapekeys_mouth(mesh_name)
            # repair_shapekeys_mouth(mesh_name, context.scene.wink_left)  # TODO
        else:
            # print('Repair normal "' + new_right_eye.name + '".')
            repair_shapekeys(mesh_name, new_right_eye.name)

        # deleted = []
        # # deleted = checkshapekeys()
        #
        # if len(deleted) > 0:
        #     text = 'Following shape keys get deleted: '
        #     for key in deleted:
        #         text += key + ', '
        #     self.report({'WARNING'}, text)

        wm.progress_end()

        if not is_correct['result']:
            self.report({'ERROR'}, is_correct['message'])
            self.report({'ERROR'}, 'Eye tracking will not work unless the bone hierarchy is exactly as following: Hips > Spine > Chest > Neck > Head'
                                   '\nFurthermore the mesh containing the eyes has to be called "Body" and the armature "Armature".')
        else:
            context.scene.eye_mode = 'TESTING'
            self.report({'INFO'}, 'Created eye tracking!')

        return {'FINISHED'}

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

    def copy_shape_key(self, context, from_shape, new_names, new_index):
        mesh = bpy.data.objects[context.scene.mesh_name_eye]
        blinking = not context.scene.disable_eye_blinking
        new_name = new_names[new_index - 1]

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


# Repair vrc shape keys
def repair_shapekeys(mesh_name, vertex_group):
    # This is done to fix a very weird bug where the mouth stays open sometimes
    tools.common.set_default_stage()
    mesh = bpy.data.objects[mesh_name]
    tools.common.unselect_all()
    tools.common.select(mesh)
    tools.common.switch('EDIT')
    tools.common.switch('OBJECT')

    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()

    # Get a vertex from the eye vertex group # TODO https://i.imgur.com/tWi8lk6.png after many times resetting the eyes
    print('DEBUG: Group: ' + vertex_group)
    group = mesh.vertex_groups.get(vertex_group)
    if group is None:
        print('DEBUG: Group: ' + vertex_group + ' not found!')
        repair_shapekeys_mouth(mesh_name)
        return
    print('DEBUG: Group: ' + vertex_group + ' found!')

    vcoords = False
    gi = group.index
    for v in mesh.data.vertices:
        for g in v.groups:
            if g.group == gi:
                vcoords = v.co.xyz

    if vcoords is False:
        return

    print('DEBUG: Repairing shapes!')
    # Move that vertex by a tiny amount
    moved = False
    i = 0
    for key in bm.verts.layers.shape.keys():
        if not key.startswith('vrc.'):
            continue
        print('DEBUG: Repairing shape: ' + key)
        value = bm.verts.layers.shape.get(key)
        for index, vert in enumerate(bm.verts):
            if vert.co.xyz == vcoords:
                if index < i:
                    continue
                shapekey = vert
                shapekey_coords = mesh.matrix_world * shapekey[value]
                shapekey_coords[0] -= 0.00007 * randBoolNumber()
                shapekey_coords[1] -= 0.00007 * randBoolNumber()
                shapekey_coords[2] -= 0.00007 * randBoolNumber()
                shapekey[value] = mesh.matrix_world.inverted() * shapekey_coords
                print('DEBUG: Repaired shape: ' + key)
                i += 1
                moved = True
                break

    bm.to_mesh(mesh.data)

    if not moved:
        print('Error: Shapekey repairing failed for some reason! Using random shapekey method now.')
        repair_shapekeys_mouth(mesh_name)


def randBoolNumber():
    if random() < 0.5:
        return -1
    return 1


# Repair vrc shape keys with random vertex
def repair_shapekeys_mouth(mesh_name):  # TODO Add vertex repairing!
    # This is done to fix a very weird bug where the mouth stays open sometimes
    tools.common.set_default_stage()
    mesh = bpy.data.objects[mesh_name]
    tools.common.unselect_all()
    tools.common.select(mesh)
    tools.common.switch('EDIT')
    tools.common.switch('OBJECT')

    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()

    # Move that vertex by a tiny amount
    moved = False
    for key in bm.verts.layers.shape.keys():
        if not key.startswith('vrc'):
            continue
        value = bm.verts.layers.shape.get(key)
        for vert in bm.verts:
            shapekey = vert
            shapekey_coords = mesh.matrix_world * shapekey[value]
            shapekey_coords[0] -= 0.00007
            shapekey_coords[1] -= 0.00007
            shapekey_coords[2] -= 0.00007
            shapekey[value] = mesh.matrix_world.inverted() * shapekey_coords
            print('TEST')
            moved = True
            break

    bm.to_mesh(mesh.data)

    if not moved:
        print('Error: Random shapekey repairing failed for some reason! Canceling!')


def fix_eye_position(context, old_eye, new_eye, head, right_side):
    # Verify that the new eye bone is in the correct position
    # by comparing the old eye vertex group average vector location
    mesh_name = context.scene.mesh_name_eye
    scale = -context.scene.eye_distance + 1

    if not context.scene.disable_eye_movement:
        if head is not None:
            coords_eye = tools.common.find_center_vector_of_vertex_group(mesh_name, old_eye.name)
        else:
            coords_eye = tools.common.find_center_vector_of_vertex_group(mesh_name, new_eye.name)

        if coords_eye is False:
            return

        if head is not None:
            mesh = bpy.data.objects[mesh_name]
            p1 = mesh.matrix_world * head.head
            p2 = mesh.matrix_world * coords_eye
            length = (p1 - p2).length
            print(length)  # TODO calculate scale if bone is too close to center of the eye

    # dist = math.sqrt((coords_eye[0] - head.head[x_cord]) ** 2 + (coords_eye[1] - head.head[y_cord]) ** 2 + (coords_eye[2] - head.head[z_cord]) ** 2)
    # dist2 = np.linalg.norm(coords_eye - head.head)
    # dist3 = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)
    # dist4 = np.linalg.norm(p1 - p2)
    # print(dist)
    # print(dist2)
    # print(2 ** 2)
    # print(dist4)

    # Check if bone matrix == world matrix
    armature = tools.common.get_armature()
    x_cord = 0
    y_cord = 1
    z_cord = 2
    for index, bone in enumerate(armature.pose.bones):
        if index == 5:
            bone_pos = bone.matrix
            world_pos = armature.matrix_world * bone.matrix
            if abs(bone_pos[0][0]) != abs(world_pos[0][0]):
                z_cord = 1
                y_cord = 2

    if context.scene.disable_eye_movement:
        if head is not None:
            if right_side:
                new_eye.head[x_cord] = head.head[x_cord] + 0.05
            else:
                new_eye.head[x_cord] = head.head[x_cord] - 0.05
            new_eye.head[y_cord] = head.head[y_cord]
            new_eye.head[z_cord] = head.head[z_cord]
    else:
        new_eye.head[x_cord] = old_eye.head[x_cord] + scale * (coords_eye[0] - old_eye.head[x_cord])
        new_eye.head[y_cord] = old_eye.head[y_cord] + scale * (coords_eye[1] - old_eye.head[y_cord])
        new_eye.head[z_cord] = old_eye.head[z_cord] + scale * (coords_eye[2] - old_eye.head[z_cord])

    new_eye.tail[x_cord] = new_eye.head[x_cord]
    new_eye.tail[y_cord] = new_eye.head[y_cord]
    new_eye.tail[z_cord] = new_eye.head[z_cord] + 0.1


eye_left = None
eye_right = None
eye_left_data = None
eye_right_data = None


class StartTestingButton(bpy.types.Operator):
    bl_idname = 'eyes.test'
    bl_label = 'Start Eye Testing'
    bl_description = 'This will let you test how the eye movement will look ingame.\n' \
                     "Don't forget to stop the Testing process afterwards.\n" \
                     'Bones "EyeLeft" and "EyeRight" are required.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = tools.common.get_armature()
        if 'LeftEye' in armature.pose.bones:
            if 'RightEye' in armature.pose.bones:
                if bpy.data.objects.get(context.scene.mesh_name_eye) is not None:
                    return True
        return False

    def execute(self, context):
        armature = tools.common.set_default_stage()
        tools.common.switch('POSE')
        armature.data.pose_position = 'POSE'

        global eye_left, eye_right, eye_left_data, eye_right_data
        eye_left = armature.pose.bones.get('LeftEye')
        eye_right = armature.pose.bones.get('RightEye')
        eye_left_data = armature.data.bones.get('LeftEye')
        eye_right_data = armature.data.bones.get('RightEye')

        if eye_left is None or eye_right is None or eye_left_data is None or eye_right_data is None:
            return {'FINISHED'}

        for shape_key in bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys.key_blocks:
            shape_key.value = 0

        for pb in tools.common.get_armature().data.bones:
            pb.select = True
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()
        for pb in tools.common.get_armature().data.bones:
            pb.select = False
            pb.hide = True

        # eye_left.select = True
        # eye_right.select = True
        eye_left_data.hide = False
        eye_right_data.hide = False

        context.scene.eye_rotation_x = 0
        context.scene.eye_rotation_y = 0

        return {'FINISHED'}


class StopTestingButton(bpy.types.Operator):
    bl_idname = 'eyes.test_stop'
    bl_label = 'Stop Eye Testing'
    bl_description = 'Stops the testing process.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        global eye_left, eye_right, eye_left_data, eye_right_data
        if eye_left:
            context.scene.eye_rotation_x = 0
            context.scene.eye_rotation_y = 0

        if not context.object or context.object.mode != 'POSE':
            tools.common.set_default_stage()
            tools.common.switch('POSE')

        for pb in tools.common.get_armature().data.bones:
            pb.hide = False
            pb.select = True
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()
        for pb in tools.common.get_armature().data.bones:
            pb.select = False

        armature = tools.common.set_default_stage()
        armature.data.pose_position = 'REST'

        for shape_key in bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys.key_blocks:
            shape_key.value = 0

        eye_left = None
        eye_right = None
        eye_left_data = None
        eye_right_data = None

        return {'FINISHED'}


# This gets called by the eye testing sliders
def set_rotation(self, context):
    global eye_left, eye_right, eye_left_data, eye_right_data

    if not eye_left:
        StopTestingButton.execute(self, context)
        self.report({'ERROR'}, "Something went wrong. Please try eye testing again.")
        return None

    eye_left_data.select = True
    eye_right_data.select = True

    bpy.ops.pose.rot_clear()

    eye_left_data.select = False
    eye_right_data.select = False

    eye_left.rotation_mode = 'XYZ'
    eye_left.rotation_euler.rotate_axis('X', math.radians(context.scene.eye_rotation_x))
    eye_left.rotation_euler.rotate_axis('Y', math.radians(context.scene.eye_rotation_y))

    eye_right.rotation_mode = 'XYZ'
    eye_right.rotation_euler.rotate_axis('X', math.radians(context.scene.eye_rotation_x))
    eye_right.rotation_euler.rotate_axis('Y', math.radians(context.scene.eye_rotation_y))
    return None


def stop_testing(self, context):
        global eye_left, eye_right, eye_left_data, eye_right_data
        if not eye_left or not eye_right or not eye_left_data or not eye_right_data:
            return None

        armature = tools.common.set_default_stage()
        tools.common.switch('POSE')
        armature.data.pose_position = 'POSE'

        context.scene.eye_rotation_x = 0
        context.scene.eye_rotation_y = 0

        for pb in armature.data.bones:
            pb.hide = False
            pb.select = True
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()
        for pb in armature.data.bones:
            pb.select = False

        armature = tools.common.set_default_stage()
        armature.data.pose_position = 'REST'

        for shape_key in bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys.key_blocks:
            shape_key.value = 0

        eye_left = None
        eye_right = None
        eye_left_data = None
        eye_right_data = None
        return None


class ResetRotationButton(bpy.types.Operator):
    bl_idname = 'eyes.reset_rotation'
    bl_label = 'Reset Rotation'
    bl_description = "This resets the eye positions."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = tools.common.get_armature()
        if 'LeftEye' in armature.pose.bones:
            if 'RightEye' in armature.pose.bones:
                return True
        return False

    def execute(self, context):
        context.scene.eye_rotation_x = 0
        context.scene.eye_rotation_y = 0

        return {'FINISHED'}


class AdjustEyesButton(bpy.types.Operator):
    bl_idname = 'eyes.adjust_eyes'
    bl_label = 'Set Range'
    bl_description = "Let's you readjust the movement range of the eyes.\n" \
                     "This get's saved."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = tools.common.get_armature()
        if 'LeftEye' in armature.pose.bones:
            if 'RightEye' in armature.pose.bones:
                return True
        return False

    def execute(self, context):
        if context.scene.disable_eye_movement:
            return {'FINISHED'}

        armature = tools.common.set_default_stage()
        tools.common.switch('EDIT')

        new_eye_left = armature.data.edit_bones.get('LeftEye')
        new_eye_right = armature.data.edit_bones.get('RightEye')
        old_eye_left = armature.pose.bones.get(context.scene.eye_left)
        old_eye_right = armature.pose.bones.get(context.scene.eye_right)

        fix_eye_position(context, old_eye_left, new_eye_left, None, False)
        fix_eye_position(context, old_eye_right, new_eye_right, None, True)

        tools.common.switch('POSE')

        global eye_left, eye_right, eye_left_data, eye_right_data
        eye_left = armature.pose.bones.get('LeftEye')
        eye_right = armature.pose.bones.get('RightEye')
        eye_left_data = armature.data.bones.get('LeftEye')
        eye_right_data = armature.data.bones.get('RightEye')

        return {'FINISHED'}


class StartIrisHeightButton(bpy.types.Operator):
    bl_idname = 'eyes.adjust_iris_height_start'
    bl_label = 'Start Iris Height Adjustment'
    bl_description = "Let's you readjust the distance of the iris from the eye ball.\n" \
                     "Use this to fix clipping of the iris into the eye ball.\n" \
                     "This get's saved."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = tools.common.get_armature()
        if 'LeftEye' in armature.pose.bones:
            if 'RightEye' in armature.pose.bones:
                return True
        return False

    def execute(self, context):
        if context.scene.disable_eye_movement:
            return {'FINISHED'}

        armature = tools.common.set_default_stage()
        armature.hide = True

        mesh = bpy.data.objects[context.scene.mesh_name_eye]
        tools.common.select(mesh)
        tools.common.switch('EDIT')

        if len(mesh.vertex_groups) > 0:
            tools.common.select(mesh)
            tools.common.switch('EDIT')
            bpy.ops.mesh.select_mode(type='VERT')

            vgs = [mesh.vertex_groups.get('LeftEye'), mesh.vertex_groups.get('RightEye')]
            for vg in vgs:
                if vg:
                    bpy.ops.object.vertex_group_set_active(group=vg.name)
                    bpy.ops.object.vertex_group_select()

            import bmesh
            [i.index for i in bmesh.from_edit_mesh(bpy.context.active_object.data).verts if i.select]

            bm = bmesh.from_edit_mesh(mesh.data)
            for v in bm.verts:
                if v.select:
                    v.co.y += context.scene.iris_height * 0.01
                    print(v.co)

        return {'FINISHED'}


class TestBlinking(bpy.types.Operator):
    bl_idname = 'eyes.test_blink'
    bl_label = 'Test'
    bl_description = "This let's you see how eye blinking will look ingame."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        mesh = bpy.data.objects[context.scene.mesh_name_eye]
        if hasattr(mesh.data, 'shape_keys'):
            if hasattr(mesh.data.shape_keys, 'key_blocks'):
                if 'vrc.blink_left' in mesh.data.shape_keys.key_blocks:
                    if 'vrc.blink_right' in mesh.data.shape_keys.key_blocks:
                        return True
        return False

    def execute(self, context):
        mesh = bpy.data.objects[context.scene.mesh_name_eye]
        shapes = ['vrc.blink_left', 'vrc.blink_right']

        for shape_key in mesh.data.shape_keys.key_blocks:
            if shape_key.name in shapes:
                mesh.data.shape_keys.key_blocks[shape_key.name].value = context.scene.eye_blink_shape
            else:
                mesh.data.shape_keys.key_blocks[shape_key.name].value = 0

        return {'FINISHED'}


class TestLowerlid(bpy.types.Operator):
    bl_idname = 'eyes.test_lowerlid'
    bl_label = 'Test'
    bl_description = "This let's you see how lowerlids will look ingame."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        mesh = bpy.data.objects[context.scene.mesh_name_eye]
        if hasattr(mesh.data, 'shape_keys'):
            if hasattr(mesh.data.shape_keys, 'key_blocks'):
                if 'vrc.lowerlid_left' in mesh.data.shape_keys.key_blocks:
                    if 'vrc.lowerlid_right' in mesh.data.shape_keys.key_blocks:
                        return True
        return False

    def execute(self, context):
        mesh = bpy.data.objects[context.scene.mesh_name_eye]
        shapes = OrderedDict()
        shapes['vrc.lowerlid_left'] = context.scene.eye_lowerlid_shape
        shapes['vrc.lowerlid_right'] = context.scene.eye_lowerlid_shape

        for shape_key in mesh.data.shape_keys.key_blocks:
            if shape_key.name in shapes:
                mesh.data.shape_keys.key_blocks[shape_key.name].value = context.scene.eye_lowerlid_shape
            else:
                mesh.data.shape_keys.key_blocks[shape_key.name].value = 0

        return {'FINISHED'}


class ResetBlinkTest(bpy.types.Operator):
    bl_idname = 'eyes.reset_blink_test'
    bl_label = 'Reset Shapes'
    bl_description = "This resets the blink testing."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        for shape_key in bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys.key_blocks:
            shape_key.value = 0
        context.scene.eye_blink_shape = 1
        context.scene.eye_lowerlid_shape = 1

        return {'FINISHED'}
