import bpy

from .main import ToolPanel
from ..tools import common as Common
from ..tools import viseme as Viseme

from ..tools.register import register_wrap
from ..translations import t


@register_wrap
class VisemePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_viseme_v3'
    bl_label = t('VisemePanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        mesh_count = len(Common.get_meshes_objects(check=False))
        if mesh_count == 0:
            row = col.row(align=True)
            row.scale_y = 1.1
            row.label(text=t('VisemePanel.error.noMesh'), icon='ERROR')
            col.separator()
        elif mesh_count > 1:
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'mesh_name_viseme', icon='MESH_DATA')
            col.separator()

        row = col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, 'mouth_a', icon='SHAPEKEY_DATA')
        row = col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, 'mouth_o', icon='SHAPEKEY_DATA')
        row = col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, 'mouth_ch', icon='SHAPEKEY_DATA')

        col.separator()
        row = col.row(align=True)
        row.prop(context.scene, 'shape_intensity')

        col.separator()
        row = col.row(align=True)
        row.operator(Viseme.AutoVisemeButton.bl_idname, icon='TRIA_RIGHT')
