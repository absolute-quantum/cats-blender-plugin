import bpy

from .. import globs
from .main import ToolPanel
from .main import layout_split
from ..tools import common as Common
from ..tools import decimation as Decimation
from ..tools import bake as Bake
from ..tools import armature_manual as Armature_manual
from ..tools.register import register_wrap
from ..translations import t

@register_wrap
class BakePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_catsbake'
    bl_label = 'Bake'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        # TODO: Quest (decimate) and Desktop (nodecimate) presets

        col.label(text="Presets:")

        col.label(text="General options:")
        row = col.row(align=True)
        row.prop(context.scene, 'bake_resolution', expand=True)
        row = col.row(align=True)
        row.prop(context.scene, 'bake_use_decimation', expand=True)
        if context.scene.bake_use_decimation:
            row = col.row(align=True)
            row.separator()
            row.prop(context.scene, 'bake_preserve_seams', expand=True)
        row = col.row(align=True)
        row.prop(context.scene, 'bake_generate_uvmap', expand=True)
        if context.scene.bake_generate_uvmap:
            row = col.row(align=True)
            row.separator()
            row.prop(context.scene, 'bake_prioritize_face', expand=True)
            if context.scene.bake_prioritize_face:
                row = col.row(align=True)
                row.separator()
                row.prop(context.scene, 'bake_face_scale', expand=True)
        col.separator()
        row = col.row(align=True)
        col.label(text="Bake passes:")
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
        if context.scene.bake_pass_diffuse and context.scene.bake_pass_smoothness:
            row = col.row(align=True)
            row.separator()
            row.prop(context.scene, 'bake_smoothness_diffusepack', expand=True)
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
        row.prop(context.scene, 'bake_pass_emit', expand=True)
        row = col.row(align=True)
        col.separator()
        col.separator()
        row.operator(Bake.BakeButton.bl_idname, icon='RENDER_STILL')
