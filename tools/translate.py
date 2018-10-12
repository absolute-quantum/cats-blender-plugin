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
import collections
import copy
import json
import re
import os
import bpy
import pathlib
import tools.common
import requests.exceptions
import mmd_tools_local.translations

from datetime import datetime, timezone
from googletrans import Translator
from collections import OrderedDict

dictionary = None
dictionary_google = None

translation_splitter = "---"
time_format = "%Y-%m-%d %H:%M:%S"

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")
dictionary_file = os.path.join(resources_dir, "dictionary.json")
dictionary_google_file = os.path.join(resources_dir, "dictionary_google.json")


class TranslateShapekeyButton(bpy.types.Operator):
    bl_idname = 'translate.shapekeys'
    bl_label = 'Translate Shape Keys'
    bl_description = "Translates all shape keys using the internal dictionary and Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, 'You need Blender 2.79 or higher for this function.')
            return {'FINISHED'}

        to_translate = []

        for mesh in tools.common.get_meshes_objects(mode=2):
            if tools.common.has_shapekeys(mesh):
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if 'vrc.' not in shapekey.name and shapekey.name not in to_translate:
                        to_translate.append(shapekey.name)

        update_dictionary(to_translate, translating_shapes=True, self=self)

        tools.common.update_shapekey_orders()

        i = 0
        for mesh in tools.common.get_meshes_objects(mode=2):
            if tools.common.has_shapekeys(mesh):
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if 'vrc.' not in shapekey.name:
                        shapekey.name, translated = translate(shapekey.name, add_space=True, translating_shapes=True)
                        if translated:
                            i += 1

        self.report({'INFO'}, 'Translated ' + str(i) + ' shape keys.')
        return {'FINISHED'}


class TranslateBonesButton(bpy.types.Operator):
    bl_idname = 'translate.bones'
    bl_label = 'Translate Bones'
    bl_description = "Translates all bones using the internal dictionary and Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not tools.common.get_armature():
            return False
        return True

    def execute(self, context):
        to_translate = []
        for armature in tools.common.get_armature_objects():
            for bone in armature.data.bones:
                to_translate.append(bone.name)

        update_dictionary(to_translate, self=self)

        count = 0
        for armature in tools.common.get_armature_objects():
            for bone in armature.data.bones:
                bone.name, translated = translate(bone.name)
                if translated:
                    count += 1

        self.report({'INFO'}, 'Translated ' + str(count) + ' bones.')
        return {'FINISHED'}


class TranslateObjectsButton(bpy.types.Operator):
    bl_idname = 'translate.objects'
    bl_label = 'Translate Meshes & Objects'
    bl_description = "Translates all meshes and objects using the internal dictionary and Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, 'You need Blender 2.79 or higher for this function.')
            return {'FINISHED'}
        to_translate = []
        for obj in bpy.data.objects:
            if obj.name not in to_translate:
                to_translate.append(obj.name)
            if obj.type == 'ARMATURE':
                if obj.data and obj.data.name not in to_translate:
                    to_translate.append(obj.data.name)
                if obj.animation_data and obj.animation_data.action:
                    to_translate.append(obj.animation_data.action.name)

        update_dictionary(to_translate, self=self)

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
    bl_description = "Translates all materials using the internal dictionary and Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, 'You need Blender 2.79 or higher for this function.')
            return {'FINISHED'}

        to_translate = []
        for mesh in tools.common.get_meshes_objects(mode=2):
            for matslot in mesh.material_slots:
                if matslot.name not in to_translate:
                    to_translate.append(matslot.name)

        update_dictionary(to_translate, self=self)

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
    bl_description = "Translates all textures using the internal dictionary and Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        # It currently seems to do nothing. This should probably only added when the folder textures really get translated. Currently only the materials are important
        self.report({'INFO'}, 'Translated all textures')
        return {'FINISHED'}

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
    bl_description = "Translates everything using the internal dictionary and Google Translate"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, 'You need Blender 2.79 or higher for this function.')
            return {'FINISHED'}

        error_shown = False

        try:
            if tools.common.get_armature():
                bpy.ops.translate.bones('INVOKE_DEFAULT')
        except RuntimeError as e:
            self.report({'ERROR'}, str(e).replace('Error: ', ''))
            error_shown = True

        try:
            bpy.ops.translate.shapekeys('INVOKE_DEFAULT')
        except RuntimeError as e:
            if not error_shown:
                self.report({'ERROR'}, str(e).replace('Error: ', ''))
                error_shown = True

        try:
            bpy.ops.translate.objects('INVOKE_DEFAULT')
        except RuntimeError as e:
            if not error_shown:
                self.report({'ERROR'}, str(e).replace('Error: ', ''))
                error_shown = True

        try:
            bpy.ops.translate.materials('INVOKE_DEFAULT')
        except RuntimeError as e:
            if not error_shown:
                self.report({'ERROR'}, str(e).replace('Error: ', ''))
                error_shown = True

        if error_shown:
            return {'CANCELLED'}
        self.report({'INFO'}, 'Translated everything.')
        return {'FINISHED'}


