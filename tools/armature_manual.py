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
# Repo: https://github.com/Grim-es/shotariya
# Code author: Neitri
# Repo: https://github.com/netri/blender_neitri_tools
# Edits by: Hotox, Neitri
import copy

import bpy
import webbrowser
import tools.common
import tools.eyetracking
import tools.armature_bones as Bones

mmd_tools_installed = False
try:
    import mmd_tools_local
    mmd_tools_installed = True
except:
    pass


class ImportModel(bpy.types.Operator):
    bl_idname = 'armature_manual.import_model'
    bl_label = 'Import Model'
    bl_description = 'Import a model of the selected type'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()
        if context.scene.import_mode == 'MMD':
            if not mmd_tools_installed:
                bpy.context.window_manager.popup_menu(popup_enable_mmd, title='mmd_tools is not installed!', icon='ERROR')
                return {'FINISHED'}

            try:
                bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT', scale=0.08, types={'MESH', 'ARMATURE', 'MORPHS'})
            except AttributeError:
                bpy.context.window_manager.popup_menu(popup_enable_mmd, title='mmd_tools is not enabled!', icon='ERROR')
            except (TypeError, ValueError):
                bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT')

        elif context.scene.import_mode == 'XPS':
            try:
                bpy.ops.xps_tools.import_model('INVOKE_DEFAULT')
            except AttributeError:
                bpy.context.window_manager.popup_menu(popup_install_xps, title='XPS Tools is not installed or enabled!', icon='ERROR')
            except (TypeError, ValueError):
                bpy.ops.xps_tools.import_model('INVOKE_DEFAULT')

        elif context.scene.import_mode == 'FBX':
            try:
                bpy.ops.import_scene.fbx('INVOKE_DEFAULT', automatic_bone_orientation=True)
            except (TypeError, ValueError):
                bpy.ops.import_scene.fbx('INVOKE_DEFAULT')

        return {'FINISHED'}


def popup_enable_mmd(self, context):
    layout = self.layout
    col = layout.column(align=True)

    row = col.row(align=True)
    row.label("The plugin 'mmd_tools' is required for this function.")
    col.separator()
    row = col.row(align=True)
    row.label("Please restart Blender.")


def popup_enable_xps(self, context):
    layout = self.layout
    col = layout.column(align=True)

    row = col.row(align=True)
    row.label("The plugin 'XPS Tools' is required for this function.")
    col.separator()
    row = col.row(align=True)
    row.label("Please enable it in your User Preferences.")


def popup_install_xps(self, context):
    layout = self.layout
    col = layout.column(align=True)

    row = col.row(align=True)
    row.label("The plugin 'XPS Tools' is required for this function.")
    col.separator()
    row = col.row(align=True)
    row.label("If it is not enabled please enable it in your User Preferences.")
    row = col.row(align=True)
    row.label("If it is not installed please click here to go to this link to download and install it")
    col.separator()
    row = col.row(align=True)
    row.operator('armature_manual.xps_tools', icon='LOAD_FACTORY')


class XpsToolsButton(bpy.types.Operator):
    bl_idname = 'armature_manual.xps_tools'
    bl_label = 'Install XPS Tools'

    def execute(self, context):
        webbrowser.open('https://github.com/johnzero7/XNALaraMesh')

        self.report({'INFO'}, 'XPS Tools link opened')
        return {'FINISHED'}


class ExportModel(bpy.types.Operator):
    bl_idname = 'armature_manual.export_model'
    bl_label = 'Export Model'
    bl_description = 'Export this model as .fbx for Unity.\n' \
                     '\n' \
                     'Automatically sets the optimal export settings'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        protected_export = False
        for mesh in tools.common.get_meshes_objects():
            if protected_export:
                break
            if mesh.data.shape_keys:
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if shapekey.name == 'Basis Original':
                        protected_export = True
                        break

        try:
            if protected_export:
                bpy.ops.export_scene.fbx('INVOKE_DEFAULT',
                                         object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
                                         use_mesh_modifiers=False,
                                         add_leaf_bones=False,
                                         bake_anim=False,
                                         mesh_smooth_type='FACE')
            else:
                bpy.ops.export_scene.fbx('INVOKE_DEFAULT',
                                         object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
                                         use_mesh_modifiers=False,
                                         add_leaf_bones=False,
                                         bake_anim=False)
        except (TypeError, ValueError):
            bpy.ops.export_scene.fbx('INVOKE_DEFAULT')

        return {'FINISHED'}


