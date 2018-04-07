# -*- coding: utf-8 -*-

import bpy
from mmd_tools_local import bpyutils
from mmd_tools_local.bpyutils import ObjectOp
from mmd_tools_local.bpyutils import TransformConstraintOp

class FnMorph(object):

    def __init__(self, morph, model):
        self.__morph = morph
        self.__rig = model

    @classmethod
    def storeShapeKeyOrder(cls, obj, shape_key_names):
        if len(shape_key_names) < 1:
            return
        assert(bpy.context.scene.objects.active == obj)
        if obj.data.shape_keys is None:
            bpy.ops.object.shape_key_add()

        if bpy.app.version < (2, 73, 0):
            def __move_to_bottom(key_blocks, name):
                obj.active_shape_key_index = key_blocks.find(name)
                for move in range(len(key_blocks)-1-obj.active_shape_key_index):
                    bpy.ops.object.shape_key_move(type='DOWN')
        else:
            def __move_to_bottom(key_blocks, name):
                obj.active_shape_key_index = key_blocks.find(name)
                bpy.ops.object.shape_key_move(type='BOTTOM')

        key_blocks = obj.data.shape_keys.key_blocks
        for name in shape_key_names:
            if name not in key_blocks:
                obj.shape_key_add(name)
            elif len(key_blocks) > 1:
                __move_to_bottom(key_blocks, name)

    @classmethod
    def fixShapeKeyOrder(cls, obj, shape_key_names):
        if len(shape_key_names) < 1:
            return
        assert(bpy.context.scene.objects.active == obj)
        key_blocks = getattr(obj.data.shape_keys, 'key_blocks', None)
        if key_blocks is None:
            return
        if bpy.app.version < (2, 73, 0):
            len_key_blocks = len(key_blocks)
            for ii, name in enumerate(reversed(shape_key_names)):
                idx = key_blocks.find(name)
                if idx < 0:
                    continue
                obj.active_shape_key_index = idx
                offset = (len_key_blocks - 1 - idx) - ii
                move_type = 'UP' if offset < 0 else 'DOWN'
                for move in range(abs(offset)):
                    bpy.ops.object.shape_key_move(type=move_type)
        else:
            for name in shape_key_names:
                idx = key_blocks.find(name)
                if idx < 0:
                    continue
                obj.active_shape_key_index = idx
                bpy.ops.object.shape_key_move(type='BOTTOM')

    @staticmethod
    def get_morph_slider(rig):
        return _MorphSlider(rig)

    @staticmethod
    def category_guess(morph):
        name_lower = morph.name.lower()
        if 'mouth' in name_lower:
            morph.category = 'MOUTH'
        elif 'eye' in name_lower:
            if 'brow' in name_lower:
                morph.category = 'EYEBROW'
            else:
                morph.category = 'EYE'

    @classmethod
    def load_morphs(cls, rig):
        mmd_root = rig.rootObject().mmd_root
        vertex_morphs = mmd_root.vertex_morphs
        for obj in rig.meshes():
            for kb in getattr(obj.data.shape_keys, 'key_blocks', ())[1:]:
                if not kb.name.startswith('mmd_') and kb.name not in vertex_morphs:
                    item = vertex_morphs.add()
                    item.name = kb.name
                    item.name_e = kb.name
                    cls.category_guess(item)

    def update_mat_related_mesh(self, new_mesh=None):
        for offset in self.__morph.data:
            # Use the new_mesh if provided  
            meshObj = new_mesh          
            if new_mesh is None:
                # Try to find the mesh by material name
                meshObj = self.__rig.findMesh(offset.material)
            
            if meshObj is None:
                # Given this point we need to loop through all the meshes
                for mesh in self.__rig.meshes():
                    if mesh.data.materials.find(offset.material) >= 0:
                        meshObj = mesh
                        break

            # Finally update the reference
            if meshObj is not None:
                offset.related_mesh = meshObj.data.name


