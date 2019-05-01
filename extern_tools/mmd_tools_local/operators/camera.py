# -*- coding: utf-8 -*-

from bpy.props import FloatProperty
from bpy.props import BoolProperty
from bpy.props import EnumProperty
from bpy.types import Operator

from mmd_tools_local import register_wrap
from mmd_tools_local.core.camera import MMDCamera

@register_wrap
class ConvertToMMDCamera(Operator):
    bl_idname = 'mmd_tools.convert_to_mmd_camera'
    bl_label = 'Convert to MMD Camera'
    bl_description = 'Create a camera rig for MMD'
    bl_options = {'REGISTER', 'UNDO'}

    scale = FloatProperty(
        name='Scale',
        description='Scaling factor for initializing the camera',
        default=1.0,
        )

    bake_animation = BoolProperty(
        name='Bake Animation',
        description='Bake camera animation to a new MMD camera rig',
        default=False,
        options={'SKIP_SAVE'},
        )

    camera_source = EnumProperty(
        name='Camera Source',
        description='Select camera source to bake animation (camera target is the selected or DoF object)',
        items = [
            ('CURRENT', 'Current', 'Current active camera object', 0),
            ('SCENE', 'Scene', 'Scene camera object', 1),
            ],
        default='CURRENT',
        )

    min_distance = FloatProperty(
        name='Min Distance',
        description='Minimum distance to camera target when baking animation',
        default=0.1,
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
            from mmd_tools_local.bpyutils import SceneOp
            obj = context.active_object
            targets = [x for x in context.selected_objects if x != obj]
            target = targets[0] if len(targets) == 1 else None
            if self.camera_source == 'SCENE':
                obj = None
            camera = MMDCamera.newMMDCameraAnimation(obj, target, self.scale, self.min_distance).camera()
            camera.select = True
            SceneOp(context).active_object = camera
        else:
            MMDCamera.convertToMMDCamera(context.active_object, self.scale)
        return {'FINISHED'}
