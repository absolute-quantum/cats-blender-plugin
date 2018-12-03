import bpy

from ui.main import ToolPanel

from tools.register import register_wrap
from tools.common import version_2_79_or_older


@register_wrap
class BoneRootPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_boneroot_v3'
    bl_label = 'Bone Parenting'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, 'root_bone', icon='BONE_DATA')
        row = box.row(align=True)
        row.operator('refresh.root', icon='FILE_REFRESH')
        row.operator('root.function', icon='TRIA_RIGHT')
