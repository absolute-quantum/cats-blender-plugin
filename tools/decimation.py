# MIT License

# Copyright (c) 2018 Hotox

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

# Code author: Hotox
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by:

import bpy

from . import common as Common
from . import armature_bones as Bones
from .register import register_wrap


ignore_shapes = []
ignore_meshes = []


@register_wrap
class ScanButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.auto_scan'
    bl_label = 'Scan for decimation models'
    bl_description = 'Separates the mesh.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if context.scene.add_shape_key == "":
            return False

        return True

    def execute(self, context):
        shape = context.scene.add_shape_key
        shapes = Common.get_shapekeys_decimation_list(self, context)
        count = len(shapes)

        if count > 1 and shapes.index(shape) == count - 1:
            context.scene.add_shape_key = shapes[count - 2]

        ignore_shapes.append(shape)

        return {'FINISHED'}


@register_wrap
class AddShapeButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.add_shape'
    bl_label = 'Add'
    bl_description = 'Adds the selected shape key to the whitelist.\n' \
                     'This means that every mesh containing that shape key will be not decimated.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if context.scene.add_shape_key == "":
            return False

        return True

    def execute(self, context):
        shape = context.scene.add_shape_key
        shapes = Common.get_shapekeys_decimation_list(self, context)
        count = len(shapes)

        if count > 1 and shapes.index(shape) == count - 1:
            context.scene.add_shape_key = shapes[count - 2]

        ignore_shapes.append(shape)

        return {'FINISHED'}


@register_wrap
class AddMeshButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.add_mesh'
    bl_label = 'Add'
    bl_description = 'Adds the selected mesh to the whitelist.\n' \
                     'This means that this mesh will be not decimated.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if context.scene.add_mesh == "":
            return False
        return True

    def execute(self, context):
        ignore_meshes.append(context.scene.add_mesh)

        return {'FINISHED'}


@register_wrap
class RemoveShapeButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.remove_shape'
    bl_label = ''
    bl_description = 'Removes the selected shape key from the whitelist.\n' \
                     'This means that this shape key is no longer decimation safe!'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    shape_name = bpy.props.StringProperty()

    def execute(self, context):
        ignore_shapes.remove(self.shape_name)

        return {'FINISHED'}


@register_wrap
class RemoveMeshButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.remove_mesh'
    bl_label = ''
    bl_description = 'Removes the selected mesh from the whitelist.\n' \
                     'This means that this mesh will be decimated.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    mesh_name = bpy.props.StringProperty()

    def execute(self, context):
        ignore_meshes.remove(self.mesh_name)

        return {'FINISHED'}


