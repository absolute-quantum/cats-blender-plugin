# -*- coding: utf-8 -*-

import bpy
from bpy.types import Operator

from mmd_tools_local import bpyutils
from mmd_tools_local.core.bone import FnBone
from mmd_tools_local.translations import DictionaryEnum
import mmd_tools_local.core.model as mmd_model


class CleanRiggingObjects(Operator):
    bl_idname = 'mmd_tools.clean_rig'
    bl_label = 'Clean Rig'
    bl_description = 'Delete temporary physics objects of selected object and revert physics to default MMD state'
    bl_options = {'PRESET'}

    def execute(self, context):
        root = mmd_model.Model.findRoot(context.active_object)
        rig = mmd_model.Model(root)
        rig.clean()
        context.scene.objects.active = root
        return {'FINISHED'}

class BuildRig(Operator):
    bl_idname = 'mmd_tools.build_rig'
    bl_label = 'Build Rig'
    bl_description = 'Translate physics of selected object into format usable by Blender'
    bl_options = {'PRESET'}

    def execute(self, context):
        root = mmd_model.Model.findRoot(context.active_object)
        rig = mmd_model.Model(root)
        rig.build()
        context.scene.objects.active = root
        return {'FINISHED'}

class CleanAdditionalTransformConstraints(Operator):
    bl_idname = 'mmd_tools.clean_additional_transform'
    bl_label = 'Clean Additional Transform'
    bl_description = 'Delete shadow bones of selected object and revert bones to default MMD state'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        rig.cleanAdditionalTransformConstraints()
        context.scene.objects.active = obj
        return {'FINISHED'}

class ApplyAdditionalTransformConstraints(Operator):
    bl_idname = 'mmd_tools.apply_additional_transform'
    bl_label = 'Apply Additional Transform'
    bl_description = 'Translate appended bones of selected object for Blender'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        rig.applyAdditionalTransformConstraints()
        context.scene.objects.active = obj
        return {'FINISHED'}

class SetupBoneLocalAxes(Operator):
    bl_idname = 'mmd_tools.bone_local_axes_setup'
    bl_label = 'Setup Bone Local Axes'
    bl_description = 'Setup local axes of each bone'
    bl_options = {'INTERNAL'}

    type = bpy.props.EnumProperty(
        name='Type',
        description='Select type',
        items = [
            ('DISABLE', 'Disable', 'Disable MMD local axes of selected bones', 0),
            ('LOAD', 'Load', 'Load/Enable MMD local axes of selected bones from their bone axes', 1),
            ('APPLY', 'Apply', 'Align bone axes to MMD local axes of each bone', 2),
            ],
        default='LOAD',
        )

    def execute(self, context):
        arm = context.active_object
        if not arm or arm.type != 'ARMATURE':
            self.report({'ERROR'}, 'Active object is not an armature object')
            return {'CANCELLED'}

        if self.type == 'APPLY':
            FnBone.apply_bone_local_axes(arm)
            #FnBone.apply_additional_transformation(arm)
        else:
            FnBone.load_bone_local_axes(arm, enable=(self.type=='LOAD'))
        return {'FINISHED'}

class CreateMMDModelRoot(Operator):
    bl_idname = 'mmd_tools.create_mmd_model_root_object'
    bl_label = 'Create a MMD Model Root Object'
    bl_description = 'Create a MMD model root object with a basic armature'
    bl_options = {'PRESET'}

    name_j = bpy.props.StringProperty(
        name='Name',
        description='The name of the MMD model',
        default='New MMD Model',
        )
    name_e = bpy.props.StringProperty(
        name='Name(Eng)',
        description='The english name of the MMD model',
        default='New MMD Model',
        )
    scale = bpy.props.FloatProperty(
        name='Scale',
        description='Scale',
        default=1.0,
        )

    def execute(self, context):
        rig = mmd_model.Model.create(self.name_j, self.name_e, self.scale)
        arm = rig.armature()
        with bpyutils.edit_object(arm) as data:
            bone = data.edit_bones.new(name=u'全ての親')
            bone.head = [0.0, 0.0, 0.0]
            bone.tail = [0.0, 0.0, 5.0*self.scale]
        arm.pose.bones[u'全ての親'].mmd_bone.name_j = u'全ての親'
        arm.pose.bones[u'全ての親'].mmd_bone.name_e = 'Root'

        rig.initialDisplayFrames(root_bone_name=arm.data.bones[0].name)
        root = rig.rootObject()
        context.scene.objects.active = root
        root.select = True
        return {'FINISHED'}

    def invoke(self, context, event):
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

