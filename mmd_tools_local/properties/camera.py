# -*- coding: utf-8 -*-

import math

from bpy.types import PropertyGroup
from bpy.props import FloatProperty, BoolProperty

import mmd_tools_local.core.camera as mmd_camera


def _getMMDCameraAngle(prop):
    empty = prop.id_data
    cam = mmd_camera.MMDCamera(empty).camera()
    return math.atan(cam.data.sensor_height/cam.data.lens/2) * 2

def _setMMDCameraAngle(prop, value):
    empty = prop.id_data
    cam = mmd_camera.MMDCamera(empty).camera()
    cam.data.lens = cam.data.sensor_height/math.tan(value/2)/2

def _getIsPerspective(prop):
    empty = prop.id_data
    cam = mmd_camera.MMDCamera(empty).camera()
    return cam.data.type == 'PERSP'

def _setIsPerspective(prop, value):
    empty = prop.id_data
    cam = mmd_camera.MMDCamera(empty).camera()
    cam.data.type = 'PERSP' if value else 'ORTHO'


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
