# -*- coding: utf-8 -*-

import itertools
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Callable, Dict, Optional, Set, Tuple

import bpy
from mmd_tools_local.core.model import FnModel, Model
from mmd_tools_local.translations import DictionaryEnum
from mmd_tools_local.utils import convertLRToName, convertNameToLR

if TYPE_CHECKING:
    from mmd_tools_local.properties.morph import _MorphBase
    from mmd_tools_local.properties.root import MMDRoot
    from mmd_tools_local.properties.translations import (MMDTranslation,
                                                   MMDTranslationElement,
                                                   MMDTranslationElementIndex)


class MMDTranslationElementType(Enum):
    BONE = 'Bones'
    MORPH = 'Morphs'
    MATERIAL = 'Materials'
    DISPLAY = 'Display'
    PHYSICS = 'Physics'
    INFO = 'Information'


class MMDDataHandlerABC(ABC):
    @classmethod
    @property
    @abstractmethod
    def type_name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def draw_item(cls, layout: bpy.types.UILayout, mmd_translation_element: 'MMDTranslationElement', index: int):
        pass

    @classmethod
    @abstractmethod
    def collect_data(cls, mmd_translation: 'MMDTranslation'):
        pass

    @classmethod
    @abstractmethod
    def update_index(cls, mmd_translation_element: 'MMDTranslationElement'):
        pass

    @classmethod
    @abstractmethod
    def update_query(cls, mmd_translation: 'MMDTranslation', filter_selected: bool, filter_visible: bool, check_blank_name: Callable[[str, str], bool]):
        pass

    @classmethod
    @abstractmethod
    def set_names(cls, mmd_translation_element: 'MMDTranslationElement', name: Optional[str], name_j: Optional[str], name_e: Optional[str]):
        pass

    @classmethod
    @abstractmethod
    def get_names(cls, mmd_translation_element: 'MMDTranslationElement') -> Tuple[str, str, str]:
        """Returns (name, name_j, name_e)"""

    @classmethod
    def is_restorable(cls, mmd_translation_element: 'MMDTranslationElement') -> bool:
        return (mmd_translation_element.name, mmd_translation_element.name_j, mmd_translation_element.name_e) != cls.get_names(mmd_translation_element)

    @classmethod
    def check_data_visible(cls, filter_selected: bool, filter_visible: bool, select: bool, hide: bool) -> bool:
        return (
            filter_selected and not select
            or
            filter_visible and hide
        )

    @classmethod
    def prop_restorable(cls, layout: bpy.types.UILayout, mmd_translation_element: 'MMDTranslationElement', prop_name: str, original_value: str, index: int):
        row = layout.row(align=True)
        row.prop(mmd_translation_element, prop_name, text='')

        if getattr(mmd_translation_element, prop_name) == original_value:
            row.label(text='', icon='BLANK1')
            return

        op = row.operator('mmd_tools.restore_mmd_translation_element_name', text='', icon='FILE_REFRESH')
        op.index = index
        op.prop_name = prop_name
        op.restore_value = original_value

    @classmethod
    def prop_disabled(cls, layout: bpy.types.UILayout, mmd_translation_element: 'MMDTranslationElement', prop_name: str):
        row = layout.row(align=True)
        row.enabled = False
        row.prop(mmd_translation_element, prop_name, text='')
        row.label(text='', icon='BLANK1')


