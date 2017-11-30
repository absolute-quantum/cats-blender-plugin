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

        return True

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

    def get_vertex_group(self, mesh, vertex_group):
        # iterate through the vertex group
        for group in bpy.data.objects[mesh].vertex_groups:
            # Find the vertex group
            if group.name == vertex_group:
                # Return the group
                return bpy.data.objects[mesh].vertex_groups[vertex_group]

    # self.copy_shape_key(context, shapes[0], 'vrc.blink_left', 1)
    def copy_shape_key(self, mesh_name, from_shape, new_name, new_index):
        mesh = bpy.data.objects[mesh_name]

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
                mesh.shape_key_add(name=new_name, from_mix=True)

                # Select the created shapekey
                mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1

                # Re-adjust index position
                position_correct = False
                bpy.ops.object.shape_key_move(type='TOP')
                while position_correct is False:
                    if mesh.active_shape_key_index > new_index:
                        bpy.ops.object.shape_key_move(type='DOWN')
                    else:
                        position_correct = True

        # reset shape values back to 0
        for shapekey in mesh.data.shape_keys.key_blocks:
            shapekey.value = 0

        mesh.active_shape_key_index = 0
        return from_shape

    def fix_eye_position(self, mesh_name, old_eyebone, eyebone, scale):
        # Verify that the new eye bone is in the correct position
        # by comparing the old eye vertex group average vector location
        coords_eye = tools.common.find_center_vector_of_vertex_group(mesh_name, old_eyebone)

        if coords_eye is False:
            return False

        eyebone.head[0] = coords_eye[0]
        eyebone.head[1] = coords_eye[1] + scale
        eyebone.head[2] = coords_eye[2]

        eyebone.tail[0] = coords_eye[0]
        eyebone.tail[1] = coords_eye[1] + scale
        eyebone.tail[2] = coords_eye[2] + 0.2

    def execute(self, context):
        # PreserveState = tools.common.PreserveState()
        # PreserveState.save()

        tools.common.unhide_all()

        armature = tools.common.get_armature()
        tools.common.select(armature)

        # Why does two times edit works?
        tools.common.switch('EDIT')
        tools.common.switch('EDIT')

        # Selectors
        left_eye_selector = context.scene.eye_left
        right_eye_selector = context.scene.eye_right

        # Find existing LeftEye/RightEye and rename
        if 'LeftEye' in bpy.context.object.data.edit_bones:
            bpy.context.object.data.edit_bones['LeftEye'].name = 'OldLeftEye'
            left_eye_selector = 'OldLeftEye'

        if 'RightEye' in bpy.context.object.data.edit_bones:
            bpy.context.object.data.edit_bones['RightEye'].name = 'OldRightEye'
            right_eye_selector = 'OldRightEye'

        # Find the existing vertex group of the left eye bone
        if self.vertex_group_exists(context.scene.mesh_name_eye, left_eye_selector) is False:
            self.report({'ERROR'}, 'The left eye bone has no existing vertex group or no vertices assigned to it, this is probably the wrong eye bone')
            return {'CANCELLED'}

        # Find the existing vertex group of the right eye bone
        if self.vertex_group_exists(context.scene.mesh_name_eye, right_eye_selector) is False:
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
        self.set_to_center_mass(new_right_eye, right_eye_selector)
        self.set_to_center_mass(new_left_eye, left_eye_selector)

        # Set the eye bone up straight
        new_right_eye.tail[2] = new_right_eye.head[2] + 0.3
        new_left_eye.tail[2] = new_left_eye.head[2] + 0.3

        # Switch to mesh
        bpy.context.scene.objects.active = bpy.data.objects[context.scene.mesh_name_eye]

        tools.common.switch('OBJECT')

        # Make sure the bones are positioned correctly
        # not too far away from eye vertex (behind and infront)
        if context.scene.experimental_eye_fix:
            self.fix_eye_position(context.scene.mesh_name_eye, right_eye_selector, new_right_eye, context.scene.eye_distance)
            self.fix_eye_position(context.scene.mesh_name_eye, left_eye_selector, new_left_eye, context.scene.eye_distance)

        # Copy the existing eye vertex group to the new one
        self.copy_vertex_group(context.scene.mesh_name_eye, right_eye_selector, 'RightEye')
        self.copy_vertex_group(context.scene.mesh_name_eye, left_eye_selector, 'LeftEye')

        # Store shape keys to ignore changes during copying
        selected_shapes = [context.scene.wink_left, context.scene.wink_right, context.scene.lowerlid_left, context.scene.lowerlid_right]

        # Copy shape key mixes from user defined shape keys and rename them to the correct liking of VRC
        mesh_name = context.scene.mesh_name_eye
        shapes = [context.scene.wink_left, context.scene.wink_right, context.scene.lowerlid_left, context.scene.lowerlid_right]
        shapes[0] = self.copy_shape_key(mesh_name, shapes[0], 'vrc.blink_left', 1)
        shapes[1] = self.copy_shape_key(mesh_name, shapes[1], 'vrc.blink_right', 2)
        shapes[2] = self.copy_shape_key(mesh_name, shapes[2], 'vrc.lowerlid_left', 3)
        shapes[3] = self.copy_shape_key(mesh_name, shapes[3], 'vrc.lowerlid_right', 4)

        # Reset the scenes in case they were changed
        context.scene.wink_left = shapes[0]
        context.scene.wink_right = shapes[1]
        context.scene.lowerlid_left = shapes[2]
        context.scene.lowerlid_right = shapes[3]

        # Remove empty objects
        tools.common.switch('EDIT')
        tools.common.remove_empty()

        # Fix armature name
        tools.common.fix_armature_name()

        # Check for correct bone hierarchy
        is_correct = tools.armature.check_hierarchy([['Hips', 'Spine', 'Chest', 'Neck', 'Head']])

        repair_shapekeys(context.scene.mesh_name_eye, 'RightEye')

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


def addvertex(meshname, shapekey_name):
    mesh = bpy.data.objects[meshname].data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    print(" ")
    if shapekey_name in bm.verts.layers.shape.keys():
        val = bm.verts.layers.shape.get(shapekey_name)
        print("%s = %s" % (shapekey_name, val))
        sk = mesh.shape_keys.key_blocks[shapekey_name]
        print("v=%f, f=%f" % (sk.value, sk.frame))
        for i in range(len(bm.verts)):
            v = bm.verts[i]
            delta = v[val] - v.co
            if (delta.length > 0):
                print("v[%d]+%s" % (i, delta))

    print(" ")


# Check which shape keys will be deleted on export by Blender
def checkshapekeys():
    for ob in bpy.data.objects:
        if ob.type == 'MESH':
            mesh = ob
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()

    deleted_shapes = []
    for key in bm.verts.layers.shape.keys():
        if key == 'Basis':
            continue
        val = bm.verts.layers.shape.get(key)
        delete = True
        for vert in bm.verts:
            delta = vert[val] - vert.co
            if delta.length > 0:
                delete = False
                break
        if delete:
            deleted_shapes.append(key)

    return deleted_shapes


# Repair vrc shape keys
def repair_shapekeys(mesh_name, vertex_group):
    mesh = bpy.data.objects[mesh_name]
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()

    # Get a vertex from the eye vertex group
    gi = mesh.vertex_groups[vertex_group].index
    for v in mesh.data.vertices:
        for g in v.groups:
            if g.group == gi:
                vcoords = v.co.xyz

    if vcoords is None:
        return

    # Move that vertex by a tiny amount
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
                break

    bm.to_mesh(mesh.data)
