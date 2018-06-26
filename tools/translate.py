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
import os
import bpy
import csv
import pathlib
import tools.common
import requests.exceptions
import mmd_tools_local.translations

from googletrans import Translator
from collections import OrderedDict

dictionary = None


class TranslateShapekeyButton(bpy.types.Operator):
    bl_idname = 'translate.shapekeys'
    bl_label = 'Translate Shape Keys'
    bl_description = "Translates all shape keys with Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, 'You need Blender 2.79 or higher for this function.')
            return {'FINISHED'}

        tools.common.unhide_all()

        to_translate = []

        for mesh in tools.common.get_meshes_objects(mode=2):
            if mesh.data.shape_keys and mesh.data.shape_keys.key_blocks:
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if 'vrc.' not in shapekey.name and shapekey.name not in to_translate:
                        to_translate.append(shapekey.name)

        if not update_dictionary(to_translate):
            self.report({'ERROR'}, 'Could not connect to Google. Some parts could not be translated.')

        tools.common.update_shapekey_orders()

        i = 0
        for mesh in tools.common.get_meshes_objects(mode=2):
            if mesh.data.shape_keys and mesh.data.shape_keys.key_blocks:
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if 'vrc.' not in shapekey.name:
                        shapekey.name, translated = translate(shapekey.name, add_space=True)
                        if translated:
                            i += 1

        self.report({'INFO'}, 'Translated ' + str(i) + ' shape keys.')
        return {'FINISHED'}


class TranslateBonesButton(bpy.types.Operator):
    bl_idname = 'translate.bones'
    bl_label = 'Translate Bones'
    bl_description = 'Translates all bones with the build-in dictionary and the untranslated parts with Google Translate'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not tools.common.get_armature():
            return False
        return True

    def execute(self, context):
        tools.common.unhide_all()

        to_translate = []
        for bone in tools.common.get_armature().data.bones:
            to_translate.append(bone.name)

        if not update_dictionary(to_translate):
            self.report({'ERROR'}, 'Could not connect to Google. Some parts could not be translated.')

        count = 0
        for bone in tools.common.get_armature().data.bones:
            bone.name, translated = translate(bone.name)
            if translated:
                count += 1

        self.report({'INFO'}, 'Translated ' + str(count) + ' bones.')
        return {'FINISHED'}


class TranslateObjectsButton(bpy.types.Operator):
    bl_idname = 'translate.objects'
    bl_label = 'Translate Meshes & Objects'
    bl_description = "Translates all meshes and objects with Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, 'You need Blender 2.79 or higher for this function.')
            return {'FINISHED'}

        tools.common.unhide_all()

        to_translate = []
        for obj in bpy.data.objects:
            if obj.name not in to_translate:
                to_translate.append(obj.name)
            if obj.type == 'ARMATURE':
                if obj.data and obj.data.name not in to_translate:
                    to_translate.append(obj.data.name)
                if obj.animation_data and obj.animation_data.action:
                    to_translate.append(obj.animation_data.action.name)

        if not update_dictionary(to_translate):
            self.report({'ERROR'}, 'Could not connect to Google. Some parts could not be translated.')

        i = 0
        for obj in bpy.data.objects:
            obj.name, translated = translate(obj.name)
            if translated:
                i += 1

            if obj.type == 'ARMATURE':
                if obj.data:
                    obj.data.name, translated = translate(obj.data.name)
                    if translated:
                        i += 1

                if obj.animation_data and obj.animation_data.action:
                    obj.animation_data.action.name, translated = translate(obj.animation_data.action.name)
                    if translated:
                        i += 1

        self.report({'INFO'}, 'Translated ' + str(i) + ' meshes and objects.')
        return {'FINISHED'}


class TranslateMaterialsButton(bpy.types.Operator):
    bl_idname = 'translate.materials'
    bl_label = 'Translate Materials'
    bl_description = "Translates all materials with Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, 'You need Blender 2.79 or higher for this function.')
            return {'FINISHED'}

        tools.common.unhide_all()

        to_translate = []
        for mesh in tools.common.get_meshes_objects(mode=2):
            for matslot in mesh.material_slots:
                if matslot.name not in to_translate:
                    to_translate.append(matslot.name)

        if not update_dictionary(to_translate):
            self.report({'ERROR'}, 'Could not connect to Google. Some parts could not be translated.')

        i = 0
        for mesh in tools.common.get_meshes_objects(mode=2):
            tools.common.select(mesh)
            for index, matslot in enumerate(mesh.material_slots):
                mesh.active_material_index = index
                if bpy.context.object.active_material:
                    bpy.context.object.active_material.name, translated = translate(bpy.context.object.active_material.name)
                    if translated:
                        i += 1

        tools.common.unselect_all()

        self.report({'INFO'}, 'Translated ' + str(i) + ' materials.')
        return {'FINISHED'}