class MMDBoneHandler(MMDDataHandlerABC):
    @classmethod
    @property
    def type_name(cls) -> str:
        return MMDTranslationElementType.BONE.name

    @classmethod
    def draw_item(cls, layout: bpy.types.UILayout, mmd_translation_element: 'MMDTranslationElement', index: int):
        pose_bone: bpy.types.PoseBone = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        row = layout.row(align=True)
        row.label(text='', icon='BONE_DATA')
        prop_row = row.row()
        cls.prop_restorable(prop_row, mmd_translation_element, 'name', pose_bone.name, index)
        cls.prop_restorable(prop_row, mmd_translation_element, 'name_j', pose_bone.mmd_bone.name_j, index)
        cls.prop_restorable(prop_row, mmd_translation_element, 'name_e', pose_bone.mmd_bone.name_e, index)
        row.prop(pose_bone.bone, 'select', text='', emboss=False, icon_only=True, icon='RESTRICT_SELECT_OFF' if pose_bone.bone.select else 'RESTRICT_SELECT_ON')
        row.prop(pose_bone.bone, 'hide', text='', emboss=False, icon_only=True, icon='HIDE_ON' if pose_bone.bone.hide else 'HIDE_OFF')

    @classmethod
    def collect_data(cls, mmd_translation: 'MMDTranslation'):
        armature_object: bpy.types.Object = FnModel.find_armature(mmd_translation.id_data)
        armature: bpy.types.Armature = armature_object.data
        visible_layer_indices = {i for i, visible in enumerate(armature.layers) if visible}
        pose_bone: bpy.types.PoseBone
        for index, pose_bone in enumerate(armature_object.pose.bones):
            layers = pose_bone.bone.layers
            if not any(layers[i] for i in visible_layer_indices):
                continue

            mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements.add()
            mmd_translation_element.type = MMDTranslationElementType.BONE.name
            mmd_translation_element.object = armature_object
            mmd_translation_element.data_path = f'pose.bones[{index}]'
            mmd_translation_element.name = pose_bone.name
            mmd_translation_element.name_j = pose_bone.mmd_bone.name_j
            mmd_translation_element.name_e = pose_bone.mmd_bone.name_e

    @classmethod
    def update_index(cls, mmd_translation_element: 'MMDTranslationElement'):
        bpy.context.view_layer.objects.active = mmd_translation_element.object
        mmd_translation_element.object.id_data.data.bones.active = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path).bone

    @classmethod
    def update_query(cls, mmd_translation: 'MMDTranslation', filter_selected: bool, filter_visible: bool, check_blank_name: Callable[[str, str], bool]):
        mmd_translation_element: 'MMDTranslationElement'
        for index, mmd_translation_element in enumerate(mmd_translation.translation_elements):
            if mmd_translation_element.type != MMDTranslationElementType.BONE.name:
                continue

            pose_bone: bpy.types.PoseBone = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)

            if cls.check_data_visible(filter_selected, filter_visible, pose_bone.bone.select, pose_bone.bone.hide):
                continue

            if check_blank_name(mmd_translation_element.name_j, mmd_translation_element.name_e):
                continue

            if mmd_translation.filter_restorable and not cls.is_restorable(mmd_translation_element):
                continue

            mmd_translation_element_index: 'MMDTranslationElementIndex' = mmd_translation.filtered_translation_element_indices.add()
            mmd_translation_element_index.value = index

    @classmethod
    def set_names(cls, mmd_translation_element: 'MMDTranslationElement', name: Optional[str], name_j: Optional[str], name_e: Optional[str]):
        pose_bone: bpy.types.PoseBone = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        if name is not None:
            pose_bone.name = name
        if name_j is not None:
            pose_bone.mmd_bone.name_j = name_j
        if name_e is not None:
            pose_bone.mmd_bone.name_e = name_e

    @classmethod
    def get_names(cls, mmd_translation_element: 'MMDTranslationElement') -> Tuple[str, str, str]:
        pose_bone: bpy.types.PoseBone = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        return (pose_bone.name, pose_bone.mmd_bone.name_j, pose_bone.mmd_bone.name_e)


