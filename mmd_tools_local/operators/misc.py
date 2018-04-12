# -*- coding: utf-8 -*-

import re

import bpy
from bpy.types import Operator

from mmd_tools_local import utils
from mmd_tools_local.bpyutils import ObjectOp
from mmd_tools_local.core import model as mmd_model
from mmd_tools_local.core.morph import FnMorph
from mmd_tools_local.core.material import FnMaterial


class MoveObject(Operator, utils.ItemMoveOp):
    bl_idname = 'mmd_tools.object_move'
    bl_label = 'Move Object'
    bl_description = 'Move active object up/down in the list'
    bl_options = {'INTERNAL'}

    __PREFIX_REGEXP = re.compile(r'(?P<prefix>[0-9A-Z]{3}_)(?P<name>.*)')

    @classmethod
    def set_index(cls, obj, index):
        m = cls.__PREFIX_REGEXP.match(obj.name)
        name = m.group('name') if m else obj.name
        obj.name = '%s_%s'%(utils.int2base(index, 36, 3), name)

    @classmethod
    def get_name(cls, obj, prefix=None):
        m = cls.__PREFIX_REGEXP.match(obj.name)
        name = m.group('name') if m else obj.name
        return name[len(prefix):] if prefix and name.startswith(prefix) else name

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
            self.report({ 'ERROR' }, 'Can not move object "%s"'%obj.name)
            return { 'CANCELLED' }

        objects.sort(key=lambda x: x.name)
        self.move(objects, objects.index(obj), self.type)
        self.normalize_indices(objects)
        return { 'FINISHED' }

    def __get_objects(self, obj):
        class __MovableList(list):
            def move(self, index_old, index_new):
                item = self[index_old]
                self.remove(item)
                self.insert(index_new, item)

        objects = []
        root = mmd_model.Model.findRoot(obj)
        if root:
            rig = mmd_model.Model(root)
            if obj.mmd_type == 'NONE' and obj.type == 'MESH':
                objects = rig.meshes()
            elif obj.mmd_type == 'RIGID_BODY':
                objects = rig.rigidBodies()
            elif obj.mmd_type == 'JOINT':
                objects = rig.joints()
        return __MovableList(objects)

class CleanShapeKeys(Operator):
    bl_idname = 'mmd_tools.clean_shape_keys'
    bl_label = 'Clean Shape Keys'
    bl_description = 'Remove unused shape keys of selected mesh objects'
    bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects) > 0

    @staticmethod
    def __can_remove(key_block):
        if key_block.relative_key == key_block:
            return False # Basis
        for v0, v1 in zip(key_block.relative_key.data, key_block.data):
            if v0.co != v1.co:
                return False
        return True

    def __shape_key_clean(self, obj, key_blocks):
        for kb in key_blocks:
            if self.__can_remove(kb):
                obj.shape_key_remove(kb)
        if len(key_blocks) == 1:
            obj.shape_key_remove(key_blocks[0])

    def execute(self, context):
        for ob in context.selected_objects:
            if ob.type != 'MESH' or ob.data.shape_keys is None:
                continue
            if not ob.data.shape_keys.use_relative:
                continue # not be considered yet
            self.__shape_key_clean(ObjectOp(ob), ob.data.shape_keys.key_blocks)
        return {'FINISHED'}

class SeparateByMaterials(Operator):
    bl_idname = 'mmd_tools.separate_by_materials'
    bl_label = 'Separate by materials'
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
        root = mmd_model.Model.findRoot(obj)
        if root:
            bpy.ops.mmd_tools.clear_temp_materials()
            bpy.ops.mmd_tools.clear_uv_morph_view()
        if root:
            # Store the current material names
            rig = mmd_model.Model(root)
            mat_names = [getattr(mat, 'name', None) for mat in rig.materials()]
        utils.separateByMaterials(obj)
        if self.clean_shape_keys:
            bpy.ops.mmd_tools.clean_shape_keys()
        if root:
            rig = mmd_model.Model(root)
            # The material morphs store the name of the mesh, not of the object.
            # So they will not be out of sync
            for mesh in rig.meshes():
                if len(mesh.data.materials) > 0:
                    mat = mesh.data.materials[0]
                    idx = mat_names.index(getattr(mat, 'name', None))
                    MoveObject.set_index(mesh, idx)

        if root and len(root.mmd_root.material_morphs) > 0:
            for morph in root.mmd_root.material_morphs:
                mo = FnMorph(morph, mmd_model.Model(root))
                mo.update_mat_related_mesh()
        utils.clearUnusedMeshes()
        return {'FINISHED'}

