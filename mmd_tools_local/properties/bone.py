# -*- coding: utf-8 -*-

from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty, FloatVectorProperty

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

class MMDBone(PropertyGroup):
    name_j = StringProperty(
        name='Name',
        description='Japanese Name',
        default='',
        )

    name_e = StringProperty(
        name='Name(Eng)',
        description='English Name',
        default='',
        )

    bone_id = IntProperty(
        name='Bone ID',
        default=-1,
        )

    transform_order = IntProperty(
        name='Transform Order',
        description='Deformation tier',
        min=0,
        max=100,
        )

    is_controllable = BoolProperty(
        name='Controllable',
        description='Is controllable',
        default=True,
        )

    transform_after_dynamics = BoolProperty(
        name='After Dynamics',
        description='After physics',
        default=False,
        )

    enabled_fixed_axis = BoolProperty(
        name='Fixed Axis',
        description='Use fixed axis',
        default=False,
        )

    fixed_axis = FloatVectorProperty(
        name='Fixed Axis',
        description='Fixed axis',
        subtype='XYZ',
        size=3,
        default=[0, 0, 0],
        )

    enabled_local_axes = BoolProperty(
        name='Local Axes',
        description='Use local axes',
        default=False,
        )

    local_axis_x = FloatVectorProperty(
        name='Local X-Axis',
        description='Local x-axis',
        subtype='XYZ',
        size=3,
        default=[1, 0, 0],
        )

    local_axis_z = FloatVectorProperty(
        name='Local Z-Axis',
        description='Local z-axis',
        subtype='XYZ',
        size=3,
        default=[0, 0, 1],
        )

    is_tip = BoolProperty(
        name='Tip Bone',
        description='Is zero length bone',
        default=False,
        )

    ik_rotation_constraint = FloatProperty(
        name='IK Rotation Constraint',
        description='The unit angle of IK',
        subtype='ANGLE',
        soft_min=0,
        soft_max=4,
        default=1,
        )

    has_additional_rotation = BoolProperty(
        name='Additional Rotation',
        description='Additional rotation',
        default=False,
        update=_updateMMDBoneAdditionalTransform,
        )

    has_additional_location = BoolProperty(
        name='Additional Location',
        description='Additional location',
        default=False,
        update=_updateMMDBoneAdditionalTransform,
        )

    additional_transform_bone = StringProperty(
        name='Additional Transform Bone',
        description='Additional transform bone',
        set=_setAdditionalTransformBone,
        get=_getAdditionalTransformBone,
        update=_updateMMDBoneAdditionalTransform,
        )

    additional_transform_bone_id = IntProperty(
        name='Additional Transform Bone ID',
        default=-1,
        update=_updateMMDBoneAdditionalTransform,
        )

    additional_transform_influence = FloatProperty(
        name='Additional Transform Influence',
        description='Additional transform influence',
        default=1,
        soft_min=-1,
        soft_max=1,
        update=_updateAdditionalTransformInfluence,
        )

    is_additional_transform_dirty = BoolProperty(
        name='',
        default=True
        )
