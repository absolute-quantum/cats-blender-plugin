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
import random
import tools.common
from mathutils import Vector


class CopyProtectionEnable(bpy.types.Operator):
    bl_idname = 'copyprotection.enable'
    bl_label = 'Enable Protection'
    bl_description = 'Protects your model from piracy. Only do this if you know what you are doing!'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if len(tools.common.get_meshes_objects()) != 1:
            return False
        return True

    def execute(self, context):
        mesh = tools.common.get_meshes_objects()[0]
        tools.common.set_default_stage()
        tools.common.unselect_all()
        tools.common.select(mesh)
        tools.common.switch('OBJECT')

        mesh.show_only_shape_key = False
        bpy.ops.object.shape_key_clear()

        if not mesh.data.shape_keys:
            mesh.shape_key_add(name='Basis', from_mix=False)

        # 1. Rename original shapekey
        basis_original = None
        for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if i == 0:
                basis_original = shapekey
        basis_original.name = 'Basis Original'

        # 2. Mangle verts into THE SINGULARITY!!!
        for index, vert in enumerate(mesh.data.vertices):
            mesh.data.vertices[index].co = Vector((random.uniform(-.4, .4), random.uniform(-.4, .4), random.uniform(0, .4)))
        mesh.data.update()

        # 3. Create a new shapekey that distorts all the vertices
        basis_obfuscated = mesh.shape_key_add(name='Basis', from_mix=False)

        # 4. Put newly created shapekey as new basis key
        mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
        bpy.ops.object.shape_key_move(type='TOP')

        # Make all shape keys relative to the original basis
        for shapekey in mesh.data.shape_keys.key_blocks:
            if shapekey and shapekey.name != 'Basis' and shapekey.name != 'Basis Original':
                shapekey.relative_key = basis_original

        # Make the original basis relative to the obfuscated one
        basis_original.relative_key = basis_obfuscated

        # Make obfuscated basis the new basis and repair shape key order
        tools.common.repair_viseme_order(mesh.name)

        self.report({'INFO'}, 'Model secured!')
        return {'FINISHED'}


class CopyProtectionDisable(bpy.types.Operator):
    bl_idname = 'copyprotection.disable'
    bl_label = 'Disable Protection'
    bl_description = 'Removes the copy protections from this model'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        mesh = tools.common.get_meshes_objects()[0]

        tools.common.set_default_stage()
        tools.common.unselect_all()
        tools.common.select(mesh)
        tools.common.switch('OBJECT')

        for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if i == 0:
                mesh.active_shape_key_index = i
                bpy.ops.object.shape_key_remove(all=False)

            if shapekey.name == 'Basis Original':
                shapekey.name = 'Basis'
                break

        tools.common.repair_viseme_order(mesh.name)

        self.report({'INFO'}, 'Model un-secured!')
        return {'FINISHED'}
