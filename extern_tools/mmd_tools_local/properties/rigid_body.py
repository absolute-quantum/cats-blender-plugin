# -*- coding: utf-8 -*-

import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, IntProperty, BoolVectorProperty, EnumProperty, FloatVectorProperty

from mmd_tools_local import register_wrap
from mmd_tools_local import bpyutils
from mmd_tools_local.core import rigid_body
from mmd_tools_local.core.model import getRigidBodySize, Model


def _updateCollisionGroup(prop, context):
    obj = prop.id_data
    materials = obj.data.materials
    if len(materials) == 0:
        materials.append(rigid_body.RigidBodyMaterial.getMaterial(prop.collision_group_number))
    else:
        obj.material_slots[0].material = rigid_body.RigidBodyMaterial.getMaterial(prop.collision_group_number)

def _updateType(prop, context):
    obj = prop.id_data
    rb = obj.rigid_body
    if rb:
        rb.kinematic = (int(prop.type) == rigid_body.MODE_STATIC)

def _updateShape(prop, context):
    obj = prop.id_data

    if len(obj.data.vertices) > 0:
        size = prop.size
        prop.size = size # update mesh

    rb = obj.rigid_body
    if rb:
        rb.collision_shape = prop.shape


def _get_bone(prop):
    obj = prop.id_data
    relation = obj.constraints.get('mmd_tools_rigid_parent', None)
    if relation:
        arm = relation.target
        bone_name = relation.subtarget
        if arm is not None and bone_name in arm.data.bones:
            return bone_name
    return prop.get('bone', '')

def _set_bone(prop, value):
    bone_name = value
    obj = prop.id_data
    relation = obj.constraints.get('mmd_tools_rigid_parent', None)
    if relation is None:
        relation = obj.constraints.new('CHILD_OF')
        relation.name = 'mmd_tools_rigid_parent'
        relation.mute = True

    arm = relation.target
    if arm is None:
        root = Model.findRoot(obj)
        if root:
            arm = relation.target = Model(root).armature()

    if arm is not None and bone_name in arm.data.bones:
        relation.subtarget = bone_name
    else:
        relation.subtarget = bone_name = ''

    prop['bone'] = bone_name


def _get_size(prop):
    if prop.id_data.mmd_type != 'RIGID_BODY':
        return (0, 0, 0)
    return getRigidBodySize(prop.id_data)

def _set_size(prop, value):
    obj = prop.id_data
    assert(obj.mode == 'OBJECT') # not support other mode yet
    shape = prop.shape

    mesh = obj.data
    rb = obj.rigid_body

    if len(mesh.vertices) == 0 or rb is None or rb.collision_shape != shape:
        if shape == 'SPHERE':
            bpyutils.makeSphere(
                radius=value[0],
                target_object=obj,
                )
        elif shape == 'BOX':
            bpyutils.makeBox(
                size=value,
                target_object=obj,
                )
        elif shape == 'CAPSULE':
            bpyutils.makeCapsule(
                radius=value[0],
                height=value[1],
                target_object=obj,
                )
        mesh.update()
        if rb:
            rb.collision_shape = shape
    else:
        if shape == 'SPHERE':
            radius = max(value[0], 1e-3)
            for v in mesh.vertices:
                vec = v.co.normalized()
                v.co = vec * radius
        elif shape == 'BOX':
            x = max(value[0], 1e-3)
            y = max(value[1], 1e-3)
            z = max(value[2], 1e-3)
            for v in mesh.vertices:
                x0, y0, z0 = v.co
                x0 = -x if x0 < 0 else x
                y0 = -y if y0 < 0 else y
                z0 = -z if z0 < 0 else z
                v.co = [x0, y0, z0]
        elif shape == 'CAPSULE':
            r0, h0, xx = getRigidBodySize(prop.id_data)
            h0 *= 0.5
            radius = max(value[0], 1e-3)
            height = max(value[1], 1e-3)*0.5
            scale = radius/max(r0, 1e-3)
            for v in mesh.vertices:
                x0, y0, z0 = v.co
                x0 *= scale
                y0 *= scale
                if z0 < 0:
                    z0 = (z0 + h0)*scale - height
                else:
                    z0 = (z0 - h0)*scale + height
                v.co = [x0, y0, z0]
        mesh.update()

def _get_rigid_name(prop):
    return prop.get('name', '')

def _set_rigid_name(prop, value):
    prop['name'] = value


@register_wrap
class MMDRigidBody(PropertyGroup):
    name_j = StringProperty(
        name='Name',
        description='Japanese Name',
        default='',
        get=_get_rigid_name,
        set=_set_rigid_name,
        )

    name_e = StringProperty(
        name='Name(Eng)',
        description='English Name',
        default='',
        )

    collision_group_number = IntProperty(
        name='Collision Group',
        description='The collision group of the object',
        min=0,
        max=15,
        default=1,
        update=_updateCollisionGroup,
        )

    collision_group_mask = BoolVectorProperty(
        name='Collision Group Mask',
        description='The groups the object can not collide with',
        size=16,
        subtype='LAYER',
        )

    type = EnumProperty(
        name='Rigid Type',
        description='Select rigid type',
        items = [
            (str(rigid_body.MODE_STATIC), 'Bone',
                "Rigid body's orientation completely determined by attached bone", 1),
            (str(rigid_body.MODE_DYNAMIC), 'Physics',
                "Attached bone's orientation completely determined by rigid body", 2),
            (str(rigid_body.MODE_DYNAMIC_BONE), 'Physics + Bone',
                "Bone determined by combination of parent and attached rigid body", 3),
            ],
        update=_updateType,
        )

    shape = EnumProperty(
        name='Shape',
        description='Select the collision shape',
        items = [
            ('SPHERE', 'Sphere', '', 1),
            ('BOX', 'Box', '', 2),
            ('CAPSULE', 'Capsule', '', 3),
            ],
        update=_updateShape,
        )

    bone = StringProperty(
        name='Bone',
        description='Target bone',
        default='',
        get=_get_bone,
        set=_set_bone,
        )

    size = FloatVectorProperty(
        name='Size',
        description='Size of the object',
        subtype='XYZ',
        size=3,
        min=0,
        step=0.1,
        get=_get_size,
        set=_set_size,
        )


def _updateSpringLinear(prop, context):
    obj = prop.id_data
    rbc = obj.rigid_body_constraint
    if rbc:
        rbc.spring_stiffness_x = prop.spring_linear[0]
        rbc.spring_stiffness_y = prop.spring_linear[1]
        rbc.spring_stiffness_z = prop.spring_linear[2]

def _updateSpringAngular(prop, context):
    obj = prop.id_data
    rbc = obj.rigid_body_constraint
    if rbc and hasattr(rbc, 'use_spring_ang_x'):
        rbc.spring_stiffness_ang_x = prop.spring_angular[0]
        rbc.spring_stiffness_ang_y = prop.spring_angular[1]
        rbc.spring_stiffness_ang_z = prop.spring_angular[2]


@register_wrap
class MMDJoint(PropertyGroup):
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

    spring_linear = FloatVectorProperty(
        name='Spring(Linear)',
        description='Spring constant of movement',
        subtype='XYZ',
        size=3,
        min=0,
        step=0.1,
        update=_updateSpringLinear,
        )

    spring_angular = FloatVectorProperty(
        name='Spring(Angular)',
        description='Spring constant of rotation',
        subtype='XYZ',
        size=3,
        min=0,
        step=0.1,
        update=_updateSpringAngular,
        )
