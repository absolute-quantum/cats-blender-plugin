import bpy
import globs
import tools.common
import tools.supporter

from ui.main import ToolPanel
from ui.main import get_emtpy_icon
from tools.common import version_2_79_or_older

from tools.register import register_wrap

@register_wrap
class ArmaturePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_armature_v3'
    bl_label = 'Model'

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        if bpy.app.version < (2, 79, 0):
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text='Old Blender version detected!', icon='ERROR')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text='Some features might not work!', icon_value=get_emtpy_icon())
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text='Please update to Blender 2.79!', icon_value=get_emtpy_icon())
            col.separator()
            col.separator()

        # if addon_updater_ops.updater.update_ready:  # TODO
        #     col.separator()
        #     row = col.row(align=True)
        #     row.scale_y = 0.75
        #     row.label(text='New Cats version available!', icon='INFO')
        #     row = col.row(align=True)
        #     row.scale_y = 0.75
        #     row.label(text='Check the Updater panel!', icon_value=get_emtpy_icon())
        #     col.separator()
        #     col.separator()

        if not globs.dict_found:
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text='Dictionary not found!', icon='INFO')
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text='Translations will work, but are not optimized.', icon_value=get_emtpy_icon())
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text='Reinstall Cats to fix this.', icon_value=get_emtpy_icon())
            col.separator()
            col.separator()

        # Show news from the plugin
        if tools.supporter.supporter_data and tools.supporter.supporter_data.get('news') and tools.supporter.supporter_data.get('news'):
            showed_info = False
            for i, news in enumerate(tools.supporter.supporter_data.get('news')):
                info = news.get('info')
                icon = news.get('icon')
                custom_icon = news.get('custom_icon')
                if info and not news.get('disabled'):
                    showed_info = True

                    row = col.row(align=True)
                    row.scale_y = 0.75
                    if custom_icon:
                        try:
                            row.label(text=info, icon_value=tools.supporter.preview_collections["supporter_icons"][custom_icon].icon_id)
                        except KeyError:
                            row.label(text=info)
                    elif icon:
                        try:
                            row.label(text=info, icon=icon)
                        except TypeError:
                            row.label(text=info)
                    else:
                        row.label(text=info)
            if showed_info:
                col.separator()
                col.separator()

        # row = col.row(align=True)
        # row.prop(context.scene, 'import_mode', expand=True)
        # row = col.row(align=True)
        # row.scale_y = 1.4
        # row.operator('armature_manual.import_model', icon='ARMATURE_DATA')

        arm_count = len(tools.common.get_armature_objects())
        if arm_count == 0:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.7
            row.operator('importer.import_any_model', text='Import Model', icon='ARMATURE_DATA')
            row = split.row(align=True)
            row.alignment = 'RIGHT'
            row.scale_y = 1.7
            row.operator("model.popup", text="", icon='COLLAPSEMENU')
            return
        else:
            split = col.row(align=True)
            row = split.row(align=True)
            row.scale_y = 1.4
            row.operator('importer.import_any_model', text='Import Model', icon='ARMATURE_DATA')
            row.operator('importer.export_model', icon='ARMATURE_DATA').action = 'CHECK'
            row = split.row(align=True)
            row.scale_y = 1.4
            row.operator("model.popup", text="", icon='COLLAPSEMENU')

            # split = col.row(align=True)
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator('importer.import_any_model', text='Import Model', icon='ARMATURE_DATA')
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator("model.popup", text="", icon='COLLAPSEMENU')
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator('importer.export_model', icon='ARMATURE_DATA').action = 'CHECK'
            #
            # split = col.row(align=True)
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator("model.popup", text="", icon='COLLAPSEMENU')
            # row = split.row(align=True)
            # row.scale_y = 1.4
            # row.operator('importer.import_any_model', text='Import Model', icon='ARMATURE_DATA')
            # row.operator('importer.export_model', icon='ARMATURE_DATA').action = 'CHECK'

        if arm_count > 1:
            col.separator()
            col.separator()
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'armature', icon='ARMATURE_DATA')

        col.separator()
        col.separator()
        split = col.row(align=True)
        row = split.row(align=True)
        row.scale_y = 1.5
        row.operator('armature.fix', icon=globs.ICON_FIX_MODEL)
        row = split.row(align=True)
        row.alignment = 'RIGHT'
        row.scale_y = 1.5
        row.operator("armature.settings", text="", icon='MODIFIER')

        if context.scene.full_body:
            row = col.row(align=True)
            row.scale_y = 0.9
            row.label(text='You can safely ignore the', icon='INFO')
            row = col.row(align=True)
            row.scale_y = 0.5
            row.label(text='"Spine length zero" warning in Unity.', icon_value=get_emtpy_icon())
            col.separator()
        else:
            col.separator()
            col.separator()

        armature = tools.common.get_armature()
        if not armature or armature.mode != 'POSE':
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator('armature_manual.start_pose_mode', icon='POSE_HLT')
        else:
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator('armature_manual.stop_pose_mode', icon=globs.ICON_POSE_MODE)
            if not tools.eyetracking.eye_left:
                row = col.row(align=True)
                row.scale_y = 0.9
                row.operator('armature_manual.pose_to_shape', icon='SHAPEKEY_DATA')
                row = col.row(align=True)
                row.scale_y = 0.9
                row.operator('armature_manual.pose_to_rest', icon='POSE_HLT')
