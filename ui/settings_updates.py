import bpy
import globs
import tools.common
import tools.supporter
import addon_updater_ops

from ui.main import ToolPanel
from ui.main import get_emtpy_icon

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
        row.operator('settings.reset_google_dict', icon='X')
        if globs.dev_branch:
            row = col.row(align=True)
            row.scale_y = 0.8
            row.operator('settings.debug_translations', icon='X')

        if tools.settings.settings_changed():
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.8
            row.label(text='Restart required.', icon='ERROR')
            row = col.row(align=True)
            row.scale_y = 0.8
            row.label(text='Some changes require a Blender restart.', icon_value=get_emtpy_icon())
            row = col.row(align=True)
            row.operator('settings.revert', icon='RECOVER_LAST')

        # Updater
        # addon_updater_ops.check_for_update_background()
        addon_updater_ops.update_settings_ui(self, context)
