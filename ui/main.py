# GPL License

from ..tools.common import version_2_79_or_older
from ..tools.translations import t

class ToolPanel(object):
    bl_label = t('ToolPanel.label')
    bl_idname = '3D_VIEW_TS_vrc'
    bl_category = t('ToolPanel.category')
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if version_2_79_or_older() else 'UI'


def layout_split(layout, factor=0.0, align=False):
    if version_2_79_or_older():
        return layout.split(percentage=factor, align=align)
    return layout.split(factor=factor, align=align)


def add_button_with_small_button(layout, button_1_idname, button_1_icon, button_2_idname, button_2_icon, scale=1):
    row = layout.row(align=True)
    row.scale_y = scale
    subcol = layout_split(row, factor=0, align=True)
    subcol.operator(button_1_idname, icon=button_1_icon)
    subcol = layout_split(row, factor=0, align=True)
    subcol.operator(button_2_idname, text="", icon=button_2_icon)