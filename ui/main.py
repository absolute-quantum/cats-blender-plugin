from tools.common import version_2_79_or_older
from tools.supporter import preview_collections


class ToolPanel(object):
    bl_label = 'Cats Blender Plugin'
    bl_idname = '3D_VIEW_TS_vrc'
    bl_category = 'CATS'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if version_2_79_or_older() else 'UI'


def layout_split(layout, factor=0.0, align=False):
    if version_2_79_or_older():
        return layout.split(percentage=factor, align=align)
    return layout.split(factor=factor, align=align)


def get_emtpy_icon():
    return preview_collections["custom_icons"]["empty"].icon_id
