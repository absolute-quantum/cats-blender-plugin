import bpy
import globs

from ui.main import ToolPanel
from ui.main import layout_split

from tools import armature_manual, translate

from tools.register import register_wrap


@register_wrap
class ManualPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_manual_v3'
    bl_label = 'Model Options'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        button_height = 1

        col = box.column(align=True)
        # if not context.scene.show_manual_options:
        #     row = col.row(align=False)
        #     row.prop(context.scene, 'show_manual_options', emboss=True, expand=False, icon='TRIA_RIGHT')
        # else:
        #     row = col.row(align=True)
        #     row.prop(context.scene, 'show_manual_options', emboss=True, expand=False, icon='TRIA_DOWN')

        row = layout_split(col, factor=0.32, align=True)
        row.scale_y = button_height
        row.label(text="Separate by:", icon='MESH_DATA')
        row.operator(armature_manual.SeparateByMaterials.bl_idname, text='Materials')
        row.operator(armature_manual.SeparateByLooseParts.bl_idname, text='Loose Parts')
        row.operator(armature_manual.SeparateByShapekeys.bl_idname, text='Shapes')

        row = layout_split(col, factor=0.4, align=True)
        row.scale_y = button_height
        row.label(text="Join Meshes:", icon='AUTOMERGE_ON')
        row.operator(armature_manual.JoinMeshes.bl_idname, text='All')
        row.operator(armature_manual.JoinMeshesSelected.bl_idname, text='Selected')

        row = layout_split(col, factor=0.4, align=True)
        row.scale_y = button_height
        row.label(text="Merge Weights:", icon='BONE_DATA')
        row.operator(armature_manual.MergeWeights.bl_idname, text='To Parents')
        row.operator(armature_manual.MergeWeightsToActive.bl_idname, text='To Active')

        # row = col.row(align=True)
        # row.scale_y = button_height
        # row.operator('armature_manual.merge_weights', icon='BONE_DATA')

        # Translate
        col.separator()
        row = col.row(align=True)
        row.label(text="Translate:", icon='FILE_REFRESH')

        row = col.row(align=True)
        row.scale_y = button_height
        row.prop(context.scene, 'use_google_only')

        split = layout_split(col, factor=0.27, align=True)

        row = split.row(align=True)
        row.scale_y = 2
        row.operator(translate.TranslateAllButton.bl_idname, text='All', icon=globs.ICON_ALL)

        row = split.column(align=True)
        row.operator(translate.TranslateShapekeyButton.bl_idname, text='Shape Keys', icon='SHAPEKEY_DATA')
        row.operator(translate.TranslateObjectsButton.bl_idname, text='Objects', icon='MESH_DATA')

        row = split.column(align=True)
        row.operator(translate.TranslateBonesButton.bl_idname, text='Bones', icon='BONE_DATA')
        row.operator(translate.TranslateMaterialsButton.bl_idname, text='Materials', icon='MATERIAL')

        col.separator()
        # col.separator()
        row = col.row(align=True)
        row.scale_y = 0.85

        if not context.scene.show_more_options:
            row.prop(context.scene, 'show_more_options', icon=globs.ICON_ADD, emboss=True, expand=False, toggle=False, event=False)
        else:
            row.prop(context.scene, 'show_more_options', icon=globs.ICON_REMOVE, emboss=True, expand=False, toggle=False, event=False)

            col.separator()
            row = layout_split(col, factor=0.23, align=True)
            row.scale_y = button_height
            row.label(text="Delete:", icon='X')
            row.operator(armature_manual.RemoveZeroWeight.bl_idname, text='Zero Weight Bones')
            row.operator(armature_manual.RemoveConstraints.bl_idname, text='Constraints')

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(armature_manual.DuplicateBonesButton.bl_idname, icon='GROUP_BONE')

            col.separator()
            row = layout_split(col, factor=0.27, align=True)
            row.scale_y = button_height
            row.label(text="Normals:", icon='SNAP_NORMAL')
            row.operator(armature_manual.RecalculateNormals.bl_idname, text='Recalculate')
            row.operator(armature_manual.FlipNormals.bl_idname, text='Flip')

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(armature_manual.ApplyTransformations.bl_idname, icon='OUTLINER_DATA_ARMATURE')

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(armature_manual.RemoveDoubles.bl_idname, icon='X')

            # row = col.row(align=True)
            # row.scale_y = 1
            # subcol = layout_split(row, factor=0, align=True)
            # subcol.scale_y = button_height
            # subcol.operator(armature_manual.RemoveDoubles.bl_idname, icon='STICKY_UVS_VERT')
            # subcol = layout_split(row, factor=0, align=True)
            # subcol.scale_y = button_height
            # subcol.operator(armature_manual.RemoveDoublesNormal.bl_idname, text="", icon='X')

            col.separator()
            # row = col.row(align=True)
            # row.scale_y = button_height
            # row.label(text="Other:", icon='COLLAPSEMENU')

            row = col.row(align=True)
            row.scale_y = 1
            subcol = layout_split(row, factor=0, align=True)
            subcol.scale_y = button_height
            subcol.operator(armature_manual.FixFBTButton.bl_idname, icon='MODIFIER')
            subcol = layout_split(row, factor=0, align=True)
            subcol.scale_y = button_height
            subcol.operator(armature_manual.RemoveFBTButton.bl_idname, text="", icon='X')

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator(armature_manual.FixVRMShapesButton.bl_idname, icon='SHAPEKEY_DATA')
