# -*- coding: utf-8 -*-

import bpy
from bpy.types import Panel

from mmd_tools_local import register_wrap
from mmd_tools_local.core.material import FnMaterial


ICON_FILE_FOLDER = 'FILE_FOLDER'
if bpy.app.version < (2, 80, 0):
    ICON_FILE_FOLDER = 'FILESEL'


@register_wrap
class MMDMaterialPanel(Panel):
    bl_idname = 'MATERIAL_PT_mmd_tools_material'
    bl_label = 'MMD Material'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj.active_material and obj.mmd_type == 'NONE'

    def draw(self, context):
        material = context.active_object.active_material
        mmd_material = material.mmd_material

        layout = self.layout

        col = layout.column()

        row = col.row(align=True)
        row.label(text='Information:')
        if not mmd_material.is_id_unique():
            row.label(icon='ERROR')
        row.prop(mmd_material, 'material_id', text='ID')

        col.prop(mmd_material, 'name_j')
        col.prop(mmd_material, 'name_e')
        col.prop(mmd_material, 'comment')

        col = layout.column()
        col.label(text='Color:')
        r = col.row()
        r.prop(mmd_material, 'diffuse_color')
        r.prop(mmd_material, 'alpha', slider=True)
        r = col.row()
        r.prop(mmd_material, 'specular_color')
        r.prop(mmd_material, 'shininess', slider=True)
        r = col.row()
        r.prop(mmd_material, 'ambient_color')
        r.label() # for alignment only

        col = layout.column()
        col.label(text='Shadow:')
        r = col.row()
        r.prop(mmd_material, 'is_double_sided')
        r.prop(mmd_material, 'enabled_drop_shadow')
        r = col.row()
        r.prop(mmd_material, 'enabled_self_shadow_map')
        r.prop(mmd_material, 'enabled_self_shadow')

        col = layout.column()
        r = col.row()
        r.prop(mmd_material, 'enabled_toon_edge')
        r = col.row()
        r.active = mmd_material.enabled_toon_edge
        r.prop(mmd_material, 'edge_color')
        r.prop(mmd_material, 'edge_weight', slider=True)

@register_wrap
class MMDTexturePanel(Panel):
    bl_idname = 'MATERIAL_PT_mmd_tools_texture'
    bl_label = 'MMD Texture'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj.active_material and obj.mmd_type == 'NONE'

    def draw(self, context):
        material = context.active_object.active_material
        mmd_material = material.mmd_material

        layout = self.layout

        fnMat = FnMaterial(material)

        col = layout.column()
        col.label(text='Texture:')
        r = col.row(align=True)
        tex = fnMat.get_texture()
        if tex:
            if tex.type == 'IMAGE' and tex.image:
                r.prop(tex.image, 'filepath', text='')
                r.operator('mmd_tools.material_remove_texture', text='', icon='PANEL_CLOSE')
            else:
                r.operator('mmd_tools.material_remove_texture', text='Remove', icon='PANEL_CLOSE')
                r.label(icon='ERROR')
        else:
            r.operator('mmd_tools.material_open_texture', text='Add', icon=ICON_FILE_FOLDER)

        col = layout.column()
        col.label(text='Sphere Texture:')
        r = col.row(align=True)
        tex = fnMat.get_sphere_texture()
        if tex:
            if tex.type == 'IMAGE' and tex.image:
                r.prop(tex.image, 'filepath', text='')
                r.operator('mmd_tools.material_remove_sphere_texture', text='', icon='PANEL_CLOSE')
            else:
                r.operator('mmd_tools.material_remove_sphere_texture', text='Remove', icon='PANEL_CLOSE')
                r.label(icon='ERROR')
        else:
            r.operator('mmd_tools.material_open_sphere_texture', text='Add', icon=ICON_FILE_FOLDER)
        col.row(align=True).prop(mmd_material, 'sphere_texture_type', expand=True)

        col = layout.column()
        row = col.row()
        row.prop(mmd_material, 'is_shared_toon_texture')
        r = row.row()
        r.active = mmd_material.is_shared_toon_texture
        r.prop(mmd_material, 'shared_toon_texture')
        r = col.row()
        r.active = not mmd_material.is_shared_toon_texture
        r.prop(mmd_material, 'toon_texture')

