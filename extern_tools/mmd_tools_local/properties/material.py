# -*- coding: utf-8 -*-

import bpy
from mmd_tools_local import utils
from mmd_tools_local.core import material
from mmd_tools_local.core.material import FnMaterial
from mmd_tools_local.core.model import Model


def _updateAmbientColor(prop, context):
    FnMaterial(prop.id_data).update_ambient_color()


def _updateDiffuseColor(prop, context):
    FnMaterial(prop.id_data).update_diffuse_color()


def _updateAlpha(prop, context):
    FnMaterial(prop.id_data).update_alpha()


def _updateSpecularColor(prop, context):
    FnMaterial(prop.id_data).update_specular_color()


def _updateShininess(prop, context):
    FnMaterial(prop.id_data).update_shininess()


def _updateIsDoubleSided(prop, context):
    FnMaterial(prop.id_data).update_is_double_sided()


def _updateSphereMapType(prop, context):
    FnMaterial(prop.id_data).update_sphere_texture_type(context.active_object)


def _updateToonTexture(prop, context):
    FnMaterial(prop.id_data).update_toon_texture()


def _updateDropShadow(prop, context):
    FnMaterial(prop.id_data).update_drop_shadow()


def _updateSelfShadowMap(prop, context):
    FnMaterial(prop.id_data).update_self_shadow_map()


def _updateSelfShadow(prop, context):
    FnMaterial(prop.id_data).update_self_shadow()


def _updateEnabledToonEdge(prop, context):
    FnMaterial(prop.id_data).update_enabled_toon_edge()


def _updateEdgeColor(prop, context):
    FnMaterial(prop.id_data).update_edge_color()


def _updateEdgeWeight(prop, context):
    FnMaterial(prop.id_data).update_edge_weight()


def _getNameJ(prop):
    return prop.get('name_j', '')


def _setNameJ(prop, value):
    old_value = prop.get('name_j')
    prop_value = value
    if prop_value and prop_value != old_value:
        root = Model.findRoot(bpy.context.active_object)
        if root:
            rig = Model(root)
            prop_value = utils.uniqueName(value, [mat.mmd_material.name_j for mat in rig.materials() if mat])
        else:
            prop_value = utils.uniqueName(value, [mat.mmd_material.name_j for mat in bpy.data.materials])

    prop['name_j'] = prop_value

# ===========================================
# Property classes
# ===========================================


class MMDMaterial(bpy.types.PropertyGroup):
    """ マテリアル
    """
    name_j: bpy.props.StringProperty(
        name='Name',
        description='Japanese Name',
        default='',
        set=_setNameJ,
        get=_getNameJ,
    )

    name_e: bpy.props.StringProperty(
        name='Name(Eng)',
        description='English Name',
        default='',
    )

    material_id: bpy.props.IntProperty(
        name='Material ID',
        description='Unique ID for the reference of material morph',
        default=-1,
        min=-1,
    )

    ambient_color: bpy.props.FloatVectorProperty(
        name='Ambient Color',
        description='Ambient color',
        subtype='COLOR',
        size=3,
        min=0,
        max=1,
        precision=3,
        step=0.1,
        default=[0.4, 0.4, 0.4],
        update=_updateAmbientColor,
    )

    diffuse_color: bpy.props.FloatVectorProperty(
        name='Diffuse Color',
        description='Diffuse color',
        subtype='COLOR',
        size=3,
        min=0,
        max=1,
        precision=3,
        step=0.1,
        default=[0.8, 0.8, 0.8],
        update=_updateDiffuseColor,
    )

    alpha: bpy.props.FloatProperty(
        name='Alpha',
        description='Alpha transparency',
        min=0,
        max=1,
        precision=3,
        step=0.1,
        default=1.0,
        update=_updateAlpha,
    )

    specular_color: bpy.props.FloatVectorProperty(
        name='Specular Color',
        description='Specular color',
        subtype='COLOR',
        size=3,
        min=0,
        max=1,
        precision=3,
        step=0.1,
        default=[0.625, 0.625, 0.625],
        update=_updateSpecularColor,
    )

    shininess: bpy.props.FloatProperty(
        name='Reflect',
        description='Sharpness of reflected highlights',
        min=0,
        soft_max=512,
        step=100.0,
        default=50.0,
        update=_updateShininess,
    )

    is_double_sided: bpy.props.BoolProperty(
        name='Double Sided',
        description='Both sides of mesh should be rendered',
        default=False,
        update=_updateIsDoubleSided,
    )

    enabled_drop_shadow: bpy.props.BoolProperty(
        name='Ground Shadow',
        description='Display ground shadow',
        default=True,
        update=_updateDropShadow,
    )

    enabled_self_shadow_map: bpy.props.BoolProperty(
        name='Self Shadow Map',
        description='Object can become shadowed by other objects',
        default=True,
        update=_updateSelfShadowMap,
    )

    enabled_self_shadow: bpy.props.BoolProperty(
        name='Self Shadow',
        description='Object can cast shadows',
        default=True,
        update=_updateSelfShadow,
    )

    enabled_toon_edge: bpy.props.BoolProperty(
        name='Toon Edge',
        description='Use toon edge',
        default=False,
        update=_updateEnabledToonEdge,
    )

    edge_color: bpy.props.FloatVectorProperty(
        name='Edge Color',
        description='Toon edge color',
        subtype='COLOR',
        size=4,
        min=0,
        max=1,
        precision=3,
        step=0.1,
        default=[0, 0, 0, 1],
        update=_updateEdgeColor,
    )

    edge_weight: bpy.props.FloatProperty(
        name='Edge Weight',
        description='Toon edge size',
        min=0,
        max=100,
        soft_max=2,
        step=1.0,
        default=1.0,
        update=_updateEdgeWeight,
    )

    sphere_texture_type: bpy.props.EnumProperty(
        name='Sphere Map Type',
        description='Choose sphere texture blend type',
        items=[
            (str(material.SPHERE_MODE_OFF),    'Off',        '', 1),
            (str(material.SPHERE_MODE_MULT),   'Multiply',   '', 2),
            (str(material.SPHERE_MODE_ADD),    'Add',        '', 3),
            (str(material.SPHERE_MODE_SUBTEX), 'SubTexture', '', 4),
        ],
        update=_updateSphereMapType,
    )

    is_shared_toon_texture: bpy.props.BoolProperty(
        name='Use Shared Toon Texture',
        description='Use shared toon texture or custom toon texture',
        default=False,
        update=_updateToonTexture,
    )

    toon_texture: bpy.props.StringProperty(
        name='Toon Texture',
        subtype='FILE_PATH',
        description='The file path of custom toon texture',
        default='',
        update=_updateToonTexture,
    )

    shared_toon_texture: bpy.props.IntProperty(
        name='Shared Toon Texture',
        description='Shared toon texture id (toon01.bmp ~ toon10.bmp)',
        default=0,
        min=0,
        max=9,
        update=_updateToonTexture,
    )

    comment: bpy.props.StringProperty(
        name='Comment',
        description='Comment',
    )

    def is_id_unique(self):
        return self.material_id < 0 or not next((m for m in bpy.data.materials if m.mmd_material != self and m.mmd_material.material_id == self.material_id), None)
