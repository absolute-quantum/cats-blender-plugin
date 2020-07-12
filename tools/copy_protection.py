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
# Edits by: GiveMeAllYourCats, Hotox

import bpy
import random
import webbrowser

from . import common as Common
from .register import register_wrap
from ..translations import t


@register_wrap
class CopyProtectionEnable(bpy.types.Operator):
    bl_idname = 'cats_copyprotection.enable'
    bl_label = t('CopyProtectionEnable.label')
    bl_description = t('CopyProtectionEnable.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if len(Common.get_meshes_objects(check=False)) == 0:
            return False
        return True

    def execute(self, context):
        for mesh in Common.get_meshes_objects():
            armature = Common.set_default_stage()
            Common.unselect_all()
            Common.set_active(mesh)
            Common.switch('EDIT')

            # Convert quad faces to tris first
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

            Common.switch('OBJECT')

            mesh.show_only_shape_key = False
            bpy.ops.object.shape_key_clear()

            if not Common.has_shapekeys(mesh):
                mesh.shape_key_add(name='Basis', from_mix=False)

            # 1. Rename original shapekey
            basis_original = None
            for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                if i == 0:
                    basis_original = shapekey
            basis_original.name = 'Basis Original'

            # 2. Mangle verts into THE SINGULARITY!!!

            # Check if bone matrix == world matrix, important for xps models
            xps = False
            for index, bone in enumerate(armature.pose.bones):
                if index == 5:
                    bone_pos = bone.matrix
                    world_pos = Common.matmul(armature.matrix_world, bone.matrix)
                    if abs(bone_pos[0][0]) != abs(world_pos[0][0]):
                        xps = True
                        break

            max_height = 0
            for index, vert in enumerate(mesh.data.vertices):
                if not xps:
                    if max_height < mesh.data.vertices[index].co.z:
                        max_height = mesh.data.vertices[index].co.z
                else:
                    if max_height < mesh.data.vertices[index].co.y:
                        max_height = mesh.data.vertices[index].co.y

            max_height /= 3

            for index, vert in enumerate(mesh.data.vertices):
                vector = (random.uniform(-max_height, max_height),
                          random.uniform(-max_height, max_height),
                          random.uniform(0, max_height))

                if not xps:
                    mesh.data.vertices[index].co = (vector[0], vector[1], vector[2])
                else:
                    mesh.data.vertices[index].co = (vector[0], vector[2], vector[1])

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
            Common.sort_shape_keys(mesh.name)

        self.report({'INFO'}, t('CopyProtectionEnable.success'))
        return {'FINISHED'}


@register_wrap
class CopyProtectionDisable(bpy.types.Operator):
    bl_idname = 'cats_copyprotection.disable'
    bl_label = t('CopyProtectionDisable.label')
    bl_description = t('CopyProtectionDisable.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        for mesh in Common.get_meshes_objects():
            Common.set_default_stage()
            Common.unselect_all()
            Common.set_active(mesh)
            Common.switch('OBJECT')

            for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                if i == 0:
                    mesh.active_shape_key_index = i
                    bpy.ops.object.shape_key_remove(all=False)

                if shapekey.name == 'Basis Original':
                    shapekey.name = 'Basis'
                    shapekey.relative_key = shapekey
                    break

            Common.sort_shape_keys(mesh.name)

        self.report({'INFO'}, t('CopyProtectionDisable.success'))
        return {'FINISHED'}


@register_wrap
class ProtectionTutorialButton(bpy.types.Operator):
    bl_idname = 'cats_copyprotection.tutorial'
    bl_label = t('ProtectionTutorialButton.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('ProtectionTutorialButton.URL'))

        # mesh = Common.get_meshes_objects()[0]
        # Common.select(mesh)
        # Common.switch('OBJECT')
        #
        # for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
        #     if i == 1:
        #         shapekey.value = 1.5

        self.report({'INFO'}, t('ProtectionTutorialButton.success'))
        return {'FINISHED'}
