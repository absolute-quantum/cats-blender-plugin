# -*- coding: utf-8 -*-

import bpy

def setupFrameRanges():
    s, e = 1, 1
    for i in bpy.data.actions:
        ts, te = i.frame_range
        s = min(s, ts)
        e = max(e, te)
    bpy.context.scene.frame_start = int(s)
    bpy.context.scene.frame_end = int(e)
    if bpy.context.scene.rigidbody_world is not None:
        bpy.context.scene.rigidbody_world.point_cache.frame_start = int(s)
        bpy.context.scene.rigidbody_world.point_cache.frame_end = int(e)

def setupLighting():
    bpy.context.scene.world.light_settings.use_ambient_occlusion = True
    bpy.context.scene.world.light_settings.use_environment_light = True
    bpy.context.scene.world.light_settings.use_indirect_light = True

def setupFps():
    bpy.context.scene.render.fps = 30
    bpy.context.scene.render.fps_base = 1
