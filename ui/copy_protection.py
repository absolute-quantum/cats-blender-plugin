import bpy

from .. import globs
from .main import ToolPanel
from ..tools import common as Common
from ..tools import copy_protection as Copy_protection
from ..tools import importer as Importer
from ..tools.register import register_wrap
from ..translations import t


# @register_wrap
class CopyProtectionPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_copyprotection_v3'
    bl_label = t('CopyProtectionPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.scale_y = 0.75
        row.label(text=t('CopyProtectionPanel.desc1'))
        row = col.row(align=True)
        row.scale_y = 0.75
        row.label(text=t('CopyProtectionPanel.desc2'))
        col.separator()
        row = col.row(align=True)
        row.label(text=t('CopyProtectionPanel.desc3'))
        row = col.row(align=True)
        row.operator(Copy_protection.ProtectionTutorialButton.bl_idname, icon='FORWARD')
        col.separator()
        col.separator()
        # row = col.row(align=True)
        # row.label(text='Randomization Level:')
        # row = col.row(align=True)
        # row.prop(context.scene, 'protection_mode', expand=True)

        row = col.row(align=True)
        row.scale_y = 1.3
        meshes = Common.get_meshes_objects(check=False)
        if len(meshes) > 0 and Common.has_shapekeys(meshes[0]) and meshes[0].data.shape_keys.key_blocks.get('Basis Original'):
            row.operator(Copy_protection.CopyProtectionDisable.bl_idname, icon=globs.ICON_UNPROTECT)
            row = col.row(align=True)
            row.operator(Importer.ExportModel.bl_idname, icon='ARMATURE_DATA').action = 'CHECK'
        else:
            row.operator(Copy_protection.CopyProtectionEnable.bl_idname, icon=globs.ICON_PROTECT)
