import bpy

from .. import globs
from .. import updater
from .main import ToolPanel
from ..tools import common as Common
from ..tools import armature as Armature
from ..tools import importer as Importer
from ..tools import supporter as Supporter
from ..tools import eyetracking as Eyetracking
from ..tools import armature_manual as Armature_manual
from ..tools.register import register_wrap
from ..tools.translations import t


@register_wrap
class ArmaturePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_armature_v3'
    bl_label = t('ArmaturePanel.label')

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        updater.check_for_update_background(check_on_startup=True)
        updater.draw_update_notification_panel(box)

        col = box.column(align=True)

        if bpy.app.version < (2, 79, 0):
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ArmaturePanel.warn.oldBlender1'), icon='ERROR')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ArmaturePanel.warn.oldBlender2'), icon='BLANK1')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ArmaturePanel.warn.oldBlender3'), icon='BLANK1')
            col.separator()
            col.separator()

        # if addon_updater_ops.updater.update_ready:  # TODO
        #     col.separator()
        #     row = col.row(align=True)
        #     row.scale_y = 0.75
        #     row.label(text='New Cats version available!', icon='INFO')
        #     row = col.row(align=True)
        #     row.scale_y = 0.75
        #     row.label(text='Check the Updater panel!', icon='BLANK1')
        #     col.separator()
        #     col.separator()

        if not globs.dict_found:
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ArmaturePanel.warn.noDict1'), icon='INFO')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ArmaturePanel.warn.noDict2'), icon='BLANK1')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ArmaturePanel.warn.noDict3'), icon='BLANK1')
            col.separator()
            col.separator()

        # Show news from the plugin
        if Supporter.supporter_data and Supporter.supporter_data.get('news') and Supporter.supporter_data.get('news'):
            showed_info = False
            for i, news in enumerate(Supporter.supporter_data.get('news')):
                info = news.get('info')
                icon = news.get('icon')
                custom_icon = news.get('custom_icon')
                if info and not news.get('disabled'):
                    showed_info = True

                    row = col.row(align=True)
                    row.scale_y = 0.75
                    if custom_icon:
                        try:
                            row.label(text=info, icon_value=Supporter.preview_collections["supporter_icons"][custom_icon].icon_id)
                        except KeyError:
                            row.label(text=info)
                    elif icon:
                        try:
                            row.label(text=info, icon=icon)
                        except TypeError:
                            row.label(text=info)
                    else:
                        row.label(text=info)
            if showed_info:
                col.separator()
                col.separator()

        # row = col.row(align=True)
        # row.prop(context.scene, 'import_mode', expand=True)
        # row = col.row(align=True)
        # row.scale_y = 1.4
        # row.operator('armature_manual.import_model', icon='ARMATURE_DATA')

        arm_count = len(Common.get_armature_objects())
        if arm_count == 0:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.7
            row.operator(Importer.ImportAnyModel.bl_idname, text=t('ArmaturePanel.ImportAnyModel.label'), icon='ARMATURE_DATA')
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 1.7
            row.operator(Importer.ModelsPopup.bl_idname, text="", icon='COLLAPSEMENU')
            return
        else:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.4
            row.operator(Importer.ImportAnyModel.bl_idname, text=t('ArmaturePanel.ImportAnyModel.label'), icon='ARMATURE_DATA')
            row.operator(Importer.ExportModel.bl_idname, icon='ARMATURE_DATA').action = 'CHECK'
            row = split.row(align=True)
            row.scale_y = 1.4
            row.operator(Importer.ModelsPopup.bl_idname, text="", icon='COLLAPSEMENU')

            # split = col.row(align=True)
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator('importer.import_any_model', text='Import Model', icon='ARMATURE_DATA')
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator("model.popup", text="", icon='COLLAPSEMENU')
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator('importer.export_model', icon='ARMATURE_DATA').action = 'CHECK'
            #
            # split = col.row(align=True)
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator("model.popup", text="", icon='COLLAPSEMENU')
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator('importer.import_any_model', text='Import Model', icon='ARMATURE_DATA')
            # row.operator('importer.export_model', icon='ARMATURE_DATA').action = 'CHECK'

        if arm_count > 1:
            col.separator()
            col.separator()
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'armature', icon='ARMATURE_DATA')

        col.separator()
        col.separator()

        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator(Armature.FixArmature.bl_idname, icon=globs.ICON_FIX_MODEL)
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.scale_y = 1.5
        row.operator(ModelSettings.bl_idname, text="", icon='MODIFIER')

        col.separator()
        col.separator()

        armature_obj = Common.get_armature()
        if not armature_obj or armature_obj.mode != 'POSE':
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.1
            row.operator(Armature_manual.StartPoseMode.bl_idname, icon='POSE_HLT')
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 1.1
            row.operator(Armature_manual.StartPoseModeNoReset.bl_idname, text="", icon='POSE_HLT')
        else:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.1
            row.operator(Armature_manual.StopPoseMode.bl_idname, icon=globs.ICON_POSE_MODE)
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 1.1
            row.operator(Armature_manual.StopPoseModeNoReset.bl_idname, text='', icon=globs.ICON_POSE_MODE)
            if not Eyetracking.eye_left:
                row = col.row(align=True)
                row.scale_y = 0.9
                row.operator(Armature_manual.PoseToShape.bl_idname, icon='SHAPEKEY_DATA')
                row = col.row(align=True)
                row.scale_y = 0.9
                row.operator(Armature_manual.PoseToRest.bl_idname, icon='POSE_HLT')


@register_wrap
class ModelSettings(bpy.types.Operator):
    bl_idname = "cats_armature.settings"
    bl_label = t('ModelSettings.label')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 3.25))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.active = context.scene.remove_zero_weight
        row.prop(context.scene, 'keep_end_bones')
        row = col.row(align=True)
        row.prop(context.scene, 'keep_upper_chest')
        row = col.row(align=True)
        row.prop(context.scene, 'keep_twist_bones')
        row = col.row(align=True)
        row.prop(context.scene, 'fix_twist_bones')
        row = col.row(align=True)
        row.prop(context.scene, 'join_meshes')
        row = col.row(align=True)
        row.prop(context.scene, 'connect_bones')
        if not Common.version_2_79_or_older():
            row = col.row(align=True)
            row.prop(context.scene, 'fix_materials')
        row = col.row(align=True)
        row.prop(context.scene, 'combine_mats')
        row = col.row(align=True)
        row.prop(context.scene, 'remove_zero_weight')
        row = col.row(align=True)
        row.prop(context.scene, 'remove_rigidbodies_joints')

        col.separator()
        row = col.row(align=True)
        row.scale_y = 0.7
        row.label(text=t('ModelSettings.warn.fbtFix1'), icon='INFO')
        row = col.row(align=True)
        row.scale_y = 0.7
        row.label(text=t('ModelSettings.warn.fbtFix2'), icon_value=Supporter.preview_collections["custom_icons"]["empty"].icon_id)
        row = col.row(align=True)
        row.scale_y = 0.7
        row.label(text=t('ModelSettings.warn.fbtFix3'), icon_value=Supporter.preview_collections["custom_icons"]["empty"].icon_id)
        col.separator()
