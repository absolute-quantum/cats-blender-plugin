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
# Edits by:

import bpy
import tools.common

from collections import OrderedDict

class AutoVisemeButton(bpy.types.Operator):
    bl_idname = 'auto.viseme'
    bl_label = 'Create visemes'

    bl_options = {'REGISTER', 'UNDO'}

    def mix_shapekey(self, target_mesh, shapekey_data, new_index, rename_to, intensity):
        mesh = bpy.data.objects[target_mesh]

        # first set value to 0 for all shape keys, so we don't mess up
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            shapekey.value = 0

        random_mix = True

        for shapekey_data_context in shapekey_data:
            selector = shapekey_data_context[0]
            shapekey_value = shapekey_data_context[1]

            for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                if random_mix:
                    if selector is not shapekey.name:
                        if 'Basis' not in shapekey.name:
                            shapekey.value = 0.00001
                            random_mix = False

                if selector == shapekey.name:
                    mesh.active_shape_key_index = index
                    shapekey.value = shapekey_value * intensity

        mesh.shape_key_add(name=rename_to, from_mix=True)
        bpy.ops.object.shape_key_clear()

        # Select the created shapekey
        mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1

        # Re-adjust index position
        position_correct = False
        while position_correct is False:
            bpy.ops.object.shape_key_move(type='DOWN')

            if mesh.active_shape_key_index == new_index:
                position_correct = True

    def execute(self, context):
        tools.common.unhide_all()

        tools.common.unselect_all()
        tools.common.select(bpy.data.objects[context.scene.mesh_name_viseme])

        shapekey_data = OrderedDict()
        shapekey_data['vrc.v_aa'] = {
            'index': 5,
            'mix': [
                [(context.scene.mouth_a), (1)]
            ]
        }
        shapekey_data['vrc.v_ch'] = {
            'index': 6,
            'mix': [
                [(context.scene.mouth_ch), (1)]
            ]
        }
        shapekey_data['vrc.v_dd'] = {
            'index': 7,
            'mix': [
                [(context.scene.mouth_a), (0.3)],
                [(context.scene.mouth_ch), (0.7)]
            ]
        }
        shapekey_data['vrc.v_e'] = {
            'index': 8,
            'mix': [
                [(context.scene.mouth_ch), (0.7)],
                [(context.scene.mouth_o), (0.3)]
            ]
        }
        shapekey_data['vrc.v_ff'] = {
            'index': 9,
            'mix': [
                [(context.scene.mouth_a), (0.2)],
                [(context.scene.mouth_ch), (0.4)]
            ]
        }
        shapekey_data['vrc.v_ih'] = {
            'index': 10,
            'mix': [
                [(context.scene.mouth_a), (0.5)],
                [(context.scene.mouth_ch), (0.2)]
            ]
        }
        shapekey_data['vrc.v_kk'] = {
            'index': 11,
            'mix': [
                [(context.scene.mouth_a), (0.7)],
                [(context.scene.mouth_ch), (0.4)]
            ]
        }
        shapekey_data['vrc.v_nn'] = {
            'index': 12,
            'mix': [
                [(context.scene.mouth_a), (0.2)],
                [(context.scene.mouth_ch), (0.7)],
            ]
        }
        shapekey_data['vrc.v_oh'] = {
            'index': 13,
            'mix': [
                [(context.scene.mouth_a), (0.2)],
                [(context.scene.mouth_o), (0.8)]
            ]
        }
        shapekey_data['vrc.v_ou'] = {
            'index': 14,
            'mix': [
                [(context.scene.mouth_o), (1.0)]
            ]
        }
        shapekey_data['vrc.v_pp'] = {
            'index': 15,
            'mix': [
                [(context.scene.mouth_a), (0.00001)],
            ]
        }
        shapekey_data['vrc.v_rr'] = {
            'index': 16,
            'mix': [
                [(context.scene.mouth_ch), (0.5)],
                [(context.scene.mouth_o), (0.3)]
            ]
        }
        shapekey_data['vrc.v_sil'] = {
            'index': 17,
            'mix': [
                [(context.scene.mouth_o), (0.00001)],
            ]
        }
        shapekey_data['vrc.v_ss'] = {
            'index': 18,
            'mix': [
                [(context.scene.mouth_ch), (0.8)],
            ]
        }
        shapekey_data['vrc.v_th'] = {
            'index': 19,
            'mix': [
                [(context.scene.mouth_a), (0.4)],
                [(context.scene.mouth_o), (0.15)]
            ]
        }

        # Remove any existing viseme shape key
        for key in shapekey_data:
            for index, shapekey in enumerate(bpy.data.objects[context.scene.mesh_name_viseme].data.shape_keys.key_blocks):
                obj = shapekey_data[key]
                if shapekey.name == key:
                    bpy.context.active_object.active_shape_key_index = index
                    bpy.ops.object.shape_key_remove()

        # Add the shape keys
        for key in shapekey_data:
            obj = shapekey_data[key]
            self.mix_shapekey(context.scene.mesh_name_viseme, obj['mix'], obj['index'], key, context.scene.shape_intensity)

        # Remove empty objects
        bpy.ops.object.mode_set(mode='EDIT')
        tools.common.remove_empty()

        # Fix armature name
        tools.common.fix_armature_name()

        # Set shapekey index back to 0
        bpy.context.object.active_shape_key_index = 0

        self.report({'INFO'}, 'Created mouth visemes!')

        return{'FINISHED'}
