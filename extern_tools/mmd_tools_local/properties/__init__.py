# -*- coding: utf-8 -*-

if "bpy" in locals():
    if bpy.app.version < (2, 71, 0):
        import imp as importlib
    else:
        import importlib
    importlib.reload(morph)
    importlib.reload(root)
    importlib.reload(camera)
    importlib.reload(material)
    importlib.reload(bone)
    importlib.reload(rigid_body)
else:
    import bpy
    from . import (
        morph,
        root,
        camera,
        material,
        bone,
        rigid_body,
        )

__properties = {
    bpy.types.Object: {
        'mmd_type': bpy.props.EnumProperty(
            name='Type',
            description='Internal MMD type of this object (DO NOT CHANGE IT DIRECTLY)',
            default='NONE',
            items=[
                ('NONE', 'None', '', 1),
                ('ROOT', 'Root', '', 2),
                ('RIGID_GRP_OBJ', 'Rigid Body Grp Empty', '', 3),
                ('JOINT_GRP_OBJ', 'Joint Grp Empty', '', 4),
                ('TEMPORARY_GRP_OBJ', 'Temporary Grp Empty', '', 5),
                ('PLACEHOLDER', 'Place Holder', '', 6),

                ('CAMERA', 'Camera', '', 21),
                ('JOINT', 'Joint', '', 22),
                ('RIGID_BODY', 'Rigid body', '', 23),
                ('LIGHT', 'Light', '', 24),

                ('TRACK_TARGET', 'Track Target', '', 51),
                ('NON_COLLISION_CONSTRAINT', 'Non Collision Constraint', '', 52),
                ('SPRING_CONSTRAINT', 'Spring Constraint', '', 53),
                ('SPRING_GOAL', 'Spring Goal', '', 54),
                ]
            ),
        'mmd_root': bpy.props.PointerProperty(type=root.MMDRoot),
        'mmd_camera': bpy.props.PointerProperty(type=camera.MMDCamera),
        'mmd_rigid': bpy.props.PointerProperty(type=rigid_body.MMDRigidBody),
        'mmd_joint': bpy.props.PointerProperty(type=rigid_body.MMDJoint),
        'is_mmd_glsl_light': bpy.props.BoolProperty(name='is_mmd_glsl_light', default=False),
        },
    bpy.types.Material: {
        'mmd_material': bpy.props.PointerProperty(type=material.MMDMaterial),
        },
    bpy.types.PoseBone: {
        'mmd_bone': bpy.props.PointerProperty(type=bone.MMDBone),
        'is_mmd_shadow_bone': bpy.props.BoolProperty(name='is_mmd_shadow_bone', default=False),
        'mmd_shadow_bone_type': bpy.props.StringProperty(name='mmd_shadow_bone_type'),
        'mmd_ik_toggle': bone._MMDPoseBoneProp.mmd_ik_toggle,
        }
    }

def __patch(properties): # temporary patching, should be removed in the future
    prop_obj = properties.setdefault(bpy.types.Object, {})
    prop_arm = properties.setdefault(bpy.types.Armature, {})
    prop_cam = properties.setdefault(bpy.types.Camera, {})

    prop_obj['select'] = bpy.props.BoolProperty(
        get=lambda prop: prop.select_get(),
        set=lambda prop, value: prop.select_set(value),
        )
    prop_obj['hide'] = bpy.props.BoolProperty(
        get=lambda prop: prop.hide_get(),
        set=lambda prop, value: prop.hide_set(value) or setattr(prop, 'hide_viewport', False),
        )
    prop_obj['show_x_ray'] = bpy.props.BoolProperty(
        get=lambda prop: prop.show_in_front,
        set=lambda prop, value: setattr(prop, 'show_in_front', value),
        )
    prop_obj['empty_draw_size'] = bpy.props.FloatProperty(
        get=lambda prop: prop.empty_display_size,
        set=lambda prop, value: setattr(prop, 'empty_display_size', value),
        )
    prop_obj['empty_draw_type'] = bpy.props.StringProperty(
        get=lambda prop: prop.empty_display_type,
        set=lambda prop, value: setattr(prop, 'empty_display_type', value),
        )
    prop_obj['draw_type'] = bpy.props.StringProperty(
        get=lambda prop: prop.display_type,
        set=lambda prop, value: setattr(prop, 'display_type', value),
        )
    prop_arm['draw_type'] = bpy.props.StringProperty(
        get=lambda prop: prop.display_type,
        set=lambda prop, value: setattr(prop, 'display_type', value),
        )
    prop_cam['draw_size'] = bpy.props.FloatProperty(
        get=lambda prop: prop.display_size,
        set=lambda prop, value: setattr(prop, 'display_size', value),
        )

if bpy.app.version >= (2, 80, 0):
    __patch(__properties)

def register():
    for typ, t in __properties.items():
        for attr, prop in t.items():
            if hasattr(typ, attr):
                print(' * warning: overwrite ', typ, attr)
            setattr(typ, attr, prop)

def unregister():
    for typ, t in __properties.items():
        for attr in t.keys():
            if hasattr(typ, attr):
                delattr(typ, attr)
