import bpy
import globs
import addon_utils
import tools.common
import tools.supporter

from ui.main import ToolPanel
from ui.main import layout_split
from importlib import import_module

from tools.common import version_2_79_or_older
from tools.register import register_wrap

from tools import atlas, material, bonemerge, rootbone

draw_smc_ui = None
old_smc_version = False
smc_is_disabled = False
found_very_old_smc = False


def check_for_smc():
    global draw_smc_ui, old_smc_version, smc_is_disabled, found_very_old_smc

    draw_smc_ui = None
    found_very_old_smc = False

    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Shotariya-don":
            if hasattr(bpy.context.scene, 'shotariya_tex_idx'):
                found_very_old_smc = True
            continue
        if mod.bl_info['name'] == "Shotariya's Material Combiner":
            if mod.bl_info['version'] < (2, 0, 3, 2):
                old_smc_version = True
                print('TOO OLD!')
                continue
            if not hasattr(bpy.context.scene, 'smc_ob_data'):
                smc_is_disabled = True
                print('DISABLED!')
                continue

            print('FOUND!')
            old_smc_version = False
            smc_is_disabled = False
            draw_smc_ui = getattr(import_module(mod.__name__ + '.operators.ui.include'), 'draw_ui')


@register_wrap
class AtlasList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        mat = item.material
        row = layout.row()
        row.prop(mat, 'name', emboss=False, text='', icon_value=layout.icon(mat))
        sub_row = row.row()
        sub_row.scale_x = 0.2
        row.prop(mat, 'add_to_atlas', text='')


