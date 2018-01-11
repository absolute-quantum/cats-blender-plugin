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

import re
import webbrowser

import bpy
import tools.common
from mmd_tools_local import utils
from mmd_tools_local.core.material import FnMaterial
from collections import OrderedDict

mmd_tools_installed = False
try:
    import mmd_tools
    mmd_tools_installed = True
except:
    pass


class ImportModel(bpy.types.Operator):
    bl_idname = 'armature_manual.import_model'
    bl_label = 'Import Model'
    bl_description = 'Import a MMD model (.pmx, .pmd)\n' \
                     '\n' \
                     'Only available when mmd_tools is installed.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if context.scene.import_mode == 'MMD':
            if not mmd_tools_installed:
                bpy.context.window_manager.popup_menu(popup_install_mmd, title='mmd_tools is not installed!', icon='ERROR')
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
    row.label("Please enable it in your User Preferences.")


def popup_install_mmd(self, context):
    layout = self.layout
    col = layout.column(align=True)

    row = col.row(align=True)
    row.label("The plugin 'mmd_tools' is required for this function.")
    col.separator()
    row = col.row(align=True)
    row.label("Please click here to go to this link and follow")
    row = col.row(align=True)
    row.label("the installation guide there in order to install it:")
    col.separator()
    row = col.row(align=True)
    row.operator('armature_manual.mmd_tools', icon='LOAD_FACTORY')


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


