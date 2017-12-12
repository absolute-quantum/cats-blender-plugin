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
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not mmd_tools_installed:
            self.report({'ERROR'}, 'mmd_tools not installed!')
            return {'FINISHED'}

        try:
            bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT')
        except:
            self.report({'ERROR'}, 'mmd_tools not enabled! Please enable mmd_tools.')

        return {'FINISHED'}


# # Our finalizing operator, shall run after transform
# class Finalize(bpy.types.Operator):
#     bl_idname = "test.finalize"
#     bl_label = "Finalize"
#
#     def execute(self, context):
#         bpy.ops.mmd_tools.set_shadeless_glsl_shading()
#
#         for obj in bpy.data.objects:
#             if obj.parent is not None:
#                 continue
#             try:
#                 obj.mmd_root.use_toon_texture = False
#                 obj.mmd_root.use_sphere_texture = False
#                 break
#             except:
#                 pass
#         print("DONE!")
#         return {'FINISHED'}
#
#
# # Our finalizing operator, shall run after transform
# class Import(bpy.types.Operator):
#     bl_idname = "test.import"
#     bl_label = "Import"
#
#     def execute(self, context):
#         bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT')
#         print("IMPORTED!")
#         return {'FINISHED'}
#
#
# # Macro operator to concatenate transform and our finalization
# class Test(bpy.types.Macro):
#     bl_idname = "TEST_OT_Test"
#     bl_label = "Test"


class JoinMeshes(bpy.types.Operator):
    bl_idname = 'armature_manual.join_meshes'
    bl_label = 'Join Meshes'
    bl_description = 'Join the Model meshes into a single one.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        i = 0
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                i += 1
        return i > 0

    def execute(self, context):
        mesh = tools.common.join_meshes()
        if mesh is not None:
            tools.common.repair_viseme_order(mesh.name)

        self.report({'INFO'}, 'Meshes joined.')
        return {'FINISHED'}


class SeparateByMaterials(bpy.types.Operator):
    bl_idname = 'armature_manual.separate_by_materials'
    bl_label = 'Separate by Materials'
    bl_description = 'Separates selected mesh by materials.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH'

    @staticmethod
    def __can_remove(key_block):
        if key_block.relative_key == key_block:
            return False  # Basis
        for v0, v1 in zip(key_block.relative_key.data, key_block.data):
            if v0.co != v1.co:
                return False
        return True

    def __shape_key_clean(self, context, obj, key_blocks):
        for kb in key_blocks:
            if self.__can_remove(kb):
                obj.shape_key_remove(kb)

    def __shape_key_clean_old(self, context, obj, key_blocks):
        context.scene.objects.active = obj
        for i in reversed(range(len(key_blocks))):
            kb = key_blocks[i]
            if self.__can_remove(kb):
                obj.active_shape_key_index = i
                bpy.ops.object.shape_key_remove()

    __do_shape_key_clean = __shape_key_clean_old if bpy.app.version < (2, 75, 0) else __shape_key_clean

    def execute(self, context):
        obj = context.active_object
        utils.separateByMaterials(obj)

        for ob in context.selected_objects:
            if ob.type != 'MESH' or ob.data.shape_keys is None:
                continue
            if not ob.data.shape_keys.use_relative:
                continue  # not be considered yet
            key_blocks = ob.data.shape_keys.key_blocks
            counts = len(key_blocks)
            self.__do_shape_key_clean(context, ob, key_blocks)
            counts -= len(key_blocks)

        utils.clearUnusedMeshes()
        return {'FINISHED'}


class MixWeights(bpy.types.Operator):
    bl_idname = 'armature_manual.mix_weights'
    bl_label = 'Mix Weights'
    bl_description = 'Deletes the selected bones and adds their weight to their respective parents.\n' \
                     'Only available in Edit or Pose Mode with bones selected!\n'
    bl_options = {'REGISTER', 'UNDO'}

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
    bl_options = {'REGISTER', 'UNDO'}

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
