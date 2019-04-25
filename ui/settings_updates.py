import bpy

from .. import globs
from .. import updater
from .main import ToolPanel
from ..tools import settings as Settings
from ..tools.register import register_wrap


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
        row.operator(Settings.ResetGoogleDictButton.bl_idname, icon='X')
        if globs.dev_branch:
            row = col.row(align=True)
            row.scale_y = 0.8
            row.operator(Settings.DebugTranslations.bl_idname, icon='X')

        if Settings.settings_changed():
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.8
            row.label(text='Restart required.', icon='ERROR')
            row = col.row(align=True)
            row.scale_y = 0.8
            row.label(text='Some changes require a Blender restart.', icon='BLANK1')
            row = col.row(align=True)
            row.operator(Settings.RevertChangesButton.bl_idname, icon='RECOVER_LAST')

        col.separator()
        updater.draw_updater_panel(context, box)
