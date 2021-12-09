import bpy
import addon_utils

from .main import ToolPanel
from ..tools import common as Common
from ..tools import bake as Bake
from ..tools.register import register_wrap
from ..tools.translations import t


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
        col.label(text=t('BakePanel.generaloptionslabel'))
        row = col.row(align=True)
        row.prop(context.scene, 'bake_resolution', expand=True)
        row = col.row(align=True)
        row.prop(context.scene, 'bake_sharpen', expand=True)
        row = col.row(align=True)
        row.prop(context.scene, 'bake_denoise', expand=True)
        row = col.row(align=True)
        row.prop(context.scene, 'bake_use_decimation', expand=True)
        if context.scene.bake_use_decimation:
            row = col.row(align=True)
            row.separator()
            row.prop(context.scene, 'bake_max_tris', expand=True)
            row = col.row(align=True)
            row.separator()
            row.prop(context.scene, 'bake_remove_doubles', expand=True)
            row = col.row(align=True)
            row.separator()
            #row.prop(context.scene, 'bake_loop_decimate', expand=True)
            #row = col.row(align=True)
            #row.separator()
            row.prop(context.scene, 'bake_preserve_seams', expand=True)
            #row = col.row(align=True)
            #row.separator()
            #row.prop(context.scene, 'bake_animation_weighting', expand=True)
            #if context.scene.bake_animation_weighting: #and not context.scene.bake_loop_decimate:
            #    row = col.row(align=True)
            #    row.separator()
            #    row.prop(context.scene, 'bake_animation_weighting_factor', expand=True)
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
        row.prop(context.scene, 'bake_optimize_static', expand=True)
        row = col.row(align=True)
        row.prop(context.scene, 'bake_cleanup_shapekeys', expand=True)
        row = col.row(align=True)
        row.prop(context.scene, 'bake_merge_twistbones', expand=True)
        row = col.row(align=True)
        row.prop(context.scene, 'bake_apply_keys', expand=True)
        #row = col.row(align=True)
        #row.prop(context.scene, 'bake_create_disable_shapekeys', expand=True)
        #row = col.row(align=True)
        #row.prop(context.scene, 'bake_simplify_armature', expand=True)
        row = col.row(align=True)
        row.prop(context.scene, 'bake_quick_compare', expand=True)
        col.separator()
        row = col.row(align=True)
        col.label(text=t('BakePanel.bakepasseslabel'))
        row = col.row(align=True)
        row.prop(context.scene, 'bake_pass_diffuse', expand=True)
        if context.scene.bake_pass_diffuse:
            if bpy.app.version >= (2, 92, 0):
                row = col.row(align=True)
                row.separator()
                row.prop(context.scene, 'bake_diffuse_vertex_colors', expand=True)
        if context.scene.bake_pass_diffuse and (context.scene.bake_pass_smoothness or context.scene.bake_pass_alpha) and not context.scene.bake_diffuse_vertex_colors:
            row = col.row(align=True)
            row.separator()
            row.label(text=t('BakePanel.alphalabel'))
            row.prop(context.scene, 'bake_diffuse_alpha_pack', expand=True)
            if (context.scene.bake_diffuse_alpha_pack == "TRANSPARENCY") and not context.scene.bake_pass_alpha:
                col.label(text=t('BakePanel.transparencywarning'), icon="INFO")
            elif (context.scene.bake_diffuse_alpha_pack == "SMOOTHNESS") and not context.scene.bake_pass_smoothness:
                col.label(text=t('BakePanel.smoothnesswarning'), icon="INFO")
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
        if context.scene.bake_pass_diffuse and context.scene.bake_pass_ao:
            row = col.row(align=True)
            row.prop(context.scene, 'bake_pass_questdiffuse', expand=True)
            if context.scene.bake_pass_questdiffuse:
                row = col.row(align=True)
                row.separator()
                row.prop(context.scene, 'bake_questdiffuse_opacity', expand=True)
            col.separator()
        row = col.row(align=True)
        row.prop(context.scene, 'bake_pass_alpha', expand=True)
        col.separator()
        row = col.row(align=True)
        row.prop(context.scene, 'bake_pass_metallic', expand=True)
        if context.scene.bake_pass_metallic and context.scene.bake_pass_smoothness:
            row = col.row(align=True)
            row.separator()
            row.label(text=t('BakePanel.alphalabel'))
            row.prop(context.scene, 'bake_metallic_alpha_pack', expand=True)
            if context.scene.bake_diffuse_alpha_pack == "SMOOTHNESS" and context.scene.bake_metallic_alpha_pack == "SMOOTHNESS":
                col.label(text=t('BakePanel.doublepackwarning'), icon="INFO")
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
            row.label(text="No render device configured in Settings. Bake will use CPU", icon="INFO")
        row = col.row(align=True)
        row.operator(Bake.BakeButton.bl_idname, icon='RENDER_STILL')
        if not addon_utils.check("render_auto_tile_size")[1] and Common.version_2_93_or_older():
            row = col.row(align=True)
            row.label(text="Enabling \"Auto Tile Size\" plugin reccomended!", icon="INFO")
