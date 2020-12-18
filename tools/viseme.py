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
from . import common as Common
from .register import register_wrap

from collections import OrderedDict
from ..translations import t


@register_wrap
class AutoVisemeButton(bpy.types.Operator):
    bl_idname = 'cats_viseme.create'
    bl_label = t('AutoVisemeButton.label')
    bl_description = t('AutoVisemeButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not Common.get_meshes_objects(check=False):
            return False
        return True

    def execute(self, context):
        mesh = Common.get_objects()[context.scene.mesh_name_viseme]

        if not Common.has_shapekeys(mesh):
            self.report({'ERROR'}, t('AutoVisemeButton.error.noShapekeys'))
            return {'CANCELLED'}

        if context.scene.mouth_a == "Basis" \
                or context.scene.mouth_o == "Basis" \
                or context.scene.mouth_ch == "Basis":
            self.report({'ERROR'}, t('AutoVisemeButton.error.selectShapekeys'))
            return {'CANCELLED'}

        saved_data = Common.SavedData()

        Common.set_default_stage()

        wm = bpy.context.window_manager

        mesh = Common.get_objects()[context.scene.mesh_name_viseme]
        Common.set_active(mesh)

        # Fix a small bug
        bpy.context.object.show_only_shape_key = False

        # Rename selected shapes and rename them back at the end
        shapes = [context.scene.mouth_a, context.scene.mouth_o, context.scene.mouth_ch]
        renamed_shapes = [context.scene.mouth_a, context.scene.mouth_o, context.scene.mouth_ch]
        mesh = Common.get_objects()[context.scene.mesh_name_viseme]
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if shapekey.name == context.scene.mouth_a:
                print(shapekey.name + " " + context.scene.mouth_a)
                shapekey.name = shapekey.name + "_old"
                context.scene.mouth_a = shapekey.name
                renamed_shapes[0] = shapekey.name
            if shapekey.name == context.scene.mouth_o:
                print(shapekey.name + " " + context.scene.mouth_a)
                if context.scene.mouth_a != context.scene.mouth_o:
                    shapekey.name = shapekey.name + "_old"
                context.scene.mouth_o = shapekey.name
                renamed_shapes[1] = shapekey.name
            if shapekey.name == context.scene.mouth_ch:
                print(shapekey.name + " " + context.scene.mouth_a)
                if context.scene.mouth_a != context.scene.mouth_ch and context.scene.mouth_o != context.scene.mouth_ch:
                    shapekey.name = shapekey.name + "_old"
                context.scene.mouth_ch = shapekey.name
                renamed_shapes[2] = shapekey.name
            wm.progress_update(index)

        shape_a = context.scene.mouth_a
        shape_o = context.scene.mouth_o
        shape_ch = context.scene.mouth_ch

        # Set up the shape keys. Some values are made in order to keep Blender from deleting them. There should never be duplicate shape keys!
        shapekey_data = OrderedDict()
        shapekey_data['vrc.v_aa'] = {
            'mix': [
                [(shape_a), (0.9998)]
            ]
        }
        shapekey_data['vrc.v_ch'] = {
            'mix': [
                [(shape_ch), (0.9996)]
            ]
        }
        shapekey_data['vrc.v_dd'] = {
            'mix': [
                [(shape_a), (0.3)],
                [(shape_ch), (0.7)]
            ]
        }
        shapekey_data['vrc.v_e'] = {
            'mix': [
                [(shape_ch), (0.7)],
                [(shape_o), (0.3)]
            ]
        }
        shapekey_data['vrc.v_ff'] = {
            'mix': [
                [(shape_a), (0.2)],
                [(shape_ch), (0.4)]
            ]
        }
        shapekey_data['vrc.v_ih'] = {
            'mix': [
                [(shape_a), (0.5)],
                [(shape_ch), (0.2)]
            ]
        }
        shapekey_data['vrc.v_kk'] = {
            'mix': [
                [(shape_a), (0.7)],
                [(shape_ch), (0.4)]
            ]
        }
        shapekey_data['vrc.v_nn'] = {
            'mix': [
                [(shape_a), (0.2)],
                [(shape_ch), (0.7)]
            ]
        }
        shapekey_data['vrc.v_oh'] = {
            'mix': [
                [(shape_a), (0.2)],
                [(shape_o), (0.8)]
            ]
        }
        shapekey_data['vrc.v_ou'] = {
            'mix': [
                [(shape_o), (0.9994)]
            ]
        }
        shapekey_data['vrc.v_pp'] = {
            'mix': [
                [(shape_a), (0.0004)],
                [(shape_o), (0.0004)]
            ]
        }
        shapekey_data['vrc.v_rr'] = {
            'mix': [
                [(shape_ch), (0.5)],
                [(shape_o), (0.3)]
            ]
        }
        shapekey_data['vrc.v_sil'] = {
            'mix': [
                [(shape_a), (0.0002)],
                [(shape_ch), (0.0002)]
            ]
        }
        shapekey_data['vrc.v_ss'] = {
            'mix': [
                [(shape_ch), (0.8)],
            ]
        }
        shapekey_data['vrc.v_th'] = {
            'mix': [
                [(shape_a), (0.4)],
                [(shape_o), (0.15)]
            ]
        }

        total_fors = len(shapekey_data)
        wm.progress_begin(0, total_fors)

        # Add the shape keys
        for index, key in enumerate(shapekey_data):
            obj = shapekey_data[key]
            wm.progress_update(index)
            self.mix_shapekey(context, renamed_shapes, obj['mix'], key, context.scene.shape_intensity)

        # Rename shapes back
        if shapes[0] not in mesh.data.shape_keys.key_blocks:
            shapekey = mesh.data.shape_keys.key_blocks.get(renamed_shapes[0])
            shapekey.name = shapes[0]
            if renamed_shapes[2] == renamed_shapes[0]:
                renamed_shapes[2] = shapes[0]
            if renamed_shapes[1] == renamed_shapes[0]:
                renamed_shapes[1] = shapes[0]
            renamed_shapes[0] = shapes[0]

        if shapes[1] not in mesh.data.shape_keys.key_blocks:
            shapekey = mesh.data.shape_keys.key_blocks.get(renamed_shapes[1])
            shapekey.name = shapes[1]
            if renamed_shapes[2] == renamed_shapes[1]:
                renamed_shapes[2] = shapes[1]
            renamed_shapes[1] = shapes[1]

        if shapes[2] not in mesh.data.shape_keys.key_blocks:
            shapekey = mesh.data.shape_keys.key_blocks.get(renamed_shapes[2])
            shapekey.name = shapes[2]
            renamed_shapes[2] = shapes[2]

        # Reset context scenes
        try:
            context.scene.mouth_a = renamed_shapes[0]
        except TypeError:
            pass

        try:
            context.scene.mouth_o = renamed_shapes[1]
        except TypeError:
            pass

        try:
            context.scene.mouth_ch = renamed_shapes[2]
        except TypeError:
            pass

        # Set shapekey index back to 0
        bpy.context.object.active_shape_key_index = 0

        # Remove empty objects
        Common.switch('EDIT')
        Common.remove_empty()

        # Fix armature name
        Common.fix_armature_names()

        # Sort visemes
        Common.sort_shape_keys(mesh.name)

        saved_data.load()

        wm.progress_end()

        self.report({'INFO'}, t('AutoVisemeButton.success'))

        return {'FINISHED'}

    def mix_shapekey(self, context, shapes, shapekey_data, rename_to, intensity):
        mesh = Common.get_objects()[context.scene.mesh_name_viseme]

        # Remove existing shapekey
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if shapekey.name == rename_to:
                bpy.context.active_object.active_shape_key_index = index
                bpy.ops.object.shape_key_remove()
                break

        # Reset all shape keys
        bpy.ops.object.shape_key_clear()

        # Set the shape key values
        for shapekey_data_context in shapekey_data:
            selector = shapekey_data_context[0]
            shapekey_value = shapekey_data_context[1]

            for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                if selector == shapekey.name:
                    # mesh.active_shape_key_index = index
                    shapekey.slider_max = 10
                    shapekey.value = shapekey_value * intensity

        # Create the new shape key
        mesh.shape_key_add(name=rename_to, from_mix=True)

        # Reset all shape keys and sliders
        bpy.ops.object.shape_key_clear()
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if shapekey.name in shapes:
                shapekey.slider_max = 1
        mesh.active_shape_key_index = 0

        # Reset context scenes
        context.scene.mouth_a = shapes[0]
        context.scene.mouth_o = shapes[1]
        context.scene.mouth_ch = shapes[2]