class StartPoseMode(bpy.types.Operator):
    bl_idname = 'armature_manual.start_pose_mode'
    bl_label = 'Start Pose Mode'
    bl_description = 'Starts the pose mode.\n' \
                     'This lets you test how your model will move'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if tools.common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        current = ""
        if bpy.context.active_object is not None and bpy.context.active_object.mode == 'EDIT' and bpy.context.active_object.type == 'ARMATURE' and len(bpy.context.selected_editable_bones) > 0:
            current = bpy.context.selected_editable_bones[0].name

        armature = tools.common.set_default_stage()
        tools.common.switch('POSE')
        armature.data.pose_position = 'POSE'

        for mesh in tools.common.get_meshes_objects():
            if mesh.data.shape_keys is not None:
                for shape_key in mesh.data.shape_keys.key_blocks:
                    shape_key.value = 0

        for pb in armature.data.bones:
            pb.select = True
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()

        bone = armature.data.bones.get(current)
        if bone is not None:
            for pb in armature.data.bones:
                if bone.name != pb.name:
                    pb.select = False
        else:
            for index, pb in enumerate(armature.data.bones):
                if index != 0:
                    pb.select = False

        bpy.context.space_data.transform_manipulators = {'ROTATE'}

        return {'FINISHED'}


class StopPoseMode(bpy.types.Operator):
    bl_idname = 'armature_manual.stop_pose_mode'
    bl_label = 'Stop Pose Mode'
    bl_description = 'Stops the pose mode and resets the pose to normal'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if tools.common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        armature = tools.common.get_armature()
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

        for mesh in tools.common.get_meshes_objects():
            if mesh.data.shape_keys is not None:
                for shape_key in mesh.data.shape_keys.key_blocks:
                    shape_key.value = 0

        bpy.context.space_data.transform_manipulators = {'TRANSLATE'}
        tools.eyetracking.eye_left = None

        return {'FINISHED'}


class PoseToShape(bpy.types.Operator):
    bl_idname = 'armature_manual.pose_to_shape'
    bl_label = 'Pose to Shape Key'
    bl_description = 'INFO: Join your meshes first!' \
                     '\n' \
                     '\nThis saves your current pose as a new shape key.' \
                     '\nThe new shape key will be at the bottom of your shape key list of the mesh'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not bpy.context.active_object or bpy.context.active_object.mode != 'POSE':
            return False

        meshes = tools.common.get_meshes_objects()
        return meshes and len(meshes) == 1

    def execute(self, context):
        mesh = tools.common.get_meshes_objects()[0]
        tools.common.unselect_all()
        tools.common.select(mesh)

        # Apply armature mod
        mod = mesh.modifiers.new("Pose", 'ARMATURE')
        mod.object = tools.common.get_armature()
        bpy.ops.object.modifier_apply(apply_as='SHAPE', modifier=mod.name)

        armature = tools.common.set_default_stage()
        tools.common.switch('POSE')
        armature.data.pose_position = 'POSE'

        self.report({'INFO'}, 'Pose successfully saved as shape key.')
        return {'FINISHED'}


class JoinMeshes(bpy.types.Operator):
    bl_idname = 'armature_manual.join_meshes'
    bl_label = 'Join Meshes'
    bl_description = 'Joins the model meshes into a single one and applies all unapplied decimation modifiers'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        meshes = tools.common.get_meshes_objects()
        return meshes and len(meshes) > 0

    def execute(self, context):
        mesh = tools.common.join_meshes()
        if mesh:
            tools.common.repair_viseme_order(mesh.name)

        self.report({'INFO'}, 'Meshes joined.')
        return {'FINISHED'}


