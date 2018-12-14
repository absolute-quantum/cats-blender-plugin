import bpy
import globs
import updater
import tools.common
import tools.supporter

from ui.main import ToolPanel
from ui.main import get_emtpy_icon

from tools import settings

from tools.register import register_wrap


@register_wrap
class UpdaterPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_updater_v3'
    bl_label = 'Settings & Updates'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.scale_y = 0.8
        row.label(text='Settings:', icon=globs.ICON_SETTINGS)
        col.separator()

        row = col.row(align=True)
        row.prop(context.scene, 'embed_textures')
        # row = col.row(align=True)
        # row.prop(context.scene, 'use_custom_mmd_tools')
        # row = col.row(align=True)
        # row.prop(context.scene, 'disable_vrchat_features')
        row = col.row(align=True)
        row.scale_y = 0.8
        row.operator(settings.ResetGoogleDictButton.bl_idname, icon='X')
        if globs.dev_branch:
            row = col.row(align=True)
            row.scale_y = 0.8
            row.operator(settings.DebugTranslations.bl_idname, icon='X')

        if tools.settings.settings_changed():
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.8
            row.label(text='Restart required.', icon='ERROR')
            row = col.row(align=True)
            row.scale_y = 0.8
            row.label(text='Some changes require a Blender restart.', icon_value=get_emtpy_icon())
            row = col.row(align=True)
            row.operator(settings.RevertChangesButton.bl_idname, icon='RECOVER_LAST')

        updater.draw_updater_panel(context, layout)
