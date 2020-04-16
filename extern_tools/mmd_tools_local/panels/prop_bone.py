# -*- coding: utf-8 -*-

from bpy.types import Panel

from mmd_tools_local import register_wrap

@register_wrap
class MMDBonePanel(Panel):
    bl_idname = 'BONE_PT_mmd_tools_bone'
    bl_label = 'MMD Bone Tools'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'bone'

    @classmethod
    def poll(cls, context):
        return context.active_bone

    def __draw_ik_data(self, pose_bone):
        bones = pose_bone.id_data.pose.bones
        ik_bone_names = tuple(c.subtarget for c in pose_bone.constraints if c.type == 'IK' and c.subtarget in bones)
        if ik_bone_names:
            ik_custom_map = {getattr(b.constraints.get('mmd_ik_target_custom', None), 'subtarget', None) for b in bones if not b.is_mmd_shadow_bone}
            row = self.layout.column(align=True)
            for name in ik_bone_names:
                if name in ik_custom_map:
                    row.prop(bones[name].mmd_bone, 'ik_rotation_constraint', text='IK Angle {%s}'%name)
                else:
                    row.prop(pose_bone.mmd_bone, 'ik_rotation_constraint', text='IK Angle (%s)'%name)

    def draw(self, context):
        pose_bone = context.active_pose_bone or \
                    context.active_object.pose.bones.get(context.active_bone.name, None)
        if pose_bone is None:
            return

        layout = self.layout
        if pose_bone.is_mmd_shadow_bone:
            layout.label(text='MMD Shadow Bone!', icon='INFO')
            return

        mmd_bone = pose_bone.mmd_bone

        c = layout.column()

        row = c.row(align=True)
        row.label(text='Information:')
        if not mmd_bone.is_id_unique():
            row.label(icon='ERROR')
        row.prop(mmd_bone, 'bone_id', text='ID')

        c.prop(mmd_bone, 'name_j')
        c.prop(mmd_bone, 'name_e')

        c = layout.column(align=True)
        row = c.row()
        row.prop(mmd_bone, 'transform_order')
        row.prop(mmd_bone, 'transform_after_dynamics')
        row = c.row()
        row.prop(mmd_bone, 'is_controllable')
        row.prop(mmd_bone, 'is_tip')

        self.__draw_ik_data(pose_bone)

        c = layout.column(align=True)
        row = c.row(align=True)
        row.prop(mmd_bone, 'enabled_fixed_axis')
        row.operator('mmd_tools.bone_fixed_axis_setup', text='', icon='X').type = 'DISABLE'
        row.operator('mmd_tools.bone_fixed_axis_setup', text='Load').type = 'LOAD'
        row.operator('mmd_tools.bone_fixed_axis_setup', text='Apply').type = 'APPLY'
        row = c.row()
        row.active = mmd_bone.enabled_fixed_axis
        row.column(align=True).prop(mmd_bone, 'fixed_axis', text='')

        c = layout.column(align=True)
        row = c.row(align=True)
        row.prop(mmd_bone, 'enabled_local_axes')
        row.operator('mmd_tools.bone_local_axes_setup', text='', icon='X').type = 'DISABLE'
        row.operator('mmd_tools.bone_local_axes_setup', text='Load').type = 'LOAD'
        row.operator('mmd_tools.bone_local_axes_setup', text='Apply').type = 'APPLY'
        row = c.row()
        row.active = mmd_bone.enabled_local_axes
        row.column(align=True).prop(mmd_bone, 'local_axis_x')
        row.column(align=True).prop(mmd_bone, 'local_axis_z')

        c = layout.column(align=True)
        row = c.row(align=True)
        row.prop(mmd_bone, 'has_additional_rotation', text='Rotate +', toggle=True)
        row.prop(mmd_bone, 'has_additional_location', text='Move +', toggle=True)
        if mmd_bone.is_additional_transform_dirty:
            row.label(icon='ERROR')
        c.prop_search(mmd_bone, 'additional_transform_bone', pose_bone.id_data.pose, 'bones', icon='BONE_DATA', text='')
        c.prop(mmd_bone, 'additional_transform_influence', text='Influence', slider=True)