@register_wrap
class OptimizePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_optimize_v3'
    bl_label = 'Optimization'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'optimize_mode', expand=True)

        if context.scene.optimize_mode == 'ATLAS':

            if not version_2_79_or_older():  # TODO
                col = box.column(align=True)
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text='Not yet compatible with 2.8!', icon='INFO')
                col.separator()
                return

            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text='A greatly improved Atlas Generator.')

            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 0.9
            row.label(text='Made by shotaryia', icon_value=tools.supporter.preview_collections["custom_icons"]["heart1"].icon_id)
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 0.9
            row.operator(atlas.AtlasHelpButton.bl_idname, text="", icon='QUESTION')
            # row.separator()
            # row = split.row(align=False)
            # row.alignment = 'RIGHT'
            # row.scale_y = 0.9
            # row.operator(atlas.AtlasHelpButton.bl_idname, text="", icon='QUESTION')
            col.separator()

            # Draw v1.0 mat comb ui
            # if found_very_old_smc and not draw_smc_ui:
            #     col.separator()
            #
            #     box2 = col.box()
            #     col2 = box2.column(align=True)
            #
            #     row = col2.row(align=True)
            #     row.scale_y = 0.75
            #     row.label(text="Old Combiner version, consider upgrading:", icon='INFO')
            #     col2.separator()
            #     row = col2.row(align=True)
            #     row.operator(atlas.ShotariyaButton.bl_idname, text='Download Material Combiner v2.0', icon=globs.ICON_URL)
            #     col.separator()
            #
            #     if len(context.scene.material_list) == 0:
            #         col.separator()
            #         row = col.row(align=True)
            #         row.scale_y = 1.2
            #         row.operator(atlas.GenerateMaterialListButton.bl_idname, icon='TRIA_RIGHT')
            #         col.separator()
            #     else:
            #         # row = col.row(align=True)
            #         # row.scale_y = 0.75
            #         # row.label(text='Select Materials to Combine:')
            #         row = col.row(align=True)
            #         row.template_list('AtlasList', '', context.scene, 'material_list', context.scene, 'material_list_index', rows=8, type='DEFAULT')
            #
            #         row = layout_split(col, factor=0.8, align=True)
            #         row.scale_y = 1.2
            #         row.operator(atlas.GenerateMaterialListButton.bl_idname, text='Update Material List', icon='FILE_REFRESH')
            #         if context.scene.clear_materials:
            #             row.operator(atlas.CheckMaterialListButton.bl_idname, text='', icon='CHECKBOX_HLT')
            #         else:
            #             row.operator(atlas.CheckMaterialListButton.bl_idname, text='', icon='CHECKBOX_DEHLT')
            #
            #         row.operator(atlas.ClearMaterialListButton.bl_idname, text='', icon='X')
            #         col.separator()
            #
            #     row = col.row(align=True)
            #     row.scale_y = 1.7
            #     row.operator(atlas.AutoAtlasNewButton.bl_idname, icon='TRIA_RIGHT')
            #     check_for_smc()
            #     return

            # Found very old v1.0 mat comb
            if found_very_old_smc and not draw_smc_ui:
                col.separator()
                box = col.box()
                col = box.column(align=True)

                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Your Material Combiner is outdated!")
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Please update to the latest version.")
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Download and install it manually:")
                col.separator()
                row = col.row(align=True)
                row.operator(atlas.ShotariyaButton.bl_idname, icon=globs.ICON_URL)

                check_for_smc()
                return

            # Draw v2.0 mat comb ui
            if old_smc_version:
                col.separator()
                box = col.box()
                col = box.column(align=True)

                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Your Material Combiner is outdated!")
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Please update to the latest version.")
                col.separator()
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Update via the 'Updates'' panel")
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="in the 'MatCombiner' tab to the " + ("left." if version_2_79_or_older() else "right."))

                check_for_smc()
                return

            if smc_is_disabled:
                col.separator()
                box = col.box()
                col = box.column(align=True)

                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Material Combiner is not enabled!")
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Enable it in your user preferences:")
                col.separator()
                row = col.row(align=True)
                row.operator(atlas.EnableSMC.bl_idname, icon='CHECKBOX_HLT')

                check_for_smc()
                return

            if not draw_smc_ui:
                col.separator()
                box = col.box()
                col = box.column(align=True)

                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Material Combiner is not installed!")
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="Download and install it manually:")
                col.separator()
                row = col.row(align=True)
                row.operator(atlas.ShotariyaButton.bl_idname, icon=globs.ICON_URL)

                check_for_smc()
                return

            if not hasattr(bpy.context.scene, 'smc_ob_data'):
                check_for_smc()
                return

            draw_smc_ui(context, col)

        elif context.scene.optimize_mode == 'MATERIAL':

            # if not version_2_79_or_older():  # TODO
            #     col = box.column(align=True)
            #     row = col.row(align=True)
            #     row.scale_y = 0.75
            #     row.label(text='Not yet compatible with 2.8!', icon='INFO')
            #     col.separator()
            #     return

            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator(material.CombineMaterialsButton.bl_idname, icon='MATERIAL')

            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator(material.OneTexPerMatButton.bl_idname, icon='TEXTURE')
            subcol = row.row(align=True)
            subcol.alignment = 'RIGHT'
            subcol.scale_y = 1.1
            subcol.operator(material.OneTexPerMatOnlyButton.bl_idname, text="", icon='X')

            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator(material.StandardizeTextures.bl_idname, icon=globs.ICON_SHADING_TEXTURE)

            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator(material.ConvertAllToPngButton.bl_idname, icon='IMAGE_RGB_ALPHA')

        elif context.scene.optimize_mode == 'BONEMERGING':
            if len(tools.common.get_meshes_objects(check=False)) > 1:
                row = box.row(align=True)
                row.prop(context.scene, 'merge_mesh')
            row = box.row(align=True)
            row.prop(context.scene, 'merge_bone')
            row = box.row(align=True)
            row.prop(context.scene, 'merge_ratio')
            row = box.row(align=True)
            col.separator()
            row.operator(rootbone.RefreshRootButton.bl_idname, icon='FILE_REFRESH')
            row.operator(bonemerge.BoneMergeButton.bl_idname, icon='AUTOMERGE_ON')