class TranslateMMDModel(Operator):
    bl_idname = 'mmd_tools.translate_mmd_model'
    bl_label = 'Translate a MMD Model'
    bl_description = 'Translate Japanese names of a MMD model'

    dictionary = bpy.props.EnumProperty(
        name='Dictionary',
        items=DictionaryEnum.get_dictionary_items,
        description='Translate names from Japanese to English using selected dictionary',
        )
    types = bpy.props.EnumProperty(
        name='Types',
        description='Select which parts will be translated',
        options={'ENUM_FLAG'},
        items = [
            ('BONE', 'Bones', 'Bones', 1),
            ('MORPH', 'Morphs', 'Morphs', 2),
            ('MATERIAL', 'Materials', 'Materials', 4),
            ('DISPLAY', 'Display', 'Display frames', 8),
            ('PHYSICS', 'Physics', 'Rigidbodies and joints', 16),
            ('INFO', 'Information', 'Model name and comments', 32),
            ],
        default={'BONE', 'MORPH', 'MATERIAL', 'DISPLAY', 'PHYSICS',},
        )
    modes = bpy.props.EnumProperty(
        name='Modes',
        description='Select translation mode',
        options={'ENUM_FLAG'},
        items = [
            ('MMD', 'MMD Names', 'Fill MMD English names', 1),
            ('BLENDER', 'Blender Names', 'Translate blender names (experimental)', 2),
            ],
        default={'MMD'},
        )
    use_morph_prefix = bpy.props.BoolProperty(
        name='Use Morph Prefix',
        description='Add/remove prefix to English name of morph',
        default=False,
        )
    overwrite = bpy.props.BoolProperty(
        name='Overwrite',
        description='Overwrite a translated English name',
        default=False,
        )
    allow_fails = bpy.props.BoolProperty(
        name='Allow Fails',
        description='Allow incompletely translated names',
        default=False,
        )

    def invoke(self, context, event):
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

    def execute(self, context):
        try:
            self.__translator = DictionaryEnum.get_translator(self.dictionary)
        except Exception as e:
            self.report({'ERROR'}, 'Failed to load dictionary: %s'%e)
            return {'CANCELLED'}

        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)

        if 'MMD' in self.modes:
            for i in self.types:
                getattr(self, 'translate_%s'%i.lower())(rig)

        if 'BLENDER' in self.modes:
            self.translate_blender_names(rig)

        translator = self.__translator
        txt = translator.save_fails()
        if translator.fails:
            self.report({'WARNING'}, "Failed to translate %d names, see '%s' in text editor"%(len(translator.fails), txt.name))
        return {'FINISHED'}

    def translate(self, name_j, name_e):
        if not self.overwrite and name_e and self.__translator.is_translated(name_e):
            return name_e
        if self.allow_fails:
            name_e = None
        return self.__translator.translate(name_j, name_e)

    def translate_blender_names(self, rig):
        if 'BONE' in self.types:
            for b in rig.armature().pose.bones:
                rig.renameBone(b.name, self.translate(b.name, b.name))

        if 'MORPH' in self.types:
            for i in (x for x in rig.meshes() if x.data.shape_keys):
                for kb in i.data.shape_keys.key_blocks:
                    kb.name = self.translate(kb.name, kb.name)

        if 'MATERIAL' in self.types:
            for m in (x for x in rig.materials() if x):
                m.name = self.translate(m.name, m.name)

        if 'DISPLAY' in self.types:
            for g in rig.armature().pose.bone_groups:
                g.name = self.translate(g.name, g.name)

        if 'PHYSICS' in self.types:
            for i in rig.rigidBodies():
                i.name = self.translate(i.name, i.name)

            for i in rig.joints():
                i.name = self.translate(i.name, i.name)

        if 'INFO' in self.types:
            objects = [rig.rootObject(), rig.armature()]
            objects.extend(rig.meshes())
            for i in objects:
                i.name = self.translate(i.name, i.name)

    def translate_info(self, rig):
        mmd_root = rig.rootObject().mmd_root
        mmd_root.name_e = self.translate(mmd_root.name, mmd_root.name_e)

        comment_text = bpy.data.texts.get(mmd_root.comment_text, None)
        comment_e_text = bpy.data.texts.get(mmd_root.comment_e_text, None)
        if comment_text and comment_e_text:
            comment_e = self.translate(comment_text.as_string(), comment_e_text.as_string())
            comment_e_text.from_string(comment_e)

    def translate_bone(self, rig):
        bones = rig.armature().pose.bones
        for b in bones:
            if b.is_mmd_shadow_bone:
                continue
            b.mmd_bone.name_e = self.translate(b.mmd_bone.name_j, b.mmd_bone.name_e)

    def translate_morph(self, rig):
        mmd_root = rig.rootObject().mmd_root
        attr_list = ('group', 'vertex', 'bone', 'uv', 'material')
        prefix_list = ('G_', '', 'B_', 'UV_', 'M_')
        for attr, prefix in zip(attr_list, prefix_list):
            for m in getattr(mmd_root, attr+'_morphs', []):
                m.name_e = self.translate(m.name, m.name_e)
                if not prefix:
                    continue
                if self.use_morph_prefix:
                    if not m.name_e.startswith(prefix):
                        m.name_e = prefix + m.name_e
                elif m.name_e.startswith(prefix):
                    m.name_e = m.name_e[len(prefix):]

    def translate_material(self, rig):
        for m in rig.materials():
            if m is None:
                continue
            m.mmd_material.name_e = self.translate(m.mmd_material.name_j, m.mmd_material.name_e)

    def translate_display(self, rig):
        mmd_root = rig.rootObject().mmd_root
        for f in mmd_root.display_item_frames:
            f.name_e = self.translate(f.name, f.name_e)

    def translate_physics(self, rig):
        for i in rig.rigidBodies():
            i.mmd_rigid.name_e = self.translate(i.mmd_rigid.name_j, i.mmd_rigid.name_e)

        for i in rig.joints():
            i.mmd_joint.name_e = self.translate(i.mmd_joint.name_j, i.mmd_joint.name_e)
