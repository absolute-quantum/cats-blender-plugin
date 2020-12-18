import bpy

from .. import globs
from .main import ToolPanel
from .main import layout_split
from ..tools import common as Common
from ..tools import decimation as Decimation
from ..tools import armature_manual as Armature_manual
from ..tools.register import register_wrap
from ..translations import t

@register_wrap
class AutoDecimatePresetGood(bpy.types.Operator):
    bl_idname = 'cats_decimation.preset_good'
    bl_label = t('DecimationPanel.preset.good.label')
    bl_description = t('DecimationPanel.preset.good.description')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        context.scene.max_tris = 70000
        return {'FINISHED'}

@register_wrap
class AutoDecimatePresetExcellent(bpy.types.Operator):
    bl_idname = 'cats_decimation.preset_excellent'
    bl_label = t('DecimationPanel.preset.excellent.label')
    bl_description = t('DecimationPanel.preset.excellent.description')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        context.scene.max_tris = 32000
        return {'FINISHED'}

@register_wrap
class AutoDecimatePresetQuest(bpy.types.Operator):
    bl_idname = 'cats_decimation.preset_quest'
    bl_label = t('DecimationPanel.preset.quest.label')
    bl_description = t('DecimationPanel.preset.quest.description')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        context.scene.max_tris = 5000
        return {'FINISHED'}

@register_wrap
class DecimationPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_decimation_v3'
    bl_label = t('DecimationPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        # row = col.row(align=True)
        # row.label(text='Auto Decimation is currently experimental.')
        # row = col.row(align=True)
        # row.scale_y = 0.5
        # row.label(text='It works but it might not look good. Test for yourself.')
        # col.separator()
        row = col.row(align=True)
        row.label(text=t('DecimationPanel.decimationMode'))
        row = col.row(align=True)
        row.prop(context.scene, 'decimation_mode', expand=True)
        row = col.row(align=True)
        row.scale_y = 0.7
        if context.scene.decimation_mode == 'SMART':
            row.label(text=t('DecimationPanel.smartModeDesc'))
        elif context.scene.decimation_mode == 'SAFE':
            row.label(text=t('DecimationPanel.safeModeDesc'))
        elif context.scene.decimation_mode == 'HALF':
            row.label(text=t('DecimationPanel.halfModeDesc'))
        elif context.scene.decimation_mode == 'FULL':
            row.label(text=t('DecimationPanel.fullModeDesc'))

        elif context.scene.decimation_mode == 'CUSTOM':
            col.separator()

            if len(Common.get_meshes_objects(check=False)) <= 1:
                row = col.row(align=True)
                row.label(text=t('DecimationPanel.customSeparateMaterials'))
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator(Armature_manual.SeparateByMaterials.bl_idname, text=t('DecimationPanel.SeparateByMaterials.label'), icon='PLAY')
                return
            else:
                row = col.row(align=True)
                row.label(text=t('DecimationPanel.customJoinMeshes'))
                row = col.row(align=True)
                row.scale_y = 1.2
                row.operator(Armature_manual.JoinMeshes.bl_idname, icon='PAUSE')

            col.separator()
            col.separator()
            row = col.row(align=True)
            row.label(text=t('DecimationPanel.customWhitelist'))
            row = col.row(align=True)
            row.prop(context.scene, 'selection_mode', expand=True)
            col.separator()
            col.separator()

            if context.scene.selection_mode == 'SHAPES':
                row = layout_split(col, factor=0.7, align=False)
                row.prop(context.scene, 'add_shape_key', icon='SHAPEKEY_DATA')
                row.operator(Decimation.AddShapeButton.bl_idname, icon=globs.ICON_ADD)
                col.separator()

                box2 = col.box()
                col = box2.column(align=True)

                if len(Decimation.ignore_shapes) == 0:
                    col.label(text=t('DecimationPanel.warn.noShapekeySelected'))

                for shape in Decimation.ignore_shapes:
                    row = layout_split(col, factor=0.8, align=False)
                    row.label(text=shape, icon='SHAPEKEY_DATA')
                    op = row.operator(Decimation.RemoveShapeButton.bl_idname, icon=globs.ICON_REMOVE)
                    op.shape_name = shape
            elif context.scene.selection_mode == 'MESHES':
                row = layout_split(col, factor=0.7, align=False)
                row.prop(context.scene, 'add_mesh', icon='MESH_DATA')
                row.operator(Decimation.AddMeshButton.bl_idname, icon=globs.ICON_ADD)
                col.separator()

                if context.scene.add_mesh == '':
                    row = col.row(align=True)
                    col.label(text=t('DecimationPanel.warn.noDecimation'), icon='ERROR')

                box2 = col.box()
                col = box2.column(align=True)

                if len(Decimation.ignore_meshes) == 0:
                    col.label(text=t('DecimationPanel.warn.noMeshSelected'))

                for mesh in Decimation.ignore_meshes:
                    row = layout_split(col, factor=0.8, align=False)
                    row.label(text=mesh, icon='MESH_DATA')
                    op = row.operator(Decimation.RemoveMeshButton.bl_idname, icon=globs.ICON_REMOVE)
                    op.mesh_name = mesh

            col = box.column(align=True)

            if len(Decimation.ignore_shapes) == 0 and len(Decimation.ignore_meshes) == 0:
                col.label(text=t('DecimationPanel.warn.emptyList'), icon='ERROR')
                row = col.row(align=True)
            else:
                col.label(text=t('DecimationPanel.warn.correctWhitelist'), icon='INFO')
                row = col.row(align=True)

            # # row = col.row(align=True)
            # # rows = 2
            # # row = layout.row()
            # # row.template_list("auto.decimate_list", "", bpy.context.scene, "auto", bpy.context.scene, "custom_index", rows=rows)
            #
            # obj = context.object
            #
            # # template_list now takes two new args.
            # # The first one is the identifier of the registered UIList to use (if you want only the default list,
            # # with no custom draw code, use "UI_UL_list").
            # layout.template_list("ShapekeyList", "", ('heyho', 'heyho2'), "material_slots", ('heyho', 'heyho2'), "active_material_index")

        col.separator()
        col.separator()
        row = col.row(align=True)
        row.prop(context.scene, 'decimate_fingers')
        row = col.row(align=True)
        row.prop(context.scene, 'decimation_remove_doubles')
        row = col.row(align=True)
        row.prop(context.scene, 'decimation_animation_weighting', expand=True)
        if context.scene.decimation_animation_weighting:
            row = col.row(align=True)
            row.separator()
            row.prop(context.scene, 'decimation_animation_weighting_factor', expand=True)
            col.separator()
        row = col.row(align=True)
        row.operator(Decimation.AutoDecimatePresetGood.bl_idname)
        row.operator(Decimation.AutoDecimatePresetExcellent.bl_idname)
        row.operator(Decimation.AutoDecimatePresetQuest.bl_idname)
        row = col.row(align=True)
        row.prop(context.scene, 'max_tris')
        col.separator()
        col.label(text=t('DecimationPanel.warn.notIfBaking'), icon='INFO')
        row = col.row(align=True)
        row.scale_y = 1.2
        row.operator(Decimation.AutoDecimateButton.bl_idname, icon='MOD_DECIM')
