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

from . import common as Common
from . import armature as Armature
from .register import register_wrap


iris_heights = None


@register_wrap
class CreateEyesButton(bpy.types.Operator):
    bl_idname = 'cats_eyes.create_eye_tracking'
    bl_label = 'Create Eye Tracking'
    bl_description = 'This will let you track someone when they come close to you and it enables blinking.\n' \
                     "You should do decimation before this operation.\n" \
                     "Test the resulting eye movement in the 'Testing' tab"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    mesh = None

    @classmethod
    def poll(cls, context):
        if not Common.get_meshes_objects(check=False):
            return False
        return True

    def execute(self, context):
        saved_data = Common.SavedData()

        # Set the stage
        armature = Common.set_default_stage()
        Common.switch('EDIT')

        self.mesh = Common.get_objects().get(context.scene.mesh_name_eye)

        # Set up old bones
        bone_eye_left = armature.data.edit_bones.get(context.scene.eye_left)
        bone_eye_right = armature.data.edit_bones.get(context.scene.eye_right)

        shape_wink_left = context.scene.wink_left
        shape_wink_right = context.scene.wink_right
        shape_look_up = context.scene.upperlid_up

        if not bone_eye_left:
            saved_data.load()
            self.report({'ERROR'}, 'The bone "' + context.scene.eye_left + '" does not exist.')
            return {'CANCELLED'}

        if not bone_eye_right:
            saved_data.load()
            self.report({'ERROR'}, 'The bone "' + context.scene.eye_right + '" does not exist.')
            return {'CANCELLED'}

        shapes_to_keep = ['eyes_closed', 'eyes_lookup', 'eyes_lookdown']
        if shape_wink_left in shapes_to_keep or shape_wink_right in shapes_to_keep or shape_look_up in shapes_to_keep:
            saved_data.load()
            self.report({'ERROR'}, 'Please don\'t select any of the following shapekeys:'
                                   '\n  - eyes_closed, eyes_lookup, eyes_lookdown'
                                   '\n'
                                   '\nIf you really want to use these shapekeys, duplicate them and select the copy instead')
            return {'CANCELLED'}

        if not Common.has_shapekeys(self.mesh):
            self.mesh.shape_key_add(name='Basis', from_mix=False)

        # Rename eye bones
        bone_eye_left.name = 'LeftEye'
        bone_eye_right.name = 'RightEye'

        # Put eye bones straight up
        for bone in [bone_eye_left, bone_eye_right]:
            bone.tail[2] = bone.head[2] + bone.length
            bone.tail[1] = bone.head[1]
            bone.tail[0] = bone.head[0]

        # Switch to mesh
        Common.set_active(self.mesh)
        Common.switch('OBJECT')

        # Fix a small bug
        bpy.context.object.show_only_shape_key = False

        # Set up the shape keys.
        shapekey_data = OrderedDict()
        shapekey_data['eyes_closed'] = [
            (shape_wink_left, 1),
            (shape_wink_right, 1)
        ]
        shapekey_data['eyes_lookup'] = [
            (shape_look_up, 1)
        ]
        shapekey_data['eyes_lookdown'] = [
            (shape_look_up, -1)
        ]

        # Mix the new shapekeys
        self.mix_shapekeys(shapekey_data)

        # Sort the shapekeys
        Common.sort_shape_keys(self.mesh.name)

        # Reset the scenes in case they were changed
        # context.scene.eye_left = old_eye_left.name
        # context.scene.eye_right = old_eye_right.name
        # context.scene.wink_left = shape_wink_left
        # context.scene.wink_right = shape_wink_right
        # context.scene.upperlid_up = shape_look_up

        saved_data.load()

        context.scene.eye_mode = 'TESTING'
        self.report({'INFO'}, 'Created eye tracking!')

        return {'FINISHED'}

    def mix_shapekeys(self, shapekey_data):
        for new_shape_name, shapekey_data in shapekey_data.items():

            # Check if all required shapekeys for this one exist
            all_exist = True
            for shapekey_values in shapekey_data:
                shapekey = self.mesh.data.shape_keys.key_blocks.get(shapekey_values[0])
                if not shapekey:
                    all_exist = False

            # If not all required shapekeys for the mixing exist, continue
            if not all_exist:
                continue

            # Reset all shape keys
            bpy.ops.object.shape_key_clear()

            # Remove existing shapekey
            for index, shapekey in enumerate(self.mesh.data.shape_keys.key_blocks):
                if shapekey.name == new_shape_name:
                    bpy.context.active_object.active_shape_key_index = index
                    bpy.ops.object.shape_key_remove()
                    break

            # Set the shape key values
            for shapekey_values in shapekey_data:
                shapekey_name, shapekey_value = shapekey_values

                shapekey = self.mesh.data.shape_keys.key_blocks.get(shapekey_name)
                shapekey.slider_min = -10
                shapekey.slider_max = 10
                shapekey.value = shapekey_value

            # Create the new shape key
            self.mesh.shape_key_add(name=new_shape_name, from_mix=True)

            # Reset all shape keys and sliders
            for shapekey_values in shapekey_data:
                shapekey = self.mesh.data.shape_keys.key_blocks.get(shapekey_values[0])
                shapekey.slider_min = 0
                shapekey.slider_max = 1
                shapekey.value = 0

            self.mesh.active_shape_key_index = 0


