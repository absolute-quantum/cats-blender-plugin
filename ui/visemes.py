import bpy
import tools.common
import tools.supporter

from ui.main import ToolPanel

from tools.register import register_wrap


@register_wrap
class VisemePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_viseme_v3'
    bl_label = 'Visemes'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        mesh_count = len(tools.common.get_meshes_objects())
        if mesh_count == 0:
            row = col.row(align=True)
            row.scale_y = 1.1
            row.label(text='No meshes found!', icon='ERROR')
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
        row.operator('auto.viseme', icon='TRIA_RIGHT')
