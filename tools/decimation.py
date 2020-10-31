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
from ..translations import t


ignore_shapes = []
ignore_meshes = []


@register_wrap
class ScanButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.auto_scan'
    bl_label = t('ScanButton.label')
    bl_description = t('ScanButton.desc')
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
    bl_label = t('AddShapeButton.label')
    bl_description = t('AddShapeButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if context.scene.add_shape_key == "":
            return False
        return True

    def execute(self, context):
        shape = context.scene.add_shape_key
        shapes = [x[0] for x in Common.get_shapekeys_decimation_list(self, context)]
        count = len(shapes)

        if count > 1 and shapes.index(shape) == count - 1:
            context.scene.add_shape_key = shapes[count - 2]

        ignore_shapes.append(shape)

        return {'FINISHED'}


@register_wrap
class AddMeshButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.add_mesh'
    bl_label = t('AddMeshButton.label')
    bl_description = t('AddMeshButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if context.scene.add_mesh == "":
            return False
        return True

    def execute(self, context):
        ignore_meshes.append(context.scene.add_mesh)

        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                if obj.parent and obj.parent.type == 'ARMATURE' and obj.parent.name == bpy.context.scene.armature:
                    if obj.name in ignore_meshes:
                        continue
                    context.scene.add_mesh = obj.name
                    break

        return {'FINISHED'}


@register_wrap
class RemoveShapeButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.remove_shape'
    bl_label = t('RemoveShapeButton.label')
    bl_description = t('RemoveShapeButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    shape_name = bpy.props.StringProperty()

    def execute(self, context):
        ignore_shapes.remove(self.shape_name)

        return {'FINISHED'}


@register_wrap
class RemoveMeshButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.remove_mesh'
    bl_label = t('RemoveMeshButton.label')
    bl_description = t('RemoveMeshButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    mesh_name = bpy.props.StringProperty()

    def execute(self, context):
        ignore_meshes.remove(self.mesh_name)

        return {'FINISHED'}


@register_wrap
class AutoDecimateButton(bpy.types.Operator):
    bl_idname = 'cats_decimation.auto_decimate'
    bl_label = t('AutoDecimateButton.label')
    bl_description = t('AutoDecimateButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    armature_name: bpy.props.StringProperty(
        name = 'armature_name',
    )

    preserve_seams: bpy.props.BoolProperty(
        name = 'preserve_seams',
    )

    seperate_materials: bpy.props.BoolProperty(
        name = 'seperate_materials'
    )

    def execute(self, context):
        meshes = Common.get_meshes_objects()
        if not meshes or len(meshes) == 0:
            self.report({'ERROR'}, t('AutoDecimateButton.error.noMesh'))
            return {'FINISHED'}

        saved_data = Common.SavedData()

        if context.scene.decimation_mode != 'CUSTOM':
            mesh = Common.join_meshes(repair_shape_keys=False, armature_name=self.armature_name)
            if self.seperate_materials:
                Common.separate_by_materials(context, mesh)

        self.decimate(context)

        Common.join_meshes(armature_name=self.armature_name)

        saved_data.load()

        return {'FINISHED'}

    def decimate(self, context):
        print('START DECIMATION')
        Common.set_default_stage()

        custom_decimation = context.scene.decimation_mode == 'CUSTOM'
        full_decimation = context.scene.decimation_mode == 'FULL'
        half_decimation = context.scene.decimation_mode == 'HALF'
        safe_decimation = context.scene.decimation_mode == 'SAFE'
        smart_decimation = context.scene.decimation_mode == 'SMART'
        save_fingers = context.scene.decimate_fingers
        max_tris = context.scene.max_tris
        meshes = []
        current_tris_count = 0
        tris_count = 0

        meshes_obj = Common.get_meshes_objects(armature_name=self.armature_name)

        for mesh in meshes_obj:
            Common.set_active(mesh)
            Common.switch('EDIT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
            Common.switch('OBJECT')
            if context.scene.decimation_remove_doubles:
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
                elif smart_decimation:
                    if len(mesh.data.shape_keys.key_blocks) == 1:
                        bpy.ops.object.shape_key_remove(all=True)
                    else:
                        # Add a duplicate basis key which we un-apply to fix shape keys
                        mesh.active_shape_key_index = 0
                        bpy.ops.object.shape_key_add(from_mix=False)
                        mesh.active_shape_key.name = "CATS Basis"
                        mesh.active_shape_key_index = 0
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
            message = [t('decimate.cantDecimateWithSettings', number=str(max_tris))]
            if safe_decimation:
                message.append(t('decimate.safeTryOptions'))
            elif half_decimation:
                message.append(t('decimate.halfTryOptions'))
            elif custom_decimation:
                message.append(t('decimate.customTryOptions'))
            if save_fingers:
                if full_decimation or smart_decimation:
                    message.append(t('decimate.disableFingersOrIncrease'))
                else:
                    message[1] = message[1][:-1]
                    message.append(t('decimate.disableFingers'))
            Common.show_error(6, message)
            return

        try:
            decimation = (max_tris - current_tris_count + tris_count) / tris_count
        except ZeroDivisionError:
            decimation = 1
        if decimation >= 1:
            Common.show_error(6, [t('decimate.noDecimationNeeded', number=str(max_tris))])
            return
        elif decimation <= 0:
            Common.show_error(4.5, [t('decimate.cantDecimate1', number=str(max_tris)),
                                    t('decimate.cantDecimate2')])

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
            if not smart_decimation:
                mod = mesh_obj.modifiers.new("Decimate", 'DECIMATE')
                mod.ratio = decimation
                mod.use_collapse_triangulate = True
                Common.apply_modifier(mod)
            else:
                Common.switch('EDIT')
                bpy.ops.mesh.select_mode(type="VERT")
                bpy.ops.mesh.select_all(action="SELECT")
                # TODO: Fix decimation calculation when pinning seams
                if self.preserve_seams:
                    bpy.ops.mesh.select_all(action="DESELECT")
                    bpy.ops.uv.seams_from_islands()

                    # select all seams
                    Common.switch('OBJECT')
                    me = mesh_obj.data
                    for edge in me.edges:
                        if edge.use_seam:
                            edge.select = True

                    Common.switch('EDIT')
                    bpy.ops.mesh.select_all(action="INVERT")

                #TODO: If we can create a vertex group with weights roughly equal to 'how likely is this to be animated',
                #      we can create much better topology by inverse-weighting against it.
                bpy.ops.mesh.decimate(ratio=decimation,
                                      use_vertex_group=False,
                                      vertex_group_factor=1.0,
                                      invert_vertex_group=False,
                                      use_symmetry=True,
                                      symmetry_axis='X')
                Common.switch('OBJECT')

            tris_after = len(mesh_obj.data.polygons)
            print(tris)
            print(tris_after)

            current_tris_count = current_tris_count - tris + tris_after
            tris_count = tris_count - tris
            # Repair shape keys if SMART mode is enabled
            if smart_decimation and Common.has_shapekeys(mesh_obj):
                for idx in range(1, len(mesh_obj.data.shape_keys.key_blocks) - 1):
                    if "Reverted" in mesh_obj.data.shape_keys.key_blocks[idx].name:
                        continue
                    mesh_obj.active_shape_key_index = idx
                    Common.switch('EDIT')
                    bpy.ops.mesh.blend_from_shape(shape="CATS Basis", blend=-1.0, add=True)
                    Common.switch('OBJECT')
                mesh_obj.shape_key_remove(key=mesh_obj.data.shape_keys.key_blocks["CATS Basis"])
                mesh_obj.active_shape_key_index = 0




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
        #         Common.apply_modifier(mod)
        #
        #         Common.unselect_all()
        #         break


@register_wrap
class AutoDecimatePresetGood(bpy.types.Operator):
    bl_idname = 'cats_decimation.preset_good'
    bl_label = t('DecimationPanel.preset.good.label')
    bl_description = t('DecimationPanel.preset.good.description')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        bpy.context.scene.max_tris = 70000
        return {'FINISHED'}


@register_wrap
class AutoDecimatePresetExcellent(bpy.types.Operator):
    bl_idname = 'cats_decimation.preset_excellent'
    bl_label = t('DecimationPanel.preset.excellent.label')
    bl_description = t('DecimationPanel.preset.excellent.description')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        bpy.context.scene.max_tris = 32000
        return {'FINISHED'}


@register_wrap
class AutoDecimatePresetQuest(bpy.types.Operator):
    bl_idname = 'cats_decimation.preset_quest'
    bl_label = t('DecimationPanel.preset.quest.label')
    bl_description = t('DecimationPanel.preset.quest.description')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        bpy.context.scene.max_tris = 5000
        return {'FINISHED'}
