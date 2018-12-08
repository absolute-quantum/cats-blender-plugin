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
from tools.register import register_wrap


@register_wrap
class ShapeKeyApplier(bpy.types.Operator):
    # Replace the 'Basis' shape key with the currently selected shape key
    bl_idname = "object.shape_key_to_basis"
    bl_label = "Apply Selected Shapekey as Basis"
    bl_description = 'Applies the selected shape key as the new Basis and creates a reverted shape key from the selected one'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object.active_shape_key and bpy.context.object.active_shape_key_index > 0

    def execute(self, context):
        mesh = tools.common.get_active()

        # Get shapekey which will be the new basis
        new_basis_shapekey = mesh.active_shape_key
        new_basis_shapekey_name = new_basis_shapekey.name

        # Check for reverted shape keys
        if ' - Reverted' in new_basis_shapekey_name and new_basis_shapekey.relative_key.name != 'Basis':
            for shapekey in mesh.data.shape_keys.key_blocks:
                if ' - Reverted' in shapekey.name and shapekey.relative_key.name == 'Basis':
                    tools.common.show_error(7.3, ['To revert the shape keys, please apply the "Reverted" shape keys in reverse order.',
                                                  'Start with the shape key called "' + shapekey.name + '".',
                                                  '',
                                                  "If you didn't change the shape key order, you can revert the shape keys from top to bottom."])
                    return {'FINISHED'}

            tools.common.show_error(7.3, ['To revert the shape keys, please apply the "Reverted" shape keys in reverse order.',
                                          'Start with the reverted shape key that uses the relative key called "Basis".',
                                          '',
                                          "If you didn't change the shape key order, you can revert the shape keys from top to bottom."])
            return {'FINISHED'}

        # Set up shape keys
        mesh.show_only_shape_key = False
        bpy.ops.object.shape_key_clear()
        new_basis_shapekey.value = 1

        # Find old basis and rename it
        old_basis_shapekey = None
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if index == 0:
                shapekey.name = new_basis_shapekey_name + ' - Reverted'
                shapekey.relative_key = new_basis_shapekey
                old_basis_shapekey = shapekey
                break

        # Rename new basis after old basis was renamed
        new_basis_shapekey.name = 'Basis'

        # Mix every shape keys with the new basis
        for index in range(0, len(mesh.data.shape_keys.key_blocks)):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey and shapekey.name != 'Basis' and ' - Reverted' not in shapekey.name:
                shapekey.value = 1
                mesh.shape_key_add(name=shapekey.name + '-New', from_mix=True)
                shapekey.value = 0

        # Remove all the unmixed shape keys except basis and the reverted ones
        for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey and not shapekey.name.endswith('-New') and shapekey.name != 'Basis' and ' - Reverted' not in shapekey.name:
                bpy.ops.object.shape_key_remove(all=False)

        # Fix the names and the relative shape key
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if shapekey and shapekey.name.endswith('-New'):
                shapekey.name = shapekey.name[:-4]
                shapekey.relative_key = new_basis_shapekey

        # Repair important shape key order
        tools.common.sort_shape_keys(mesh.name)

        # Correctly apply the new basis as basis (important step, doesn't work otherwise)
        tools.common.switch('EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.remove_doubles(threshold=0)
        tools.common.switch('OBJECT')

        # If a reversed shapekey was applied as basis, fix the name
        if ' - Reverted - Reverted' in old_basis_shapekey.name:
            old_basis_shapekey.name = old_basis_shapekey.name.replace(' - Reverted - Reverted', '')
            self.report({'INFO'}, 'Successfully removed shapekey "' + old_basis_shapekey.name + '" from the Basis.')
        else:
            self.report({'INFO'}, 'Successfully set shapekey "' + new_basis_shapekey_name + '" as the new Basis.')
        return {'FINISHED'}


def addToShapekeyMenu(self, context):
    self.layout.separator()
    self.layout.operator(ShapeKeyApplier.bl_idname, text="Apply Selected Shapekey as Basis", icon="KEY_HLT")
