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

import re
import bpy
import tools.common

from googletrans import Translator
from mmd_tools_local import utils
from mmd_tools_local.translations import DictionaryEnum


class TranslateShapekeyButton(bpy.types.Operator):
    bl_idname = 'translate.shapekeys'
    bl_label = 'Shape Keys'
    bl_description = "Translates all shape keys with Google Translate."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        tools.common.unhide_all()

        to_translate = []
        translated = []

        for obj in bpy.data.objects:
            if hasattr(obj.data, 'shape_keys'):
                if hasattr(obj.data.shape_keys, 'key_blocks'):
                    for index, shapekey in enumerate(obj.data.shape_keys.key_blocks):
                        to_translate.append(shapekey.name)

        translator = Translator()
        translations = translator.translate(to_translate)
        for translation in translations:
            translated.append(translation.text)

        i = 0
        for obj in bpy.data.objects:
            if hasattr(obj.data, 'shape_keys'):
                if hasattr(obj.data.shape_keys, 'key_blocks'):
                    for index, shapekey in enumerate(obj.data.shape_keys.key_blocks):
                        shapekey.name = translated[i]
                        i += 1

        self.report({'INFO'}, 'Translated ' + str(i) + ' shape keys.')
        return {'FINISHED'}


class TranslateBonesButton(bpy.types.Operator):
    bl_idname = 'translate.bones'
    bl_label = 'Bones'
    bl_description = 'Translates all bones with the build-in dictionary and the untranslated parts with Google Translate.\n'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    dictionary = bpy.props.EnumProperty(
        name='Dictionary',
        items=DictionaryEnum.get_dictionary_items,
        description='Translate names from Japanese to English using selected dictionary',
    )

    @classmethod
    def poll(cls, context):
        if tools.common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        tools.common.unhide_all()
        count = translate_bones(self.dictionary)

        if count[1] == 0:
            self.report({'INFO'}, 'Translated ' + str(count[0]) + ' bones.')
        else:
            self.report({'INFO'}, 'Translated ' + str(count[0]) + ' bones, ' + str(count[1]) + ' of them with Google Tanslate.')
        return {'FINISHED'}


class TranslateMeshesButton(bpy.types.Operator):
    bl_idname = 'translate.meshes'
    bl_label = 'Meshes & Objects'
    bl_description = "Translates all meshes and objects with Google Translate."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        tools.common.unhide_all()

        to_translate = []
        translated = []
        translator = Translator()

        objects = bpy.data.objects
        for obj in objects:
            to_translate.append(obj.name)

        translations = translator.translate(to_translate, src='ja')
        for translation in translations:
            translated.append(translation.text)

        i = 0
        for obj in objects:
            obj.name = translated[i]
            i += 1

        self.report({'INFO'}, 'Translated ' + str(i) + ' meshes and objects.')
        return {'FINISHED'}


class TranslateMaterialsButton(bpy.types.Operator):
    bl_idname = 'translate.materials'
    bl_label = 'Materials'
    bl_description = "Translates all materials with Google Translate."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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

        self.report({'INFO'}, 'Translated ' + str(i) + ' materials.')
        return {'FINISHED'}


class TranslateTexturesButton(bpy.types.Operator):
    bl_idname = 'translate.textures'
    bl_label = 'Textures'
    bl_description = "Translates all textures with Google Translate."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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

        self.report({'INFO'}, 'Translated ' + str(i) + 'textures.')
        return {'FINISHED'}


def translate_bones(dictionary):
    armature = tools.common.get_armature().data
    translator = DictionaryEnum.get_translator(dictionary)
    regex = u'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]+'  # Regex to look for japanese chars

    google_input = []
    google_output = []

    count = [0, 0]

    # Translate with the local mmd_tools dictionary
    for bone in armature.bones:
        translated_name = utils.convertNameToLR(bone.name, True)
        translated_name = translator.translate(translated_name)
        bone.name = translated_name
        count[0] += 1

        # Check if name contains untranslated chars and add them to the list
        match = re.findall(regex, translated_name)
        if match is not None:
            for name in match:
                if name not in google_input:
                    google_input.append(name)

    # Translate the list with google translate
    try:
        translator = Translator()
        translations = translator.translate(google_input)
    except:
        return count

    for translation in translations:
        count[1] += 1
        google_output.append(translation.text.capitalize())

    # Replace all untranslated parts in the bones with translations
    for bone in armature.bones:
        bone_name = bone.name
        match = re.findall(regex, bone_name)
        if match is not None:
            for index, name in enumerate(google_input):
                if name in match:
                    bone.name = bone_name.replace(name, google_output[index])

    return count