class TranslateTexturesButton(bpy.types.Operator):
    bl_idname = 'translate.textures'
    bl_label = 'Translate Textures'
    bl_description = "Translates all textures with Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        # It currently seems to do nothing. This should probably only added when the folder textures really get translated. Currently only the materials are important
        self.report({'INFO'}, 'Translated all textures')
        return {'FINISHED'}

        tools.common.unhide_all()

        translator = Translator()

        to_translate = []
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                for matslot in ob.material_slots:
                    for texslot in bpy.data.materials[matslot.name].texture_slots:
                        if texslot:
                            print(texslot.name)
                            to_translate.append(texslot.name)

        translated = []
        try:
            translations = translator.translate(to_translate)
        except SSLError:
            self.report({'ERROR'}, 'Could not connect to Google. Please check your internet connection.')
            return {'FINISHED'}

        for translation in translations:
            translated.append(translation.text)

        i = 0
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                for matslot in ob.material_slots:
                    for texslot in bpy.data.materials[matslot.name].texture_slots:
                        if texslot:
                            bpy.data.textures[texslot.name].name = translated[i]
                            i += 1

        tools.common.unselect_all()

        self.report({'INFO'}, 'Translated ' + str(i) + 'textures.')
        return {'FINISHED'}


class TranslateAllButton(bpy.types.Operator):
    bl_idname = 'translate.all'
    bl_label = 'Translate Everything'
    bl_description = "Translates everything"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, 'You need Blender 2.79 or higher for this function.')
            return {'FINISHED'}

        bpy.ops.translate.bones('INVOKE_DEFAULT')
        bpy.ops.translate.shapekeys('INVOKE_DEFAULT')
        bpy.ops.translate.objects('INVOKE_DEFAULT')
        bpy.ops.translate.materials('INVOKE_DEFAULT')

        self.report({'INFO'}, 'Translated everything.')
        return {'FINISHED'}


def load_translations():
    main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
    resources_dir = os.path.join(str(main_dir), "resources")
    supporters_file = os.path.join(resources_dir, "dictionary.csv")

    global dictionary
    dictionary = OrderedDict()
    temp_dict = {}

    try:
        with open(supporters_file) as file:
            data = csv.reader(file, delimiter=',')
            for row in data:
                name = row[0]
                translation = row[1]

                if translation.startswith(' "'):
                    translation = translation[2:-1]
                if translation.startswith('"'):
                    translation = translation[1:-1]

                temp_dict[name] = translation
            print('DICTIONARY LOADED!')
    except FileNotFoundError:
        print('DICTIONARY NOT FOUND!')
        pass

    for translation in mmd_tools_local.translations.jp_to_en_tuples:
        if translation[0] not in temp_dict.keys() and translation[0] != '.':
            temp_dict[translation[0]] = translation[1]
            # print('"' + translation[0] + '" - "' + translation[1] + '"')

    # Sort dictionary
    for key in sorted(temp_dict, key=lambda k: len(k), reverse=True):
        dictionary[key] = temp_dict[key]

    # for key in dictionary.keys():
    #     print('"' + key + '" - "' + dictionary[key] + '"')


def update_dictionary(to_translate_list):
    global dictionary
    translator = Translator()
    regex = u'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]+'  # Regex to look for japanese chars

    # Check if single string is given and put it into an array
    if type(to_translate_list) is str:
        to_translate_list = [to_translate_list]

    google_input = []

    # Translate every
    for to_translate in to_translate_list:
        length = len(to_translate)
        translated_count = 0

        to_translate = fix_jp_chars(to_translate)

        # Remove spaces, there are no spaces in japan
        match = re.findall(regex, to_translate)
        if match:
            to_translate = to_translate.replace(' ', '')

        # Translate with internal dictionary
        for key, value in dictionary.items():
            if key in to_translate:
                to_translate = to_translate.replace(key, value)

                # Check if string is fully translated
                translated_count += len(key)
                if translated_count >= length:
                    break

        # If not fully translated, translate the rest with Google
        if translated_count < length:

            match = re.findall(regex, to_translate)
            if match:
                for name in match:
                    if name not in google_input and name not in dictionary.keys():
                        google_input.append(name)

    if not google_input:
        print('GOOGLE LIST EMPTY')
        return True

    # Translate the list with google translate
    print('GOOGLE DICT UPDATE!')
    try:
        translations = translator.translate(google_input)
    except requests.exceptions.ConnectionError:
        print('DICTIONARY UPDATE FAILED!')
        return False

    # Update the dictionary
    for i, translation in enumerate(translations):
        dictionary[google_input[i]] = translation.text.capitalize()
        print(google_input[i], translation.text.capitalize())

    print('DICTIONARY UPDATE SUCCEEDED!')
    return True


def translate(to_translate, add_space=False):
    global dictionary
    regex = u'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]+'  # Regex to look for japanese chars

    pre_translation = to_translate
    length = len(to_translate)
    translated_count = 0

    addition = ''
    if add_space:
        addition = ' '

    to_translate = fix_jp_chars(to_translate)

    # Remove spaces, there are no spaces in japan
    match = re.findall(regex, to_translate)
    if match:
        to_translate = to_translate.replace(' ', '')

    # Translate with internal dictionary
    for key, value in dictionary.items():
        if key in to_translate:
            if value:
                to_translate = to_translate.replace(key, addition + value)
            else:
                to_translate = to_translate.replace(key, value)

            # Check if string is fully translated
            translated_count += len(key)
            if translated_count >= length:
                break

    to_translate = to_translate.replace('.L', '_L').replace('.R', '_R').replace('  ', ' ').strip()

    # print(to_translate)

    return to_translate, pre_translation != to_translate


def fix_jp_chars(name):
    for values in mmd_tools_local.translations.jp_half_to_full_tuples:
        if values[0] in name:
            name = name.replace(values[0], values[1])
    return name
