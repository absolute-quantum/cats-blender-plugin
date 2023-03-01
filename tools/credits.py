# GPL License

import bpy
import webbrowser
from .register import register_wrap
from .translations import t

@register_wrap
class ForumButton(bpy.types.Operator):
    bl_idname = 'cats_credits.forum'
    bl_label = t('ForumButton.label')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('ForumButton.URL'))

        self.report({'INFO'}, t('ForumButton.success'))
        return {'FINISHED'}


@register_wrap
class DiscordButton(bpy.types.Operator):
    bl_idname = 'cats_credits.discord'
    bl_label = t('DiscordButton.label')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('DiscordButton.URL'))

        self.report({'INFO'}, t('DiscordButton.success'))
        return {'FINISHED'}


@register_wrap
class PatchnotesButton(bpy.types.Operator):
    bl_idname = 'cats_credits.patchnotes'
    bl_label = t('PatchnotesButton.label')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('PatchnotesButton.URL'))

        self.report({'INFO'}, t('PatchnotesButton.success'))
        return {'FINISHED'}
