import bpy

from .. import globs
from .main import ToolPanel
from ..tools import supporter as Supporter
from ..tools import credits as Credits
from ..tools.register import register_wrap
from ..tools.common import version_2_79_or_older


@register_wrap
class CreditsPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_credits_v3'
    bl_label = 'Credits'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)

        row.label(text='Cats Blender Plugin (' + globs.version_str + ')', icon_value=Supporter.preview_collections["custom_icons"]["cats1"].icon_id)
        col.separator()
        row = col.row(align=True)
        row.label(text='Created by Hotox and GiveMeAllYourCats')
        row = col.row(align=True)
        row.label(text='For the awesome VRChat community <3')
        row.scale_y = 0.5
        col.separator()
        row = col.row(align=True)
        row.label(text='Special thanks to: Shotariya and Neitri')
        col.separator()
        row = col.row(align=True)
        row.label(text='Do you need help or found a bug?')

        row = col.row(align=True)
        row.scale_y = 1.4
        row.operator(Credits.DiscordButton.bl_idname, icon_value=Supporter.preview_collections["custom_icons"]["discord1"].icon_id)
        row = col.row(align=True)
        row.operator(Credits.ForumButton.bl_idname, icon_value=Supporter.preview_collections["custom_icons"]["cats1"].icon_id)
        row = col.row(align=True)
        row.operator(Credits.PatchnotesButton.bl_idname, icon='WORDWRAP_ON')
