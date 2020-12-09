# -*- coding: utf-8 -*-

import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty
from bpy.props import IntProperty
from bpy.props import FloatVectorProperty
from bpy.props import FloatProperty
from bpy.props import CollectionProperty
from bpy.props import EnumProperty

from mmd_tools_local import register_wrap
from mmd_tools_local.core.model import Model as FnModel
from mmd_tools_local.core.bone import FnBone
from mmd_tools_local.core.material import FnMaterial
from mmd_tools_local.core.morph import FnMorph
from mmd_tools_local import utils


def _get_name(prop):
    return prop.get('name', '')

def _set_name(prop, value):
    mmd_root = prop.id_data.mmd_root
    #morph_type = mmd_root.active_morph_type
    morph_type = '%s_morphs'%prop.bl_rna.identifier[:-5].lower()
    #assert(prop.bl_rna.identifier.endswith('Morph'))
    #print('_set_name:', prop, value, morph_type)
    prop_name = prop.get('name', None)
    if prop_name == value:
        return

    used_names = {x.name for x in getattr(mmd_root, morph_type) if x != prop}
    value = utils.uniqueName(value, used_names)
    if prop_name is not None:
        if morph_type == 'vertex_morphs':
            kb_list = {}
            for mesh in FnModel(prop.id_data).meshes():
                for kb in getattr(mesh.data.shape_keys, 'key_blocks', ()):
                    kb_list.setdefault(kb.name, []).append(kb)

            if prop_name in kb_list:
                value = utils.uniqueName(value, used_names|kb_list.keys())
                for kb in kb_list[prop_name]:
                    kb.name = value

        elif morph_type == 'uv_morphs':
            vg_list = {}
            for mesh in FnModel(prop.id_data).meshes():
                for vg, n, x in FnMorph.get_uv_morph_vertex_groups(mesh):
                    vg_list.setdefault(n, []).append(vg)

            if prop_name in vg_list:
                value = utils.uniqueName(value, used_names|vg_list.keys())
                for vg in vg_list[prop_name]:
                    vg.name = vg.name.replace(prop_name, value)

        if 1:#morph_type != 'group_morphs':
            for m in mmd_root.group_morphs:
                for d in m.data:
                    if d.name == prop_name and d.morph_type == morph_type:
                        d.name = value

        frame_facial = mmd_root.display_item_frames.get(u'表情')
        for item in getattr(frame_facial, 'data', []):
            if item.name == prop_name and item.morph_type == morph_type:
                item.name = value
                break

        obj = FnModel(prop.id_data).morph_slider.placeholder()
        if obj and value not in obj.data.shape_keys.key_blocks:
            kb = obj.data.shape_keys.key_blocks.get(prop_name, None)
            if kb:
                kb.name = value

    prop['name'] = value

@register_wrap
class _MorphBase:
    name = StringProperty(
        name='Name',
        description='Japanese Name',
        set=_set_name,
        get=_get_name,
        )
    name_e = StringProperty(
        name='Name(Eng)',
        description='English Name',
        default='',
        )
    category = EnumProperty(
        name='Category',
        description='Select category',
        items = [
            ('SYSTEM', 'Hidden', '', 0),
            ('EYEBROW', 'Eye Brow', '', 1),
            ('EYE', 'Eye', '', 2),
            ('MOUTH', 'Mouth', '', 3),
            ('OTHER', 'Other', '', 4),
            ],
        default='OTHER',
        )


def _get_bone(prop):
    bone_id = prop.get('bone_id', -1)
    if bone_id < 0:
        return ''
    root = prop.id_data
    fnModel = FnModel(root)
    arm = fnModel.armature()
    fnBone = FnBone.from_bone_id(arm, bone_id)
    if not fnBone:
        return ''
    return fnBone.pose_bone.name

def _set_bone(prop, value):
    root = prop.id_data
    fnModel = FnModel(root)
    arm = fnModel.armature()
    if value not in arm.pose.bones.keys():
        prop['bone_id'] = -1
        return
    pose_bone = arm.pose.bones[value]
    fnBone = FnBone(pose_bone)
    prop['bone_id'] = fnBone.bone_id

def _update_bone_morph_data(prop, context):
    if not prop.name.startswith('mmd_bind'):
        return
    arm = FnModel(prop.id_data).morph_slider.dummy_armature
    if arm:
        bone = arm.pose.bones.get(prop.name, None)
        if bone:
            bone.location = prop.location
            bone.rotation_quaternion = prop.rotation.__class__(*prop.rotation.to_axis_angle()) # Fix for consistency

