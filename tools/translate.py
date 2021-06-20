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
import copy
import json
import pathlib
import platform
import traceback
import collections
import requests.exceptions

from datetime import datetime, timezone
from collections import OrderedDict

from . import common as Common
from .register import register_wrap
from .. import globs
# from ..googletrans import Translator  # TODO Remove this
from ..extern_tools.google_trans_new.google_trans_new import google_translator
from .translations import t

from mmd_tools_local import translations as mmd_translations

dictionary = {}
dictionary_google = {}

main_dir = pathlib.Path(os.path.dirname(__file__)).parent.resolve()
resources_dir = os.path.join(str(main_dir), "resources")
dictionary_file = os.path.join(resources_dir, "dictionary.json")
dictionary_google_file = os.path.join(resources_dir, "dictionary_google.json")


@register_wrap
class TranslateShapekeyButton(bpy.types.Operator):
    bl_idname = 'cats_translate.shapekeys'
    bl_label = t('TranslateShapekeyButton.label')
    bl_description = t('TranslateShapekeyButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, t('TranslateX.error.wrongVersion'))
            return {'FINISHED'}

        saved_data = Common.SavedData()

        to_translate = []

        for mesh in Common.get_meshes_objects(mode=2):
            if Common.has_shapekeys(mesh):
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if 'vrc.' not in shapekey.name and shapekey.name not in to_translate:
                        to_translate.append(shapekey.name)

        update_dictionary(to_translate, translating_shapes=True, self=self)

        Common.update_shapekey_orders()

        i = 0
        for mesh in Common.get_meshes_objects(mode=2):
            if Common.has_shapekeys(mesh):
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if 'vrc.' not in shapekey.name:
                        shapekey.name, translated = translate(shapekey.name, add_space=True, translating_shapes=True)
                        if translated:
                            i += 1

        Common.ui_refresh()

        saved_data.load()

        self.report({'INFO'}, t('TranslateShapekeyButton.success', number=str(i)))
        return {'FINISHED'}


@register_wrap
class TranslateBonesButton(bpy.types.Operator):
    bl_idname = 'cats_translate.bones'
    bl_label = t('TranslateBonesButton.label')
    bl_description = t('TranslateBonesButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not Common.get_armature():
            return False
        return True

    def execute(self, context):
        to_translate = []
        for armature in Common.get_armature_objects():
            for bone in armature.data.bones:
                to_translate.append(bone.name)

        update_dictionary(to_translate, self=self)

        count = 0
        for armature in Common.get_armature_objects():
            for bone in armature.data.bones:
                bone.name, translated = translate(bone.name)
                if translated:
                    count += 1

        self.report({'INFO'}, t('TranslateBonesButton.success', number=str(count)))
        return {'FINISHED'}


@register_wrap
class TranslateObjectsButton(bpy.types.Operator):
    bl_idname = 'cats_translate.objects'
    bl_label = t('TranslateObjectsButton.label')
    bl_description = t('TranslateObjectsButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, t('TranslateX.error.wrongVersion'))
            return {'FINISHED'}
        to_translate = []
        for obj in Common.get_objects():
            if obj.name not in to_translate:
                to_translate.append(obj.name)
            if obj.type == 'ARMATURE':
                if obj.data and obj.data.name not in to_translate:
                    to_translate.append(obj.data.name)
                if obj.animation_data and obj.animation_data.action:
                    to_translate.append(obj.animation_data.action.name)

        update_dictionary(to_translate, self=self)

        i = 0
        for obj in Common.get_objects():
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

        self.report({'INFO'}, t('TranslateObjectsButton.success', number=str(i)))
        return {'FINISHED'}


@register_wrap
class TranslateMaterialsButton(bpy.types.Operator):
    bl_idname = 'cats_translate.materials'
    bl_label = t('TranslateMaterialsButton.label')
    bl_description = t('TranslateMaterialsButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, t('TranslateX.error.wrongVersion'))
            return {'FINISHED'}

        saved_data = Common.SavedData()

        to_translate = []
        for mesh in Common.get_meshes_objects(mode=2):
            for matslot in mesh.material_slots:
                if matslot.name not in to_translate:
                    to_translate.append(matslot.name)

        update_dictionary(to_translate, self=self)

        i = 0
        for mesh in Common.get_meshes_objects(mode=2):
            Common.set_active(mesh)
            for index, matslot in enumerate(mesh.material_slots):
                mesh.active_material_index = index
                if bpy.context.object.active_material:
                    bpy.context.object.active_material.name, translated = translate(bpy.context.object.active_material.name)
                    if translated:
                        i += 1

        saved_data.load()
        self.report({'INFO'}, t('TranslateMaterialsButton.success', number=str(i)))
        return {'FINISHED'}


# @register_wrap
# class TranslateTexturesButton(bpy.types.Operator):
#     bl_idname = 'cats_translate.textures'
#     bl_label = t('TranslateTexturesButton.label')
#     bl_description = t('TranslateTexturesButton.desc')
#     bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
#
#     def execute(self, context):
#         # It currently seems to do nothing. This should probably only added when the folder textures really get translated. Currently only the materials are important
#         self.report({'INFO'}, t('TranslateTexturesButton.success_alt'))
#         return {'FINISHED'}
#
#         translator = google_translator()
#
#         to_translate = []
#         for ob in Common.get_objects():
#             if ob.type == 'MESH':
#                 for matslot in ob.material_slots:
#                     for texslot in bpy.data.materials[matslot.name].texture_slots:
#                         if texslot:
#                             print(texslot.name)
#                             to_translate.append(texslot.name)
#
#         translated = []
#         try:
#             translations = translator.translate(to_translate, lang_tgt='en')
#         except SSLError:
#             self.report({'ERROR'}, t('TranslateTexturesButton.error.noInternet'))
#             return {'FINISHED'}
#
#         for translation in translations:
#             translated.append(translation)
#
#         i = 0
#         for ob in Common.get_objects():
#             if ob.type == 'MESH':
#                 for matslot in ob.material_slots:
#                     for texslot in bpy.data.materials[matslot.name].texture_slots:
#                         if texslot:
#                             bpy.data.textures[texslot.name].name = translated[i]
#                             i += 1
#
#         Common.unselect_all()
#
#         self.report({'INFO'}, t('TranslateTexturesButton.success', number=str(i)))
#         return {'FINISHED'}


@register_wrap
class TranslateAllButton(bpy.types.Operator):
    bl_idname = 'cats_translate.all'
    bl_label = t('TranslateAllButton.label')
    bl_description = t('TranslateAllButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if bpy.app.version < (2, 79, 0):
            self.report({'ERROR'}, t('TranslateX.error.wrongVersion'))
            return {'FINISHED'}

        error_shown = False

        try:
            if Common.get_armature():
                bpy.ops.cats_translate.bones('INVOKE_DEFAULT')
        except RuntimeError as e:
            self.report({'ERROR'}, str(e).replace('Error: ', ''))
            error_shown = True

        try:
            bpy.ops.cats_translate.shapekeys('INVOKE_DEFAULT')
        except RuntimeError as e:
            if not error_shown:
                self.report({'ERROR'}, str(e).replace('Error: ', ''))
                error_shown = True

        try:
            bpy.ops.cats_translate.objects('INVOKE_DEFAULT')
        except RuntimeError as e:
            if not error_shown:
                self.report({'ERROR'}, str(e).replace('Error: ', ''))
                error_shown = True

        try:
            bpy.ops.cats_translate.materials('INVOKE_DEFAULT')
        except RuntimeError as e:
            if not error_shown:
                self.report({'ERROR'}, str(e).replace('Error: ', ''))
                error_shown = True

        if error_shown:
            return {'CANCELLED'}
        self.report({'INFO'}, t('TranslateAllButton.success'))
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
            # print('DICTIONARY LOADED!')
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
                    or 'translations_full' not in dictionary_google:
                reset_google_dict()
            else:
                for name, trans in dictionary_google.get('translations').items():
                    if not name:
                        continue

                    if name in temp_dict.keys():
                        print(name, 'ALREADY IN INTERNAL DICT!')
                        continue

                    temp_dict[name] = trans

            # print('GOOGLE DICTIONARY LOADED!')
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

    # Translate the rest with google translate
    print('GOOGLE DICT UPDATE!')
    translator = google_translator(url_suffix='com')
    token_tries = 0
    while True:
        try:
            translations = [translator.translate(text, lang_src='ja', lang_tgt='en').strip() for text in google_input]
            break
        except (requests.exceptions.ConnectionError, ConnectionRefusedError):
            print('CONNECTION TO GOOGLE FAILED!')
            if self:
                self.report({'ERROR'}, t('update_dictionary.error.cantConnect'))
            return
        except json.JSONDecodeError:
            if self:
                self.report({'ERROR'}, t('update_dictionary.error.temporaryBan') + t('update_dictionary.error.catsTranslated'))
            print('YOU GOT BANNED BY GOOGLE!')
            return
        except RuntimeError as e:
            error = Common.html_to_text(str(e))
            if self:
                if 'Please try your request again later' in error:
                    self.report({'ERROR'}, t('update_dictionary.error.temporaryBan') + t('update_dictionary.error.catsTranslated'))
                    print('YOU GOT BANNED BY GOOGLE!')
                    return

                if 'Error 403' in error:
                    self.report({'ERROR'}, t('update_dictionary.error.cantAccess') + t('update_dictionary.error.catsTranslated'))
                    print('NO PERMISSION TO USE GOOGLE TRANSLATE!')
                    return

                self.report({'ERROR'}, t('update_dictionary.error.errorMsg') + t('update_dictionary.error.catsTranslated') + '\n' + '\nGoogle: ' + error)
            print('', 'You got an error message from Google:', error, '')
            return
        except AttributeError:
            # If the translator wasn't able to create a stable connection to Google, just retry it again
            # This is an issue with Google since Nov 2020: https://github.com/ssut/py-googletrans/issues/234
            token_tries += 1
            if token_tries < 3:
                print('RETRY', token_tries)
                translator = google_translator(url_suffix='com')
                continue

            # If if didn't work after 20 tries, just quit
            # The response from Google was printed into "cats/resources/google-response.txt"
            if self:
                self.report({'ERROR'}, t('update_dictionary.error.apiChanged'))
            print('ERROR: GOOGLE API CHANGED!')
            print(traceback.format_exc())
            return

    # Update the dictionaries
    for i, translation in enumerate(translations):
        name = google_input[i]

        if use_google_only:
            dictionary_google['translations_full'][name] = translation
        else:
            # Capitalize words
            translation_words = translation.split(' ')
            translation_words = [word.capitalize() for word in translation_words]
            translation = ' '.join(translation_words)

            dictionary[name] = translation
            dictionary_google['translations'][name] = translation

        print(google_input[i], '->', translation)

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

    # print('"' + pre_translation + '"')
    # print('"' + to_translate + '"')

    return to_translate, pre_translation != to_translate


def fix_jp_chars(name):
    for values in mmd_translations.jp_half_to_full_tuples:
        if values[0] in name:
            name = name.replace(values[0], values[1])
    return name


def reset_google_dict():
    global dictionary_google
    dictionary_google = OrderedDict()

    now_utc = datetime.now(timezone.utc).strftime(globs.time_format)

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
