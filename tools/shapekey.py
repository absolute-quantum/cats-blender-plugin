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
from . import common as Common
from .register import register_wrap
from ..translations import t


@register_wrap
class ShapeKeyApplier(bpy.types.Operator):
    # Replace the 'Basis' shape key with the currently selected shape key
    bl_idname = "cats_shapekey.shape_key_to_basis"
    bl_label = t('ShapeKeyApplier.label')
    bl_description = t('ShapeKeyApplier.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bpy.context.object.active_shape_key and bpy.context.object.active_shape_key_index > 0

    def execute(self, context):
        mesh = Common.get_active()

        # Get shapekey which will be the new basis
        new_basis_shapekey = mesh.active_shape_key
        new_basis_shapekey_name = new_basis_shapekey.name
        new_basis_shapekey_value = new_basis_shapekey.value

        # Check for reverted shape keys
        if ' - Reverted' in new_basis_shapekey_name and new_basis_shapekey.relative_key.name != 'Basis':
            for shapekey in mesh.data.shape_keys.key_blocks:
                if ' - Reverted' in shapekey.name and shapekey.relative_key.name == 'Basis':
                    Common.show_error(t('ShapeKeyApplier.error.revert.scale'), t('ShapeKeyApplier.error.revert', name=shapekey.name))
                    return {'FINISHED'}

            Common.show_error(t('ShapeKeyApplier.error.revert.scale'), t('ShapeKeyApplier.error.revert'))
            return {'FINISHED'}

        # Set up shape keys
        mesh.show_only_shape_key = False
        bpy.ops.object.shape_key_clear()

        # Create a copy of the new basis shapekey to make it's current value stay as it is
        new_basis_shapekey.value = new_basis_shapekey_value
        if new_basis_shapekey_value == 0:
            new_basis_shapekey.value = 1
        new_basis_shapekey.name = new_basis_shapekey_name + '--Old'

        # Replace old new basis with new new basis
        new_basis_shapekey = mesh.shape_key_add(name=new_basis_shapekey_name, from_mix=True)
        new_basis_shapekey.value = 1

        # Delete the old one
        for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey.name == new_basis_shapekey_name + '--Old':
                bpy.ops.object.shape_key_remove(all=False)
                break

        # Find old basis and rename it
        old_basis_shapekey = mesh.data.shape_keys.key_blocks[0]
        old_basis_shapekey.name = new_basis_shapekey_name + ' - Reverted'
        old_basis_shapekey.relative_key = new_basis_shapekey

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
        Common.sort_shape_keys(mesh.name)

        # Correctly apply the new basis as basis (important step, doesn't work otherwise)
        Common.switch('EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.remove_doubles(threshold=0)
        Common.switch('OBJECT')

        # If a reversed shapekey was applied as basis, fix the name
        if ' - Reverted - Reverted' in old_basis_shapekey.name:
            old_basis_shapekey.name = old_basis_shapekey.name.replace(' - Reverted - Reverted', '')
            self.report({'INFO'}, t('ShapeKeyApplier.successRemoved', name=old_basis_shapekey.name))
        else:
            self.report({'INFO'}, t('ShapeKeyApplier.successSet', name=new_basis_shapekey_name))
        return {'FINISHED'}


def addToShapekeyMenu(self, context):
    self.layout.separator()
    self.layout.operator(ShapeKeyApplier.bl_idname, text=t('addToShapekeyMenu.ShapeKeyApplier.label'), icon="KEY_HLT")
