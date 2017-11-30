# -*- coding: utf-8 -*-

from bpy.props import FloatProperty
from bpy.props import BoolProperty
from bpy.types import Operator

from mmd_tools_local.core.camera import MMDCamera

class ConvertToMMDCamera(Operator):
    bl_idname = 'mmd_tools.convert_to_mmd_camera'
    bl_label = 'Convert to MMD Camera'
    bl_description = 'Create a camera rig for MMD'

    scale = FloatProperty(
        name='Scale',
        description='Scaling factor for initializing the camera',
        default=1.0,
        )

    bake_animation = BoolProperty(
        name='Bake Animation',
        description='Bake the animation of active camera (with a selected target) to a new MMD camera rig',
        default=False,
        options={'SKIP_SAVE'},
        )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'CAMERA'

    def invoke(self, context, event):
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

    def execute(self, context):
        if self.bake_animation:
            obj = context.active_object
            target = None
            if len(context.selected_objects) == 2 and obj in context.selected_objects:
                target = context.selected_objects[0]
                if target == obj:
                    target = context.selected_objects[1]
            elif len(context.selected_objects) == 1 and obj not in context.selected_objects:
                target = context.selected_objects[0]
            MMDCamera.newMMDCameraAnimation(obj, target, self.scale)
        else:
            MMDCamera.convertToMMDCamera(context.active_object, self.scale)
        return {'FINISHED'}