class MMDMorphHandler(MMDDataHandlerABC):
    @classmethod
    @property
    def type_name(cls) -> str:
        return MMDTranslationElementType.MORPH.name

    @classmethod
    def draw_item(cls, layout: bpy.types.UILayout, mmd_translation_element: 'MMDTranslationElement', index: int):
        morph: '_MorphBase' = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        row = layout.row(align=True)
        row.label(text='', icon='SHAPEKEY_DATA')
        prop_row = row.row()
        cls.prop_disabled(prop_row, mmd_translation_element, 'name')
        cls.prop_restorable(prop_row, mmd_translation_element, 'name', morph.name, index)
        cls.prop_restorable(prop_row, mmd_translation_element, 'name_e', morph.name_e, index)
        row.label(text='', icon='BLANK1')
        row.label(text='', icon='BLANK1')

    MORPH_DATA_PATH_EXTRACT = re.compile(r"mmd_root\.(?P<morphs_name>[^\[]*)\[(?P<index>\d*)\]")

    @classmethod
    def collect_data(cls, mmd_translation: 'MMDTranslation'):
        root_object: bpy.types.Object = mmd_translation.id_data
        mmd_root: 'MMDRoot' = root_object.mmd_root

        for morphs_name, morphs in {
            'material_morphs': mmd_root.material_morphs,
            'uv_morphs': mmd_root.uv_morphs,
            'bone_morphs': mmd_root.bone_morphs,
            'vertex_morphs': mmd_root.vertex_morphs,
            'group_morphs': mmd_root.group_morphs,
        }.items():
            morph: '_MorphBase'
            for index, morph in enumerate(morphs):
                mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements.add()
                mmd_translation_element.type = MMDTranslationElementType.MORPH.name
                mmd_translation_element.object = root_object
                mmd_translation_element.data_path = f'mmd_root.{morphs_name}[{index}]'
                mmd_translation_element.name = morph.name
                # mmd_translation_element.name_j = None
                mmd_translation_element.name_e = morph.name_e

    @classmethod
    def update_index(cls, mmd_translation_element: 'MMDTranslationElement'):
        match = cls.MORPH_DATA_PATH_EXTRACT.match(mmd_translation_element.data_path)
        if not match:
            return

        mmd_translation_element.object.mmd_root.active_morph_type = match['morphs_name']
        mmd_translation_element.object.mmd_root.active_morph = int(match['index'])

    @classmethod
    def update_query(cls, mmd_translation: 'MMDTranslation', filter_selected: bool, filter_visible: bool, check_blank_name: Callable[[str, str], bool]):
        mmd_translation_element: 'MMDTranslationElement'
        for index, mmd_translation_element in enumerate(mmd_translation.translation_elements):
            if mmd_translation_element.type != MMDTranslationElementType.MORPH.name:
                continue

            morph: '_MorphBase' = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
            if check_blank_name(morph.name, morph.name_e):
                continue

            if mmd_translation.filter_restorable and not cls.is_restorable(mmd_translation_element):
                continue

            mmd_translation_element_index: 'MMDTranslationElementIndex' = mmd_translation.filtered_translation_element_indices.add()
            mmd_translation_element_index.value = index

    @classmethod
    def set_names(cls, mmd_translation_element: 'MMDTranslationElement', name: Optional[str], name_j: Optional[str], name_e: Optional[str]):
        morph: '_MorphBase' = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        if name is not None:
            morph.name = name
        if name_e is not None:
            morph.name_e = name_e

    @classmethod
    def get_names(cls, mmd_translation_element: 'MMDTranslationElement') -> Tuple[str, str, str]:
        morph: '_MorphBase' = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        return (morph.name, '', morph.name_e)


