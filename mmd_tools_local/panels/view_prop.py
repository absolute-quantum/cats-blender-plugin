# -*- coding: utf-8 -*-

from bpy.types import Panel

import mmd_tools_local.core.model as mmd_model

class _PanelBase(object):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

class MMDModelObjectDisplayPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_root_object_display'
    bl_label = 'MMD Display'

    @classmethod
    def poll(cls, context):
        return mmd_model.Model.findRoot(context.active_object)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        root = mmd_model.Model.findRoot(obj)

        row = layout.row(align=True)
        c = row.column(align=True)
        c.prop(root.mmd_root, 'show_meshes', text='Mesh')
        c.prop(root.mmd_root, 'show_armature', text='Armature')
        c.prop(root.mmd_root, 'show_rigid_bodies', text='Rigid Body')
        c.prop(root.mmd_root, 'show_joints', text='Joint')
        c = row.column(align=True)
        c.prop(root.mmd_root, 'show_temporary_objects', text='Temporary Object')
        c.label() # for alignment only
        c.prop(root.mmd_root, 'show_names_of_rigid_bodies', text='Rigid Body Name')
        c.prop(root.mmd_root, 'show_names_of_joints', text='Joint Name')

        if context.scene.render.engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:
            row = layout.row(align=True)
            row.prop(root.mmd_root, 'use_toon_texture', text='Toon Texture')
            row.prop(root.mmd_root, 'use_sphere_texture', text='Sphere Texture')


class MMDViewPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_view'
    bl_label = 'MMD Shading'

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        c = col.column(align=True)
        r = c.row(align=True)
        r.operator('mmd_tools.set_glsl_shading', text='GLSL')
        r.operator('mmd_tools.set_shadeless_glsl_shading', text='Shadeless')
        r = c.row(align=True)
        r.operator('mmd_tools.reset_shading', text='Reset')