class MmdToolsButton(bpy.types.Operator):
    bl_idname = 'armature_manual.mmd_tools'
    bl_label = 'Install mmd_tools'

    def execute(self, context):
        webbrowser.open('https://github.com/powroupi/blender_mmd_tools')

        self.report({'INFO'}, 'mmd_tools link opened')
        return {'FINISHED'}


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
                     'Automatically sets the optimal export settings.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        try:
            bpy.ops.export_scene.fbx('INVOKE_DEFAULT', object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'}, use_mesh_modifiers=False, add_leaf_bones=False, bake_anim=False)
        except (TypeError, ValueError):
            bpy.ops.export_scene.fbx('INVOKE_DEFAULT')

        return {'FINISHED'}


class StartPoseMode(bpy.types.Operator):
    bl_idname = 'armature_manual.start_pose_mode'
    bl_label = 'Start Pose Mode'
    bl_description = 'Starts the pose mode.\n' \
                     'This lets you test how bones will move.\n'
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
    bl_description = 'Stops the pose mode and resets the pose to normal.\n'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if tools.common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        armature = tools.common.get_armature()
        for pb in armature.data.bones:
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

        return {'FINISHED'}


class JoinMeshes(bpy.types.Operator):
    bl_idname = 'armature_manual.join_meshes'
    bl_label = 'Join Meshes'
    bl_description = 'Joins the model meshes into a single one and applies all unapplied decimation modifiers.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        i = 0
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                if ob.parent is not None and ob.parent.type == 'ARMATURE':
                    i += 1
        return i > 0

    def execute(self, context):
        mesh = tools.common.join_meshes(context)
        if mesh is not None:
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

        tools.common.separate_by_materials(context, obj)
        return {'FINISHED'}


class MixWeights(bpy.types.Operator):
    bl_idname = 'armature_manual.mix_weights'
    bl_label = 'Mix Weights'
    bl_description = 'Deletes the selected bones and adds their weight to their respective parents.\n' \
                     '\n' \
                     'Only available in Edit or Pose Mode with bones selected.\n'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    _armature = None
    _bone_names_to_work_on = None
    _objects_to_work_on = None

    @classmethod
    def poll(cls, context):
        if bpy.context.active_object is None:
            return False

        if bpy.context.selected_editable_bones is None:
            return False

        # if bpy.context.active_object.mode == 'OBJECT' and len(bpy.context.selected_bones) > 0:
        #     return True

        if bpy.context.active_object.mode == 'EDIT' and len(bpy.context.selected_editable_bones) > 0:
            return True

        if bpy.context.active_object.mode == 'POSE' and len(bpy.context.selected_pose_bones) > 0:
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
        if bpy.context.selected_editable_bones is not None and len(bpy.context.selected_editable_bones) > 0:
            bones_to_work_on = bpy.context.selected_editable_bones
        elif bpy.context.selected_pose_bones is not None and len(bpy.context.selected_pose_bones) > 0:
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
        if bpy.context.selected_editable_bones is not None and len(bpy.context.selected_editable_bones) > 0:
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


class SeparateByMaterialsCustom(bpy.types.Operator):
    bl_idname = 'armature_manual.separate_by_materials'
    bl_label = 'Separate By Materials'
    bl_description = 'Separate by materials'
    bl_options = {'PRESET'}

    clean_shape_keys = bpy.props.BoolProperty(
        name='Clean Shape Keys',
        description='Remove unused shape keys of separated objects',
        default=True,
        options={'SKIP_SAVE'},
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    def execute(self, context):
        obj = context.active_object

        clear_temp_materials(self)
        clear_uv_morph_view()

        mat_names = []

        for mesh in tools.common.get_meshes_objects():
            for mat in mesh.data.materials:
                # control the case of a material shared among different meshes
                if mat not in mat_names:
                    mat_names.append(mat)

        separateByMaterials(obj)

        # The material morphs store the name of the mesh, not of the object.
        # So they will not be out of sync
        for mesh in tools.common.get_meshes_objects():
            if len(mesh.data.materials) == 1:
                mat = mesh.data.materials[0]
                idx = mat_names.index(mat.name)
                MoveObject.set_index(mesh, idx)

        # if root and len(root.mmd_root.material_morphs) > 0:
        #     for morph in root.mmd_root.material_morphs:
        #         mo = FnMorph(morph, mmd_model.Model(root))
        #         mo.update_mat_related_mesh()
        utils.clearUnusedMeshes()
        return {'FINISHED'}


class JoinMeshesTest(bpy.types.Operator):
    bl_idname = 'armature_manual.join_meshes_test'
    bl_label = 'Join Meshes Test'
    bl_description = 'Joins all meshes.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        i = 0
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                if ob.parent is not None and ob.parent.type == 'ARMATURE':
                    i += 1
        return i > 0

    def execute(self, context):

        clear_temp_materials(self)
        clear_uv_morph_view()

        # Find all the meshes
        meshes_list = sorted(tools.common.get_meshes_objects(), key=lambda x: x.name)
        active_mesh = meshes_list[0]

        tools.common.unselect_all()
        act_layer = context.scene.active_layer
        for mesh in meshes_list:
            mesh.layers[act_layer] = True
            mesh.hide_select = False
            mesh.hide = False
            mesh.select = True
        bpy.context.scene.objects.active = active_mesh

        # Store the current order of the materials
        for m in meshes_list[1:]:
            for mat in m.data.materials:
                if mat and mat.name not in active_mesh.data.materials:
                    active_mesh.data.materials.append(mat)

        # Store the current order of shape keys (vertex morphs)
        __get_key_blocks = lambda x: x.data.shape_keys.key_blocks if x.data.shape_keys else []
        shape_key_names = OrderedDict((kb.name, None) for m in meshes_list for kb in __get_key_blocks(m))
        # shape_key_names = sorted(shape_key_names.keys(), key=lambda x: root.mmd_root.vertex_morphs.find(x))
        # FnMorph.storeShapeKeyOrder(active_mesh, shape_key_names)
        # active_mesh.active_shape_key_index = 0
        #
        # # Join selected meshes
        # bpy.ops.object.join()
        #
        # if len(root.mmd_root.material_morphs) > 0:
        #     for morph in root.mmd_root.material_morphs:
        #         mo = FnMorph(morph, rig)
        #         mo.update_mat_related_mesh(active_mesh)

        utils.clearUnusedMeshes()
        return {'FINISHED'}


def clear_temp_materials(self):
    for mesh in tools.common.get_meshes():
        mats_to_delete = []
        for mat in mesh.data.materials:
            if mat and "_temp" in mat.name:
                mats_to_delete.append(mat)
        for temp_mat in reversed(mats_to_delete):
            base_mat_name = temp_mat.name.split('_temp')[0]
            if FnMaterial.swap_materials(mesh, temp_mat.name, base_mat_name) is None:
                self.report({'WARNING'}, 'Base material for %s was not found' % temp_mat.name)
            else:
                temp_idx = mesh.data.materials.find(temp_mat.name)
                mat = mesh.data.materials.pop(index=temp_idx)
                if mat.users < 1:
                    bpy.data.materials.remove(mat)


def clear_uv_morph_view():
    for m in tools.common.get_meshes():
        mesh = m.data
        uv_textures = mesh.uv_textures
        for t in uv_textures:
            if t.name.startswith('__uv.'):
                uv_textures.remove(t)
        if len(uv_textures) > 0:
            uv_textures[0].active_render = True
            uv_textures.active_index = 0

        animation_data = mesh.animation_data
        if animation_data:
            nla_tracks = animation_data.nla_tracks
            for t in nla_tracks:
                if t.name.startswith('__uv.'):
                    nla_tracks.remove(t)
            if animation_data.action and animation_data.action.name.startswith('__uv.'):
                animation_data.action = None
            if animation_data.action is None and len(nla_tracks) == 0:
                mesh.animation_data_clear()

    for act in bpy.data.actions:
        if act.name.startswith('__uv.') and act.users < 1:
            bpy.data.actions.remove(act)


def separateByMaterials(meshObj):
    prev_parent = meshObj.parent
    dummy_parent = bpy.data.objects.new(name='tmp', object_data=None)
    meshObj.parent = dummy_parent
    meshObj.active_shape_key_index = 0

    tools.common.switch('EDIT')

    try:
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='MATERIAL')
    finally:
        bpy.ops.object.mode_set(mode='OBJECT')

    for i in dummy_parent.children:
        mesh = i.data
        if len(mesh.polygons) > 0:
            mat_index = mesh.polygons[0].material_index
            mat = mesh.materials[mat_index]
            for k in mesh.materials:
                mesh.materials.pop(index=0, update_data=True)
            mesh.materials.append(mat)
            for po in mesh.polygons:
                po.material_index = 0
            i.name = mat.name
            i.parent = prev_parent


class MoveObject(bpy.types.Operator, utils.ItemMoveOp):
    bl_idname = 'mmd_tools.object_move'
    bl_label = 'Move Object'
    bl_description = 'Move active object up/down in the list'
    bl_options = {'INTERNAL'}

    __PREFIX_REGEXP = re.compile(r'(?P<prefix>[0-9A-Z]{3}_)(?P<name>.*)')

    @classmethod
    def set_index(cls, obj, index):
        m = cls.__PREFIX_REGEXP.match(obj.name)
        name = m.group('name') if m else obj.name
        obj.name = '%s_%s' % (utils.int2base(index, 36, 3), name)

    @classmethod
    def normalize_indices(cls, objects):
        for i, x in enumerate(objects):
            cls.set_index(x, i)

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        obj = context.active_object
        objects = self.__get_objects(obj)
        if obj not in objects:
            self.report({'ERROR'}, 'Can not move object "%s"' % obj.name)
            return {'CANCELLED'}

        objects.sort(key=lambda x: x.name)
        self.move(objects, objects.index(obj), self.type)
        self.normalize_indices(objects)
        return {'FINISHED'}

    def __get_objects(self, obj):
        class __MovableList(list):
            def move(self, index_old, index_new):
                item = self[index_old]
                self.remove(item)
                self.insert(index_new, item)

        objects = []
        if obj.mmd_type == 'NONE' and obj.type == 'MESH':
            objects = tools.common.get_meshes_objects()

        return __MovableList(objects)
