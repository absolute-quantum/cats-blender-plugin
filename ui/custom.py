import bpy

from .main import ToolPanel
from .. import globs
from ..tools import common as Common
from ..tools import supporter as Supporter
from ..tools import armature_bones as Armature_bones
from ..tools import armature_custom as Armature_custom
from ..tools.register import register_wrap
from ..translations import t


@register_wrap
class CustomPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_custom_v3'
    bl_label = t('CustomPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.operator(Armature_custom.CustomModelTutorialButton.bl_idname, icon='FORWARD')
        col.separator()

        row = col.row(align=True)
        row.prop(context.scene, 'merge_mode', expand=True)
        col.separator()

        # Merge Armatures
        if context.scene.merge_mode == 'ARMATURE':
            row = col.row(align=True)
            row.scale_y = 1.05
            row.label(text=t('CustomPanel.mergeArmatures'))

            if len(Common.get_armature_objects()) <= 1:
                row = col.row(align=True)
                row.scale_y = 1.05
                col.label(text=t('CustomPanel.warn.twoArmatures'), icon='INFO')
                return

            row = col.row(align=True)
            row.scale_y = 0.95
            row.prop(context.scene, 'merge_same_bones')

            row = col.row(align=True)
            row.scale_y = 0.95
            row.prop(context.scene, 'apply_transforms')
            row.active = context.scene.merge_armatures_join_meshes

            row = col.row(align=True)
            row.scale_y = 0.95
            row.prop(context.scene, 'merge_armatures_join_meshes')

            row = col.row(align=True)
            row.scale_y = 0.95
            row.prop(context.scene, 'merge_armatures_remove_zero_weight_bones')

            row = col.row(align=True)
            row.scale_y = 1.05
            row.prop(context.scene, 'merge_armature_into', text=t('CustomPanel.mergeInto'), icon=globs.ICON_MOD_ARMATURE)
            row = col.row(align=True)
            row.scale_y = 1.05
            row.prop(context.scene, 'merge_armature', text=t('CustomPanel.toMerge'), icon_value=Supporter.preview_collections["custom_icons"]["UP_ARROW"].icon_id)

            if not context.scene.merge_same_bones:
                found = False
                base_armature = Common.get_armature(armature_name=context.scene.merge_armature_into)
                merge_armature = Common.get_armature(armature_name=context.scene.merge_armature)
                if merge_armature:
                    for bone in Armature_bones.dont_delete_these_main_bones:
                        if 'Eye' not in bone and bone in merge_armature.pose.bones and bone in base_armature.pose.bones:
                            found = True
                            break
                if not found:
                    row = col.row(align=True)
                    row.scale_y = 1.05
                    row.prop(context.scene, 'attach_to_bone', text=t('CustomPanel.attachToBone'), icon='BONE_DATA')
                else:
                    row = col.row(align=True)
                    row.scale_y = 1.05
                    row.label(text=t('CustomPanel.armaturesCanMerge'))

            row = col.row(align=True)
            row.scale_y = 1.2
            row.operator(Armature_custom.MergeArmature.bl_idname, icon='ARMATURE_DATA')

        # Attach Mesh
        else:
            row = col.row(align=True)
            row.scale_y = 1.05
            row.label(text=t('CustomPanel.attachMesh1'))

            if len(Common.get_armature_objects()) == 0 or len(Common.get_meshes_objects(mode=1, check=False)) == 0:
                row = col.row(align=True)
                row.scale_y = 1.05
                col.label(text=t('CustomPanel.warn.noArmOrMesh1'), icon='INFO')
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text=t('CustomPanel.warn.noArmOrMesh2'), icon='BLANK1')
                return

            row = col.row(align=True)
            row.scale_y = 0.95
            row.prop(context.scene, 'merge_armatures_join_meshes')

            row = col.row(align=True)
            row.scale_y = 1.05
            row.prop(context.scene, 'merge_armature_into', text=t('CustomPanel.mergeInto'), icon=globs.ICON_MOD_ARMATURE)
            row = col.row(align=True)
            row.scale_y = 1.05
            row.prop(context.scene, 'attach_mesh', text=t('CustomPanel.attachMesh2'), icon_value=Supporter.preview_collections["custom_icons"]["UP_ARROW"].icon_id)

            row = col.row(align=True)
            row.scale_y = 1.05
            row.prop(context.scene, 'attach_to_bone', text=t('CustomPanel.attachToBone'), icon='BONE_DATA')

            row = col.row(align=True)
            row.scale_y = 1.2
            row.operator(Armature_custom.AttachMesh.bl_idname, icon='ARMATURE_DATA')
