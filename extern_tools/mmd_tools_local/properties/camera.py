# -*- coding: utf-8 -*-

import math

import bpy
from bpy.types import PropertyGroup
from bpy.props import FloatProperty, BoolProperty

from mmd_tools_local import register_wrap
import mmd_tools_local.core.camera as mmd_camera


if bpy.app.version < (2, 80, 0):
    def __get_camera(empty):
        return mmd_camera.MMDCamera(empty).camera()
else:
    def __get_camera(empty):
        cam = mmd_camera.MMDCamera(empty).camera()
        if empty.is_evaluated:
            depsgraph = __find_depsgraph(empty)
            return cam.evaluated_get(depsgraph) if depsgraph else cam
        return cam

    def __find_depsgraph(obj):
        depsgraph = bpy.context.view_layer.depsgraph
        if obj == depsgraph.objects.get(obj.name):
            return depsgraph
        for view_layer in (l for s in bpy.data.scenes for l in s.view_layers):
            if obj == view_layer.depsgraph.objects.get(obj.name):
                return view_layer.depsgraph
        return None


def _getMMDCameraAngle(prop):
    if not mmd_camera.MMDCamera.isMMDCamera(prop.id_data):
        return 0
    cam = __get_camera(prop.id_data)
    return math.atan(cam.data.sensor_height/cam.data.lens/2) * 2

def _setMMDCameraAngle(prop, value):
    cam = __get_camera(prop.id_data)
    cam.data.lens = cam.data.sensor_height/math.tan(value/2)/2

def _getIsPerspective(prop):
    if not mmd_camera.MMDCamera.isMMDCamera(prop.id_data):
        return False
    cam = __get_camera(prop.id_data)
    return cam.data.type == 'PERSP'

def _setIsPerspective(prop, value):
    cam = __get_camera(prop.id_data)
    cam.data.type = 'PERSP' if value else 'ORTHO'


@register_wrap
class MMDCamera(PropertyGroup):
    angle = FloatProperty(
        name='Angle',
        description='Camera lens field of view',
        subtype='ANGLE',
        get=_getMMDCameraAngle,
        set=_setMMDCameraAngle,
        min=math.radians(1),
        max=math.radians(180),
        soft_max=math.radians(125),
        step=100.0,
        )

    is_perspective = BoolProperty(
        name='Perspective',
        description='Is perspective',
        default=True,
        get=_getIsPerspective,
        set=_setIsPerspective,
        )
