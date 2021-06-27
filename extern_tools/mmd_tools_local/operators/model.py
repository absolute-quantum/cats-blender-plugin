# -*- coding: utf-8 -*-

import bpy
from bpy.types import Operator

from mmd_tools_local import register_wrap
from mmd_tools_local.bpyutils import SceneOp
from mmd_tools_local.core.bone import FnBone
from mmd_tools_local.translations import DictionaryEnum
import mmd_tools_local.core.model as mmd_model


@register_wrap
class MorphSliderSetup(Operator):
    bl_idname = 'mmd_tools.morph_slider_setup'
    bl_label = 'Morph Slider Setup'
    bl_description = 'Translate MMD morphs of selected object into format usable by Blender'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    type = bpy.props.EnumProperty(
        name='Type',
        description='Select type',
        items = [
            ('CREATE', 'Create', 'Create placeholder object for morph sliders', 'SHAPEKEY_DATA', 0),
            ('BIND', 'Bind', 'Bind morph sliders', 'DRIVER', 1),
            ('UNBIND', 'Unbind', 'Unbind morph sliders', 'X', 2),
            ],
        default='CREATE',
        )

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(context.active_object)
        rig = mmd_model.Model(root)
        if self.type == 'BIND':
            rig.morph_slider.bind()
        elif self.type == 'UNBIND':
            rig.morph_slider.unbind()
        else:
            rig.morph_slider.create()
        SceneOp(context).active_object = obj
        return {'FINISHED'}

@register_wrap
class CleanRiggingObjects(Operator):
    bl_idname = 'mmd_tools.clean_rig'
    bl_label = 'Clean Rig'
    bl_description = 'Delete temporary physics objects of selected object and revert physics to default MMD state'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        root = mmd_model.Model.findRoot(context.active_object)
        rig = mmd_model.Model(root)
        rig.clean()
        SceneOp(context).active_object = root
        return {'FINISHED'}

@register_wrap
class BuildRig(Operator):
    bl_idname = 'mmd_tools.build_rig'
    bl_label = 'Build Rig'
    bl_description = 'Translate physics of selected object into format usable by Blender'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        root = mmd_model.Model.findRoot(context.active_object)
        rig = mmd_model.Model(root)
        rig.build()
        SceneOp(context).active_object = root
        return {'FINISHED'}

@register_wrap
class CleanAdditionalTransformConstraints(Operator):
    bl_idname = 'mmd_tools.clean_additional_transform'
    bl_label = 'Clean Additional Transform'
    bl_description = 'Delete shadow bones of selected object and revert bones to default MMD state'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        rig.cleanAdditionalTransformConstraints()
        SceneOp(context).active_object = obj
        return {'FINISHED'}

@register_wrap
class ApplyAdditionalTransformConstraints(Operator):
    bl_idname = 'mmd_tools.apply_additional_transform'
    bl_label = 'Apply Additional Transform'
    bl_description = 'Translate appended bones of selected object for Blender'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        rig.applyAdditionalTransformConstraints()
        SceneOp(context).active_object = obj
        return {'FINISHED'}

@register_wrap
class SetupBoneFixedAxes(Operator):
    bl_idname = 'mmd_tools.bone_fixed_axis_setup'
    bl_label = 'Setup Bone Fixed Axis'
    bl_description = 'Setup fixed axis of selected bones'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    type = bpy.props.EnumProperty(
        name='Type',
        description='Select type',
        items = [
            ('DISABLE', 'Disable', 'Disable MMD fixed axis of selected bones', 0),
            ('LOAD', 'Load', 'Load/Enable MMD fixed axis of selected bones from their Y-axis or the only rotatable axis', 1),
            ('APPLY', 'Apply', 'Align bone axes to MMD fixed axis of each bone', 2),
            ],
        default='LOAD',
        )

    def execute(self, context):
        arm = context.active_object
        if not arm or arm.type != 'ARMATURE':
            self.report({'ERROR'}, 'Active object is not an armature object')
            return {'CANCELLED'}

        if self.type == 'APPLY':
            FnBone.apply_bone_fixed_axis(arm)
            FnBone.apply_additional_transformation(arm)
        else:
            FnBone.load_bone_fixed_axis(arm, enable=(self.type=='LOAD'))
        return {'FINISHED'}

@register_wrap
class SetupBoneLocalAxes(Operator):
    bl_idname = 'mmd_tools.bone_local_axes_setup'
    bl_label = 'Setup Bone Local Axes'
    bl_description = 'Setup local axes of each bone'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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
            FnBone.apply_additional_transformation(arm)
        else:
            FnBone.load_bone_local_axes(arm, enable=(self.type=='LOAD'))
        return {'FINISHED'}

