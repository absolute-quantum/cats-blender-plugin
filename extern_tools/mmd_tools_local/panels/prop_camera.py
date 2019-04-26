# -*- coding: utf-8 -*-

from bpy.types import Panel

from mmd_tools_local import register_wrap
from mmd_tools_local.core.camera import MMDCamera

@register_wrap
class MMDCameraPanel(Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_camera'
    bl_label = 'MMD Camera Tools'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and (obj.type == 'CAMERA' or MMDCamera.isMMDCamera(obj))

    def draw(self, context):
        obj = context.active_object

        layout = self.layout

        if MMDCamera.isMMDCamera(obj):
            mmd_cam = MMDCamera(obj)
            empty = mmd_cam.object()
            camera = mmd_cam.camera()

            row = layout.row()

            c = row.column()
            c.prop(empty, 'location')
            c.prop(camera, 'location', index=1, text='Distance')

            c = row.column()
            c.prop(empty, 'rotation_euler')

            layout.prop(empty.mmd_camera, 'angle')
            layout.prop(empty.mmd_camera, 'is_perspective')
        else:
            layout.operator('mmd_tools.convert_to_mmd_camera', text='Convert')