class MMDMaterialHandler(MMDDataHandlerABC):
    @classmethod
    @property
    def type_name(cls) -> str:
        return MMDTranslationElementType.MATERIAL.name

    @classmethod
    def draw_item(cls, layout: bpy.types.UILayout, mmd_translation_element: 'MMDTranslationElement', index: int):
        mesh_object: bpy.types.Object = mmd_translation_element.object
        material: bpy.types.Material = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        row = layout.row(align=True)
        row.label(text='', icon='MATERIAL_DATA')
        prop_row = row.row()
        cls.prop_restorable(prop_row, mmd_translation_element, 'name', material.name, index)
        cls.prop_restorable(prop_row, mmd_translation_element, 'name_j', material.mmd_material.name_j, index)
        cls.prop_restorable(prop_row, mmd_translation_element, 'name_e', material.mmd_material.name_e, index)
        row.prop(mesh_object, 'select', text='', emboss=False, icon_only=True, icon='RESTRICT_SELECT_OFF' if mesh_object.select else 'RESTRICT_SELECT_ON')
        row.prop(mesh_object, 'hide', text='', emboss=False, icon_only=True, icon='HIDE_ON' if mesh_object.hide else 'HIDE_OFF')

    MATERIAL_DATA_PATH_EXTRACT = re.compile(r"data\.materials\[(?P<index>\d*)\]")

    @classmethod
    def collect_data(cls, mmd_translation: 'MMDTranslation'):
        checked_materials: Set[bpy.types.Material] = set()
        mesh_object: bpy.types.Object
        for mesh_object in FnModel.child_meshes(FnModel.find_armature(mmd_translation.id_data)):
            material: bpy.types.Material
            for index, material in enumerate(mesh_object.data.materials):
                if material in checked_materials:
                    continue

                checked_materials.add(material)

                if not hasattr(material, 'mmd_material'):
                    continue

                mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements.add()
                mmd_translation_element.type = MMDTranslationElementType.MATERIAL.name
                mmd_translation_element.object = mesh_object
                mmd_translation_element.data_path = f'data.materials[{index}]'
                mmd_translation_element.name = material.name
                mmd_translation_element.name_j = material.mmd_material.name_j
                mmd_translation_element.name_e = material.mmd_material.name_e

    @classmethod
    def update_index(cls, mmd_translation_element: 'MMDTranslationElement'):
        id_data: bpy.types.Object = mmd_translation_element.object
        bpy.context.view_layer.objects.active = id_data

        match = cls.MATERIAL_DATA_PATH_EXTRACT.match(mmd_translation_element.data_path)
        if not match:
            return

        id_data.active_material_index = int(match['index'])

    @classmethod
    def update_query(cls, mmd_translation: 'MMDTranslation', filter_selected: bool, filter_visible: bool, check_blank_name: Callable[[str, str], bool]):
        mmd_translation_element: 'MMDTranslationElement'
        for index, mmd_translation_element in enumerate(mmd_translation.translation_elements):
            if mmd_translation_element.type != MMDTranslationElementType.MATERIAL.name:
                continue

            mesh_object: bpy.types.Object = mmd_translation_element.object
            if cls.check_data_visible(filter_selected, filter_visible, mesh_object.select, mesh_object.hide):
                continue

            material: bpy.types.Material = mesh_object.path_resolve(mmd_translation_element.data_path)
            if check_blank_name(material.mmd_material.name_j, material.mmd_material.name_e):
                continue

            if mmd_translation.filter_restorable and not cls.is_restorable(mmd_translation_element):
                continue

            mmd_translation_element_index: 'MMDTranslationElementIndex' = mmd_translation.filtered_translation_element_indices.add()
            mmd_translation_element_index.value = index

    @classmethod
    def set_names(cls, mmd_translation_element: 'MMDTranslationElement', name: Optional[str], name_j: Optional[str], name_e: Optional[str]):
        material: bpy.types.Material = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        if name is not None:
            material.name = name
        if name_j is not None:
            material.mmd_material.name_j = name_j
        if name_e is not None:
            material.mmd_material.name_e = name_e

    @classmethod
    def get_names(cls, mmd_translation_element: 'MMDTranslationElement') -> Tuple[str, str, str]:
        material: bpy.types.Material = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        return (material.name, material.mmd_material.name_j, material.mmd_material.name_e)


