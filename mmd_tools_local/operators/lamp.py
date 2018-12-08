# -*- coding: utf-8 -*-

from bpy.props import FloatProperty
from bpy.types import Operator

from mmd_tools_local import register_wrap
from mmd_tools_local.core.lamp import MMDLamp

@register_wrap
class ConvertToMMDLamp(Operator):
    bl_idname = 'mmd_tools.convert_to_mmd_lamp'
    bl_label = 'Convert to MMD Lamp'
    bl_description = 'Create a lamp rig for MMD'
    bl_options = {'REGISTER', 'UNDO'}

    scale = FloatProperty(
        name='Scale',
        description='Scaling factor for initializing the lamp',
        default=1.0,
        )

    @classmethod
    def poll(cls, context):
        return MMDLamp.isLamp(context.active_object)

    def invoke(self, context, event):
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

    def execute(self, context):
        MMDLamp.convertToMMDLamp(context.active_object, self.scale)
        return {'FINISHED'}