@register_wrap
class AutoDecimateButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.auto_decimate'
    bl_label = 'Quick Decimation'
    bl_description = 'This will automatically decimate your model while preserving the shape keys.\n' \
                     'You should manually remove unimportant meshes first.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        meshes = Common.get_meshes_objects()
        if not meshes or len(meshes) == 0:
            self.report({'ERROR'}, 'No meshes found!')
            return {'FINISHED'}

        saved_data = Common.SavedData()

        if context.scene.decimation_mode != 'CUSTOM':
            mesh = Common.join_meshes(repair_shape_keys=False)
            Common.separate_by_materials(context, mesh)

        self.decimate(context)

        Common.join_meshes()

        saved_data.load()

        return {'FINISHED'}

    def decimate(self, context):
        print('START DECIMATION')
        Common.set_default_stage()

        custom_decimation = context.scene.decimation_mode == 'CUSTOM'
        full_decimation = context.scene.decimation_mode == 'FULL'
        half_decimation = context.scene.decimation_mode == 'HALF'
        safe_decimation = context.scene.decimation_mode == 'SAFE'
        save_fingers = context.scene.decimate_fingers
        max_tris = context.scene.max_tris
        meshes = []
        current_tris_count = 0
        tris_count = 0

        meshes_obj = Common.get_meshes_objects()

        for mesh in meshes_obj:
            Common.set_active(mesh)
            Common.switch('EDIT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            Common.switch('OBJECT')
            Common.remove_doubles(mesh, 0.00001, save_shapes=True)
            current_tris_count += len(mesh.data.polygons)

        if save_fingers:
            for mesh in meshes_obj:
                if len(mesh.vertex_groups) > 0:
                    Common.set_active(mesh)
                    Common.switch('EDIT')

                    bpy.ops.mesh.select_mode(type='VERT')

                    for finger in Bones.bone_finger_list:
                        print(finger)
                        vgs = [mesh.vertex_groups.get(finger + 'L'), mesh.vertex_groups.get(finger + 'R')]
                        for vg in vgs:
                            if vg:
                                bpy.ops.object.vertex_group_set_active(group=vg.name)
                                bpy.ops.object.vertex_group_select()
                                try:
                                    bpy.ops.mesh.separate(type='SELECTED')
                                except RuntimeError:
                                    pass

                    bpy.ops.object.mode_set(mode='OBJECT')

                    Common.unselect_all()

        for mesh in meshes_obj:
            Common.set_active(mesh)
            tris = len(mesh.data.polygons)

            if custom_decimation and mesh.name in ignore_meshes:
                Common.unselect_all()
                continue

            if Common.has_shapekeys(mesh):
                if full_decimation:
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
                elif custom_decimation:
                    found = False
                    for shape in ignore_shapes:
                        if shape in mesh.data.shape_keys.key_blocks:
                            found = True
                            break
                    if found:
                        Common.unselect_all()
                        continue
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
                elif half_decimation and len(mesh.data.shape_keys.key_blocks) < 4:
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
                elif len(mesh.data.shape_keys.key_blocks) == 1:
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
            else:
                meshes.append((mesh, tris))
                tris_count += tris

            Common.unselect_all()

        print(current_tris_count)
        print(tris_count)

        print((current_tris_count - tris_count), '>', max_tris)

        if (current_tris_count - tris_count) > max_tris:
            message = ['This model can not be decimated to ' + str(max_tris) + ' tris with the specified settings.']
            if safe_decimation:
                message.append('Try to use Custom, Half or Full Decimation.')
            elif half_decimation:
                message.append('Try to use Custom or Full Decimation.')
            elif custom_decimation:
                message.append('Select fewer shape keys and/or meshes or use Full Decimation.')
            if save_fingers:
                if full_decimation:
                    message.append("Disable 'Save Fingers' or increase the Tris Count.")
                else:
                    message[1] = message[1][:-1]
                    message.append("or disable 'Save Fingers'.")
            Common.show_error(6, message)
            return

        try:
            decimation = (max_tris - current_tris_count + tris_count) / tris_count
        except ZeroDivisionError:
            decimation = 1
        if decimation >= 1:
            Common.show_error(6, ['The model already has less than ' + str(max_tris) + ' tris. Nothing had to be decimated.'])
            return
        elif decimation <= 0:
            Common.show_error(4.5, ['The model could not be decimated to ' + str(max_tris) + ' tris.',
                                          'It got decimated as much as possible within the limits.'])

        meshes.sort(key=lambda x: x[1])

        for mesh in reversed(meshes):
            mesh_obj = mesh[0]
            tris = mesh[1]

            Common.set_active(mesh_obj)
            print(mesh_obj.name)

            # Calculate new decimation ratio
            try:
                decimation = (max_tris - current_tris_count + tris_count) / tris_count
            except ZeroDivisionError:
                decimation = 1
            print(decimation)

            # Apply decimation mod
            mod = mesh_obj.modifiers.new("Decimate", 'DECIMATE')
            mod.ratio = decimation
            mod.use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)

            tris_after = len(mesh_obj.data.polygons)
            print(tris)
            print(tris_after)

            current_tris_count = current_tris_count - tris + tris_after
            tris_count = tris_count - tris

            Common.unselect_all()

        # # Check if decimated correctly
        # if decimation < 0:
        #     print('')
        #     print('RECHECK!')
        #
        #     current_tris_count = 0
        #     tris_count = 0
        #
        #     for mesh in Common.get_meshes_objects():
        #         Common.select(mesh)
        #         tris = len(bpy.context.active_object.data.polygons)
        #         tris_count += tris
        #         print(tris_count)
        #
        #     for mesh in reversed(meshes):
        #         mesh_obj = mesh[0]
        #         Common.select(mesh_obj)
        #
        #         # Calculate new decimation ratio
        #         decimation = (max_tris - tris_count) / tris_count
        #         print(decimation)
        #
        #         # Apply decimation mod
        #         mod = mesh_obj.modifiers.new("Decimate", 'DECIMATE')
        #         mod.ratio = decimation
        #         mod.use_collapse_triangulate = True
        #         bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
        #
        #         Common.unselect_all()
        #         break






