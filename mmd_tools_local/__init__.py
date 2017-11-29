# -*- coding: utf-8 -*-

import logging
import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty

from . import properties
from . import operators
from . import panels

bl_info= {
    "name": "mmd_tools",
    "author": "sugiany",
    "version": (0, 6, 0),
    "blender": (2, 71, 0),
    "location": "View3D > Tool Shelf > MMD Tools Panel",
    "description": "Utility tools for MMD model editing. (powroupi's forked version)",
    "warning": "",
    "wiki_url": "https://github.com/powroupi/blender_mmd_tools/wiki",
    "tracker_url": "https://github.com/powroupi/blender_mmd_tools/issues",
    "category": "Object"}

# if "bpy" in locals():
#     import imp
#     if "import_pmx" in locals():
#         imp.reload(import_pmx)
#     if "export_pmx" in locals():
#         imp.reload(export_pmx)
#     if "import_vmd" in locals():
#         imp.reload(import_vmd)
#     if "mmd_camera" in locals():
#         imp.reload(mmd_camera)
#     if "utils" in locals():
#         imp.reload(utils)
#     if "cycles_converter" in locals():
#         imp.reload(cycles_converter)
#     if "auto_scene_setup" in locals():
#         imp.reload(auto_scene_setup)

logging.basicConfig(format='%(message)s')


class MMDToolsAddonPreferences(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    shared_toon_folder = StringProperty(
            name="Shared Toon Texture Folder",
            description=('Directory path to toon textures. This is normally the ' +
                         '"Data" directory within of your MikuMikuDance directory'),
            subtype='DIR_PATH',
            )
    base_texture_folder = StringProperty(
            name='Base Texture Folder',
            description='Path for textures shared between models',
            subtype='DIR_PATH',
            )
    dictionary_folder = StringProperty(
            name='Dictionary Folder',
            description='Path for searching csv dictionaries',
            subtype='DIR_PATH',
            default=__file__[:-11],
            )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "shared_toon_folder")
        layout.prop(self, "base_texture_folder")
        layout.prop(self, "dictionary_folder")


def menu_func_import(self, context):
    self.layout.operator(operators.fileio.ImportPmx.bl_idname, text="MikuMikuDance Model (.pmd, .pmx)")
    self.layout.operator(operators.fileio.ImportVmd.bl_idname, text="MikuMikuDance Motion (.vmd)")
    self.layout.operator(operators.fileio.ImportVpd.bl_idname, text="Vocaloid Pose Data (.vpd)")

def menu_func_export(self, context):
    self.layout.operator(operators.fileio.ExportPmx.bl_idname, text="MikuMikuDance Model (.pmx)")
    self.layout.operator(operators.fileio.ExportVmd.bl_idname, text="MikuMikuDance Motion (.vmd)")
    self.layout.operator(operators.fileio.ExportVpd.bl_idname, text="Vocaloid Pose Data (.vpd)")

def menu_func_armature(self, context):
    self.layout.operator(operators.model.CreateMMDModelRoot.bl_idname, text='Create MMD Model')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)
    bpy.types.INFO_MT_armature_add.append(menu_func_armature)
    properties.register()

def unregister():
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)
    bpy.types.INFO_MT_armature_add.remove(menu_func_armature)
    properties.unregister()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
