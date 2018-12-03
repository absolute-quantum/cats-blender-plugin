import bpy
import globs
import tools.common
import tools.supporter
import addon_updater_ops

from ui.main import ToolPanel
from ui.main import layout_split
from ui.main import get_emtpy_icon

from tools.register import register_wrap


@register_wrap
class SupporterPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_supporter_v3'
    bl_label = 'Supporters'

    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        # supporter_data = tools.supporter.supporter_data

        row = col.row(align=True)
        row.label(text='Do you like this plugin and want to support us?')
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator('supporter.patreon', icon_value=tools.supporter.preview_collections["custom_icons"]["heart1"].icon_id)

        if not tools.supporter.supporter_data or not tools.supporter.supporter_data.get('supporters') or len(tools.supporter.supporter_data.get('supporters')) == 0:
            return

        col.separator()
        row = col.row(align=True)
        row.label(text='Thanks to our awesome supporters! <3')
        col.separator()

        supporter_count = draw_supporter_list(col, show_tier=1)

        if supporter_count > 0:
            col.separator()

        draw_supporter_list(col, show_tier=0)

        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.2
        row.label(text='Is your name missing?', icon="INFO")
        row = col.row(align=True)
        row.scale_y = 0.3
        row.label(text='     Please contact us in our discord!')
        col.separator()
        row = col.row(align=True)
        row.scale_y = 0.8
        row.operator('supporter.reload', icon='FILE_REFRESH')


def draw_supporter_list(col, show_tier=0):
    supporter_data = tools.supporter.supporter_data.get('supporters')
    preview_collections = tools.supporter.preview_collections.get("supporter_icons")

    i = 0
    j = 0
    cont = True

    while cont:
        try:
            supporter = supporter_data[j]
            name = supporter.get('displayname')
            tier = supporter.get('tier')
            idname = supporter.get('idname')

            if not name or not idname or supporter.get('disabled'):
                j += 1
                continue

            website = False
            if 'website' in supporter.keys():
                website = True
            if not tier:
                tier = 0

            if i % 3 == 0:
                row = col.row(align=True)
                if show_tier == 1:
                    row.scale_y = 1.1

            if tier == show_tier:
                row.operator(idname,
                             emboss=website,
                             icon_value=preview_collections[name].icon_id)
                i += 1
            j += 1
        except IndexError:
            if i % 3 == 0:
                cont = False
                continue
            row.label(text='')
            i += 1
    return i
