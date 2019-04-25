# -*- coding: utf-8 -*-

import math

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatProperty, BoolProperty

from .. import register_wrap
from .. core import camera as mmd_camera

if bpy.app.version < (2, 80, 0):
    def __update_depsgraph(cam, data_prop_name):
        pass
else:
    def __update_depsgraph(cam, data_prop_name):
        cam_dep = bpy.context.depsgraph.objects.get(cam.name, None)
        if cam_dep:
            setattr(cam_dep.data, data_prop_name, getattr(cam.data, data_prop_name))

def _getMMDCameraAngle(prop):
    empty = prop.id_data
    cam = mmd_camera.MMDCamera(empty).camera()
    return math.atan(cam.data.sensor_height/cam.data.lens/2) * 2

def _setMMDCameraAngle(prop, value):
    empty = prop.id_data
    cam = mmd_camera.MMDCamera(empty).camera()
    cam.data.lens = cam.data.sensor_height/math.tan(value/2)/2
    __update_depsgraph(cam, 'lens')

def _getIsPerspective(prop):
    empty = prop.id_data
    cam = mmd_camera.MMDCamera(empty).camera()
    return cam.data.type == 'PERSP'

def _setIsPerspective(prop, value):
    empty = prop.id_data
    cam = mmd_camera.MMDCamera(empty).camera()
    cam.data.type = 'PERSP' if value else 'ORTHO'
    __update_depsgraph(cam, 'type')


@register_wrap
class MMDCamera(PropertyGroup):
    angle = FloatProperty(
        name='Angle',
        description='Camera lens field of view',
        subtype='ANGLE',
        get=_getMMDCameraAngle,
        set=_setMMDCameraAngle,
        min=0.1,
        max=math.radians(180),
        step=0.1,
        )

    is_perspective = BoolProperty(
        name='Perspective',
        description='Is perspective',
        default=True,
        get=_getIsPerspective,
        set=_setIsPerspective,
        )
