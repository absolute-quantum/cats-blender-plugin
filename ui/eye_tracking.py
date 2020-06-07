import bpy

from .. import globs
from .main import ToolPanel
from ..tools import common as Common
from ..tools import eyetracking as Eyetracking
from ..tools.register import register_wrap


@register_wrap
class EyeTrackingPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_eye_v3'
    bl_label = 'Eye Tracking'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'eye_mode', expand=True)

        if context.scene.eye_mode == 'CREATION':

            mesh_count = len(Common.get_meshes_objects(check=False))
            if mesh_count == 0:
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.1
                row.label(text='No meshes found!', icon='ERROR')
            elif mesh_count > 1:
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.1
                row.prop(context.scene, 'mesh_name_eye', icon='MESH_DATA')

            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'eye_left', icon='BONE_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'eye_right', icon='BONE_DATA')

            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'wink_left', icon='SHAPEKEY_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'wink_right', icon='SHAPEKEY_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'upperlid_up', icon='SHAPEKEY_DATA')

            col = box.column(align=True)
            row = col.row(align=True)
            row.operator(Eyetracking.CreateEyesButton.bl_idname, icon='TRIA_RIGHT')

            # armature = common.get_armature()
            # if "RightEye" in armature.pose.bones:
            #     row = col.row(align=True)
            #     row.label(text='Eye Bone Tweaking:')
        else:
            armature = Common.get_armature()
            if not armature:
                box.label(text='No model found!', icon='ERROR')
                return

            if bpy.context.active_object is not None and bpy.context.active_object.mode != 'POSE':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.5
                row.operator(Eyetracking.StartTestingButton.bl_idname, icon='TRIA_RIGHT')
            else:
                # col.separator()
                # row = col.row(align=True)
                # row.operator('eyes.test_stop', icon='PAUSE')

                col.separator()
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_rotation_x', icon='FILE_PARENT')
                row = col.row(align=True)
                row.prop(context.scene, 'eye_rotation_y', icon='ARROW_LEFTRIGHT')
                row = col.row(align=True)
                row.operator(Eyetracking.ResetRotationButton.bl_idname, icon=globs.ICON_EYE_ROTATION)

                col.separator()
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_blink_shape')
                row.operator(Eyetracking.TestBlinking.bl_idname, icon='RESTRICT_VIEW_OFF')
                # row = col.row(align=True)
                # row.prop(context.scene, 'eye_loop_up_shape')
                # row.operator(Eyetracking.TestLowerlid.bl_idname, icon='RESTRICT_VIEW_OFF')
                # row = col.row(align=True)
                # row.prop(context.scene, 'eye_loop_down_shape')
                # row.operator(Eyetracking.TestLowerlid.bl_idname, icon='RESTRICT_VIEW_OFF')
                row = col.row(align=True)
                row.operator(Eyetracking.ResetBlinkTest.bl_idname, icon='FILE_REFRESH')

                # col.separator()
                # col.separator()
                # col.separator()
                # row = col.row(align=True)
                # row.scale_y = 0.3
                # row.label(text="Don't forget to assign 'LeftEye' and 'RightEye'", icon='INFO')
                # row = col.row(align=True)
                # row.label(text="      to the eyes in Unity!")

                col.separator()
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.5
                row.operator(Eyetracking.StopTestingButton.bl_idname, icon='PAUSE')