# Loads the dictionaries at the start of blender
def load_translations():
    global dictionary
    dictionary = OrderedDict()
    temp_dict = OrderedDict()
    dict_found = False

    # Load internal dictionary
    try:
        with open(dictionary_file, encoding="utf8") as file:
            temp_dict = json.load(file, object_pairs_hook=collections.OrderedDict)
            dict_found = True
            print('DICTIONARY LOADED!')
    except FileNotFoundError:
        print('DICTIONARY NOT FOUND!')
        pass
    except json.decoder.JSONDecodeError:
        print("ERROR FOUND IN DICTIONARY")
        pass

    # Load local google dictionary and add it to the temp dict
    try:
        with open(dictionary_google_file, encoding="utf8") as file:
            global dictionary_google
            dictionary_google = json.load(file, object_pairs_hook=collections.OrderedDict)

            if 'created' not in dictionary_google \
                    or 'translations' not in dictionary_google \
                    or 'translations_full' not in dictionary_google \
                    or google_dict_too_old():
                reset_google_dict()
            else:
                for name, trans in dictionary_google.get('translations').items():
                    if not name:
                        continue

                    if name in temp_dict.keys():
                        print(name, 'ALREADY IN INTERNAL DICT!')
                        continue

                    temp_dict[name] = trans

            print('GOOGLE DICTIONARY LOADED!')
    except FileNotFoundError:
        print('GOOGLE DICTIONARY NOT FOUND!')
        reset_google_dict()
        pass
    except json.decoder.JSONDecodeError:
        print("ERROR FOUND IN GOOOGLE DICTIONARY")
        reset_google_dict()
        pass

    # Sort temp dictionary by lenght and put it into the global dict
    for key in sorted(temp_dict, key=lambda k: len(k), reverse=True):
        dictionary[key] = temp_dict[key]

    # for key, value in dictionary.items():
    #     print('"' + key + '" - "' + value + '"')

    return dict_found


def update_dictionary(to_translate_list, translating_shapes=False, self=None):
    global dictionary, dictionary_google
    regex = u'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]+'  # Regex to look for japanese chars

    use_google_only = False
    if translating_shapes and bpy.context.scene.use_google_only:
        use_google_only = True

    # Check if single string is given and put it into an array
    if type(to_translate_list) is str:
        to_translate_list = [to_translate_list]

    google_input = []

    # Translate everything
    for to_translate in to_translate_list:
        length = len(to_translate)
        translated_count = 0

        to_translate = fix_jp_chars(to_translate)

        # Translate shape keys with Google Translator only, if the user chose this
        if use_google_only:
            # If name doesn't contain any jp chars, don't translate
            if not re.findall(regex, to_translate):
                continue

            translated = False
            for key, value in dictionary_google.get('translations_full').items():
                if to_translate == key and value:
                    translated = True

            if not translated:
                google_input.append(to_translate)

        # Translate with internal dictionary
        else:
            for key, value in dictionary.items():
                if key in to_translate:
                    if value:
                        to_translate = to_translate.replace(key, value)
                    else:
                        continue

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
        # print('NO GOOGLE TRANSLATIONS')
        return

    # Translate the list with google translate
    print('GOOGLE DICT UPDATE!')
    translator = Translator()
    try:
        translations = translator.translate(google_input)
    except requests.exceptions.ConnectionError:
        print('CONNECTION TO GOOGLE FAILED!')
        if self:
            self.report({'ERROR'}, 'Could not connect to Google. Some parts could not be translated.')
        return
    except json.JSONDecodeError:
        if self:
            self.report({'ERROR'}, 'It looks like you got banned from Google Translate temporarily!'
                        '\nCats translated what it could with the local dictionary,'
                        '\nbut you will have to try again later for the Google translations.')
        print('YOU GOT BANNED BY GOOGLE!')
        return
    except RuntimeError as e:
        error = tools.common.html_to_text(str(e))
        if self:
            if 'Please try your request again later' in error:
                self.report({'ERROR'}, 'It looks like you got banned from Google Translate temporarily!'
                                       '\nCats translated what it could with the local dictionary, but you will have to try again later for the Google translations.')
                print('YOU GOT BANNED BY GOOGLE!')
                return

            if 'Error 403' in error:
                self.report({'ERROR'}, 'Cats was not able to access Google Translate!'
                                       '\nCats translated what it could with the local dictionary, but you will have to try again later for the Google translations.')
                print('NO PERMISSION TO USE GOOGLE TRANSLATE!')
                return

            self.report({'ERROR'}, 'You got an error message from Google Translate!'
                                   '\nCats translated what it could with the local dictionary, but you will have to try again later for the Google translations.'
                                   '\n'
                                   '\nGoogle: ' + error)
        print('', 'You got an error message from Google:', error, '')
        return

    # Update the dictionaries
    for i, translation in enumerate(translations):
        name = google_input[i]

        if use_google_only:
            dictionary_google['translations_full'][name] = translation.text
        else:
            translated_name = translation.text.capitalize()
            dictionary[name] = translated_name
            dictionary_google['translations'][name] = translated_name

        print(google_input[i], translation.text.capitalize())

    # Sort dictionary
    temp_dict = copy.deepcopy(dictionary)
    dictionary = OrderedDict()
    for key in sorted(temp_dict, key=lambda k: len(k), reverse=True):
        dictionary[key] = temp_dict[key]

    # Save the google dict locally
    save_google_dict()

    print('DICTIONARY UPDATE SUCCEEDED!')
    return


