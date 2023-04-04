# GPL License

import bpy

from .main import ToolPanel
from .. import globs
from ..tools import common as Common
from ..tools import supporter as Supporter
from ..tools import armature_bones as Armature_bones
from ..tools import armature_custom as Armature_custom
from ..tools.register import register_wrap
from ..tools.translations import t


@register_wrap
class SearchMenuOperator_merge_armature_into(bpy.types.Operator):
    bl_description = t('Scene.merge_armature_into.desc')
    bl_idname = "scene.search_menu_merge_armature_into"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name=t('Scene.merge_armature_into.label'), description=t('Scene.merge_armature_into.desc'), items=Common.get_armature_list)

    def execute(self, context):
        context.scene.merge_armature_into = self.my_enum
        print(context.scene.root_bone)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperator_merge_armature(bpy.types.Operator):
    bl_description = t('Scene.merge_armature.desc')
    bl_idname = "scene.search_menu_merge_armature"
    bl_label = t('Scene.root_bone.label')
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name=t('Scene.merge_armature.label'), description= t('Scene.merge_armature.desc'), items=Common.get_armature_merge_list)

    def execute(self, context):
        context.scene.merge_armature = self.my_enum
        print(context.scene.root_bone)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperator_attach_to_bone(bpy.types.Operator):
    bl_description = t('Scene.attach_to_bone.desc')
    bl_idname = "scene.search_menu_attach_to_bone"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name=t('Scene.attach_to_bone.label'), description= t('Scene.attach_to_bone.desc'), items=Common.get_bones_merge)

    def execute(self, context):
        context.scene.attach_to_bone = self.my_enum
        print(context.scene.root_bone)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}

@register_wrap
class SearchMenuOperator_attach_mesh(bpy.types.Operator):
    bl_description = t('Scene.attach_mesh.desc')
    bl_idname = "scene.search_menu_attach_mesh"
    bl_label = ""
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name=t('Scene.attach_mesh.label'), description= t('Scene.attach_mesh.desc'), items=Common.get_top_meshes)

    def execute(self, context):
        context.scene.attach_mesh = self.my_enum
        print(context.scene.root_bone)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}






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
            row.scale_y = 0.95
            row.prop(context.scene, 'merge_armatures_cleanup_shape_keys')

            row = col.row(align=True)
            row.scale_y = 1.05
            row.label(text=t('CustomPanel.mergeInto'))
            row.operator(SearchMenuOperator_merge_armature_into.bl_idname,text = context.scene.merge_armature_into, icon=globs.ICON_MOD_ARMATURE)
            row = col.row(align=True)
            row.scale_y = 1.05
            row.label(text=t('CustomPanel.toMerge'))
            row.operator(SearchMenuOperator_merge_armature.bl_idname,text = context.scene.merge_armature, icon_value=Supporter.preview_collections["custom_icons"]["UP_ARROW"].icon_id)

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
                    row.label(text=t('CustomPanel.attachToBone'))
                    row.operator(SearchMenuOperator_attach_to_bone.bl_idname, text=context.scene.attach_to_bone, icon='BONE_DATA')
                else:
                    row = col.row(align=True)
                    row.scale_y = 1.05
                    row.label(text=t('CustomPanel.armaturesCanMerge'))

            row = col.row(align=True)
            row.scale_y = 1.2
            row.operator(Armature_custom.MergeArmature.bl_idname, icon='ARMATURE_DATA')

        # Attach Mesh
        elif context.scene.merge_mode == "MESH":
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
            row.label(text=t('CustomPanel.mergeInto'))
            row.operator(SearchMenuOperator_merge_armature_into.bl_idname,text = context.scene.merge_armature_into, icon=globs.ICON_MOD_ARMATURE)
            row = col.row(align=True)
            row.scale_y = 1.05
            row.label(text=t('CustomPanel.attachMesh2'))
            row.operator(SearchMenuOperator_attach_mesh.bl_idname, text=context.scene.attach_mesh, icon_value=Supporter.preview_collections["custom_icons"]["UP_ARROW"].icon_id)

            row = col.row(align=True)
            row.scale_y = 1.05
            row.label(text=t('CustomPanel.attachToBone'))
            row.operator(SearchMenuOperator_attach_to_bone.bl_idname, text=context.scene.attach_to_bone, icon='BONE_DATA')

            row = col.row(align=True)
            row.scale_y = 1.2
            row.operator(Armature_custom.AttachMesh.bl_idname, icon='ARMATURE_DATA')
