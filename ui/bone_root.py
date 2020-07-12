import bpy

from .main import ToolPanel
from ..tools import rootbone as Rootbone
from ..tools.register import register_wrap
from ..translations import t


@register_wrap
class BoneRootPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_boneroot_v3'
    bl_label = t('BoneRootPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, 'root_bone', icon='BONE_DATA')
        row = box.row(align=True)
        row.operator(Rootbone.RefreshRootButton.bl_idname, icon='FILE_REFRESH')
        row.operator(Rootbone.RootButton.bl_idname, icon='TRIA_RIGHT')
