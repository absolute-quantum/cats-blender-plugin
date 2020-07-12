# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: Hotox
# Edits by: Hotox

import bpy
import webbrowser
from .register import register_wrap
from ..translations import t

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
