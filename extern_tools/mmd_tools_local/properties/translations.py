# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple

import bpy
from mmd_tools_local.core.translations import (FnTranslations,
                                         MMDTranslationElementType)
from mmd_tools_local.translations import DictionaryEnum

MMD_TRANSLATION_ELEMENT_TYPE_ENUM_ITEMS = [
    (MMDTranslationElementType.BONE.name, MMDTranslationElementType.BONE.value, 'Bones', 1),
    (MMDTranslationElementType.MORPH.name, MMDTranslationElementType.MORPH.value, 'Morphs', 2),
    (MMDTranslationElementType.MATERIAL.name, MMDTranslationElementType.MATERIAL.value, 'Materials', 4),
    (MMDTranslationElementType.DISPLAY.name, MMDTranslationElementType.DISPLAY.value, 'Display frames', 8),
    (MMDTranslationElementType.PHYSICS.name, MMDTranslationElementType.PHYSICS.value, 'Rigidbodies and joints', 16),
    (MMDTranslationElementType.INFO.name, MMDTranslationElementType.INFO.value, 'Model name and comments', 32),
]


class MMDTranslationElement(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(items=MMD_TRANSLATION_ELEMENT_TYPE_ENUM_ITEMS)
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    data_path: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    name_j: bpy.props.StringProperty()
    name_e: bpy.props.StringProperty()


class MMDTranslationElementIndex(bpy.types.PropertyGroup):
    value: bpy.props.IntProperty()


BATCH_OPERATION_SCRIPT_PRESETS: Dict[str, Tuple[str, str, str, int]] = {
    'NOTHING': ('', '', '', 1),
    'CLEAR': (None, 'Clear', '""', 10),
    'TO_ENGLISH': ('BLENDER', 'Translate to English', 'to_english(name)', 2),
    'TO_MMD_LR': ('JAPANESE', 'Blender L/R to MMD L/R', 'to_mmd_lr(name)', 3),
    'TO_BLENDER_LR': ('BLENDER', 'MMD L/R to Blender L/R', 'to_blender_lr(name_j)', 4),
    'RESTORE_BLENDER': ('BLENDER', 'Restore Blender Names', 'org_name', 5),
    'RESTORE_JAPANESE': ('JAPANESE', 'Restore Japanese MMD Names', 'org_name_j', 6),
    'RESTORE_ENGLISH': ('ENGLISH', 'Restore English MMD Names', 'org_name_e', 7),
    'ENGLISH_IF_EMPTY_JAPANESE': (None, 'Copy English MMD Names, if empty copy Japanese MMD Name', 'name_e if name_e else name_j', 8),
    'JAPANESE_IF_EMPTY_ENGLISH': (None, 'Copy Japanese MMD Names, if empty copy English MMD Name', 'name_j if name_j else name_e', 9),
}

BATCH_OPERATION_SCRIPT_PRESET_ITEMS: List[Tuple[str, str, str, int]] = [
    (k, t[1], t[2], t[3])
    for k, t in BATCH_OPERATION_SCRIPT_PRESETS.items()
]


class MMDTranslation(bpy.types.PropertyGroup):
    @staticmethod
    def _update_index(mmd_translation: 'MMDTranslation', _context):
        FnTranslations.update_index(mmd_translation)

    @staticmethod
    def _collect_data(mmd_translation: 'MMDTranslation', _context):
        FnTranslations.collect_data(mmd_translation)

    @staticmethod
    def _update_query(mmd_translation: 'MMDTranslation', _context):
        FnTranslations.update_query(mmd_translation)

    @staticmethod
    def _update_batch_operation_script_preset(mmd_translation: 'MMDTranslation', _context):
        if mmd_translation.batch_operation_script_preset == 'NOTHING':
            return

        id2scripts: Dict[str, str] = {i[0]: i[2] for i in BATCH_OPERATION_SCRIPT_PRESET_ITEMS}

        batch_operation_script = id2scripts.get(mmd_translation.batch_operation_script_preset)
        if batch_operation_script is None:
            return

        mmd_translation.batch_operation_script = batch_operation_script
        batch_operation_target = BATCH_OPERATION_SCRIPT_PRESETS[mmd_translation.batch_operation_script_preset][0]
        if batch_operation_target:
            mmd_translation.batch_operation_target = batch_operation_target

    translation_elements: bpy.props.CollectionProperty(type=MMDTranslationElement)
    filtered_translation_element_indices_active_index: bpy.props.IntProperty(update=_update_index.__func__)
    filtered_translation_element_indices: bpy.props.CollectionProperty(type=MMDTranslationElementIndex)

    filter_japanese_blank: bpy.props.BoolProperty(name='Japanese Blank', default=False, update=_update_query.__func__)
    filter_english_blank: bpy.props.BoolProperty(name='English Blank', default=False, update=_update_query.__func__)
    filter_restorable: bpy.props.BoolProperty(name='Restorable', default=False, update=_update_query.__func__)
    filter_selected: bpy.props.BoolProperty(name='Selected', default=False, update=_update_query.__func__)
    filter_visible: bpy.props.BoolProperty(name='Visible', default=False, update=_update_query.__func__)
    filter_types: bpy.props.EnumProperty(
        items=MMD_TRANSLATION_ELEMENT_TYPE_ENUM_ITEMS,
        default={'BONE', 'MORPH', 'MATERIAL', 'DISPLAY', 'PHYSICS', },
        options={'ENUM_FLAG'},
        update=_update_query.__func__,
    )

    dictionary: bpy.props.EnumProperty(
        items=DictionaryEnum.get_dictionary_items,
        name='Dictionary',
    )

    batch_operation_target: bpy.props.EnumProperty(
        items=[
            ('BLENDER', 'Blender Name (name)', '', 1),
            ('JAPANESE', 'Japanese MMD Name (name_j)', '', 2),
            ('ENGLISH', 'English MMD Name (name_e)', '', 3),
        ],
        name='Operation Target',
        default='JAPANESE',
    )

    batch_operation_script_preset: bpy.props.EnumProperty(
        items=BATCH_OPERATION_SCRIPT_PRESET_ITEMS,
        name='Operation Script Preset',
        default='NOTHING',
        update=_update_batch_operation_script_preset.__func__,
    )

    batch_operation_script: bpy.props.StringProperty()