def translate(to_translate, add_space=False, translating_shapes=False):
    global dictionary

    pre_translation = to_translate
    length = len(to_translate)
    translated_count = 0

    # Figure out whether to use google only or not
    use_google_only = False
    if translating_shapes and bpy.context.scene.use_google_only:
        use_google_only = True

    # Add space for shape keys
    addition = ''
    if add_space:
        addition = ' '

    # Convert half chars into full chars
    to_translate = fix_jp_chars(to_translate)

    # Translate shape keys with Google Translator only, if the user chose this
    if use_google_only:
        for key, value in dictionary_google.get('translations_full').items():
            if to_translate == key and value:
                to_translate = value

    # Translate with internal dictionary
    else:
        for key, value in dictionary.items():
            if key in to_translate:
                # If string is empty, don't replace it. This will be done at the end
                if not value:
                    continue

                to_translate = to_translate.replace(key, addition + value)

                # Check if string is fully translated
                translated_count += len(key)
                if translated_count >= length:
                    break

    to_translate = to_translate.replace('.L', '_L').replace('.R', '_R').replace('  ', ' ').replace('し', '').replace('っ', '').strip()

    # print(to_translate)

    return to_translate, pre_translation != to_translate


def fix_jp_chars(name):
    for values in mmd_tools_local.translations.jp_half_to_full_tuples:
        if values[0] in name:
            name = name.replace(values[0], values[1])
    return name


def google_dict_too_old():
    created = datetime.strptime(dictionary_google.get('created'), time_format)
    utc_now = datetime.strptime(datetime.now(timezone.utc).strftime(time_format), time_format)

    time_delta = abs((utc_now - created).days)

    print('DAYS SINCE GOOGLE DICT CREATION:', time_delta)

    if time_delta <= 30:
        return False

    print('DICT TOO OLD')
    return True


def reset_google_dict():
    global dictionary_google
    dictionary_google = OrderedDict()

    now_utc = datetime.now(timezone.utc).strftime(time_format)

    dictionary_google['created'] = now_utc
    dictionary_google['translations'] = {}
    dictionary_google['translations_full'] = {}

    save_google_dict()
    print('GOOGLE DICT RESET')


def save_google_dict():
    with open(dictionary_google_file, 'w', encoding="utf8") as outfile:
        json.dump(dictionary_google, outfile, ensure_ascii=False, indent=4)

# def cvs_to_json():
#     temp_dict = OrderedDict()
#
#     # Load internal dictionary
#     try:
#         with open(dictionary_file, encoding="utf8") as file:
#             data = csv.reader(file, delimiter=',')
#             for row in data:
#                 name = fix_jp_chars(str(row[0]))
#                 translation = row[1]
#
#                 if translation.startswith(' "'):
#                     translation = translation[2:-1]
#                 if translation.startswith('"'):
#                     translation = translation[1:-1]
#
#                 temp_dict[name] = translation
#             print('DICTIONARY LOADED!')
#     except FileNotFoundError:
#         print('DICTIONARY NOT FOUND!')
#         pass
#
#     # # Create json from cvs
#     dictionary_file_new = os.path.join(resources_dir, "dictionary2.json")
#     with open(dictionary_file_new, 'w', encoding="utf8") as outfile:
#         json.dump(temp_dict, outfile, ensure_ascii=False, indent=4)
