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
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by:

import bpy
import tools.common
from collections import OrderedDict



class ShapeKeyApplier(bpy.types.Operator):
    """Replace the 'Basis' shape key with the currently selected shape key"""
    bl_idname = "object.shape_key_applier"
    bl_label = "Apply Selected Shapekey as Basis"

    @classmethod
    def poll(cls, context):
        return bpy.context.object.active_shape_key_index > 0

    def execute(self, context):
        mesh = bpy.context.scene.objects.active
        mesh.show_only_shape_key = False
        bpy.ops.object.shape_key_clear()

        new_basis_shapekey = mesh.active_shape_key
        new_basis_shapekey.value = 1
        new_basis_shapekey_name = new_basis_shapekey.name

        old_basis_shapekey = None

        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if index == 0:
                shapekey.name = 'Basis Old'
                old_basis_shapekey = shapekey
                break

        new_basis_shapekey.name = 'Basis'

        for index in range(0, len(mesh.data.shape_keys.key_blocks)):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey and shapekey.name != 'Basis' and shapekey.name != 'Basis Old':
                shapekey.value = 1
                mesh.shape_key_add(name=shapekey.name + '-New', from_mix=True)
                shapekey.value = 0

        for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey and not shapekey.name.endswith('-New') and shapekey.name != 'Basis' and shapekey.name != 'Basis Old':
                bpy.ops.object.shape_key_remove(all=False)

        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if shapekey and shapekey.name.endswith('-New'):
                shapekey.name = shapekey.name[:-4]
                shapekey.relative_key = mesh.data.shape_keys.key_blocks['Basis']

        tools.common.repair_viseme_order(mesh.name)

        self.report({'INFO'}, 'Successfully set shapekey ' + new_basis_shapekey_name + ' as the new Basis.')
        return {'FINISHED'}


def addToShapekeyMenu(self, context):
    self.layout.separator()
    self.layout.operator(ShapeKeyApplier.bl_idname, text="Apply Selected Shapekey as Basis", icon="KEY_HLT")