class SeparateByMaterials(bpy.types.Operator):
    bl_idname = 'armature_manual.separate_by_materials'
    bl_label = 'Separate by Materials'
    bl_description = 'Separates selected mesh by materials.\n' \
                     '\n' \
                     'Warning: Never decimate something where you might need the shape keys later (face, mouth, eyes..)'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = tools.common.get_meshes_objects()
        return meshes and len(meshes) >= 1

    def execute(self, context):
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            tools.common.unselect_all()
            meshes = tools.common.get_meshes_objects()
            if len(meshes) == 0:
                self.report({'ERROR'}, 'No meshes found!')
                return {'FINISHED'}
            if len(meshes) > 1:
                self.report({'ERROR'}, 'Multiple meshes found!'
                                       '\nPlease select the mesh you want to separate!')
                return {'FINISHED'}
            obj = meshes[0]

        tools.common.separate_by_materials(context, obj)

        self.report({'INFO'}, 'Successfully separated by materials.')
        return {'FINISHED'}


class SeparateByLooseParts(bpy.types.Operator):
    bl_idname = 'armature_manual.separate_by_loose_parts'
    bl_label = 'Separate by Loose Parts'
    bl_description = 'Can cause a lot of lag depending on the model!\n' \
                     '\n' \
                     'Separates selected mesh by loose parts sorted by materials.\n' \
                     'This acts like separating by materials but creates more meshes for more precision.\n'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = tools.common.get_meshes_objects()
        return meshes and len(meshes) >= 1

    def execute(self, context):
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            tools.common.unselect_all()
            meshes = tools.common.get_meshes_objects()
            if len(meshes) == 0:
                self.report({'ERROR'}, 'No meshes found!')
                return {'FINISHED'}
            if len(meshes) > 1:
                self.report({'ERROR'}, 'Multiple meshes found!'
                                       '\nPlease select the mesh you want to separate!')
                return {'FINISHED'}
            obj = meshes[0]

        tools.common.separate_by_loose_parts(context, obj)

        self.report({'INFO'}, 'Successfully separated by loose parts.')
        return {'FINISHED'}


