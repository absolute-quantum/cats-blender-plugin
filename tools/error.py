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

# Code author: GiveMeAllYourCats
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: GiveMeAllYourCats

import bpy
from bpy.props import *
import os
import zipfile
import sys
import traceback


# Catch all execptions and write traceback to file
def got_error(exctype, value, tb):
    filepath = os.path.join(os.path.dirname(bpy.data.filepath), 'cats.log')
    filerino = open(filepath, 'a')
    traceback.print_tb(tb, None, filerino)
    bpy.ops.error.message('INVOKE_DEFAULT', type='Error')


sys.excepthook = got_error


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


class MessageOperator(bpy.types.Operator):
    bl_idname = 'error.message'
    bl_label = 'Message'
    type = StringProperty()
    message = StringProperty()

    def execute(self, context):
        self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=200)

    def draw(self, context):
        self.layout.label('An error has occured!!')
        self.layout.label('The developers would love this information to fix this!')
        row = self.layout.split(0.05)
        row.label('')
        row.operator('error.ok')
        row.label('')
        row.operator('error.no')


class OkOperator(bpy.types.Operator):
    bl_idname = 'error.ok'
    bl_label = 'Okay, I want to help!'

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'The blend file could not be included because it was not saved.')
        else:
            # toggle two times, so we know for sure it got packed
            bpy.ops.file.autopack_toggle()
            bpy.ops.file.autopack_toggle()

        zipf = zipfile.ZipFile('cats-blender-plugin-error.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(tempfile.gettempdir(), zipf)
        zipf.close()

        return {'FINISHED'}


class NoOperator(bpy.types.Operator):
    bl_idname = 'error.no'
    bl_label = 'No thank you'

    def execute(self, context):
        return {'FINISHED'}


bpy.utils.register_class(OkOperator)
bpy.utils.register_class(NoOperator)
bpy.utils.register_class(MessageOperator)
