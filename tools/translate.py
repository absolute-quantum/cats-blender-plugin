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
# Edits by: Hotox

import bpy
import tools.common

from googletrans import Translator

mmd_tools_installed = True
try:
    from mmd_tools import utils
    from mmd_tools.translations import DictionaryEnum
except ImportError:
    mmd_tools_installed = False

try:
    dictionary = bpy.props.EnumProperty(
        name='Dictionary',
        items=DictionaryEnum.get_dictionary_items,
        description='Translate names from Japanese to English using selected dictionary',
    )
    self.__translator = DictionaryEnum.get_translator(dictionary)
except Exception as e:
    mmd_tools_installed = False


class TranslateMeshesButton(bpy.types.Operator):
    bl_idname = 'translate.meshes'
    bl_label = 'Meshes'

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

        return{'FINISHED'}


class TranslateTexturesButton(bpy.types.Operator):
    bl_idname = 'translate.textures'
    bl_label = 'Textures'

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tools.common.unhide_all()

        to_translate = []

        objects = bpy.context.selected_editable_objects

        for ob in objects:
            for matslot in ob.material_slots:
                for texslot in bpy.data.materials[matslot.name].texture_slots:
                    if texslot is not None:
                        to_translate.append(texslot.name)

        translator = Translator()
        translated = []
        translations = translator.translate(to_translate)
        for translation in translations:
            translated.append(translation.text)

        i = 0
        for ob in objects:
            for matslot in ob.material_slots:
                for texslot in bpy.data.materials[matslot.name].texture_slots:
                    if texslot is not None:
                        bpy.data.textures[texslot.name].name = translated[i]
                        i += 1

        self.report({'INFO'}, 'Translated all textures')
        return{'FINISHED'}


class TranslateMaterialsButton(bpy.types.Operator):
    bl_idname = 'translate.materials'
    bl_label = 'Materials'

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tools.common.unhide_all()

        to_translate = []

        objects = bpy.context.selected_editable_objects

        for ob in objects:
            ob.active_material_index = 0
            for matslot in ob.material_slots:
                to_translate.append(matslot.name)

        translator = Translator()
        translated = []
        translations = translator.translate(to_translate)
        for translation in translations:
            translated.append(translation.text)

        i = 0
        for ob in objects:
            for index, matslot in enumerate(ob.material_slots):
                ob.active_material_index = index
                bpy.context.object.active_material.name = translated[i]
                i += 1

        self.report({'INFO'}, 'Translated all materials')
        return{'FINISHED'}


class TranslateBonesButton(bpy.types.Operator):
    bl_idname = 'translate.bones'
    bl_label = 'Bones'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if mmd_tools_installed is False:
            self.report({'ERROR'}, 'mmd_tools is not installed, this feature is disabled')
            return {'CANCELLED'}

        tools.common.unhide_all()
        armature = tools.common.get_armature().data

        # first mmd translate
        try:
            dictionary = bpy.props.EnumProperty(
                name='Dictionary',
                items=DictionaryEnum.get_dictionary_items,
                description='Translate names from Japanese to English using selected dictionary',
            )
            self.__translator = DictionaryEnum.get_translator(dictionary)
        except Exception as e:
            self.report({'ERROR'}, 'Failed to load dictionary: %s'%e)
            return {'CANCELLED'}

        for bone in armature.bones:
            bone.name = utils.convertNameToLR(bone.name, True)
            bone.name = self.__translator.translate(bone.name)

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
        return{'FINISHED'}


class TranslateShapekeyButton(bpy.types.Operator):
    bl_idname = 'translate.shapekeys'
    bl_label = 'Shape keys'

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

        return{'FINISHED'}