class JoinMeshes(Operator):
    bl_idname = 'mmd_tools.join_meshes'
    bl_label = 'Join Meshes'
    bl_description = 'Join the Model meshes into a single one'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        if root is None:
            self.report({ 'ERROR' }, 'Select a MMD model') 
            return { 'CANCELLED' }

        if root:
            bpy.ops.mmd_tools.clear_temp_materials()
            bpy.ops.mmd_tools.clear_uv_morph_view()

        # Find all the meshes in mmd_root
        rig = mmd_model.Model(root)
        meshes_list = sorted(rig.meshes(), key=lambda x: x.name)
        if not meshes_list:
            return { 'CANCELLED' }
        active_mesh = meshes_list[0]

        from mmd_tools_local import bpyutils
        bpyutils.select_object(active_mesh, objects=meshes_list)

        # Store the current order of the materials
        for m in meshes_list[1:]:
            for mat in m.data.materials:
                if getattr(mat, 'name', None) not in active_mesh.data.materials[:]:
                    active_mesh.data.materials.append(mat)

        # Store the current order of shape keys (vertex morphs)
        from collections import OrderedDict
        __get_key_blocks = lambda x: x.data.shape_keys.key_blocks if x.data.shape_keys else []
        shape_key_names = OrderedDict((kb.name, None) for m in meshes_list for kb in __get_key_blocks(m))
        shape_key_names = sorted(shape_key_names.keys(), key=lambda x: root.mmd_root.vertex_morphs.find(x))
        FnMorph.storeShapeKeyOrder(active_mesh, shape_key_names)
        active_mesh.active_shape_key_index = 0

        # Join selected meshes
        bpy.ops.object.join()

        if len(root.mmd_root.material_morphs) > 0:
            for morph in root.mmd_root.material_morphs:
                mo = FnMorph(morph, rig)
                mo.update_mat_related_mesh(active_mesh)

        utils.clearUnusedMeshes()
        return { 'FINISHED' }

class AttachMeshesToMMD(Operator):
    bl_idname = 'mmd_tools.attach_meshes'
    bl_label = 'Attach Meshes to Model'
    bl_description = 'Finds existing meshes and attaches them to the selected MMD model'
    bl_options = {'PRESET'}

    def execute(self, context):
        root = mmd_model.Model.findRoot(context.active_object)
        if root is None:
            self.report({ 'ERROR' }, 'Select a MMD model')
            return { 'CANCELLED' }

        rig = mmd_model.Model(root)
        armObj = rig.armature()
        if armObj is None:
            self.report({ 'ERROR' }, 'Model Armature not found')
            return { 'CANCELLED' }

        def __get_root(mesh):
            if mesh.parent is None:
                return mesh
            return __get_root(mesh.parent)

        meshes_list = (o for o in context.visible_objects if o.type == 'MESH' and o.mmd_type == 'NONE')
        for mesh in meshes_list:
            if mmd_model.Model.findRoot(mesh) is not None:
                # Do not attach meshes from other models
                continue
            mesh = __get_root(mesh)
            m = mesh.matrix_world
            mesh.parent_type = 'OBJECT'
            mesh.parent = armObj
            mesh.matrix_world = m
        return { 'FINISHED' }

class ChangeMMDIKLoopFactor(Operator):
    bl_idname = 'mmd_tools.change_mmd_ik_loop_factor'
    bl_label = 'Change MMD IK Loop Factor'
    bl_description = "Multiplier for all bones' IK iterations in Blender"
    bl_options = {'PRESET'}

    mmd_ik_loop_factor = bpy.props.IntProperty(
        name='MMD IK Loop Factor',
        description='Scaling factor of MMD IK loop',
        min=1,
        soft_max=10,
        max=100,
        options={'SKIP_SAVE'},
        )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE'

    def invoke(self, context, event):
        arm = context.active_object
        self.mmd_ik_loop_factor = max(arm.get('mmd_ik_loop_factor', 1), 1)
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

    def execute(self, context):
        arm = context.active_object

        if '_RNA_UI' not in arm:
            arm['_RNA_UI'] = {}
        prop = {}
        prop['min'] = 1
        prop['soft_min'] = 1
        prop['soft_max'] = 10
        prop['max'] = 100
        prop['description'] = 'Scaling factor of MMD IK loop'
        arm['_RNA_UI']['mmd_ik_loop_factor'] = prop

        old_factor = max(arm.get('mmd_ik_loop_factor', 1), 1)
        new_factor = arm['mmd_ik_loop_factor'] = self.mmd_ik_loop_factor
        if new_factor == old_factor:
            return { 'FINISHED' }
        for b in arm.pose.bones:
            for c in b.constraints:
                if c.type != 'IK':
                    continue
                iterations = int(c.iterations * new_factor / old_factor)
                self.report({ 'INFO' }, 'Update %s of %s: %d -> %d'%(c.name, b.name, c.iterations, iterations))
                c.iterations = iterations
        return { 'FINISHED' }