class MMDDisplayHandler(MMDDataHandlerABC):
    @classmethod
    @property
    def type_name(cls) -> str:
        return MMDTranslationElementType.DISPLAY.name

    @classmethod
    def draw_item(cls, layout: bpy.types.UILayout, mmd_translation_element: 'MMDTranslationElement', index: int):
        bone_group: bpy.types.BoneGroup = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        row = layout.row(align=True)
        row.label(text='', icon='GROUP_BONE')

        prop_row = row.row()
        cls.prop_restorable(prop_row, mmd_translation_element, 'name', bone_group.name, index)
        cls.prop_disabled(prop_row, mmd_translation_element, 'name')
        cls.prop_disabled(prop_row, mmd_translation_element, 'name_e')
        row.prop(mmd_translation_element.object, 'select', text='', emboss=False, icon_only=True, icon='RESTRICT_SELECT_OFF' if mmd_translation_element.object.select else 'RESTRICT_SELECT_ON')
        row.prop(mmd_translation_element.object, 'hide', text='', emboss=False, icon_only=True, icon='HIDE_ON' if mmd_translation_element.object.hide else 'HIDE_OFF')

    DISPLAY_DATA_PATH_EXTRACT = re.compile(r"pose\.bone_groups\[(?P<index>\d*)\]")

    @classmethod
    def collect_data(cls, mmd_translation: 'MMDTranslation'):
        armature_object: bpy.types.Object = FnModel.find_armature(mmd_translation.id_data)
        bone_group: bpy.types.BoneGroup
        for index, bone_group in enumerate(armature_object.pose.bone_groups):
            mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements.add()
            mmd_translation_element.type = MMDTranslationElementType.DISPLAY.name
            mmd_translation_element.object = armature_object
            mmd_translation_element.data_path = f'pose.bone_groups[{index}]'
            mmd_translation_element.name = bone_group.name
            # mmd_translation_element.name_j = None
            # mmd_translation_element.name_e = None

    @classmethod
    def update_index(cls, mmd_translation_element: 'MMDTranslationElement'):
        id_data: bpy.types.Object = mmd_translation_element.object
        bpy.context.view_layer.objects.active = id_data

        match = cls.DISPLAY_DATA_PATH_EXTRACT.match(mmd_translation_element.data_path)
        if not match:
            return

        id_data.pose.bone_groups.active_index = int(match['index'])

    @classmethod
    def update_query(cls, mmd_translation: 'MMDTranslation', filter_selected: bool, filter_visible: bool, check_blank_name: Callable[[str, str], bool]):
        mmd_translation_element: 'MMDTranslationElement'
        for index, mmd_translation_element in enumerate(mmd_translation.translation_elements):
            if mmd_translation_element.type != MMDTranslationElementType.DISPLAY.name:
                continue

            obj: bpy.types.Object = mmd_translation_element.object
            if cls.check_data_visible(filter_selected, filter_visible, obj.select_get(), obj.hide_get()):
                continue

            bone_group: bpy.types.BoneGroup = obj.path_resolve(mmd_translation_element.data_path)
            if check_blank_name(bone_group.name, ''):
                continue

            if mmd_translation.filter_restorable and not cls.is_restorable(mmd_translation_element):
                continue

            mmd_translation_element_index: 'MMDTranslationElementIndex' = mmd_translation.filtered_translation_element_indices.add()
            mmd_translation_element_index.value = index

    @classmethod
    def set_names(cls, mmd_translation_element: 'MMDTranslationElement', name: Optional[str], name_j: Optional[str], name_e: Optional[str]):
        bone_group: bpy.types.BoneGroup = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        if name is not None:
            bone_group.name = name

    @classmethod
    def get_names(cls, mmd_translation_element: 'MMDTranslationElement') -> Tuple[str, str, str]:
        bone_group: bpy.types.BoneGroup = mmd_translation_element.object.path_resolve(mmd_translation_element.data_path)
        return (bone_group.name, '', '')


