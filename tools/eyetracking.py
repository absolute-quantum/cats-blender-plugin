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
# Edits by: 

import bpy
import tools.common

import math
import mathutils
import numpy as np
from math import radians
from mathutils import Vector, Matrix

class CreateEyesButton(bpy.types.Operator):
    bl_idname = 'create.eyes'
    bl_label = 'Create eye tracking'

    bl_options = {'REGISTER', 'UNDO'}

    def vertex_group_exists(self, mesh_name, bone_name):
        mesh = bpy.data.objects[mesh_name]

        group_lookup = {g.index: g.name for g in mesh.vertex_groups}
        verts = {name: [] for name in group_lookup.values()}
        for v in mesh.data.vertices:
            for g in v.groups:
                verts[group_lookup[g.group]].append(v)

        try:
            verts[bone_name]
        except:
            return False

        return len(verts[bone_name]) >= 1

    def set_to_center_mass(self, bone, center_mass_bone):
        bone.head = (bpy.context.object.data.edit_bones[center_mass_bone].head + bpy.context.object.data.edit_bones[center_mass_bone].tail) / 2
        bone.tail = (bpy.context.object.data.edit_bones[center_mass_bone].head + bpy.context.object.data.edit_bones[center_mass_bone].tail) / 2

    def find_center_vector_of_vertex_group(self, mesh_name, vertex_group):
        mesh = bpy.data.objects[mesh_name]

        group_lookup = {g.index: g.name for g in mesh.vertex_groups}
        verts = {name: [] for name in group_lookup.values()}
        for v in bpy.context.object.data.vertices:
            for g in v.groups:
                verts[group_lookup[g.group]].append(v)

        # Find the average vector point of the vertex cluster
        divide_by = len(verts[vertex_group])
        total = Vector()

        if divide_by == 0:
            return False

        for vertice in verts[vertex_group]:
            total += vertice.co

        average = total / divide_by

        return average

    def copy_vertex_group(self, mesh, vertex_group, rename_to):
        # iterate through the vertex group
        vertex_group_index = 0
        for group in bpy.data.objects[mesh].vertex_groups:
            # Find the vertex group
            if group.name == vertex_group:
                # Copy the group and rename
                bpy.data.objects[mesh].vertex_groups.active_index = vertex_group_index
                new_vertex_group = bpy.ops.object.vertex_group_copy()
                bpy.data.objects[mesh].vertex_groups[vertex_group + '_copy'].name = rename_to
                break

            vertex_group_index += 1

    def copy_shape_key(self, target_mesh, shapekey_name, rename_to, new_index, random_mix = False):
        mesh = bpy.data.objects[target_mesh]

        # first set value to 0 for all shape keys, so we don't mess up
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            shapekey.value = 0

        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if random_mix is not False:
                if shapekey_name is not shapekey.name:
                    if 'Basis' not in shapekey.name:
                        shapekey.value = random_mix
                        random_mix = False

            if shapekey_name == shapekey.name:
                mesh.active_shape_key_index = index
                shapekey.value = 1
                mesh.shape_key_add(name=rename_to, from_mix=True)

                # Select the created shapekey
                mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1

                # Re-adjust index position
                position_correct = False
                while position_correct is False:
                    bpy.ops.object.shape_key_move(type='DOWN')

                    if mesh.active_shape_key_index == new_index:
                        position_correct = True

        # reset shape values back to 0
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            shapekey.value = 0

    def fix_eye_position(self, mesh_name, old_eyebone, eyebone):
        # Verify that the new eye bone is in the correct position
        # by comparing the old eye vertex group average vector location
        coords_eye = self.find_center_vector_of_vertex_group(mesh_name, old_eyebone)

        if coords_eye is False:
            return False

        vector_difference = Vector(np.subtract(coords_eye, eyebone.tail))

        # We want to have the eye bone ATLEAST behind the eye, not infront
        if vector_difference[1] > 0.05:
            # Check if the bone is infront the eye, this is always bad
            if vector_difference[1] > 0.05:
                eyebone.head[1] = eyebone.head[1] + 0.2
                eyebone.tail[1] = eyebone.tail[1] + 0.2

                return self.fix_eye_position(mesh_name, old_eyebone, eyebone)

            # Check if the bone is too much behind the eye
            if vector_difference[1] < 0.4:
                eyebone.head[1] = eyebone.head[1] - 0.2
                eyebone.tail[1] = eyebone.tail[1] - 0.2

                return self.fix_eye_position(mesh_name, old_eyebone, eyebone)

    def execute(self, context):
        tools.common.unhide_all()

        armature = tools.common.get_armature()
        bpy.context.scene.objects.active = armature
        armature.select = True

        # Why does two times edit works?
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='EDIT')

        # Find existing LeftEye/RightEye
        if 'LeftEye' in bpy.context.object.data.edit_bones:
            self.report({'ERROR'}, 'Eye tracking already exists: LeftEye bone exists')
            return{'FINISHED'}

        if 'RightEye' in bpy.context.object.data.edit_bones:
            self.report({'ERROR'}, 'Eye tracking already exists: RightEye bone exists')
            return{'FINISHED'}

        # Find the existing vertex group of the left eye bone
        if self.vertex_group_exists(context.scene.mesh_name_eye, context.scene.eye_left) is False:
            self.report({'ERROR'}, 'The left eye bone has no existing vertex group or no vertices assigned to it, this is probably the wrong eye bone')
            return {'CANCELLED'}

        # Find the existing vertex group of the right eye bone
        if self.vertex_group_exists(context.scene.mesh_name_eye, context.scene.eye_right) is False:
            self.report({'ERROR'}, 'The right eye bone has no existing vertex group or no vertices assigned to it, this is probably the wrong eye bone')
            return {'CANCELLED'}

        # Set head roll to 0 degrees
        bpy.context.object.data.edit_bones[context.scene.head].roll = 0

        # Create the new eye bones
        new_left_eye = bpy.context.object.data.edit_bones.new('LeftEye')
        new_right_eye = bpy.context.object.data.edit_bones.new('RightEye')

        # Parent them correctly
        new_left_eye.parent = bpy.context.object.data.edit_bones[context.scene.head]
        new_right_eye.parent = bpy.context.object.data.edit_bones[context.scene.head]

        # Use center of mass from old eye bone to place new eye bone in
        # TODO: might be best to just check the vertex group of the eyes and determine location from that.
        self.set_to_center_mass(new_right_eye, context.scene.eye_right)
        self.set_to_center_mass(new_left_eye, context.scene.eye_left)

        # Set the eye bone up straight
        # TODO: depending on the scale of the model, this might looked fucked: the eye bone will be too high or too low
        new_right_eye.tail[2] = new_right_eye.head[2] + 0.3
        new_left_eye.tail[2] = new_left_eye.head[2] + 0.3

        # Switch to mesh
        bpy.context.scene.objects.active = bpy.data.objects[context.scene.mesh_name_eye]

        bpy.ops.object.mode_set(mode='OBJECT')

        # Make sure the bones are positioned correctly
        # not too far away from eye vertex (behind and infront)
        if context.scene.experimental_eye_fix:
            self.fix_eye_position(context.scene.mesh_name_eye, context.scene.eye_right, new_right_eye)
            self.fix_eye_position(context.scene.mesh_name_eye, context.scene.eye_left, new_left_eye)

        # Copy the existing eye vertex group to the new one
        self.copy_vertex_group(context.scene.mesh_name_eye, context.scene.eye_right, 'RightEye')
        self.copy_vertex_group(context.scene.mesh_name_eye, context.scene.eye_left, 'LeftEye')

        # Copy shape key mixes from user defined shape keys and rename them to the correct liking of VRC
        self.copy_shape_key(context.scene.mesh_name_eye, context.scene.wink_left, 'vrc.blink_left', 1, 0.00001)
        self.copy_shape_key(context.scene.mesh_name_eye, context.scene.wink_right, 'vrc.blink_right', 2, 0.00002)
        self.copy_shape_key(context.scene.mesh_name_eye, context.scene.lowerlid_left, 'vrc.lowerlid_left', 3, 0.00003)
        self.copy_shape_key(context.scene.mesh_name_eye, context.scene.lowerlid_right, 'vrc.lowerlid_right', 4, 0.00004)


        # Remove empty objects
        tools.common.remove_empty()

        # Rename armature
        tools.common.get_armature().name = 'Armature'

        self.report({'INFO'}, 'Created eye tracking!')

        return{'FINISHED'}