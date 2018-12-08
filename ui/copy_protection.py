import bpy
import globs
import tools.common
import tools.supporter

from ui.main import ToolPanel

from tools.register import register_wrap
from tools.common import version_2_79_or_older


@register_wrap
class CopyProtectionPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_copyprotection_v3'
    bl_label = 'Copy Protection'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.scale_y = 0.8
        row.label(text='Protects your avatar from Unity cache ripping.')
        col.separator()
        row = col.row(align=True)
        row.label(text='Before use: Read the documentation!')
        row = col.row(align=True)
        row.operator('copyprotection.button', icon='FORWARD')
        col.separator()
        col.separator()
        # row = col.row(align=True)
        # row.label(text='Randomization Level:')
        # row = col.row(align=True)
        # row.prop(context.scene, 'protection_mode', expand=True)

        row = col.row(align=True)
        row.scale_y = 1.3
        meshes = tools.common.get_meshes_objects()
        if len(meshes) > 0 and tools.common.has_shapekeys(meshes[0]) and meshes[0].data.shape_keys.key_blocks.get('Basis Original'):
            row.operator('copyprotection.disable', icon=globs.ICON_UNPROTECT)
            row = col.row(align=True)
            row.operator('importer.export_model', icon='ARMATURE_DATA').action = 'CHECK'
        else:
            row.operator('copyprotection.enable', icon=globs.ICON_PROTECT)
