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
import math

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

    armature_name = bpy.props.StringProperty(
        name='armature_name',
    )

    preserve_seams = bpy.props.BoolProperty(
        name='preserve_seams',
    )

    seperate_materials = bpy.props.BoolProperty(
        name='seperate_materials'
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
        animation_weighting = context.scene.decimation_animation_weighting
        animation_weighting_factor = context.scene.decimation_animation_weighting_factor
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
            current_tris_count += Common.get_tricount(mesh.data.polygons)

        if animation_weighting:
            for mesh in meshes_obj:
                # Weight by multiplied bone weights for every pair of bones.
                # This is O(n*m^2) for n verts and m bones, generally runs relatively quickly.
                weights = dict()
                for vertex in mesh.data.vertices:
                    v_weights = [group.weight for group in vertex.groups]
                    v_mults = []
                    for idx1, w1 in enumerate(vertex.groups):
                        for idx2, w2 in enumerate(vertex.groups):
                            if idx1 != idx2:
                                # Weight [vgroup * vgroup] for index = <mult>
                                if (w1.group, w2.group) not in weights:
                                    weights[(w1.group, w2.group)] = dict()
                                weights[(w1.group, w2.group)][vertex.index] = w1.weight * w2.weight

                # Normalize per vertex group pair
                normalizedweights = dict()
                for pair, weighting in weights.items():
                    m_min = 1
                    m_max = 0
                    for _, weight in weighting.items():
                        m_min = min(m_min, weight)
                        m_max = max(m_max, weight)

                    if pair not in normalizedweights:
                        normalizedweights[pair] = dict()
                    for v_index, weight in weighting.items():
                        try:
                            normalizedweights[pair][v_index] = (weight - m_min) / (m_max - m_min)
                        except ZeroDivisionError:
                            normalizedweights[pair][v_index] = weight

                newweights = dict()
                for pair, weighting in normalizedweights.items():
                    for v_index, weight in weighting.items():
                        try:
                            newweights[v_index] = max(newweights[v_index], weight)
                        except KeyError:
                            newweights[v_index] = weight

                s_weights = dict()

                # Weight by relative shape key movement. This is kind of slow, but not too bad. It's O(n*m) for n verts and m shape keys,
                # but shape keys contain every vert (not just the ones they impact)
                # For shape key in shape keys:
                for key_block in mesh.data.shape_keys.key_blocks[1:]:
                    basis = mesh.data.shape_keys.key_blocks[0]
                    s_weights[key_block.name] = dict()

                    for idx, vert in enumerate(key_block.data):
                        s_weights[key_block.name][idx] = math.sqrt(math.pow(basis.data[idx].co[0] - vert.co[0], 2.0) +
                                                                        math.pow(basis.data[idx].co[1] - vert.co[1], 2.0) +
                                                                        math.pow(basis.data[idx].co[2] - vert.co[2], 2.0))

                # normalize min/max vert movement
                s_normalizedweights = dict()
                for keyname, weighting in s_weights.items():
                    m_min = math.inf
                    m_max = 0
                    for _, weight in weighting.items():
                        m_min = min(m_min, weight)
                        m_max = max(m_max, weight)

                    if keyname not in s_normalizedweights:
                        s_normalizedweights[keyname] = dict()
                    for v_index, weight in weighting.items():
                        try:
                            s_normalizedweights[keyname][v_index] = (weight - m_min) / (m_max - m_min)
                        except ZeroDivisionError:
                            s_normalizedweights[keyname][v_index] = weight

                # find max normalized movement over all shape keys
                for pair, weighting in s_normalizedweights.items():
                    for v_index, weight in weighting.items():
                        try:
                            newweights[v_index] = max(newweights[v_index], weight)
                        except KeyError:
                            newweights[v_index] = weight

                # TODO: ignore shape keys which move very little?
                context.view_layer.objects.active = mesh
                bpy.ops.object.vertex_group_add()
                mesh.vertex_groups[-1].name = "CATS Animation"
                for idx, weight in newweights.items():
                    mesh.vertex_groups[-1].add([idx], weight, "REPLACE")

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
            tris = Common.get_tricount(mesh)

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
                if animation_weighting:
                    mod.vertex_group = "CATS Animation"
                    mod.vertex_group_factor = animation_weighting_factor
                    mod.invert_vertex_group = True
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

                #TODO: On many meshes, un-subdividing until it's near the target verts and then decimating the rest of the way
                #      results in MUCH better topology. Something to figure out against 2.93
                bpy.ops.mesh.decimate(ratio=decimation,
                                      use_vertex_group=animation_weighting,
                                      vertex_group_factor=animation_weighting_factor,
                                      invert_vertex_group=True,
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
