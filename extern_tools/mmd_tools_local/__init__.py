# -*- coding: utf-8 -*-

bl_info = {
    "name": "mmd_tools",
    "author": "sugiany",
    "version": (2, 3, 0),
    "blender": (2, 83, 0),
    "location": "View3D > Sidebar > MMD Tools Panel",
    "description": "Utility tools for MMD model editing. (UuuNyaa's forked version)",
    "warning": "",
    "doc_url": "https://mmd-blender.fandom.com/wiki/MMD_Tools",
    "wiki_url": "https://mmd-blender.fandom.com/wiki/MMD_Tools",
    "tracker_url": "https://github.com/UuuNyaa/blender_mmd_tools/issues",
    "category": "Object",
}

import bpy
import logging

logging.basicConfig(format='%(message)s', level=logging.DEBUG)

from mmd_tools_local import auto_load
auto_load.init()

from mmd_tools_local import operators
from mmd_tools_local import properties


def menu_func_import(self, _context):
    self.layout.operator(operators.fileio.ImportPmx.bl_idname, text='MikuMikuDance Model (.pmd, .pmx)', icon='OUTLINER_OB_ARMATURE')
    self.layout.operator(operators.fileio.ImportVmd.bl_idname, text='MikuMikuDance Motion (.vmd)', icon='ANIM')
    self.layout.operator(operators.fileio.ImportVpd.bl_idname, text='Vocaloid Pose Data (.vpd)', icon='POSE_HLT')

def menu_func_export(self, _context):
    self.layout.operator(operators.fileio.ExportPmx.bl_idname, text='MikuMikuDance Model (.pmx)', icon='OUTLINER_OB_ARMATURE')
    self.layout.operator(operators.fileio.ExportVmd.bl_idname, text='MikuMikuDance Motion (.vmd)', icon='ANIM')
    self.layout.operator(operators.fileio.ExportVpd.bl_idname, text='Vocaloid Pose Data (.vpd)', icon='POSE_HLT')

def menu_func_armature(self, _context):
    self.layout.operator(operators.model.CreateMMDModelRoot.bl_idname, text='Create MMD Model', icon='OUTLINER_OB_ARMATURE')

def menu_view3d_object(self, _context):
    self.layout.separator()
    self.layout.operator('mmd_tools.clean_shape_keys')

def menu_view3d_select_object(self, _context):
    self.layout.separator()
    self.layout.operator_context = 'EXEC_DEFAULT'
    operator = self.layout.operator('mmd_tools.rigid_body_select', text='Select MMD Rigid Body')
    operator.properties = set(['collision_group_number', 'shape'])

def menu_view3d_pose_context_menu(self, _context):
    self.layout.operator('mmd_tools.flip_pose', text='MMD Flip Pose', icon='ARROW_LEFTRIGHT')

def panel_view3d_shading(self, context):
    if context.space_data.shading.type != 'SOLID':
        return

    col = self.layout.column(align=True)
    col.label(text='MMD Shading Presets')
    row = col.row(align=True)
    row.operator('mmd_tools.set_glsl_shading', text='GLSL')
    row.operator('mmd_tools.set_shadeless_glsl_shading', text='Shadeless')
    row = col.row(align=True)
    row.operator('mmd_tools.reset_shading', text='Reset')

@bpy.app.handlers.persistent
def load_handler(_dummy):
    from mmd_tools_local.core.sdef import FnSDEF
    FnSDEF.clear_cache()
    FnSDEF.register_driver_function()

    from mmd_tools_local.core.material import MigrationFnMaterial
    MigrationFnMaterial.update_mmd_shader()

def register():
    auto_load.register()
    properties.register()
    bpy.app.handlers.load_post.append(load_handler)
    bpy.types.VIEW3D_MT_object.append(menu_view3d_object)
    bpy.types.VIEW3D_MT_select_object.append(menu_view3d_select_object)
    bpy.types.VIEW3D_MT_pose.append(menu_view3d_pose_context_menu)
    bpy.types.VIEW3D_MT_pose_context_menu.append(menu_view3d_pose_context_menu)
    bpy.types.VIEW3D_PT_shading.append(panel_view3d_shading)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.VIEW3D_MT_armature_add.append(menu_func_armature)

    from mmd_tools_local.m17n import translation_dict
    bpy.app.translations.register(bl_info['name'], translation_dict)

    operators.addon_updater.register_updater(bl_info, __file__)

def unregister():
    operators.addon_updater.unregister_updater()

    bpy.app.translations.unregister(bl_info['name'])

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.VIEW3D_MT_armature_add.remove(menu_func_armature)
    bpy.types.VIEW3D_PT_shading.remove(panel_view3d_shading)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(menu_view3d_pose_context_menu)
    bpy.types.VIEW3D_MT_pose.remove(menu_view3d_pose_context_menu)
    bpy.types.VIEW3D_MT_select_object.remove(menu_view3d_select_object)
    bpy.types.VIEW3D_MT_object.remove(menu_view3d_object)
    bpy.app.handlers.load_post.remove(load_handler)
    properties.unregister()
    auto_load.unregister()

if __name__ == "__main__":
    register()
