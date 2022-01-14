import bpy
import addon_utils

from .main import ToolPanel
from ..tools import common as Common
from ..tools import bake as Bake
from ..tools.register import register_wrap
from ..tools.translations import t

from bpy.types import UIList, Operator

@register_wrap
class Bake_Platform_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # We could write some code to decide which icon to use here...
        custom_icon = 'OBJECT_DATAMODE'
        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon = custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon = custom_icon)

@register_wrap
class Bake_Platform_New(Operator):
    bl_idname = "cats_bake.platform_add"
    bl_label = "Add"

    def execute(self, context):
        context.scene.bake_platforms.add()

        return{'FINISHED'}

@register_wrap
class Bake_Platform_Delete(Operator):
    bl_idname = "cats_bake.platform_remove"
    bl_label = "Delete"

    @classmethod
    def poll(cls, context):
        return context.scene.bake_platforms

    def execute(self, context):
        bake_platforms = context.scene.bake_platforms
        index = context.scene.bake_platform_index

        bake_platforms.remove(index)
        context.scene.bake_platform_index = min(max(0, index - 1), len(bake_platforms) - 1)

        return{'FINISHED'}

@register_wrap
class BakePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_catsbake'
    bl_label = t('BakePanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.operator(Bake.BakeTutorialButton.bl_idname, icon='FORWARD')
        col.separator()

        if Common.version_2_79_or_older():
            col.label(text=t('BakePanel.versionTooOld'), icon='ERROR')
            return

        col.label(text=t('BakePanel.autodetectlabel'))
        row = col.row(align=True)
        row.operator(Bake.BakePresetDesktop.bl_idname, icon="ANTIALIASED")
        row.operator(Bake.BakePresetQuest.bl_idname, icon="ALIASED")
        col.separator()
        row = col.row()
        col.label(text="Platforms:")
        #row = col.row(align=True)
        #row.prop(context.scene, 'bake_platforms', expand=True)
        row = col.row()
        row.template_list("Bake_Platform_List", "The_List", context.scene,
                          "bake_platforms", context.scene, "bake_platform_index")
        row = col.row(align=True)
        row.operator(Bake_Platform_New.bl_idname)
        row.operator(Bake_Platform_Delete.bl_idname)
        col.separator()

        if context.scene.bake_platform_index >= 0 and context.scene.bake_platforms:
            item = context.scene.bake_platforms[context.scene.bake_platform_index]

            row = col.row(align=True)
            row.prop(item, 'name', expand=True)
            row = col.row(align=True)
            row.prop(item, 'use_decimation', expand=True)
            if item.use_decimation:
                row = col.row(align=True)
                row.separator()
                row.prop(item, 'max_tris', expand=True)
                row = col.row(align=True)
                row.separator()
                row.prop(item, 'remove_doubles', expand=True)
                row = col.row(align=True)
                row.separator()
                #row.prop(context.scene, 'bake_loop_decimate', expand=True)
                #row = col.row(align=True)
                #row.separator()
                row.prop(item, 'preserve_seams', expand=True)
                #row = col.row(align=True)
                #row.separator()
                #row.prop(context.scene, 'bake_animation_weighting', expand=True)
                #if context.scene.bake_animation_weighting: #and not context.scene.bake_loop_decimate:
                #    row = col.row(align=True)
                #    row.separator()
                #    row.prop(context.scene, 'bake_animation_weighting_factor', expand=True)
            row = col.row(align=True)
            row.prop(item, 'optimize_static', expand=True)
            row = col.row(align=True)
            row.prop(item, 'merge_twistbones', expand=True)

            if context.scene.bake_pass_diffuse and context.scene.bake_pass_ao:
                row = col.row(align=True)
                row.prop(item, "diffuse_premultiply_ao", expand=True)
                if item.diffuse_premultiply_ao:
                    row = col.row(align=True)
                    row.separator()
                    row.prop(item, 'diffuse_premultiply_opacity', expand=True)
                row = col.row(align=True)
                row.prop(item, "smoothness_premultiply_ao", expand=True)
                if item.smoothness_premultiply_ao:
                    row = col.row(align=True)
                    row.separator()
                    row.prop(item, 'diffuse_premultiply_opacity', expand=True)
            if context.scene.bake_pass_diffuse:
                if bpy.app.version >= (2, 92, 0):
                    row = col.row(align=True)
                    row.prop(item, 'diffuse_vertex_colors', expand=True)
            if context.scene.bake_pass_diffuse and (context.scene.bake_pass_smoothness or context.scene.bake_pass_alpha) and not item.diffuse_vertex_colors:
                row = col.row(align=True)
                row.label(text="Diffuse Alpha:")
                row = col.row(align=True)
                row.prop(item, 'diffuse_alpha_pack', expand=True)
                if (item.diffuse_alpha_pack == "TRANSPARENCY") and not context.scene.bake_pass_alpha:
                    col.label(text=t('BakePanel.transparencywarning'), icon="INFO")
                elif (item.diffuse_alpha_pack == "SMOOTHNESS") and not context.scene.bake_pass_smoothness:
                    col.label(text=t('BakePanel.smoothnesswarning'), icon="INFO")
            if context.scene.bake_pass_metallic and context.scene.bake_pass_smoothness:
                row = col.row(align=True)
                row.label(text="Metallic Alpha:")
                row = col.row(align=True)
                row.prop(item, 'metallic_alpha_pack', expand=True)
                if item.diffuse_alpha_pack == "SMOOTHNESS" and item.metallic_alpha_pack == "SMOOTHNESS":
                    col.label(text=t('BakePanel.doublepackwarning'), icon="INFO")

        if context.scene.bake_platforms:
            col.separator()
            col.label(text=t('BakePanel.generaloptionslabel'))
            row = col.row(align=True)
            row.prop(context.scene, 'bake_resolution', expand=True)
            row = col.row(align=True)
            row.prop(context.scene, 'bake_sharpen', expand=True)
            row = col.row(align=True)
            row.prop(context.scene, 'bake_denoise', expand=True)
            row = col.row(align=True)
            row.prop(context.scene, 'bake_generate_uvmap', expand=True)
            if context.scene.bake_generate_uvmap:
                row = col.row(align=True)
                row.separator()
                row.prop(context.scene, 'bake_prioritize_face', expand=True)
                if context.scene.bake_prioritize_face:
                    armature = Common.get_armature()
                    row = col.row(align=True)
                    row.separator()
                    row.prop(context.scene, 'bake_face_scale', expand=True)

                    if armature is None or len(Common.get_bones(names=['Head', 'head'], armature_name=armature.name, check_list=True)) == 0:
                        row = col.row(align=True)
                        row.separator()
                        row.label(text=t('BakePanel.noheadfound'), icon="INFO")
                row = col.row(align=True)
                row.separator()
                row.label(text=t('BakePanel.overlapfixlabel'))
                row.prop(context.scene, 'bake_uv_overlap_correction', expand=True)
            row = col.row(align=True)
            row.prop(context.scene, 'bake_ignore_hidden', expand=True)
            row = col.row(align=True)
            row.prop(context.scene, 'bake_cleanup_shapekeys', expand=True)
            row = col.row(align=True)
            row.prop(context.scene, 'bake_apply_keys', expand=True)
            #row = col.row(align=True)
            #row.prop(context.scene, 'bake_create_disable_shapekeys', expand=True)
            #row = col.row(align=True)
            #row.prop(context.scene, 'bake_simplify_armature', expand=True)
            col.separator()
            row = col.row(align=True)
            col.label(text=t('BakePanel.bakepasseslabel'))
            row = col.row(align=True)
            row.prop(context.scene, 'bake_pass_diffuse', expand=True)
            col.separator()
            row = col.row(align=True)
            row.prop(context.scene, 'bake_pass_normal', expand=True)
            if context.scene.bake_pass_normal:
                row = col.row(align=True)
                row.separator()
                row.prop(context.scene, 'bake_normal_apply_trans', expand=True)
            col.separator()
            row = col.row(align=True)
            row.prop(context.scene, 'bake_pass_smoothness', expand=True)
            col.separator()
            row = col.row(align=True)
            row.prop(context.scene, 'bake_pass_ao', expand=True)
            if context.scene.bake_pass_ao:
                row = col.row(align=True)
                row.separator()
                row.prop(context.scene, 'bake_illuminate_eyes', expand=True)
            col.separator()
            row = col.row(align=True)
            row.prop(context.scene, 'bake_pass_alpha', expand=True)
            col.separator()
            row = col.row(align=True)
            row.prop(context.scene, 'bake_pass_metallic', expand=True)
            col.separator()

            row = col.row(align=True)
            row.prop(context.scene, 'bake_pass_emit', expand=True)
            if context.scene.bake_pass_emit:
                row = col.row(align=True)
                row.separator()
                row.prop(context.scene, 'bake_emit_indirect', expand=True)
                if context.scene.bake_emit_indirect:
                    row = col.row(align=True)
                    row.separator()
                    row.prop(context.scene, 'bake_emit_exclude_eyes', expand=True)

            row = col.row(align=True)
        col.separator()
        col.separator()
        row = col.row(align=True)
        row.prop(context.scene, 'bake_device', expand=True)
        if context.preferences.addons['cycles'].preferences.compute_device_type == 'NONE' and context.scene.bake_device == 'GPU':
            row = col.row(align=True)
            row.label(text="No render device configured in Blender settings. Bake will use CPU", icon="INFO")
        row = col.row(align=True)
        row.operator(Bake.BakeButton.bl_idname, icon='RENDER_STILL')
        if not addon_utils.check("render_auto_tile_size")[1] and Common.version_2_93_or_older():
            row = col.row(align=True)
            row.label(text="Enabling \"Auto Tile Size\" plugin reccomended!", icon="INFO")
