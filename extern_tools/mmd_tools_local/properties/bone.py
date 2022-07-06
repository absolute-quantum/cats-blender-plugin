# -*- coding: utf-8 -*-
import bpy
from mmd_tools_local.core.bone import FnBone


def _updateMMDBoneAdditionalTransform(prop, context):
    prop['is_additional_transform_dirty'] = True
    p_bone = context.active_pose_bone
    if p_bone and p_bone.mmd_bone.as_pointer() == prop.as_pointer():
        FnBone.apply_additional_transformation(prop.id_data)


def _updateAdditionalTransformInfluence(prop, context):
    p_bone = context.active_pose_bone
    if p_bone and p_bone.mmd_bone.as_pointer() == prop.as_pointer():
        FnBone(p_bone).update_additional_transform_influence()
    else:
        prop['is_additional_transform_dirty'] = True


def _getAdditionalTransformBone(prop):
    arm = prop.id_data
    bone_id = prop.get('additional_transform_bone_id', -1)
    if bone_id < 0:
        return ''
    fnBone = FnBone.from_bone_id(arm, bone_id)
    if not fnBone:
        return ''
    return fnBone.pose_bone.name


def _setAdditionalTransformBone(prop, value):
    arm = prop.id_data
    prop['is_additional_transform_dirty'] = True
    if value not in arm.pose.bones.keys():
        prop['additional_transform_bone_id'] = -1
        return
    pose_bone = arm.pose.bones[value]
    bone = FnBone(pose_bone)
    prop['additional_transform_bone_id'] = bone.bone_id


class MMDBone(bpy.types.PropertyGroup):
    name_j: bpy.props.StringProperty(
        name='Name',
        description='Japanese Name',
        default='',
    )

    name_e: bpy.props.StringProperty(
        name='Name(Eng)',
        description='English Name',
        default='',
    )

    bone_id: bpy.props.IntProperty(
        name='Bone ID',
        description='Unique ID for the reference of bone morph and rotate+/move+',
        default=-1,
        min=-1,
    )

    transform_order: bpy.props.IntProperty(
        name='Transform Order',
        description='Deformation tier',
        min=0,
        max=100,
        soft_max=7,
    )

    is_controllable: bpy.props.BoolProperty(
        name='Controllable',
        description='Is controllable',
        default=True,
    )

    transform_after_dynamics: bpy.props.BoolProperty(
        name='After Dynamics',
        description='After physics',
        default=False,
    )

    enabled_fixed_axis: bpy.props.BoolProperty(
        name='Fixed Axis',
        description='Use fixed axis',
        default=False,
    )

    fixed_axis: bpy.props.FloatVectorProperty(
        name='Fixed Axis',
        description='Fixed axis',
        subtype='XYZ',
        size=3,
        precision=3,
        step=0.1,  # 0.1 / 100
        default=[0, 0, 0],
    )

    enabled_local_axes: bpy.props.BoolProperty(
        name='Local Axes',
        description='Use local axes',
        default=False,
    )

    local_axis_x: bpy.props.FloatVectorProperty(
        name='Local X-Axis',
        description='Local x-axis',
        subtype='XYZ',
        size=3,
        precision=3,
        step=0.1,
        default=[1, 0, 0],
    )

    local_axis_z: bpy.props.FloatVectorProperty(
        name='Local Z-Axis',
        description='Local z-axis',
        subtype='XYZ',
        size=3,
        precision=3,
        step=0.1,
        default=[0, 0, 1],
    )

    is_tip: bpy.props.BoolProperty(
        name='Tip Bone',
        description='Is zero length bone',
        default=False,
    )

    ik_rotation_constraint: bpy.props.FloatProperty(
        name='IK Rotation Constraint',
        description='The unit angle of IK',
        subtype='ANGLE',
        soft_min=0,
        soft_max=4,
        default=1,
    )

    has_additional_rotation: bpy.props.BoolProperty(
        name='Additional Rotation',
        description='Additional rotation',
        default=False,
        update=_updateMMDBoneAdditionalTransform,
    )

    has_additional_location: bpy.props.BoolProperty(
        name='Additional Location',
        description='Additional location',
        default=False,
        update=_updateMMDBoneAdditionalTransform,
    )

    additional_transform_bone: bpy.props.StringProperty(
        name='Additional Transform Bone',
        description='Additional transform bone',
        set=_setAdditionalTransformBone,
        get=_getAdditionalTransformBone,
        update=_updateMMDBoneAdditionalTransform,
    )

    additional_transform_bone_id: bpy.props.IntProperty(
        name='Additional Transform Bone ID',
        default=-1,
        update=_updateMMDBoneAdditionalTransform,
    )

    additional_transform_influence: bpy.props.FloatProperty(
        name='Additional Transform Influence',
        description='Additional transform influence',
        default=1,
        soft_min=-1,
        soft_max=1,
        update=_updateAdditionalTransformInfluence,
    )

    is_additional_transform_dirty: bpy.props.BoolProperty(
        name='',
        default=True
    )

    def is_id_unique(self):
        return self.bone_id < 0 or not next((b for b in self.id_data.pose.bones if b.mmd_bone != self and b.mmd_bone.bone_id == self.bone_id), None)


def _mmd_ik_toggle_get(prop):
    return prop.get('mmd_ik_toggle', True)


def _mmd_ik_toggle_set(prop, v):
    if v != prop.get('mmd_ik_toggle', None):
        prop['mmd_ik_toggle'] = v
        _mmd_ik_toggle_update(prop, None)


def _mmd_ik_toggle_update(prop, context):
    v = prop.mmd_ik_toggle
    #logging.debug('_mmd_ik_toggle_update %s %s', v, prop.name)
    for b in prop.id_data.pose.bones:
        for c in b.constraints:
            if c.type == 'IK' and c.subtarget == prop.name:
                #logging.debug('   %s %s', b.name, c.name)
                c.influence = v
                b = b if c.use_tail else b.parent
                for b in ([b]+b.parent_recursive)[:c.chain_count]:
                    c = next((c for c in b.constraints if c.type == 'LIMIT_ROTATION' and not c.mute), None)
                    if c:
                        c.influence = v
