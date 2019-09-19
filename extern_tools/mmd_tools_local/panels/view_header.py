# -*- coding: utf-8 -*-

from bpy.types import Header

from mmd_tools_local import register_wrap

#@register_wrap # use draw function instead
class MMDViewHeader(Header):
    bl_idname = 'MMD_TOOLS_HT_view_header'
    bl_space_type = 'VIEW_3D'

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                context.active_object.type == 'ARMATURE' and
                context.active_object.mode == 'POSE')

    def draw(self, context):
        if self.poll(context):
            self.layout.operator('mmd_tools.flip_pose', text='', icon='ARROW_LEFTRIGHT')