class MMDPhysicsHandler(MMDDataHandlerABC):
    @classmethod
    @property
    def type_name(cls) -> str:
        return MMDTranslationElementType.PHYSICS.name

    @classmethod
    def draw_item(cls, layout: bpy.types.UILayout, mmd_translation_element: 'MMDTranslationElement', index: int):
        obj: bpy.types.Object = mmd_translation_element.object

        if FnModel.is_rigid_body_object(obj):
            icon = 'MESH_ICOSPHERE'
            mmd_object = obj.mmd_rigid
        elif FnModel.is_joint_object(obj):
            icon = 'CONSTRAINT'
            mmd_object = obj.mmd_joint

        row = layout.row(align=True)
        row.label(text='', icon=icon)
        prop_row = row.row()
        cls.prop_restorable(prop_row, mmd_translation_element, 'name', obj.name, index)
        cls.prop_restorable(prop_row, mmd_translation_element, 'name_j', mmd_object.name_j, index)
        cls.prop_restorable(prop_row, mmd_translation_element, 'name_e', mmd_object.name_e, index)
        row.prop(obj, 'select', text='', emboss=False, icon_only=True, icon='RESTRICT_SELECT_OFF' if obj.select else 'RESTRICT_SELECT_ON')
        row.prop(obj, 'hide', text='', emboss=False, icon_only=True, icon='HIDE_ON' if obj.hide else 'HIDE_OFF')

    @classmethod
    def collect_data(cls, mmd_translation: 'MMDTranslation'):
        root_object: bpy.types.Object = mmd_translation.id_data
        model = Model(root_object)

        obj: bpy.types.Object
        for obj in model.rigidBodies():
            mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements.add()
            mmd_translation_element.type = MMDTranslationElementType.PHYSICS.name
            mmd_translation_element.object = obj
            mmd_translation_element.data_path = 'mmd_rigid'
            mmd_translation_element.name = obj.name
            mmd_translation_element.name_j = obj.mmd_rigid.name_j
            mmd_translation_element.name_e = obj.mmd_rigid.name_e

        obj: bpy.types.Object
        for obj in model.joints():
            mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements.add()
            mmd_translation_element.type = MMDTranslationElementType.PHYSICS.name
            mmd_translation_element.object = obj
            mmd_translation_element.data_path = 'mmd_joint'
            mmd_translation_element.name = obj.name
            mmd_translation_element.name_j = obj.mmd_joint.name_j
            mmd_translation_element.name_e = obj.mmd_joint.name_e

    @classmethod
    def update_index(cls, mmd_translation_element: 'MMDTranslationElement'):
        bpy.context.view_layer.objects.active = mmd_translation_element.object

    @classmethod
    def update_query(cls, mmd_translation: 'MMDTranslation', filter_selected: bool, filter_visible: bool, check_blank_name: Callable[[str, str], bool]):
        mmd_translation_element: 'MMDTranslationElement'
        for index, mmd_translation_element in enumerate(mmd_translation.translation_elements):
            if mmd_translation_element.type != MMDTranslationElementType.PHYSICS.name:
                continue

            obj: bpy.types.Object = mmd_translation_element.object
            if cls.check_data_visible(filter_selected, filter_visible, obj.select_get(), obj.hide_get()):
                continue

            if FnModel.is_rigid_body_object(obj):
                mmd_object = obj.mmd_rigid
            elif FnModel.is_joint_object(obj):
                mmd_object = obj.mmd_joint

            if check_blank_name(mmd_object.name_j, mmd_object.name_e):
                continue

            if mmd_translation.filter_restorable and not cls.is_restorable(mmd_translation_element):
                continue

            mmd_translation_element_index: 'MMDTranslationElementIndex' = mmd_translation.filtered_translation_element_indices.add()
            mmd_translation_element_index.value = index

    @classmethod
    def set_names(cls, mmd_translation_element: 'MMDTranslationElement', name: Optional[str], name_j: Optional[str], name_e: Optional[str]):
        obj: bpy.types.Object = mmd_translation_element.object

        if FnModel.is_rigid_body_object(obj):
            mmd_object = obj.mmd_rigid
        elif FnModel.is_joint_object(obj):
            mmd_object = obj.mmd_joint

        if name is not None:
            obj.name = name
        if name_j is not None:
            mmd_object.name_j = name_j
        if name_e is not None:
            mmd_object.name_e = name_e

    @classmethod
    def get_names(cls, mmd_translation_element: 'MMDTranslationElement') -> Tuple[str, str, str]:
        obj: bpy.types.Object = mmd_translation_element.object

        if FnModel.is_rigid_body_object(obj):
            mmd_object = obj.mmd_rigid
        elif FnModel.is_joint_object(obj):
            mmd_object = obj.mmd_joint

        return (obj.name, mmd_object.name_j, mmd_object.name_e)


