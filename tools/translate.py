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
        steps = 0
        for object in bpy.data.objects:
            if hasattr(object.data, 'shape_keys'):
                if hasattr(object.data.shape_keys, 'key_blocks'):
                    for index, shapekey in enumerate(object.data.shape_keys.key_blocks):
                        steps += 2

        wm = bpy.context.window_manager
        current_step = 0
        wm.progress_begin(current_step, steps)

        tools.common.unhide_all()

        to_translate = []
        translated = []

        for object in bpy.data.objects:
            if hasattr(object.data, 'shape_keys'):
                if hasattr(object.data.shape_keys, 'key_blocks'):
                    for index, shapekey in enumerate(object.data.shape_keys.key_blocks):
                        to_translate.append(shapekey.name)
                        current_step += 1
                        wm.progress_update(current_step)

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
                        current_step += 1
                        wm.progress_update(current_step)
                        i += 1

        wm.progress_end()
        self.report({'INFO'}, 'Translated all shape keys')

        return {'FINISHED'}


class TranslateBonesButton(bpy.types.Operator):
    bl_idname = 'translate.bones'
    bl_label = 'Bones'
    bl_description = "Translates all bones with the build-in dictionary and the untranslated parts with Google Translate."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    dictionary = bpy.props.EnumProperty(
        name='Dictionary',
        items=DictionaryEnum.get_dictionary_items,
        description='Translate names from Japanese to English using selected dictionary',
    )

    def execute(self, context):
        tools.common.unhide_all()
        translate_bones(self.dictionary)

        return {'FINISHED'}


class TranslateMeshesButton(bpy.types.Operator):
    bl_idname = 'translate.meshes'
    bl_label = 'Meshes'
    bl_description = "Translates all meshes with Google Translate."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        tools.common.unhide_all()

        to_translate = []
        translated = []
        translator = Translator()

        objects = bpy.data.objects
        for object in objects:
            if object.type != 'ARMATURE':
                to_translate.append(object.name)

        wm = bpy.context.window_manager
        current_step = 0
        translations = translator.translate(to_translate)
        steps = len(translations)
        wm.progress_begin(current_step, steps)
        for translation in translations:
            translated.append(translation.text)
            current_step += 1
            wm.progress_update(current_step)

        i = 0
        for object in objects:
            if object.type != 'ARMATURE':
                object.name = translated[i]
                i += 1

        wm.progress_end()

        self.report({'INFO'}, 'Translated all meshes')

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
            steps = len(translations)
            wm = bpy.context.window_manager
            current_step = 0
            wm.progress_begin(current_step, steps)
            for translation in translations:
                translated.append(translation.text)
                current_step += 1
                wm.progress_update(current_step)

            i = 0
            for matslot in mesh.material_slots:
                for texslot in bpy.data.materials[matslot.name].texture_slots:
                    if texslot is not None:
                        bpy.data.textures[texslot.name].name = translated[i]
                        i += 1

        tools.common.unselect_all()

        wm.progress_end()
        self.report({'INFO'}, 'Translated all textures')
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
            steps = len(translations)
            wm = bpy.context.window_manager
            current_step = 0
            wm.progress_begin(current_step, steps)
            for translation in translations:
                translated.append(translation.text)
                current_step += 1
                wm.progress_update(current_step)

            i = 0
            for index, matslot in enumerate(mesh.material_slots):
                mesh.active_material_index = index
                bpy.context.object.active_material.name = translated[i]
                i += 1

        tools.common.unselect_all()

        wm.progress_end()
        self.report({'INFO'}, 'Translated all materials')
        return {'FINISHED'}


def translate_bones(dictionary):
    armature = tools.common.get_armature().data
    translator = DictionaryEnum.get_translator(dictionary)
    regex = u'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]+'  # Regex to look for japanese chars

    google_input = []
    google_output = []

    steps = len(armature.bones)
    wm = bpy.context.window_manager
    current_step = 0
    wm.progress_begin(current_step, steps)

    # Translate with the local mmd_tools dictionary
    for bone in armature.bones:
        current_step += 1
        wm.progress_update(current_step)
        translated_name = utils.convertNameToLR(bone.name, True)
        translated_name = translator.translate(translated_name)
        bone.name = translated_name

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
        return

    for translation in translations:
        google_output.append(translation.text.capitalize())

    # Replace all untranslated parts in the bones with translations
    for bone in armature.bones:
        bone_name = bone.name
        match = re.findall(regex, bone_name)
        if match is not None:
            for index, name in enumerate(google_input):
                if name in match:
                    bone.name = bone_name.replace(name, google_output[index])

    wm.progress_end()