class MergeWeights(bpy.types.Operator):
    bl_idname = 'armature_manual.merge_weights'
    bl_label = 'Merge Weights'
    bl_description = 'Deletes the selected bones and adds their weight to their respective parents.\n' \
                     '\n' \
                     'Only available in Edit or Pose Mode with bones selected'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    _armature = None
    _bone_names_to_work_on = None
    _objects_to_work_on = None

    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None:
            return False

        # if bpy.context.selected_editable_bones is None:
        #     return False

        # if bpy.context.active_object.mode == 'OBJECT' and len(bpy.context.selected_bones) > 0:
        #     return True

        if bpy.context.active_object.mode == 'EDIT' and bpy.context.selected_editable_bones and len(bpy.context.selected_editable_bones) > 0:
            return True

        if bpy.context.active_object.mode == 'POSE' and bpy.context.selected_pose_bones and len(bpy.context.selected_pose_bones) > 0:
            return True

        return False

    def execute(self, context):

        error = self.mustSelectBones()
        if error:
            return error

        armature_edit_mode = ArmatureEditMode(self._armature)

        # create lookup table
        bone_name_to_edit_bone = dict()
        for edit_bone in self._armature.data.edit_bones:
            bone_name_to_edit_bone[edit_bone.name] = edit_bone

        for bone_name_to_remove in self._bone_names_to_work_on:
            if bone_name_to_edit_bone[bone_name_to_remove].parent is None:
                continue
            bone_name_to_add_weights_to = bone_name_to_edit_bone[bone_name_to_remove].parent.name
            self._armature.data.edit_bones.remove(bone_name_to_edit_bone[bone_name_to_remove])  # delete bone

            for object in self._objects_to_work_on:

                vertex_group_to_remove = object.vertex_groups.get(bone_name_to_remove)
                vertex_group_to_add_weights_to = object.vertex_groups.get(bone_name_to_add_weights_to)

                if vertex_group_to_remove is not None:

                    if vertex_group_to_add_weights_to is None:
                        vertex_group_to_add_weights_to = object.vertex_groups.new(bone_name_to_add_weights_to)

                    for vertex in object.data.vertices:  # transfer weight for each vertex
                        weight_to_transfer = 0
                        for group in vertex.groups:
                            if group.group == vertex_group_to_remove.index:
                                weight_to_transfer = group.weight
                                break
                        if weight_to_transfer > 0:
                            vertex_group_to_add_weights_to.add([vertex.index], weight_to_transfer, 'ADD')

                    object.vertex_groups.remove(vertex_group_to_remove)  # delete vertex group

        armature_edit_mode.restore()

        self.report({'INFO'}, 'Deleted ' + str(len(self._bone_names_to_work_on)) + ' bones and added their weights to their parents')

        return {'FINISHED'}

    def optionallySelectBones(self):

        armature = bpy.context.object
        if armature is None:
            self.report({'ERROR'}, 'Select something')
            return {'CANCELLED'}

        # find armature, try to select parent
        if armature is not None and armature.type != 'ARMATURE' and armature.parent is not None:
            armature = armature.parent
            if armature is not None and armature.type != 'ARMATURE' and armature.parent is not None:
                armature = armature.parent

        # find armature, try to select first and only child
        if armature is not None and armature.type != 'ARMATURE' and len(armature.children) == 1:
            armature = armature.children[0]
            if armature is not None and armature.type != 'ARMATURE' and len(armature.children) == 1:
                armature = armature.children[0]

        if armature is None or armature.type != 'ARMATURE':
            self.report({'ERROR'}, 'Select armature, it\'s child or it\'s parent')
            return {'CANCELLED'}

        # find which bones to work on
        if bpy.context.selected_editable_bones and len(bpy.context.selected_editable_bones) > 0:
            bones_to_work_on = bpy.context.selected_editable_bones
        elif bpy.context.selected_pose_bones and len(bpy.context.selected_pose_bones) > 0:
            bones_to_work_on = bpy.context.selected_pose_bones
        else:
            bones_to_work_on = armature.data.bones
        bone_names_to_work_on = set([bone.name for bone in bones_to_work_on])  # grab names only

        self._armature = armature
        self._bone_names_to_work_on = bone_names_to_work_on
        self._objects_to_work_on = armature.children

    def mustSelectBones(self):

        armature = bpy.context.object

        if armature is None or armature.type != 'ARMATURE':
            self.report({'ERROR'}, 'Select bones in armature edit or pose mode')
            return {'CANCELLED'}

        # find which bones to work on
        if bpy.context.selected_editable_bones and len(bpy.context.selected_editable_bones) > 0:
            bones_to_work_on = bpy.context.selected_editable_bones
        else:
            bones_to_work_on = bpy.context.selected_pose_bones
        bone_names_to_work_on = set([bone.name for bone in bones_to_work_on])  # grab names only

        if len(bone_names_to_work_on) == 0:
            self.report({'ERROR'}, 'Select at least one bone')
            return {'CANCELLED'}

        self._armature = armature
        self._bone_names_to_work_on = bone_names_to_work_on
        self._objects_to_work_on = armature.children


class ArmatureEditMode:
    def __init__(self, armature):
        # save user state, select armature, go to armature edit mode
        self._armature = armature
        self._active_object = bpy.context.scene.objects.active
        bpy.context.scene.objects.active = self._armature
        self._armature_hide = self._armature.hide
        self._armature.hide = False
        self._armature_mode = self._armature.mode
        tools.common.switch('EDIT')

    def restore(self):
        # restore user state
        tools.common.switch(self._armature_mode)
        self._armature.hide = self._armature_hide
        bpy.context.scene.objects.active = self._active_object


class RemoveZeroWeight(bpy.types.Operator):
    bl_idname = 'armature_manual.remove_zero_weight'
    bl_label = 'Remove Zero Weight Bones'
    bl_description = "Cleans up the bones hierarchy, deleting all bones that don't directly affect any vertices\n" \
                     "Don't use this if you plan to use 'Fix Model'"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if tools.common.get_armature():
            return True
        return False

    def execute(self, context):
        tools.common.set_default_stage()
        count = tools.common.delete_zero_weight()
        tools.common.set_default_stage()

        self.report({'INFO'}, 'Deleted ' + str(count) + ' zero weight bones.')
        return {'FINISHED'}