class MMDInfoHandler(MMDDataHandlerABC):
    @classmethod
    @property
    def type_name(cls) -> str:
        return MMDTranslationElementType.INFO.name

    TYPE_TO_ICONS = {
        'EMPTY': 'EMPTY_DATA',
        'ARMATURE': 'ARMATURE_DATA',
        'MESH': 'MESH_DATA',
    }

    @classmethod
    def draw_item(cls, layout: bpy.types.UILayout, mmd_translation_element: 'MMDTranslationElement', index: int):
        info_object: bpy.types.Object = mmd_translation_element.object
        row = layout.row(align=True)
        row.label(text='', icon=MMDInfoHandler.TYPE_TO_ICONS.get(info_object.type, 'OBJECT_DATA'))
        prop_row = row.row()
        cls.prop_restorable(prop_row, mmd_translation_element, 'name', info_object.name, index)
        cls.prop_disabled(prop_row, mmd_translation_element, 'name')
        cls.prop_disabled(prop_row, mmd_translation_element, 'name_e')
        row.prop(info_object, 'select', text='', emboss=False, icon_only=True, icon='RESTRICT_SELECT_OFF' if info_object.select else 'RESTRICT_SELECT_ON')
        row.prop(info_object, 'hide', text='', emboss=False, icon_only=True, icon='HIDE_ON' if info_object.hide else 'HIDE_OFF')

    @classmethod
    def collect_data(cls, mmd_translation: 'MMDTranslation'):
        root_object: bpy.types.Object = mmd_translation.id_data
        armature_object: bpy.types.Object = FnModel.find_armature(root_object)

        info_object: bpy.types.Object
        for info_object in itertools.chain([root_object, armature_object], FnModel.child_meshes(armature_object)):
            mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements.add()
            mmd_translation_element.type = MMDTranslationElementType.INFO.name
            mmd_translation_element.object = info_object
            mmd_translation_element.data_path = ''
            mmd_translation_element.name = info_object.name
            # mmd_translation_element.name_j = None
            # mmd_translation_element.name_e = None

    @classmethod
    def update_index(cls, mmd_translation_element: 'MMDTranslationElement'):
        bpy.context.view_layer.objects.active = mmd_translation_element.object

    @classmethod
    def update_query(cls, mmd_translation: 'MMDTranslation', filter_selected: bool, filter_visible: bool, check_blank_name: Callable[[str, str], bool]):
        mmd_translation_element: 'MMDTranslationElement'
        for index, mmd_translation_element in enumerate(mmd_translation.translation_elements):
            if mmd_translation_element.type != MMDTranslationElementType.INFO.name:
                continue

            info_object: bpy.types.Object = mmd_translation_element.object
            if cls.check_data_visible(filter_selected, filter_visible, info_object.select, info_object.hide):
                continue

            if check_blank_name(info_object.name, ''):
                continue

            if mmd_translation.filter_restorable and not cls.is_restorable(mmd_translation_element):
                continue

            mmd_translation_element_index: 'MMDTranslationElementIndex' = mmd_translation.filtered_translation_element_indices.add()
            mmd_translation_element_index.value = index

    @classmethod
    def set_names(cls, mmd_translation_element: 'MMDTranslationElement', name: Optional[str], name_j: Optional[str], name_e: Optional[str]):
        info_object: bpy.types.Object = mmd_translation_element.object
        if name is not None:
            info_object.name = name

    @classmethod
    def get_names(cls, mmd_translation_element: 'MMDTranslationElement') -> Tuple[str, str, str]:
        info_object: bpy.types.Object = mmd_translation_element.object
        return (info_object.name, '', '')


MMD_DATA_HANDLERS: Set[MMDDataHandlerABC] = {
    MMDBoneHandler,
    MMDMorphHandler,
    MMDMaterialHandler,
    MMDDisplayHandler,
    MMDPhysicsHandler,
    MMDInfoHandler,
}

MMD_DATA_TYPE_TO_HANDLERS: Dict[str, MMDDataHandlerABC] = {h.type_name: h for h in MMD_DATA_HANDLERS}


