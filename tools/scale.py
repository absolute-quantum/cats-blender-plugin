# GPL License

###
# Rather than being a full implementation, this links pulls from
# immersive scaler upstream so that updates are simply worked in.
#
# Code largely taken from the material combiner integration.
##

import bpy
import webbrowser
import addon_utils

from . import common as Common
from .register import register_wrap
from .translations import t

# Operator to enable the immersive scaler after it's installed
@register_wrap
class EnableIMScale(bpy.types.Operator):
    bl_idname = 'cats_scale.enable_imscale'
    bl_label = t('EnableIMScale.label')
    bl_description = t('EnableIMScale.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        # disable all wrong versions
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == "Immersive Scaler":
                if mod.bl_info['version'] < (0, 2, 7) and addon_utils.check(mod.__name__)[0]:
                    try:
                        if Common.version_2_79_or_older():
                            bpy.ops.wm.addon_disable(module=mod.__name__)
                        else:
                            bpy.ops.preferences.addon_disable(module=mod.__name__)
                    except:
                        pass
                    continue

        # then enable correct version
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == "Immersive Scaler":
                if mod.bl_info['version'] < (0, 2, 7):
                    continue
                if not addon_utils.check(mod.__name__)[0]:
                    if Common.version_2_79_or_older():
                        bpy.ops.wm.addon_enable(module=mod.__name__)
                    else:
                        bpy.ops.preferences.addon_enable(module=mod.__name__)
                    break
        self.report({'INFO'}, t('EnableIMScale.success'))
        return {'FINISHED'}


# Link to install
@register_wrap
class ImmersiveScalerButton(bpy.types.Operator):
    bl_idname = 'imscale.download_immersive_scaler'
    bl_label = t('ImmersiveScalerButton.label')
    bl_description = t('ImmersiveScalerButton.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://github.com/triazo/immersive_scaler/releases/latest')

        self.report({'INFO'}, 'ImmersiveScalerButton.success')
        return {'FINISHED'}

# Link to readme for help
@register_wrap
class ImmersiveScalerHelpButton(bpy.types.Operator):
    bl_idname = 'imscale.help'
    bl_label = t('ImmersiveScalerHelpButton.label')
    bl_description = t('ImmersiveScalerHelpButton.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('ImmersiveScalerHelpButton.URL'))

        self.report({'INFO'}, t('ImmersiveScalerHelpButton.success'))
        return {'FINISHED'}
