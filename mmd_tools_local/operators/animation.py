# -*- coding: utf-8 -*-

from bpy.types import Operator
from mmd_tools_local import auto_scene_setup

class SetFrameRange(Operator):
    bl_idname = 'mmd_tools.set_frame_range'
    bl_label = 'Set range'
    bl_description = 'Set the frame range to best values to play the animation from start to finish. And set the frame rate to 30.0.'
    bl_options = {'PRESET'}

    def execute(self, context):
        auto_scene_setup.setupFrameRanges()
        auto_scene_setup.setupFps()
        return {'FINISHED'}