@register_wrap
class BoneMorphData(PropertyGroup):
    """
    """
    bone = StringProperty(
        name='Bone',
        description='Target bone',
        set=_set_bone,
        get=_get_bone,
        )

    bone_id = IntProperty(
        name='Bone ID',
        )

    location = FloatVectorProperty(
        name='Location',
        description='Location',
        subtype='TRANSLATION',
        size=3,
        default=[0, 0, 0],
        update=_update_bone_morph_data,
        )

    rotation = FloatVectorProperty(
        name='Rotation',
        description='Rotation in quaternions',
        subtype='QUATERNION',
        size=4,
        default=[1, 0, 0, 0],
        update=_update_bone_morph_data,
        )

@register_wrap
class BoneMorph(_MorphBase, PropertyGroup):
    """Bone Morph
    """
    data = CollectionProperty(
        name='Morph Data',
        type=BoneMorphData,
        )
    active_data = IntProperty(
        name='Active Bone Data',
        min=0,
        default=0,
        )

def _get_material(prop):
    mat_id = prop.get('material_id', -1)
    if mat_id < 0:
        return ''
    fnMat = FnMaterial.from_material_id(mat_id)
    if not fnMat:
        return ''
    return fnMat.material.name

def _set_material(prop, value):
    if value not in bpy.data.materials.keys():
        prop['material_id'] = -1
        return
    mat = bpy.data.materials[value]
    fnMat = FnMaterial(mat)
    prop['material_id'] = fnMat.material_id

def _set_related_mesh(prop, value):
    rig = FnModel(prop.id_data)
    if rig.findMesh(value):
        prop['related_mesh'] = value
    else:
        prop['related_mesh'] = ''

def _get_related_mesh(prop):
    return prop.get('related_mesh', '')

def _update_material_morph_data(prop, context):
    if not prop.name.startswith('mmd_bind'):
        return
    from mmd_tools_local.core.shader import _MaterialMorph
    mat_id = prop.get('material_id', -1)
    if mat_id >= 0:
        mat = getattr(FnMaterial.from_material_id(mat_id), 'material', None)
        _MaterialMorph.update_morph_inputs(mat, prop)
    elif mat_id == -1:
        for mat in FnModel(prop.id_data).materials():
            _MaterialMorph.update_morph_inputs(mat, prop)

@register_wrap
class MaterialMorphData(PropertyGroup):
    """
    """
    related_mesh = StringProperty(
        name='Related Mesh',
        description='Stores a reference to the mesh where this morph data belongs to',
        set=_set_related_mesh,
        get=_get_related_mesh,
        )
    offset_type = EnumProperty(
        name='Offset Type',
        description='Select offset type',
        items=[
            ('MULT', 'Multiply', '', 0),
            ('ADD', 'Add', '', 1)
            ],
        default='ADD'
        )
    material = StringProperty(
        name='Material',
        description='Target material',
        get=_get_material,
        set=_set_material,
        )

    material_id = IntProperty(
        name='Material ID',
        default=-1,
        )

    diffuse_color = FloatVectorProperty(
        name='Diffuse Color',
        description='Diffuse color',
        subtype='COLOR',
        size=4,
        soft_min=0,
        soft_max=1,
        precision=3,
        step=0.1,
        default=[0, 0, 0, 1],
        update=_update_material_morph_data,
        )

    specular_color = FloatVectorProperty(
        name='Specular Color',
        description='Specular color',
        subtype='COLOR',
        size=3,
        soft_min=0,
        soft_max=1,
        precision=3,
        step=0.1,
        default=[0, 0, 0],
        update=_update_material_morph_data,
        )

    shininess = FloatProperty(
        name='Reflect',
        description='Reflect',
        soft_min=0,
        soft_max=500,
        step=100.0,
        default=0.0,
        update=_update_material_morph_data,
        )

    ambient_color = FloatVectorProperty(
        name='Ambient Color',
        description='Ambient color',
        subtype='COLOR',
        size=3,
        soft_min=0,
        soft_max=1,
        precision=3,
        step=0.1,
        default=[0, 0, 0],
        update=_update_material_morph_data,
        )

    edge_color = FloatVectorProperty(
        name='Edge Color',
        description='Edge color',
        subtype='COLOR',
        size=4,
        soft_min=0,
        soft_max=1,
        precision=3,
        step=0.1,
        default=[0, 0, 0, 1],
        update=_update_material_morph_data,
        )

    edge_weight = FloatProperty(
        name='Edge Weight',
        description='Edge weight',
        soft_min=0,
        soft_max=2,
        step=0.1,
        default=0,
        update=_update_material_morph_data,
        )

    texture_factor = FloatVectorProperty(
        name='Texture factor',
        description='Texture factor',
        subtype='COLOR',
        size=4,
        soft_min=0,
        soft_max=1,
        precision=3,
        step=0.1,
        default=[0, 0, 0, 1],
        update=_update_material_morph_data,
        )

    sphere_texture_factor = FloatVectorProperty(
        name='Sphere Texture factor',
        description='Sphere texture factor',
        subtype='COLOR',
        size=4,
        soft_min=0,
        soft_max=1,
        precision=3,
        step=0.1,
        default=[0, 0, 0, 1],
        update=_update_material_morph_data,
        )

    toon_texture_factor = FloatVectorProperty(
        name='Toon Texture factor',
        description='Toon texture factor',
        subtype='COLOR',
        size=4,
        soft_min=0,
        soft_max=1,
        precision=3,
        step=0.1,
        default=[0, 0, 0, 1],
        update=_update_material_morph_data,
        )