class FnTranslations:
    @staticmethod
    def apply_translations(root_object: bpy.types.Object):
        mmd_translation: 'MMDTranslation' = root_object.mmd_root.translation
        mmd_translation_element_index: 'MMDTranslationElementIndex'
        for mmd_translation_element_index in mmd_translation.filtered_translation_element_indices:
            mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements[mmd_translation_element_index.value]
            handler: MMDDataHandlerABC = MMD_DATA_TYPE_TO_HANDLERS[mmd_translation_element.type]
            name, name_j, name_e = handler.get_names(mmd_translation_element)
            handler.set_names(
                mmd_translation_element,
                mmd_translation_element.name if mmd_translation_element.name != name else None,
                mmd_translation_element.name_j if mmd_translation_element.name_j != name_j else None,
                mmd_translation_element.name_e if mmd_translation_element.name_e != name_e else None,
            )

    @staticmethod
    def execute_translation_batch(root_object: bpy.types.Object) -> Tuple[Dict[str, str], Optional[bpy.types.Text]]:
        mmd_translation: 'MMDTranslation' = root_object.mmd_root.translation
        batch_operation_script = mmd_translation.batch_operation_script
        if not batch_operation_script:
            return ({}, None)

        translator = DictionaryEnum.get_translator(mmd_translation.dictionary)

        def translate(name: str) -> str:
            if translator:
                return translator.translate(name, name)
            return name

        batch_operation_script_ast = compile(mmd_translation.batch_operation_script, '<string>', 'eval')
        batch_operation_target: str = mmd_translation.batch_operation_target

        mmd_translation_element_index: 'MMDTranslationElementIndex'
        for mmd_translation_element_index in mmd_translation.filtered_translation_element_indices:
            mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements[mmd_translation_element_index.value]

            handler: MMDDataHandlerABC = MMD_DATA_TYPE_TO_HANDLERS[mmd_translation_element.type]

            name = mmd_translation_element.name
            name_j = mmd_translation_element.name_j
            name_e = mmd_translation_element.name_e
            org_name, org_name_j, org_name_e = handler.get_names(mmd_translation_element)

            # pylint: disable=eval-used
            result_name = str(eval(
                batch_operation_script_ast,
                {'__builtins__': {}},
                {
                    'to_english': translate,
                    'to_mmd_lr': convertLRToName,
                    'to_blender_lr': convertNameToLR,
                    'name': name,
                    'name_j': name_j if name_j != '' else name,
                    'name_e': name_e if name_e != '' else name,
                    'org_name': org_name,
                    'org_name_j': org_name_j,
                    'org_name_e': org_name_e,
                }
            ))

            if batch_operation_target == 'BLENDER':
                mmd_translation_element.name = result_name
            elif batch_operation_target == 'JAPANESE':
                mmd_translation_element.name_j = result_name
            elif batch_operation_target == 'ENGLISH':
                mmd_translation_element.name_e = result_name

        return (translator.fails, translator.save_fails())

    @staticmethod
    def update_index(mmd_translation: 'MMDTranslation'):
        if mmd_translation.filtered_translation_element_indices_active_index < 0:
            return

        mmd_translation_element_index: 'MMDTranslationElementIndex' = mmd_translation.filtered_translation_element_indices[mmd_translation.filtered_translation_element_indices_active_index]
        mmd_translation_element: 'MMDTranslationElement' = mmd_translation.translation_elements[mmd_translation_element_index.value]

        MMD_DATA_TYPE_TO_HANDLERS[mmd_translation_element.type].update_index(mmd_translation_element)

    @staticmethod
    def collect_data(mmd_translation: 'MMDTranslation'):
        mmd_translation.translation_elements.clear()
        for handler in MMD_DATA_HANDLERS:
            handler.collect_data(mmd_translation)

    @staticmethod
    def update_query(mmd_translation: 'MMDTranslation'):
        mmd_translation.filtered_translation_element_indices.clear()
        mmd_translation.filtered_translation_element_indices_active_index = -1

        filter_japanese_blank: bool = mmd_translation.filter_japanese_blank
        filter_english_blank: bool = mmd_translation.filter_english_blank

        filter_selected: bool = mmd_translation.filter_selected
        filter_visible: bool = mmd_translation.filter_visible

        def check_blank_name(name_j: str, name_e: str) -> bool:
            return (
                filter_japanese_blank and name_j
                or
                filter_english_blank and name_e
            )

        for handler in MMD_DATA_HANDLERS:
            if handler.type_name in mmd_translation.filter_types:
                handler.update_query(mmd_translation, filter_selected, filter_visible, check_blank_name)

    @staticmethod
    def clear_data(mmd_translation: 'MMDTranslation'):
        mmd_translation.translation_elements.clear()
        mmd_translation.filtered_translation_element_indices.clear()
        mmd_translation.filtered_translation_element_indices_active_index = -1
        mmd_translation.filter_restorable = False