# Repair vrc shape keys
def repair_shapekeys(mesh_name, vertex_group):
    # This is done to fix a very weird bug where the mouth stays open sometimes
    Common.set_default_stage()
    mesh = Common.get_objects()[mesh_name]
    Common.unselect_all()
    Common.set_active(mesh)
    Common.switch('EDIT')
    Common.switch('OBJECT')

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

    vcoords = None
    gi = group.index
    for v in mesh.data.vertices:
        for g in v.groups:
            if g.group == gi:
                vcoords = v.co.xyz

    if not vcoords:
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
                shapekey_coords = Common.matmul(mesh.matrix_world, shapekey[value])
                shapekey_coords[0] -= 0.00007 * randBoolNumber()
                shapekey_coords[1] -= 0.00007 * randBoolNumber()
                shapekey_coords[2] -= 0.00007 * randBoolNumber()
                shapekey[value] = Common.matmul(mesh.matrix_world.inverted(), shapekey_coords)
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
    Common.set_default_stage()
    mesh = Common.get_objects()[mesh_name]
    Common.unselect_all()
    Common.set_active(mesh)
    Common.switch('EDIT')
    Common.switch('OBJECT')

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
            shapekey_coords = Common.matmul(mesh.matrix_world, shapekey[value])
            shapekey_coords[0] -= 0.00007
            shapekey_coords[1] -= 0.00007
            shapekey_coords[2] -= 0.00007
            shapekey[value] = Common.matmul(mesh.matrix_world.inverted(), shapekey_coords)
            print('TEST')
            moved = True
            break

    bm.to_mesh(mesh.data)

    if not moved:
        print('Error: Random shapekey repairing failed for some reason! Canceling!')


eye_left = None
eye_right = None
eye_left_data = None
eye_right_data = None
eye_mesh = None


@register_wrap
class StartTestingButton(bpy.types.Operator):
    bl_idname = 'cats_eyes.start_testing'
    bl_label = 'Start Eye Testing'
    bl_description = 'This will let you test how the eye movement will look ingame.\n' \
                     "Don't forget to stop the Testing process afterwards.\n" \
                     'Bones "LeftEye" and "RightEye" are required'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = Common.get_armature()
        if 'LeftEye' in armature.pose.bones:
            if 'RightEye' in armature.pose.bones:
                if Common.get_objects().get(context.scene.mesh_name_eye) is not None:
                    return True
        return False

    def execute(self, context):
        armature = Common.set_default_stage()
        Common.switch('POSE')
        armature.data.pose_position = 'POSE'

        global eye_left, eye_right, eye_left_data, eye_right_data, eye_mesh
        eye_left = armature.pose.bones.get('LeftEye')
        eye_right = armature.pose.bones.get('RightEye')
        eye_left_data = armature.data.bones.get('LeftEye')
        eye_right_data = armature.data.bones.get('RightEye')
        eye_mesh = Common.get_objects()[context.scene.mesh_name_eye]

        if not eye_left or not eye_right or not eye_left_data or not eye_right_data or not eye_mesh:
            return {'FINISHED'}

        for shape_key in eye_mesh.data.shape_keys.key_blocks:
            shape_key.value = 0

        for pb in Common.get_armature().data.bones:
            pb.select = True
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()
        for pb in Common.get_armature().data.bones:
            pb.select = False
            pb.hide = True

        # eye_left.select = True
        # eye_right.select = True
        eye_left_data.hide = False
        eye_right_data.hide = False

        context.scene.eye_rotation_x = 0
        context.scene.eye_rotation_y = 0

        return {'FINISHED'}


