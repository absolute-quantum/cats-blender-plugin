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
import tools.decimation
import random
from mathutils import Vector


class CopyProtectionEnable(bpy.types.Operator):
    bl_idname = 'copyprotection.enable'
    bl_label = 'Enable'

    def execute(self, context):
        self.create_obfuscated_basis()

        # Weird bug :thunk: create_obfuscated_basis is explicitly called twice
        # By doing this we are certain that the verts are indeed mangled
        bpy.ops.object.shape_key_move(type='DOWN')
        self.create_obfuscated_basis()

        basisObfuscatedKey = bpy.data.shape_keys['Key'].key_blocks['Basis']
        basisObfuscatedKey.value = 0

        # TODO: this step of the code messes with unity blendshapes somehow
        # 4. All shapekeys except Basis and BasisObfuscated needs to be mixed from
        # the BasisObfuscated key and then be replaced
        mesh = get_body_mesh()
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if (shapekey.name.endswith('New') is False and shapekey.name != 'Basis' and shapekey.name != 'BasisObfuscated'):
                mesh.active_shape_key_index = index
                shapekey.value = 1
                mesh.shape_key_add(name=shapekey.name + 'New', from_mix=True)
                shapekey.value = 0

        mesh.data.update()

        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if (shapekey.name.endswith('New') is True and shapekey.name != 'Basis' and shapekey.name != 'BasisObfuscated'):
                bpy.ops.object.shape_key_remove(all=False)

        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if (shapekey.name.endswith('New') is True and shapekey.name != 'Basis' and shapekey.name != 'BasisObfuscated'):
                shapekey.name = shapekey.name.replace('New', '')

        # Set blend from orginal basis to obfuscated basis
        bpy.data.shape_keys['Key'].key_blocks['Basis'].relative_key = bpy.data.shape_keys['Key'].key_blocks['BasisObfuscated']

        basisObfuscatedKey.value = 0
        mesh.active_shape_key_index = 0

        self.report({'INFO'}, 'Model secured!')
        return {'FINISHED'}

    def create_obfuscated_basis(self):
        mesh = get_body_mesh()

        tools.common.set_default_stage()
        tools.common.unselect_all()
        tools.common.select(mesh)
        tools.common.switch('OBJECT')

        # 1. Find existing shapekey first and remove if found
        for (i, x) in enumerate(mesh.data.shape_keys.key_blocks):
            if (x.name == 'BasisObfuscated'):
                bpy.context.object.active_shape_key_index = i
                bpy.ops.object.shape_key_remove(all=False)
                break

        # 2. Create a new shapekey that distorts all the vertices
        bpy.data.objects[mesh.name].shape_key_add(name='BasisObfuscated', from_mix=False)
        mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
        bpy.data.shape_keys['Key'].key_blocks['BasisObfuscated'].value = 1

        # Mangle verts into THE SINGULARITY!!!
        for (index, vert) in enumerate(mesh.data.vertices):
            mesh.data.vertices[index].co = Vector((random.uniform(-.1, .1), random.uniform(-.1, .1), random.uniform(0, .1)))
        mesh.data.update()

        # 3. Put newly created shapekey as new basis key
        for x in mesh.data.shape_keys.key_blocks:
            bpy.ops.object.shape_key_move(type='TOP')


class CopyProtectionDisable(bpy.types.Operator):
    bl_idname = 'copyprotection.disable'
    bl_label = 'Disable'

    def execute(self, context):
        mesh = get_body_mesh()

        tools.common.set_default_stage()
        tools.common.unselect_all()
        tools.common.select(mesh)
        tools.common.switch('OBJECT')

        for (i, x) in enumerate(mesh.data.shape_keys.key_blocks):
            if (x.name == 'BasisObfuscated'):
                bpy.context.object.active_shape_key_index = i
                bpy.ops.object.shape_key_remove(all=False)
                break

        self.report({'INFO'}, 'Model un-secured!')
        return {'FINISHED'}


def get_body_mesh():
    body = None
    for obj in bpy.data.objects:
        if obj.name == 'Body':
            body = obj

    return body
