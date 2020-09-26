import bpy

from .main import ToolPanel
from ..tools import supporter as Supporter
from ..tools.register import register_wrap
from ..tools.supporter import check_for_update_background
from ..translations import t


@register_wrap
class SupporterPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_supporter_v3'
    bl_label = t('SupporterPanel.label')

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        # supporter_data = Supporter.supporter_data
        check_for_update_background()

        row = col.row(align=True)
        row.label(text=t('SupporterPanel.desc'))
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator(Supporter.PatreonButton.bl_idname, icon_value=Supporter.preview_collections["custom_icons"]["heart1"].icon_id)

        if not Supporter.supporter_data or not Supporter.supporter_data.get('supporters') or len(Supporter.supporter_data.get('supporters')) == 0:
            return

        col.separator()
        row = col.row(align=True)
        row.label(text=t('SupporterPanel.thanks'))
        col.separator()

        supporter_count = draw_supporter_list(col, show_tier=1)

        if supporter_count > 0:
            col.separator()

        draw_supporter_list(col, show_tier=0)

        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.2
        row.label(text=t('SupporterPanel.missingName1'), icon="INFO")
        row = col.row(align=True)
        row.scale_y = 0.3
        row.label(text=t('SupporterPanel.missingName2'))
        col.separator()
        row = col.row(align=True)
        row.scale_y = 0.8
        row.operator(Supporter.ReloadButton.bl_idname, icon='FILE_REFRESH')


def draw_supporter_list(col, show_tier=0):
    supporter_data = Supporter.supporter_data.get('supporters')
    preview_collections = Supporter.preview_collections.get("supporter_icons")

    i = 0
    j = 0
    cont = True

    while cont:
        try:
            supporter_obj = supporter_data[j]
            name = supporter_obj.get('displayname')
            tier = supporter_obj.get('tier')
            idname = supporter_obj.get('idname')

            if not name or not idname or supporter_obj.get('disabled'):
                j += 1
                continue

            website = False
            if 'website' in supporter_obj.keys():
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