@register_wrap
class StopTestingButton(bpy.types.Operator):
    bl_idname = 'cats_eyes.stop_testing'
    bl_label = 'Stop Eye Testing'
    bl_description = 'Stops the testing process'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        global eye_left, eye_right, eye_left_data, eye_right_data, eye_mesh
        if eye_left:
            context.scene.eye_rotation_x = 0
            context.scene.eye_rotation_y = 0

        if not context.object or context.object.mode != 'POSE':
            Common.set_default_stage()
            Common.switch('POSE')

        for pb in Common.get_armature().data.bones:
            pb.hide = False
            pb.select = True
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()
        for pb in Common.get_armature().data.bones:
            pb.select = False

        armature = Common.set_default_stage()
        # armature.data.pose_position = 'REST'

        for shape_key in eye_mesh.data.shape_keys.key_blocks:
            shape_key.value = 0

        eye_left = None
        eye_right = None
        eye_left_data = None
        eye_right_data = None
        eye_mesh = None

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
    eye_left.rotation_euler.rotate_axis('X', -math.radians(context.scene.eye_rotation_x))
    eye_left.rotation_euler.rotate_axis('Y', math.radians(context.scene.eye_rotation_y))

    eye_right.rotation_mode = 'XYZ'
    eye_right.rotation_euler.rotate_axis('X', -math.radians(context.scene.eye_rotation_x))
    eye_right.rotation_euler.rotate_axis('Y', math.radians(context.scene.eye_rotation_y))

    shape_look_up = eye_mesh.data.shape_keys.key_blocks.get('eyes_lookup')
    shape_look_down = eye_mesh.data.shape_keys.key_blocks.get('eyes_lookdown')

    if shape_look_up:
        if context.scene.eye_rotation_x > 0:
            shape_look_up.value = context.scene.eye_rotation_x / 12
        else:
            shape_look_up.value = 0

    if shape_look_down:
        if context.scene.eye_rotation_x < 0:
            shape_look_down.value = context.scene.eye_rotation_x / -9
        else:
            shape_look_down.value = 0

    return None


def stop_testing(self, context):
        global eye_left, eye_right, eye_left_data, eye_right_data
        if not eye_left or not eye_right or not eye_left_data or not eye_right_data:
            return None

        armature = Common.set_default_stage()
        Common.switch('POSE')
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

        armature = Common.set_default_stage()
        # armature.data.pose_position = 'REST'

        for shape_key in Common.get_objects()[context.scene.mesh_name_eye].data.shape_keys.key_blocks:
            shape_key.value = 0

        eye_left = None
        eye_right = None
        eye_left_data = None
        eye_right_data = None
        return None


@register_wrap
class ResetRotationButton(bpy.types.Operator):
    bl_idname = 'cats_eyes.reset_rotation'
    bl_label = 'Reset Rotation'
    bl_description = "This resets the eye positions"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = Common.get_armature()
        if 'LeftEye' in armature.pose.bones:
            if 'RightEye' in armature.pose.bones:
                return True
        return False

    def execute(self, context):
        armature = Common.get_armature()

        context.scene.eye_rotation_x = 0
        context.scene.eye_rotation_y = 0

        global eye_left, eye_right, eye_left_data, eye_right_data
        eye_left = armature.pose.bones.get('LeftEye')
        eye_right = armature.pose.bones.get('RightEye')
        eye_left_data = armature.data.bones.get('LeftEye')
        eye_right_data = armature.data.bones.get('RightEye')

        eye_left.rotation_mode = 'XYZ'
        eye_left.rotation_euler[0] = 0
        eye_left.rotation_euler[1] = 0
        eye_left.rotation_euler[2] = 0

        eye_right.rotation_mode = 'XYZ'
        eye_right.rotation_euler[0] = 0
        eye_right.rotation_euler[1] = 0
        eye_right.rotation_euler[2] = 0

        return {'FINISHED'}


@register_wrap
class TestBlinking(bpy.types.Operator):
    bl_idname = 'cats_eyes.test_blinking'
    bl_label = 'Test'
    bl_description = "This lets you see how eye blinking will look ingame"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.has_shapekeys(eye_mesh):
            if 'eyes_closed' in eye_mesh.data.shape_keys.key_blocks:
                return True
        return False

    def execute(self, context):
        shapekey_blink = eye_mesh.data.shape_keys.key_blocks.get('eyes_closed')
        if shapekey_blink:
            shapekey_blink.value = context.scene.eye_blink_shape
        return {'FINISHED'}


@register_wrap
class ResetBlinkTest(bpy.types.Operator):
    bl_idname = 'cats_eyes.reset_blink_test'
    bl_label = 'Reset Shapes'
    bl_description = "This resets the blink testing"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        for shape_key in Common.get_objects()[context.scene.mesh_name_eye].data.shape_keys.key_blocks:
            shape_key.value = 0
        context.scene.eye_blink_shape = 1

        return {'FINISHED'}