class RemoveConstraints(bpy.types.Operator):
    bl_idname = 'armature_manual.remove_constraints'
    bl_label = 'Remove Bone Constraints'
    bl_description = "Removes constrains between bones causing specific bone movement as these are not used by VRChat"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if tools.common.get_armature():
            return True
        return False

    def execute(self, context):
        tools.common.set_default_stage()
        tools.common.delete_bone_constraints()
        tools.common.set_default_stage()

        self.report({'INFO'}, 'Removed all bone constraints.')
        return {'FINISHED'}


class RecalculateNormals(bpy.types.Operator):
    bl_idname = 'armature_manual.recalculate_normals'
    bl_label = 'Recalculate Normals'
    bl_description = "Don't use this on good looking meshes as this can screw them up.\n" \
                     "Makes normals point inside of the selected mesh.\n" \
                     "Use this if there are random inverted or darker faces on the mesh"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = tools.common.get_meshes_objects()
        return meshes and len(meshes) == 1

    def execute(self, context):
        obj = context.active_object
        if not obj or (obj and obj.type != 'MESH'):
            tools.common.unselect_all()
            meshes = tools.common.get_meshes_objects()
            if len(meshes) == 0:
                return {'FINISHED'}
            obj = meshes[0]
        mesh = obj

        tools.common.select(mesh)
        tools.common.switch('EDIT')

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)

        tools.common.set_default_stage()

        self.report({'INFO'}, 'Recalculated all normals.')
        return {'FINISHED'}


class FlipNormals(bpy.types.Operator):
    bl_idname = 'armature_manual.flip_normals'
    bl_label = 'Flip Normals'
    bl_description = "Flips the direction of the faces' normals of the selected mesh.\n" \
                     "Use this if all normals are inverted"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = tools.common.get_meshes_objects()
        return meshes and len(meshes) == 1

    def execute(self, context):
        obj = context.active_object
        if not obj or (obj and obj.type != 'MESH'):
            tools.common.unselect_all()
            meshes = tools.common.get_meshes_objects()
            if len(meshes) == 0:
                return {'FINISHED'}
            obj = meshes[0]
        mesh = obj

        tools.common.select(mesh)
        tools.common.switch('EDIT')

        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.flip_normals()

        tools.common.set_default_stage()

        self.report({'INFO'}, 'Recalculated all normals.')
        return {'FINISHED'}


