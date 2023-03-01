# GPL License

import bpy

from .main import ToolPanel
from ..tools import rootbone as Rootbone
from ..tools.register import register_wrap
from ..tools.translations import t


@register_wrap
class SearchMenuOperator_root_bone(bpy.types.Operator):
    bl_description = t('Scene.root_bone.desc')
    bl_idname = "scene.search_menu_root_bone"
    bl_label = ""#t('Scene.root_bone.label')
    bl_property = "my_enum"

    my_enum: bpy.props.EnumProperty(name=t('Scene.root_bone.label'),description= t('Scene.root_bone.desc'), items=Rootbone.get_parent_root_bones)
    
    def execute(self, context):
        context.scene.root_bone = self.my_enum
        print(context.scene.root_bone)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        wm.invoke_search_popup(self)
        return {'FINISHED'}


@register_wrap
class BoneRootPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_boneroot_v3'
    bl_label = t('BoneRootPanel.label')
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.operator(SearchMenuOperator_root_bone.bl_idname, text = context.scene.root_bone, icon='BONE_DATA')
        row = box.row(align=True)
        row.operator(Rootbone.RefreshRootButton.bl_idname, icon='FILE_REFRESH')
        row.operator(Rootbone.RootButton.bl_idname, icon='TRIA_RIGHT')