@register_wrap
class CreateMMDModelRoot(Operator):
    bl_idname = 'mmd_tools.create_mmd_model_root_object'
    bl_label = 'Create a MMD Model Root Object'
    bl_description = 'Create a MMD model root object with a basic armature'
    bl_options = {'REGISTER', 'UNDO'}

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
        rig = mmd_model.Model.create(self.name_j, self.name_e, self.scale, add_root_bone=True)
        rig.initialDisplayFrames()
        return {'FINISHED'}

    def invoke(self, context, event):
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

@register_wrap
class ConvertToMMDModel(Operator):
    bl_idname = 'mmd_tools.convert_to_mmd_model'
    bl_label = 'Convert to a MMD Model'
    bl_description = 'Convert active armature with its meshes to a MMD model (experimental)'
    bl_options = {'REGISTER', 'UNDO'}

    ambient_color_source = bpy.props.EnumProperty(
        name='Ambient Color Source',
        description='Select ambient color source',
        items = [
            ('DIFFUSE', 'Diffuse', 'Diffuse color', 0),
            ('MIRROR', 'Mirror', 'Mirror color (if property "mirror_color" is available)', 1),
            ],
        default='DIFFUSE',
        )
    edge_threshold = bpy.props.FloatProperty(
        name='Edge Threshold',
        description='MMD toon edge will not be enabled if freestyle line color alpha less than this value',
        min=0,
        max=1.001,
        precision=3,
        step=0.1,
        default=0.1,
        )
    edge_alpha_min = bpy.props.FloatProperty(
        name='Minimum Edge Alpha',
        description='Minimum alpha of MMD toon edge color',
        min=0,
        max=1,
        precision=3,
        step=0.1,
        default=0.5,
        )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and obj.mode != 'EDIT'

    def invoke(self, context, event):
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

    def execute(self, context):
        #TODO convert some basic MMD properties
        armature = context.active_object
        scale = 1
        model_name = 'New MMD Model'

        root = mmd_model.Model.findRoot(armature)
        if root is None or root != armature.parent:
            rig = mmd_model.Model.create(model_name, model_name, scale, armature=armature)

        self.__attach_meshes_to(armature, SceneOp(context).id_objects)
        self.__configure_rig(mmd_model.Model(armature.parent))
        return {'FINISHED'}

    def __attach_meshes_to(self, armature, objects):

        def __is_child_of_armature(mesh):
            if mesh.parent is None:
                return False
            return mesh.parent == armature or __is_child_of_armature(mesh.parent)

        def __is_using_armature(mesh):
            for m in mesh.modifiers:
                if m.type =='ARMATURE' and m.object == armature:
                    return True
            return False

        def __get_root(mesh):
            if mesh.parent is None:
                return mesh
            return __get_root(mesh.parent)

        for x in objects:
            if __is_using_armature(x) and not __is_child_of_armature(x):
                x_root = __get_root(x)
                m = x_root.matrix_world
                x_root.parent_type = 'OBJECT'
                x_root.parent = armature
                x_root.matrix_world = m

    def __configure_rig(self, rig):
        root = rig.rootObject()
        armature = rig.armature()
        meshes = tuple(rig.meshes())

        rig.loadMorphs()

        vertex_groups = {g.name for mesh in meshes for g in mesh.vertex_groups}
        for pose_bone in armature.pose.bones:
            if not pose_bone.parent:
                continue
            if not pose_bone.bone.use_connect and pose_bone.name not in vertex_groups:
                continue
            pose_bone.lock_location = (True, True, True)

        from mmd_tools_local.core.material import FnMaterial
        for m in {x for mesh in meshes for x in mesh.data.materials if x}:
            FnMaterial.convert_to_mmd_material(m)
            mmd_material = m.mmd_material
            if self.ambient_color_source == 'MIRROR' and hasattr(m, 'mirror_color'):
                mmd_material.ambient_color = m.mirror_color
            else:
                mmd_material.ambient_color = [0.5*c for c in mmd_material.diffuse_color]

            if hasattr(m, 'line_color'): # freestyle line color
                line_color = list(m.line_color)
                mmd_material.enabled_toon_edge = line_color[3] >= self.edge_threshold
                mmd_material.edge_color = line_color[:3] + [max(line_color[3], self.edge_alpha_min)]

        from mmd_tools_local.operators.display_item import DisplayItemQuickSetup
        DisplayItemQuickSetup.load_bone_groups(root.mmd_root, armature)
        rig.initialDisplayFrames(reset=False) # ensure default frames
        DisplayItemQuickSetup.load_facial_items(root.mmd_root)
        root.mmd_root.active_display_item_frame = 0

@register_wrap
class TranslateMMDModel(Operator):
    bl_idname = 'mmd_tools.translate_mmd_model'
    bl_label = 'Translate a MMD Model'
    bl_description = 'Translate Japanese names of a MMD model'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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