class MergeArmature(bpy.types.Operator):
    bl_idname = 'armature_manual.merge_armatures'
    bl_label = 'Merge Armatures'
    bl_description = "Merges the selected armature into the current armature. This merges all bones and meshes" \
                     "\nResults are best when both armatures are fixed by Cats." \
                     "\nOtherwise make sure that the naming scheme is similar." \
                     "\nDo not delete bones as they are needed"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(tools.common.get_armature_objects()) > 1

    def execute(self, context):
        # Set default stage
        tools.common.set_default_stage()
        tools.common.unselect_all()

        # Get both armatures
        current_armature_name = bpy.context.scene.merge_armature_into
        merge_armature_name = bpy.context.scene.merge_armature
        current_armature = bpy.data.objects[current_armature_name]
        merge_armature = bpy.data.objects[merge_armature_name]

        if not merge_armature:
            self.report({'ERROR'}, 'The armature "' + merge_armature_name + '" could not be found.')
            return {'FINISHED'}
        if not current_armature:
            self.report({'ERROR'}, 'The armature "' + current_armature_name + '" could not be found.')
            return {'FINISHED'}

        if merge_armature.parent:
            self.report({'ERROR'}, 'Please use the "Fix Model" feature on the selected armatures first!'
                                   '\nAfter that please only move the mesh (not the armature!) to the desired position.')
            return {'FINISHED'}
        if current_armature.parent:
            self.report({'ERROR'}, 'Please use the "Fix Model" feature on the selected armatures first!'
                                   '\nAfter that please only move the mesh (not the armature!) to the desired position.')
            return {'FINISHED'}

        if len(tools.common.get_meshes_objects(armature_name=merge_armature_name)) == 0:
            self.report({'ERROR'}, 'The armature "' + merge_armature_name + '" does not have any meshes.')
            return {'FINISHED'}
        if len(tools.common.get_meshes_objects(armature_name=current_armature_name)) == 0:
            self.report({'ERROR'}, 'The armature "' + merge_armature_name + '" does not have any meshes.')
            return {'FINISHED'}

        # Join meshes in both armatures
        mesh_base = tools.common.join_meshes(armature_name=current_armature_name)
        mesh = tools.common.join_meshes(armature_name=merge_armature_name)

        # Check for transform on base armature, reset if not default
        for i in [0, 1, 2]:
            if current_armature.location[i] != 0 \
                    or current_armature.rotation_euler[i] != 0 \
                    or current_armature.scale[i] != 1 \
                    or mesh_base.location[i] != 0 \
                    or mesh_base.rotation_euler[i] != 0 \
                    or mesh_base.scale[i] != 1:

                for i2 in [0, 1, 2]:
                    current_armature.location[i2] = 0
                    current_armature.rotation_euler[i2] = 0
                    current_armature.scale[i2] = 1
                    mesh_base.location[i2] = 0
                    mesh_base.rotation_euler[i2] = 0
                    mesh_base.scale[i2] = 1

                # Todo Maybe hide both armatures?
                self.report({'ERROR'},
                            'The position of your base armature and mesh has to be at 0! Only move the merge armature!'
                            "\nMaybe you switched the base and merge armatures?"
                            "\nThe base armatures position got reset for you. If you don't want that, undo this operation.")
                return {'FINISHED'}

        # Check for transform on merge armature, reset if not default
        old_loc = [0, 0, 0]
        old_scale = [1, 1, 1]
        for i in [0, 1, 2]:
            if merge_armature.location[i] != 0 or merge_armature.rotation_euler[i] != 0 or merge_armature.scale[i] != 1:

                old_loc = [merge_armature.location[0], merge_armature.location[1], merge_armature.location[2]]
                old_rot = [merge_armature.rotation_euler[0], merge_armature.rotation_euler[1],
                           merge_armature.rotation_euler[2]]
                old_scale = [merge_armature.scale[0], merge_armature.scale[1], merge_armature.scale[2]]

                for i2 in [0, 1, 2]:
                    merge_armature.location[i2] = 0
                    merge_armature.rotation_euler[i2] = 0
                    merge_armature.scale[i2] = 1

                for i2 in [0, 1, 2]:
                    if old_rot[i2] != 0 or mesh.rotation_euler[i2] != 0:
                        # Todo Maybe hide both armatures?
                        self.report({'ERROR'},
                                    'If you want to rotate the new part, only modify the mesh instead of the armature!'
                                    "\nThe merge armatures position got reset for you. If you don't want that, undo this operation.")
                        return {'FINISHED'}

                break

        # Apply transformation from mesh to armature
        for i in [0, 1, 2]:
            merge_armature.location[i] = (mesh.location[i] * old_scale[i]) + old_loc[i]
            merge_armature.rotation_euler[i] = mesh.rotation_euler[i]
            merge_armature.scale[i] = mesh.scale[i] * old_scale[i]

        tools.common.set_default_stage()
        # Apply all transformations on mesh
        tools.common.unselect_all()
        tools.common.select(mesh)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Apply all transformations on armature
        tools.common.unselect_all()
        tools.common.select(merge_armature)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Reset all transformations on mesh
        for i in [0, 1, 2]:
            mesh.location[i] = old_loc[i]
            mesh.rotation_euler[i] = 0
            mesh.scale[i] = old_scale[i]

        # Apply all transformations on mesh again
        tools.common.unselect_all()
        tools.common.select(mesh)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Go into edit mode
        tools.common.unselect_all()
        tools.common.select(merge_armature)
        tools.common.switch('EDIT')

        # Create new bone
        bones_to_merge = copy.deepcopy(Bones.dont_delete_these_main_bones)
        found = False
        root_name = ''
        for bone in bones_to_merge:
            if bone in merge_armature.data.edit_bones and 'Eye' not in bone:
                found = True
                print('AUTO MERGE!')
                break

        if not found:
            print('CUSTOM MERGE!')
            root_name = bpy.context.scene.attach_to_bone
            root = merge_armature.data.edit_bones.get(root_name)
            if root:
                root.name += '_Old'
            root = merge_armature.data.edit_bones.new(root_name)
            root.tail[2] += 0.1

            # Make new root top parent and reparent other top bones to root
            root.parent = None
            for bone2 in merge_armature.data.edit_bones:
                if not bone2.parent:
                    bone2.parent = root
            bones_to_merge.append(root.name)

        # Rename all the bones of the merge armature
        for bone in merge_armature.data.edit_bones:
            bone.name = bone.name + '.merge'

        # Go back into object mode
        tools.common.set_default_stage()
        tools.common.unselect_all()

        # Select armature in correct way
        tools.common.select(current_armature)
        merge_armature.select = True

        # Join the armatures
        if bpy.ops.object.join.poll():
            bpy.ops.object.join()

        # Set new armature
        bpy.context.scene.armature = current_armature_name
        armature = tools.common.get_armature(armature_name=current_armature_name)

        # Join the meshes
        mesh = tools.common.join_meshes(armature_name=current_armature_name)
        if mesh:
            tools.common.repair_viseme_order(mesh.name)

        # Go into edit mode
        tools.common.unselect_all()
        tools.common.select(armature)
        tools.common.switch('EDIT')

        # Reparent all bones
        for bone_name in bones_to_merge:
            old = bone_name + '.merge'
            new = bone_name
            if old in armature.data.edit_bones and new in armature.data.edit_bones:
                armature.data.edit_bones.get(old).parent = armature.data.edit_bones.get(new)

        # Remove all unused bones, constraints and vertex groups
        tools.common.set_default_stage()
        tools.common.delete_bone_constraints(armature_name=current_armature_name)
        tools.common.remove_unused_vertex_groups()
        tools.common.delete_zero_weight(armature_name=current_armature_name)
        tools.common.set_default_stage()

        # Merge bones into existing bones
        tools.common.select(mesh)
        for bone_name in bones_to_merge:
            key = bone_name + '.merge'
            value = bone_name

            # Eye pos is important, therefore they should override the old ones
            if 'Eye' in bone_name:
                key = bone_name
                value = bone_name + '.merge'

            vg = mesh.vertex_groups.get(key)
            vg2 = mesh.vertex_groups.get(value)
            if not vg or not vg2:
                continue

            mod = mesh.modifiers.new("VertexWeightMix", 'VERTEX_WEIGHT_MIX')
            mod.vertex_group_a = value  # to
            mod.vertex_group_b = key  # from
            mod.mix_mode = 'ADD'
            mod.mix_set = 'B'
            bpy.ops.object.modifier_apply(modifier=mod.name)
            mesh.vertex_groups.remove(vg)

        # Remove ".merge" from all non duplicate bones
        for bone in armature.pose.bones:
            new_name = bone.name.replace('.merge', '')
            if new_name not in armature.pose.bones:
                bone.name = new_name

        # Set new eye bone as default
        for eye_name in ['Eye_L', 'Eye_R']:
            if eye_name in armature.pose.bones and eye_name + '.merge' in armature.pose.bones:
                eye = armature.pose.bones.get(eye_name)
                eye_merged = armature.pose.bones.get(eye_name + '.merge')
                eye.name = eye.name + '_Old'
                eye_merged.name = eye_merged.name.replace('.merge', '')

        # Remove all unused bones, constraints and vertex groups
        tools.common.set_default_stage()
        tools.common.remove_unused_vertex_groups()
        tools.common.delete_zero_weight(armature_name=current_armature_name)
        tools.common.set_default_stage()

        # Fix armature name
        tools.common.fix_armature_names(armature_name=current_armature_name)

        self.report({'INFO'}, 'Armatures successfully joined.')
        return {'FINISHED'}