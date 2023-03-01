# GPL License

import bpy

from .. import globs
from .main import ToolPanel
from ..tools import common as Common
from ..tools import eyetracking as Eyetracking
from ..tools.register import register_wrap
from ..tools.translations import t


@register_wrap
class SearchMenuOperatorBoneHead(bpy.types.Operator):
    bl_description = t('Scene.head.desc')
    bl_idname = "scene.search_menu_head"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name="shapekeys", items=Common.get_bones_head)

    def execute(self, context):
        context.scene.head = self.my_enum
        print(context.scene.head)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorBoneEyeLeft(bpy.types.Operator):
    bl_description = t('Scene.eye_left.desc')
    bl_idname = "scene.search_menu_eye_left"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name="shapekeys", items=Common.get_bones_eye_l)

    def execute(self, context):
        context.scene.eye_left = self.my_enum
        print(context.scene.eye_left)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorBoneEyeRight(bpy.types.Operator):
    bl_description = t('Scene.eye_right.desc')
    bl_idname = "scene.search_menu_eye_right"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name="shapekeys", items=Common.get_bones_eye_r)

    def execute(self, context):
        context.scene.eye_right = self.my_enum
        print(context.scene.eye_right)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorShapekeyWinkLeft(bpy.types.Operator):
    bl_description = t('Scene.wink_left.desc')
    bl_idname = "scene.search_menu_wink_left"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name="shapekeys", items=Common.get_shapekeys_eye_blink_l)

    def execute(self, context):
        context.scene.wink_left = self.my_enum
        print(context.scene.wink_left)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorShapekeyWinkRight(bpy.types.Operator):
    bl_description = t('Scene.wink_right.desc')
    bl_idname = "scene.search_menu_wink_right"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name="shapekeys", items=Common.get_shapekeys_eye_blink_r)

    def execute(self, context):
        context.scene.wink_right = self.my_enum
        print(context.scene.wink_right)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorShapekeyLowerLidLeft(bpy.types.Operator):
    bl_description = t('Scene.lowerlid_left.desc')
    bl_idname = "scene.search_menu_lowerlid_left"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name="shapekeys", items=Common.get_shapekeys_eye_low_l)

    def execute(self, context):
        context.scene.lowerlid_left = self.my_enum
        print(context.scene.lowerlid_left)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperatorShapekeyLowerLidRight(bpy.types.Operator):
    bl_description = t('Scene.lowerlid_right.desc')
    bl_idname = "scene.search_menu_lowerlid_right"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name="shapekeys", items=Common.get_shapekeys_eye_low_r)

    def execute(self, context):
        context.scene.lowerlid_right = self.my_enum
        print(context.scene.lowerlid_right)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class EyeTrackingPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_eye_v3'
    bl_label = t('EyeTrackingPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.scene.show_avatar_2_tabs

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.label(text="No longer neccesary for Avatars 3.0!", icon='INFO')

        row = col.row(align=True)
        row.prop(context.scene, 'eye_mode', expand=True)

        if context.scene.eye_mode == 'CREATION':

            mesh_count = len(Common.get_meshes_objects(check=False))
            if mesh_count == 0:
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.1
                row.label(text=t('EyeTrackingPanel.error.noMesh'), icon='ERROR')
            elif mesh_count > 1:
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.1
                row.prop(context.scene, 'mesh_name_eye', icon='MESH_DATA')

            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.label(text=t('Scene.head.label')+":")
            row.operator(SearchMenuOperatorBoneHead.bl_idname, text = context.scene.head, icon='BONE_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_movement:
                row.active = False
            row.label(text=t('Scene.eye_left.label')+":")
            row.operator(SearchMenuOperatorBoneEyeLeft.bl_idname, text = context.scene.eye_left, icon='BONE_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_movement:
                row.active = False
            row.label(text=t('Scene.eye_right.label')+":")
            row.operator(SearchMenuOperatorBoneEyeRight.bl_idname, text = context.scene.eye_right, icon='BONE_DATA')

            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_blinking:
                row.active = False
            row.label(text=t('Scene.wink_left.label')+":")
            row.operator(SearchMenuOperatorShapekeyWinkLeft.bl_idname, text = context.scene.wink_left, icon='SHAPEKEY_DATA')
            #row.prop(context.scene, 'wink_left', icon='SHAPEKEY_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_blinking:
                row.active = False
            row.label(text=t('Scene.wink_right.label')+":")
            row.operator(SearchMenuOperatorShapekeyWinkRight.bl_idname, text = context.scene.wink_right, icon='SHAPEKEY_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_blinking:
                row.active = False
            row.label(text=t('Scene.lowerlid_left.label')+":")
            row.operator(SearchMenuOperatorShapekeyLowerLidLeft.bl_idname, text = context.scene.lowerlid_left, icon='SHAPEKEY_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_blinking:
                row.active = False
            row.label(text=t('Scene.lowerlid_right.label')+":")
            row.operator(SearchMenuOperatorShapekeyLowerLidRight.bl_idname, text = context.scene.lowerlid_right, icon='SHAPEKEY_DATA')

            col.separator()
            row = col.row(align=True)
            row.prop(context.scene, 'disable_eye_blinking')

            row = col.row(align=True)
            row.prop(context.scene, 'disable_eye_movement')

            if not context.scene.disable_eye_movement:
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_distance')

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
                box.label(text=t('EyeTrackingPanel.error.noArm'), icon='ERROR')
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

                # global slider_z
                # if context.scene.eye_blink_shape != slider_z:
                #     slider_z = context.scene.eye_blink_shape
                #     Eyetracking.update_bones(context, slider_z)

                col.separator()
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_distance')
                row = col.row(align=True)
                row.operator(Eyetracking.AdjustEyesButton.bl_idname, icon='CURVE_NCIRCLE')

                col.separator()
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_blink_shape')
                row.operator(Eyetracking.TestBlinking.bl_idname, icon='RESTRICT_VIEW_OFF')
                row = col.row(align=True)
                row.prop(context.scene, 'eye_lowerlid_shape')
                row.operator(Eyetracking.TestLowerlid.bl_idname, icon='RESTRICT_VIEW_OFF')
                row = col.row(align=True)
                row.operator(Eyetracking.ResetBlinkTest.bl_idname, icon='FILE_REFRESH')

                if armature.name != 'Armature':
                    col.separator()
                    col.separator()
                    col.separator()
                    row = col.row(align=True)
                    row.scale_y = 0.3
                    row.label(text=t('EyeTrackingPanel.error.wrongNameArm1'), icon='ERROR')
                    row = col.row(align=True)
                    row.label(text=t('EyeTrackingPanel.error.wrongNameArm2'))
                    row = col.row(align=True)
                    row.scale_y = 0.3
                    row.label(text=t('EyeTrackingPanel.error.wrongNameArm3') + armature.name + "')")

                if context.scene.mesh_name_eye != 'Body':
                    col.separator()
                    col.separator()
                    col.separator()
                    row = col.row(align=True)
                    row.scale_y = 0.3
                    row.label(text=t('EyeTrackingPanel.error.wrongNameBody1'), icon='ERROR')
                    row = col.row(align=True)
                    row.label(text=t('EyeTrackingPanel.error.wrongNameBody2'))
                    row = col.row(align=True)
                    row.scale_y = 0.3
                    row.label(text=t('EyeTrackingPanel.error.wrongNameBody3') + context.scene.mesh_name_eye + "')")

                col.separator()
                col.separator()
                col.separator()
                row = col.row(align=True)
                row.scale_y = 0.3
                row.label(text=t('EyeTrackingPanel.warn.assignEyes1'), icon='INFO')
                row = col.row(align=True)
                row.label(text=t('EyeTrackingPanel.warn.assignEyes2'))

                row = col.row(align=True)
                row.scale_y = 1.5
                row.operator(Eyetracking.StopTestingButton.bl_idname, icon='PAUSE')
