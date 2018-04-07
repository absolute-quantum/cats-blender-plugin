# -*- coding: utf-8 -*-

from bpy.types import Panel

from mmd_tools_local.core.material import FnMaterial

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

        col = layout.column(align=True)
        col.label('Information:')
        c = col.column()
        r = c.row()
        r.prop(mmd_material, 'name_j')
        r = c.row()
        r.prop(mmd_material, 'name_e')
        r = c.row()
        r.prop(mmd_material, 'comment')

        col = layout.column(align=True)
        col.label('Color:')
        c = col.column()
        r = c.row()
        r.prop(mmd_material, 'diffuse_color')
        r.prop(mmd_material, 'alpha', slider=True)
        r = c.row()
        r.prop(mmd_material, 'specular_color')
        r.prop(mmd_material, 'shininess', slider=True)
        r = c.row()
        r.prop(mmd_material, 'ambient_color')
        r.label() # for alignment only

        col = layout.column(align=True)
        col.label('Shadow:')
        c = col.column()
        r = c.row()
        r.prop(mmd_material, 'is_double_sided')
        r.prop(mmd_material, 'enabled_drop_shadow')
        r = c.row()
        r.prop(mmd_material, 'enabled_self_shadow_map')
        r.prop(mmd_material, 'enabled_self_shadow')

        col = layout.column(align=True)
        col.label('Edge:')
        c = col.column()
        r = c.row()
        r.prop(mmd_material, 'enabled_toon_edge')
        r = c.row()
        r.active = mmd_material.enabled_toon_edge
        r.prop(mmd_material, 'edge_color')
        r.prop(mmd_material, 'edge_weight', slider=True)


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

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label('Texture:')
        r = row.column(align=True)
        tex = fnMat.get_texture()
        if tex:
            if tex.type == 'IMAGE' and tex.image:
                r2 = r.row(align=True)
                r2.prop(tex.image, 'filepath', text='')
                r2.operator('mmd_tools.material_remove_texture', text='', icon='PANEL_CLOSE')
            else:
                r.operator('mmd_tools.material_remove_texture', text='Remove', icon='PANEL_CLOSE')
                col.label('Texture is invalid.', icon='ERROR')
        else:
            r.operator('mmd_tools.material_open_texture', text='Add', icon='FILESEL')

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label('Sphere Texture:')
        r = row.column(align=True)
        tex = fnMat.get_sphere_texture()
        if tex:
            if tex.type == 'IMAGE' and tex.image:
                r2 = r.row(align=True)
                r2.prop(tex.image, 'filepath', text='')
                r2.operator('mmd_tools.material_remove_sphere_texture', text='', icon='PANEL_CLOSE')
            else:
                r.operator('mmd_tools.material_remove_sphere_texture', text='Remove', icon='PANEL_CLOSE')
                col.label('Sphere Texture is invalid.', icon='ERROR')
        else:
            r.operator('mmd_tools.material_open_sphere_texture', text='Add', icon='FILESEL')
        r = col.row(align=True)
        r.prop(mmd_material, 'sphere_texture_type')

        col = layout.column(align=True)
        c = col.column()
        r = c.row()
        r.prop(mmd_material, 'is_shared_toon_texture')
        if mmd_material.is_shared_toon_texture:
            r.prop(mmd_material, 'shared_toon_texture')
        else:
            r = c.row()
            r.prop(mmd_material, 'toon_texture')