@register_wrap
class MaterialMorph(_MorphBase, PropertyGroup):
    """ Material Morph
    """
    data = CollectionProperty(
        name='Morph Data',
        type=MaterialMorphData,
        )
    active_data = IntProperty(
        name='Active Material Data',
        min=0,
        default=0,
        )

@register_wrap
class UVMorphOffset(PropertyGroup):
    """UV Morph Offset
    """
    index = IntProperty(
        name='Vertex Index',
        description='Vertex index',
        min=0,
        default=0,
        )
    offset = FloatVectorProperty(
        name='UV Offset',
        description='UV offset',
        size=4,
        #min=-1,
        #max=1,
        #precision=3,
        step=0.1,
        default=[0, 0, 0, 0],
        )

@register_wrap
class UVMorph(_MorphBase, PropertyGroup):
    """UV Morph
    """
    uv_index = IntProperty(
        name='UV Index',
        description='UV index (UV, UV1 ~ UV4)',
        min=0,
        max=4,
        default=0,
        )
    data_type = EnumProperty(
        name='Data Type',
        description='Select data type',
        items = [
            ('DATA', 'Data', 'Store offset data in root object (deprecated)', 0),
            ('VERTEX_GROUP', 'Vertex Group', 'Store offset data in vertex groups', 1),
            ],
        default='DATA',
        )
    data = CollectionProperty(
        name='Morph Data',
        type=UVMorphOffset,
        )
    active_data = IntProperty(
        name='Active UV Data',
        min=0,
        default=0,
        )
    vertex_group_scale = FloatProperty(
        name='Vertex Group Scale',
        description='The value scale of "Vertex Group" data type',
        precision=3,
        step=0.1,
        default=1,
        )

@register_wrap
class GroupMorphOffset(PropertyGroup):
    """Group Morph Offset
    """
    morph_type = EnumProperty(
        name='Morph Type',
        description='Select morph type',
        items = [
            ('material_morphs', 'Material', 'Material Morphs', 0),
            ('uv_morphs', 'UV', 'UV Morphs', 1),
            ('bone_morphs', 'Bone', 'Bone Morphs', 2),
            ('vertex_morphs', 'Vertex', 'Vertex Morphs', 3),
            ('group_morphs', 'Group', 'Group Morphs', 4),
            ],
        default='vertex_morphs',
        )
    factor = FloatProperty(
        name='Factor',
        description='Factor',
        soft_min=0,
        soft_max=1,
        precision=3,
        step=0.1,
        default=0
        )

@register_wrap
class GroupMorph(_MorphBase, PropertyGroup):
    """Group Morph
    """
    data = CollectionProperty(
        name='Morph Data',
        type=GroupMorphOffset,
        )
    active_data = IntProperty(
        name='Active Group Data',
        min=0,
        default=0,
        )

@register_wrap
class VertexMorph(_MorphBase, PropertyGroup):
    """Vertex Morph
    """

