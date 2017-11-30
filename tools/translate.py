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
import tools.common

from googletrans import Translator
from mmd_tools_local import utils
from mmd_tools_local.translations import DictionaryEnum


class TranslateShapekeyButton(bpy.types.Operator):
    bl_idname = 'translate.shapekeys'
    bl_label = 'Shape Keys'
    bl_description = "Translates all shape keys with Google Translate."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tools.common.unhide_all()

        to_translate = []
        translated = []

        for object in bpy.data.objects:
            if hasattr(object.data, 'shape_keys'):
                if hasattr(object.data.shape_keys, 'key_blocks'):
                    for index, shapekey in enumerate(object.data.shape_keys.key_blocks):
                        to_translate.append(shapekey.name)

        translator = Translator()
        translations = translator.translate(to_translate)
        for translation in translations:
            translated.append(translation.text)

        i = 0
        for object in bpy.data.objects:
            if hasattr(object.data, 'shape_keys'):
                if hasattr(object.data.shape_keys, 'key_blocks'):
                    for index, shapekey in enumerate(object.data.shape_keys.key_blocks):
                        shapekey.name = translated[i]
                        i += 1

        self.report({'INFO'}, 'Translated all shape keys')

        return {'FINISHED'}


class TranslateBonesButton(bpy.types.Operator):
    bl_idname = 'translate.bones'
    bl_label = 'Bones'
    bl_description = "Translates all bones with Google Translate."
    bl_options = {'REGISTER', 'UNDO'}

    dictionary = bpy.props.EnumProperty(
        name='Dictionary',
        items=DictionaryEnum.get_dictionary_items,
        description='Translate names from Japanese to English using selected dictionary',
    )

    def execute(self, context):
        tools.common.unhide_all()
        armature = tools.common.get_armature().data

        translator = DictionaryEnum.get_translator(self.dictionary)

        for bone in armature.bones:
            bone.name = utils.convertNameToLR(bone.name, True)
            bone.name = translator.translate(bone.name)

        # then translate all the bones to english just in case mmd skipped something
        # TODO: could be optimised by only translating bones that mmd skipped
        to_translate = []
        translated = []

        for bone in armature.bones:
            to_translate.append(bone.name)

        translator = Translator()
        translations = translator.translate(to_translate)
        for translation in translations:
            translated.append(translation.text)

        for i, bone in enumerate(armature.bones):
            bone.name = translated[i]

        self.report({'INFO'}, 'Translated all bones')
        return {'FINISHED'}


class TranslateMeshesButton(bpy.types.Operator):
    bl_idname = 'translate.meshes'
    bl_label = 'Meshes'
    bl_description = "Translates all meshes with Google Translate."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tools.common.unhide_all()

        to_translate = []
        translated = []
        translator = Translator()

        objects = bpy.data.objects
        for object in objects:
            if object.type != 'ARMATURE':
                to_translate.append(object.name)

        translations = translator.translate(to_translate)
        for translation in translations:
            translated.append(translation.text)

        i = 0
        for object in objects:
            if object.type != 'ARMATURE':
                object.name = translated[i]
                i += 1

        self.report({'INFO'}, 'Translated all meshes')

        return {'FINISHED'}


class TranslateTexturesButton(bpy.types.Operator):
    bl_idname = 'translate.textures'
    bl_label = 'Textures'
    bl_description = "Translates all textures with Google Translate."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # It currently seems to do nothing. This should probably only added when the folder textures really get translated. Currently only the materials are important
        self.report({'INFO'}, 'Translated all textures')
        return {'FINISHED'}

        tools.common.unhide_all()

        translator = Translator()

        for mesh in tools.common.get_meshes_objects():
            to_translate = []
            tools.common.select(mesh)

            for matslot in mesh.material_slots:
                for texslot in bpy.data.materials[matslot.name].texture_slots:
                    if texslot is not None:
                        print(texslot.name)
                        to_translate.append(texslot.name)

            translated = []
            translations = translator.translate(to_translate)
            for translation in translations:
                translated.append(translation.text)

            i = 0
            for matslot in mesh.material_slots:
                for texslot in bpy.data.materials[matslot.name].texture_slots:
                    if texslot is not None:
                        bpy.data.textures[texslot.name].name = translated[i]
                        i += 1

        tools.common.unselect_all()

        self.report({'INFO'}, 'Translated all textures')
        return {'FINISHED'}


class TranslateMaterialsButton(bpy.types.Operator):
    bl_idname = 'translate.materials'
    bl_label = 'Materials'
    bl_description = "Translates all materials with Google Translate."
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tools.common.unhide_all()

        translator = Translator()

        for mesh in tools.common.get_meshes_objects():
            to_translate = []
            tools.common.select(mesh)
            mesh.active_material_index = 0

            for matslot in mesh.material_slots:
                to_translate.append(matslot.name)

            translated = []
            translations = translator.translate(to_translate)
            for translation in translations:
                translated.append(translation.text)

            i = 0
            for index, matslot in enumerate(mesh.material_slots):
                mesh.active_material_index = index
                bpy.context.object.active_material.name = translated[i]
                i += 1

        tools.common.unselect_all()

        self.report({'INFO'}, 'Translated all materials')
        return {'FINISHED'}