class _MorphSlider:

    def __init__(self, model):
        self.__rig = model

    def placeholder(self, create=False):
        rig = self.__rig
        root = rig.rootObject()
        obj = next((x for x in root.children if x.mmd_type == 'PLACEHOLDER' and x.type == 'MESH'), None)
        if create and obj is None:
            obj = bpy.data.objects.new(name='.placeholder', object_data=bpy.data.meshes.new('.placeholder'))
            obj.mmd_type = 'PLACEHOLDER'
            obj.parent = root
            bpy.context.scene.objects.link(obj)
        if obj and obj.data.shape_keys is None:
            key = obj.shape_key_add('--- morph sliders ---')
            key.mute = True
        return obj

    def __dummy_armature(self, obj, create=False):
        arm = next((x for x in obj.children if x.mmd_type == 'PLACEHOLDER' and x.type == 'ARMATURE'), None)
        if create and arm is None:
            arm = bpy.data.objects.new(name='.dummy_armature', object_data=bpy.data.armatures.new(name='.dummy_armature'))
            arm.mmd_type = 'PLACEHOLDER'
            arm.parent = obj
            bpy.context.scene.objects.link(arm)
            arm.data.draw_type = 'STICK'
        return arm


    def get(self, morph_name):
        obj = self.placeholder()
        if obj is None:
            return None
        key_blocks = obj.data.shape_keys.key_blocks
        if key_blocks[0].mute:
            return None
        return key_blocks.get(morph_name, None)

    def create(self):
        self.__rig.loadMorphs()
        obj = self.placeholder(create=True)
        self.__load(obj, self.__rig.rootObject().mmd_root)
        return obj

    def __load(self, obj, mmd_root):
        attr_list = ('group', 'vertex', 'bone', 'uv', 'material')
        morph_key_blocks = obj.data.shape_keys.key_blocks
        for m in (x for attr in attr_list for x in getattr(mmd_root, attr+'_morphs', ())):
            name = m.name
            #if name[-1] == '\\': # fix driver's bug???
            #    m.name = name = name + ' '
            if name and name not in morph_key_blocks:
                obj.shape_key_add(name)


    @staticmethod
    def __driver_variables(id_data, path, index=-1):
        d = id_data.driver_add(path, index)
        variables = d.driver.variables
        for x in variables:
            variables.remove(x)
        return d.driver, variables

    @staticmethod
    def __add_single_prop(variables, id_obj, data_path, prefix):
        var = variables.new()
        var.name = prefix + str(len(variables))
        var.type = 'SINGLE_PROP'
        target = var.targets[0]
        target.id_type = 'OBJECT'
        target.id = id_obj
        target.data_path = data_path
        return var

    def __cleanup(self, names_in_use=None):
        names_in_use = names_in_use or {}
        rig = self.__rig
        for mesh in rig.meshes():
            for kb in getattr(mesh.data.shape_keys, 'key_blocks', ()):
                if kb.name.startswith('mmd_bind') and kb.name not in names_in_use:
                    kb.driver_remove('value')
                    kb.relative_key.mute = False
                    ObjectOp(mesh).shape_key_remove(kb)

        attributes = set(TransformConstraintOp.min_max_attributes('LOCATION', 'to'))
        attributes |= set(TransformConstraintOp.min_max_attributes('ROTATION', 'to'))
        for b in rig.armature().pose.bones:
            for c in b.constraints:
                if c.name.startswith('mmd_bind') and c.name[:-4] not in names_in_use:
                    for attr in attributes:
                        c.driver_remove(attr)
                    b.constraints.remove(c)

    def unbind(self):
        obj = self.placeholder()
        if obj:
            obj.data.shape_keys.key_blocks[0].mute = True
            arm = self.__dummy_armature(obj)
            if arm:
                for b in arm.pose.bones:
                    if b.name.startswith('mmd_bind'):
                        b.driver_remove('location')
                        b.driver_remove('rotation_quaternion')
        self.__cleanup()

    def bind(self):
        #bpy.context.user_preferences.system.use_scripts_auto_execute = True
        rig = self.__rig
        root = rig.rootObject()
        armObj = rig.armature()
        mmd_root = root.mmd_root

        obj = self.create()
        arm = self.__dummy_armature(obj, create=True)
        morph_key_blocks = obj.data.shape_keys.key_blocks

        # data gathering
        group_map = {}

        shape_key_map = {}
        for mesh in rig.meshes():
            mesh.show_only_shape_key = False
            key_blocks = getattr(mesh.data.shape_keys, 'key_blocks', ())
            for kb in key_blocks:
                kb_name = kb.name
                if kb_name not in morph_key_blocks:
                    continue

                name_bind = 'mmd_bind%s'%hash(morph_key_blocks[kb_name])
                if name_bind not in key_blocks:
                    mesh.shape_key_add(name_bind)
                kb_bind = key_blocks[name_bind]
                kb_bind.relative_key = kb
                kb_bind.slider_min = -10
                kb_bind.slider_max = 10

                data_path = 'data.shape_keys.key_blocks["%s"].value'%kb_name.replace('"', '\\"')
                groups = []
                shape_key_map.setdefault(name_bind, []).append((kb_bind, data_path, groups))
                group_map.setdefault(('vertex_morphs', kb_name), []).append(groups)

        bone_offset_map = {}
        with bpyutils.edit_object(arm) as data:
            edit_bones = data.edit_bones
            for m in mmd_root.bone_morphs:
                data_path = 'data.shape_keys.key_blocks["%s"].value'%m.name.replace('"', '\\"')
                for d in m.data:
                    if not d.bone:
                        d.name = ''
                        continue
                    d.name = str(hash(d))
                    name_bind = 'mmd_bind%s'%hash(d)
                    b = edit_bones.get(name_bind, None) or edit_bones.new(name=name_bind)
                    b.layers = [x == 10 for x in range(len(b.layers))]
                    b.head = (0, 0, 0)
                    b.tail = (0, 0, 1)
                    b.use_deform = False
                    groups = []
                    bone_offset_map[name_bind] = (m.name, d, b.name, data_path, groups)
                    group_map.setdefault(('bone_morphs', m.name), []).append(groups)

            for b in edit_bones: # cleanup
                if b.name.startswith('mmd_bind') and b.name not in bone_offset_map:
                    edit_bones.remove(b)

        for m in mmd_root.group_morphs:
            for d in m.data:
                for groups in group_map.get((d.morph_type, d.name), ()):
                    morph_name = m.name.replace('"', '\\"')
                    param = (morph_name, d.name.replace('"', '\\"'))
                    factor_path = 'mmd_root.group_morphs["%s"].data["%s"].factor'%param
                    morph_path = 'data.shape_keys.key_blocks["%s"].value'%morph_name
                    groups.append((m.name, morph_path, factor_path))

        self.__cleanup(shape_key_map.keys()|bone_offset_map.keys())

        def __config_groups(variables, expression, groups):
            for g_name, morph_path, factor_path in groups:
                var = self.__add_single_prop(variables, obj, morph_path, 'g')
                fvar = self.__add_single_prop(variables, root, factor_path, 'w')
                expression = '%s+%s*%s'%(expression, var.name, fvar.name)
            return expression

        # vertex morphs
        for kb_bind, morph_data_path, groups in (i for l in shape_key_map.values() for i in l):
            driver, variables = self.__driver_variables(kb_bind, 'value')
            var = self.__add_single_prop(variables, obj, morph_data_path, 'v')
            driver.expression = '-(%s)'%__config_groups(variables, var.name, groups)
            kb_bind.relative_key.mute = True
            kb_bind.mute = False

        # bone morphs
        def __config_bone_morph(constraints, map_type, attributes, val, val_str):
            c_name = 'mmd_bind%s.%s'%(hash(data), map_type[:3])
            c = TransformConstraintOp.create(constraints, c_name, map_type)
            TransformConstraintOp.update_min_max(c, val, None)
            c.show_expanded = False
            c.target = arm
            c.subtarget = bname
            for attr in attributes:
                driver, variables = self.__driver_variables(armObj, c.path_from_id(attr))
                var = self.__add_single_prop(variables, obj, morph_data_path, 'b')
                expression = __config_groups(variables, var.name, groups)
                sign = '-' if attr.startswith('to_min') else ''
                driver.expression = '%s%s*(%s)'%(sign, val_str, expression)

        from math import pi
        attributes_rot = TransformConstraintOp.min_max_attributes('ROTATION', 'to')
        attributes_loc = TransformConstraintOp.min_max_attributes('LOCATION', 'to')
        for morph_name, data, bname, morph_data_path, groups in bone_offset_map.values():
            b = arm.pose.bones[bname]
            root_path = 'mmd_root.bone_morphs["%s"].data["%s"]'%(morph_name.replace('"', '\\"'), data.name)
            for i in range(3):
                data_path = '%s.location[%d]'%(root_path, i)
                driver, variables = self.__driver_variables(b, 'location', index=i)
                driver.expression = self.__add_single_prop(variables, root, data_path, 'L').name
            for i in range(4):
                data_path = '%s.rotation[%d]'%(root_path, i)
                driver, variables = self.__driver_variables(b, 'rotation_quaternion', index=i)
                driver.expression = self.__add_single_prop(variables, root, data_path, 'R').name
            b.is_mmd_shadow_bone = True
            b.mmd_shadow_bone_type = 'BIND'
            pb = armObj.pose.bones[data.bone]
            __config_bone_morph(pb.constraints, 'ROTATION', attributes_rot, pi, 'pi')
            __config_bone_morph(pb.constraints, 'LOCATION', attributes_loc, 100, '100')

        #TODO material/uv morphs if possible

        morph_key_blocks[0].mute = False

