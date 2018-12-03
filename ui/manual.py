import bpy
import globs

from ui.main import ToolPanel
from ui.main import layout_split

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

        row = layout_split(col, factor=0.4, align=True)
        row.scale_y = button_height
        row.label(text="Separate by:", icon='MESH_DATA')
        row.operator('armature_manual.separate_by_materials', text='Materials')
        row.operator('armature_manual.separate_by_loose_parts', text='Loose Parts')

        row = layout_split(col, factor=0.4, align=True)
        row.scale_y = button_height
        row.label(text="Join Meshes:", icon='AUTOMERGE_ON')
        row.operator('armature_manual.join_meshes', text='All')
        row.operator('armature_manual.join_meshes_selected', text='Selected')

        row = layout_split(col, factor=0.4, align=True)
        row.scale_y = button_height
        row.label(text="Merge Weights:", icon='BONE_DATA')
        row.operator('armature_manual.merge_weights', text='To Parents')
        row.operator('armature_manual.merge_weights_to_active', text='To Active')

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
        row.operator('translate.all', text='All', icon=globs.ICON_ALL)

        row = split.column(align=True)
        row.operator('translate.shapekeys', text='Shape Keys', icon='SHAPEKEY_DATA')
        row.operator('translate.objects', text='Objects', icon='MESH_DATA')

        row = split.column(align=True)
        row.operator('translate.bones', text='Bones', icon='BONE_DATA')
        row.operator('translate.materials', text='Materials', icon='MATERIAL')

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
            row.operator('armature_manual.remove_zero_weight', text='Zero Weight Bones')
            row.operator('armature_manual.remove_constraints', text='Constraints')

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator('armature_manual.duplicate_bones', icon='GROUP_BONE')

            col.separator()
            row = layout_split(col, factor=0.27, align=True)
            row.scale_y = button_height
            row.label(text="Normals:", icon='SNAP_NORMAL')
            row.operator('armature_manual.recalculate_normals', text='Recalculate')
            row.operator('armature_manual.flip_normals', text='Flip')

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator('armature_manual.apply_transformations', icon='OUTLINER_DATA_ARMATURE')

            row = col.row(align=True)
            row.scale_y = 1
            subcol = layout_split(row, factor=0, align=True)
            subcol.scale_y = button_height
            subcol.operator('armature_manual.remove_doubles', icon='STICKY_UVS_VERT')
            subcol = layout_split(row, factor=0, align=True)
            subcol.scale_y = button_height
            subcol.operator('armature_manual.remove_doubles_normal', text="", icon='X')

            col.separator()
            # row = col.row(align=True)
            # row.scale_y = button_height
            # row.label(text="Other:", icon='COLLAPSEMENU')

            row = col.row(align=True)
            row.scale_y = 1
            subcol = layout_split(row, factor=0, align=True)
            subcol.scale_y = button_height
            subcol.operator('armature_manual.fix_fbt', icon='MODIFIER')
            subcol = layout_split(row, factor=0, align=True)
            subcol.scale_y = button_height
            subcol.operator('armature_manual.remove_fbt', text="", icon='X')

            row = col.row(align=True)
            row.scale_y = button_height
            row.operator('armature_manual.fix_vrm_shapes', icon='SHAPEKEY_DATA')
