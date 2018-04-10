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
        shapekey_name = bpy.context.object.active_shape_key.name

        bpy.ops.object.shape_key_clear()

        for shapekey in mesh.data.shape_keys.key_blocks:
            if shapekey.name != 'Basis':
                shapekey.name = 'Basis'
            break

        bpy.data.objects[mesh.name].shape_key_add(name='Basis Old', from_mix=False)

        order = OrderedDict()
        order[shapekey_name] = 0
        order['Basis'] = 1
        order['Basis Old'] = 2
        order['Basis Old.001'] = 3
        order['Basis Old.002'] = 4
        order['Basis Old.003'] = 5
        order['Basis Old.004'] = 6
        order['Basis Old.005'] = 7
        tools.common.repair_shape_order(mesh.name, order)

        bpy.context.object.active_shape_key_index = 1
        bpy.ops.object.shape_key_remove()

        mesh.data.shape_keys.key_blocks.get(shapekey_name).name = 'Basis'

        tools.common.repair_viseme_order(mesh.name)

        self.report({'INFO'}, 'Successfully set shapekey ' + shapekey_name + ' as the new Basis.')
        return {'FINISHED'}

def setActiveShapeKey (name):
    bpy.context.object.active_shape_key_index = bpy.context.object.data.shape_keys.key_blocks.keys().index(name)

def addToShapekeyMenu(self, context):
    self.layout.separator()
    self.layout.operator(ShapeKeyApplier.bl_idname, text="Apply Selected Shapekey as Basis", icon="KEY_HLT")