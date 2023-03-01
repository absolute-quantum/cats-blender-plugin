# GPL License

# (global-set-key (kbd "C-c m") (lambda () (interactive) (shell-command "zip -r ../../cats-dev.zip ../../cats-blender-plugin")))

import bpy
import addon_utils
from importlib import import_module
from importlib.util import find_spec

from .main import ToolPanel
from ..tools import scale as Scaler

from ..tools.translations import t
from ..tools.register import register_wrap

draw_imscale_ui = None
imscale_is_disabled = False
old_imscale_version = False

def check_for_imscale():
    global draw_imscale_ui, old_imscale_version, imscale_is_disabled

    draw_imscale_ui = None

    # Check if using immersive scaler shipped with cats
    if find_spec("imscale") and find_spec("imscale.immersive_scaler"):
        import imscale.immersive_scaler as imscale
        draw_imscale_ui = imscale.ui.draw_ui
        return

    # Check if it's present in blender anyway (installed separately)
    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Immersive Scaler":
            # print(mod.__name__, mod.bl_info['version'])
            # print(addon_utils.check(mod.__name__))
            if mod.bl_info['version'] < (0, 2, 7):
                old_imscale_version = True
                # print('TOO OLD!')
                continue
            if not addon_utils.check(mod.__name__)[0]:
                imscale_is_disabled = True
                # print('DISABLED!')
                continue

            # print('FOUND!')
            old_imscale_version = False
            imscale_is_disabled = False
            draw_imscale_ui = getattr(import_module(mod.__name__ + '.ui'), 'draw_ui')

            break

@register_wrap
class ScalingPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_scale_v2'
    bl_label = t('ScalingPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator(Scaler.ImmersiveScalerHelpButton.bl_idname, icon='QUESTION')

        # Installed but disabled
        if imscale_is_disabled:
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)

            row.scale_y = 0.75
            row.label(text=t('ScalingPanel.imscaleDisabled1'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ScalingPanel.imscaleDisabled2'))
            col.separator()
            row = col.row(align=True)
            row.operator(Scaler.EnableIMScale.bl_idname, icon='CHECKBOX_HLT')
            check_for_imscale()
            return None

        # Currently, instructions for an old version are the same as
        # it not being installed - a manual install either way.
        if old_imscale_version:
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)

            row.scale_y = 0.75
            row.label(text=t('ScalingPanel.imscaleOldVersion1'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ScalingPanel.imscaleNotInstalled2'))
            col.separator()
            row = col.row(align=True)
            row.operator(Scaler.ImmersiveScalerButton.bl_idname, icon='CHECKBOX_HLT')

            check_for_imscale()
            return None

        # Imscale is not found
        if not draw_imscale_ui:
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)

            row.scale_y = 0.75
            row.label(text=t('ScalingPanel.imscaleNotInstalled1'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ScalingPanel.imscaleNotInstalled2'))
            col.separator()
            row = col.row(align=True)
            row.operator(Scaler.ImmersiveScalerButton.bl_idname, icon='CHECKBOX_HLT')
            check_for_imscale()
            return None

            check_for_imscale()
            return None


        # imscale = __import__('immersive_scaler')
        return draw_imscale_ui(context, layout)
