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
import tools.common
import tools.armature_bones as Bones


ignore_shapes = []
ignore_meshes = []


class ScanButton(bpy.types.Operator):
    bl_idname = 'auto.scan'
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
        shapes = tools.common.get_shapekeys_decimation_list(self, context)
        count = len(shapes)

        if count > 1 and shapes.index(shape) == count - 1:
            context.scene.add_shape_key = shapes[count - 2]

        ignore_shapes.append(shape)

        return {'FINISHED'}


class AddShapeButton(bpy.types.Operator):
    bl_idname = 'add.shape'
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
        shapes = tools.common.get_shapekeys_decimation_list(self, context)
        count = len(shapes)

        if count > 1 and shapes.index(shape) == count - 1:
            context.scene.add_shape_key = shapes[count - 2]

        ignore_shapes.append(shape)

        return {'FINISHED'}


class AddMeshButton(bpy.types.Operator):
    bl_idname = 'add.mesh'
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


class RemoveShapeButton(bpy.types.Operator):
    bl_idname = 'remove.shape'
    bl_label = ''
    bl_description = 'Removes the selected shape key from the whitelist.\n' \
                     'This means that this shape key is no longer decimation safe!'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    shape_name = bpy.props.StringProperty()

    def execute(self, context):
        ignore_shapes.remove(self.shape_name)

        return {'FINISHED'}


class RemoveMeshButton(bpy.types.Operator):
    bl_idname = 'remove.mesh'
    bl_label = ''
    bl_description = 'Removes the selected mesh from the whitelist.\n' \
                     'This means that this mesh will be decimated.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    mesh_name = bpy.props.StringProperty()

    def execute(self, context):
        ignore_meshes.remove(self.mesh_name)

        return {'FINISHED'}


class AutoDecimateButton(bpy.types.Operator):
    bl_idname = 'auto.decimate'
    bl_label = 'Quick Decimation'
    bl_description = 'This will automatically decimate your model while preserving the shape keys.\n' \
                     'You should manually remove unimportant meshes first.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        i = 0
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                if ob.parent is not None and ob.parent.type == 'ARMATURE':
                    i += 1
        return i == 1

    def execute(self, context):
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            tools.common.unselect_all()
            meshes = tools.common.get_meshes_objects()
            if len(meshes) == 0:
                return {'FINISHED'}
            obj = meshes[0]

        if context.scene.decimation_mode != 'CUSTOM':
            tools.common.separate_by_materials(context, obj)

        self.decimate(context)

        mesh = tools.common.join_meshes()
        if mesh is not None:
            tools.common.repair_viseme_order(mesh.name)

        return {'FINISHED'}

    def decimate(self, context):
        print('START DECIMATION')
        tools.common.set_default_stage()

        custom_decimation = context.scene.decimation_mode == 'CUSTOM'
        full_decimation = context.scene.decimation_mode == 'FULL'
        half_decimation = context.scene.decimation_mode == 'HALF'
        safe_decimation = context.scene.decimation_mode == 'SAFE'
        decimate_fingers = context.scene.decimate_fingers
        meshes = []
        current_tris_count = 0
        tris_count = 0

        meshes_obj = tools.common.get_meshes_objects()

        for mesh in meshes_obj:
            current_tris_count += len(mesh.data.polygons)

        if decimate_fingers:
            for mesh in meshes_obj:
                if len(mesh.vertex_groups) > 0:
                    tools.common.select(mesh)
                    tools.common.switch('EDIT')

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

                    tools.common.unselect_all()

        for mesh in meshes_obj:
            tools.common.select(mesh)
            tris = len(mesh.data.polygons)

            if custom_decimation and mesh.name in ignore_meshes:
                tools.common.unselect_all()
                continue

            if mesh.data.shape_keys is not None:
                if full_decimation:
                    print('FULL')
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
                        print('IGNORED')
                        tools.common.unselect_all()
                        continue
                    print('CUSTOM')
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
                elif half_decimation and len(mesh.data.shape_keys.key_blocks) < 4:
                    print('HALF')
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
                elif len(mesh.data.shape_keys.key_blocks) == 1:
                    print('SAVE')
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
            else:
                meshes.append((mesh, tris))
                tris_count += tris

            tools.common.unselect_all()

        print(current_tris_count)
        print(tris_count)

        if (current_tris_count - tris_count) > context.scene.max_tris:
            message = 'This model can not be decimated to the given tris count with the specified settings.\n'
            if safe_decimation:
                message += 'Try to use Custom, Half or Full decimation.'
            elif half_decimation:
                message += 'Try to use Custom or Full decimation.'
            elif custom_decimation:
                message += 'Select fewer shape keys and/or meshes or use Full decimation.'
            if decimate_fingers:
                message = message[:-1] + " or disable 'Save Fingers'."
            self.report({'ERROR'}, message)
            return

        try:
            decimation = (context.scene.max_tris - current_tris_count + tris_count) / tris_count
        except ZeroDivisionError:
            decimation = 1
        if decimation >= 1:
            self.report({'ERROR'}, 'The model already has less tris than given. Nothing had to be decimated.')
            return
        elif decimation <= 0:
            self.report({'ERROR'}, 'The model could not be decimated to the given tris count. It got decimated as much as possible within the limits.')

        meshes.sort(key=lambda x: x[1])

        for mesh in reversed(meshes):
            mesh_obj = mesh[0]
            tris = mesh[1]

            tools.common.select(mesh_obj)
            print(mesh_obj.name)

            # Calculate new decimation ratio
            try:
                decimation = (context.scene.max_tris - current_tris_count + tris_count) / tris_count
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

            tools.common.unselect_all()

        # # Check if decimated correctly
        # if decimation < 0:
        #     print('')
        #     print('RECHECK!')
        #
        #     current_tris_count = 0
        #     tris_count = 0
        #
        #     for mesh in tools.common.get_meshes_objects():
        #         tools.common.select(mesh)
        #         tris = len(bpy.context.active_object.data.polygons)
        #         tris_count += tris
        #         print(tris_count)
        #
        #     for mesh in reversed(meshes):
        #         mesh_obj = mesh[0]
        #         tools.common.select(mesh_obj)
        #
        #         # Calculate new decimation ratio
        #         decimation = (context.scene.max_tris - tris_count) / tris_count
        #         print(decimation)
        #
        #         # Apply decimation mod
        #         mod = mesh_obj.modifiers.new("Decimate", 'DECIMATE')
        #         mod.ratio = decimation
        #         mod.use_collapse_triangulate = True
        #         bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
        #
        #         tools.common.unselect_all()
        #         break






