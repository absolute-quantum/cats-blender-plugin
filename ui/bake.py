import bpy
import addon_utils

from .. import globs
from .main import ToolPanel
from ..tools import common as Common
from ..tools import bake as Bake
from ..tools.register import register_wrap
from ..tools.translations import t

from bpy.types import UIList, Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty

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
class Bake_Lod_New(Operator):
    bl_idname = "cats_bake.lod_add"
    bl_label = "Add"

    @classmethod
    def poll(cls, context):
        return context.scene.bake_platforms

    def execute(self, context):
        bake_platforms = context.scene.bake_platforms
        index = context.scene.bake_platform_index

        lods = bake_platforms[index].lods
        lods.add()

        return{'FINISHED'}

@register_wrap
class Bake_Lod_Delete(Operator):
    bl_idname = "cats_bake.lod_remove"
    bl_label = "Delete"

    @classmethod
    def poll(cls, context):
        bake_platforms = context.scene.bake_platforms
        index = context.scene.bake_platform_index

        return context.scene.bake_platforms and len(bake_platforms[index].lods) > 1

    def execute(self, context):
        bake_platforms = context.scene.bake_platforms
        index = context.scene.bake_platform_index

        lods = bake_platforms[index].lods
        lods.remove(len(lods) - 1)

        return{'FINISHED'}

@register_wrap
class Choose_Steam_Library(Operator, ImportHelper):
    bl_idname = "cats_bake.choose_steam_library"
    bl_label = "Choose Steam Library"
    
    directory = StringProperty(subtype='DIR_PATH')
    
    @classmethod
    def poll(cls, context):
        bake_platforms = context.scene.bake_platforms
        index = context.scene.bake_platform_index

        return bake_platforms[index].export_format == "GMOD"
    def execute(self, context):
        context.scene.bake_steam_library = self.directory
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
        row.operator(Bake.BakePresetAll.bl_idname, icon="SHADERFX")
        row = col.row(align=True)
        row.operator(Bake.BakePresetDesktop.bl_idname, icon="ANTIALIASED")
        row.operator(Bake.BakePresetQuest.bl_idname, icon="ALIASED")
        row = col.row(align=True)
        row.operator(Bake.BakePresetSecondlife.bl_idname, icon="VIEW_PAN")
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
            row.separator()
            row.prop(item, 'use_decimation', expand=True)
            if item.use_decimation:
                row = col.row(align=True)
                row.separator()
                row.prop(item, 'max_tris', expand=True)
            ### BEGIN ADVANCED PLATFORM OPTIONS
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.85
            if not context.scene.bake_show_advanced_platform_options:
                row.prop(context.scene, 'bake_show_advanced_platform_options', icon=globs.ICON_ADD, emboss=True, expand=False, toggle=False, event=False)
            else:
                row.prop(context.scene, 'bake_show_advanced_platform_options', icon=globs.ICON_REMOVE, emboss=True, expand=False, toggle=False, event=False)
                if item.use_decimation:
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
                row.prop(item, 'use_physmodel', expand=True)
                if item.use_physmodel:
                    row = col.row(align=True)
                    row.prop(item, 'physmodel_lod', expand=True)
                row = col.row(align=True)
                row.prop(item, 'use_lods', expand=True)
                if item.use_lods:
                    row = col.row(align=True)
                    row.prop(item, 'lods', expand=True)
                    row = col.row(align=True)
                    row.operator(Bake_Lod_New.bl_idname)
                    row.operator(Bake_Lod_Delete.bl_idname)
                row = col.row(align=True)
                row.prop(item, 'optimize_static', expand=True)
                row = col.row(align=True)
                row.prop(item, 'merge_twistbones', expand=True)
                row = col.row(align=True)
                row.prop(item, 'generate_prop_bones', expand=True)
                if item.generate_prop_bones:
                    row = col.row(align=True)
                    row.prop(item, 'generate_prop_bone_max_influence_count', expand=True)

                row = col.row(align=True)
                row.prop(item, 'specular_setup', expand=True)
                if item.specular_setup:
                    row = col.row(align=True)
                    row.prop(item, 'specular_alpha_pack', expand=True)
                if context.scene.bake_pass_diffuse and context.scene.bake_pass_emit:
                    row = col.row(align=True)
                    row.prop(item, "diffuse_emit_overlay", expand=True)
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
                        row.prop(item, 'smoothness_premultiply_opacity', expand=True)
                if context.scene.bake_pass_diffuse:
                    if bpy.app.version >= (2, 92, 0):
                        row = col.row(align=True)
                        row.prop(item, 'diffuse_vertex_colors', expand=True)
                if context.scene.bake_pass_diffuse and (context.scene.bake_pass_smoothness or context.scene.bake_pass_alpha) and not item.diffuse_vertex_colors:
                    row = col.row(align=True)
                    row.label(text="Diffuse Alpha:")
                    row.prop(item, 'diffuse_alpha_pack', expand=True)
                    if (item.diffuse_alpha_pack == "TRANSPARENCY") and not context.scene.bake_pass_alpha:
                        col.label(text=t('BakePanel.transparencywarning'), icon="INFO")
                    elif (item.diffuse_alpha_pack == "SMOOTHNESS") and not context.scene.bake_pass_smoothness:
                        col.label(text=t('BakePanel.smoothnesswarning'), icon="INFO")
                if context.scene.bake_pass_metallic and context.scene.bake_pass_smoothness and not item.specular_setup:
                    row = col.row(align=True)
                    row.label(text="Metallic Alpha:")
                    row.prop(item, 'metallic_alpha_pack', expand=True)
                    if item.diffuse_alpha_pack == "SMOOTHNESS" and item.metallic_alpha_pack == "SMOOTHNESS":
                        col.label(text=t('BakePanel.doublepackwarning'), icon="INFO")
                row = col.row(align=True)
                row.label(text="Bone Conversion:")
                row = col.row(align=True)
                row.separator()
                row.prop(item, 'translate_bone_names')
                row = col.row(align=True)
                row.separator()
                row.prop(item, 'export_format')
                row = col.row(align=True)
                row.separator()
                row.prop(item, 'image_export_format')
        # END ADVANCED PLATFORM OPTIONS
        
        if context.scene.bake_platforms:
            col.separator()
            col.label(text=t('BakePanel.generaloptionslabel'))
            row = col.row(align=True)
            row.prop(context.scene, 'bake_resolution', expand=True)
            row = col.row(align=True)
            row.prop(context.scene, 'bake_ignore_hidden', expand=True)
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

                row = col.row(align=True)
                row.separator()
                if context.scene.bake_uv_overlap_correction != "NONE" and (not context.scene.bake_pass_ao) and (not any(plat.use_decimation for plat in context.scene.bake_platforms)) and (not context.scene.bake_pass_normal):
                    row.prop(context.scene, 'bake_optimize_solid_materials', expand=True)
                    row = col.row(align=True)
                row.separator()
                row.label(text=t('BakePanel.overlapfixlabel'))
                row.prop(context.scene, 'bake_uv_overlap_correction', expand=True)
                if context.scene.bake_uv_overlap_correction == "REPROJECT":
                    row = col.row(align=True)
                    row.separator()
                    row.prop(context.scene, 'bake_unwrap_angle', expand=True)
            row = col.row(align=True)
            row.scale_y = 0.85
            if item.export_format == "GMOD":
                row = col.row(align=True)
                row.operator(Choose_Steam_Library.bl_idname, icon="FILE_FOLDER")
                row = col.row(align=True)
                row.prop(context.scene, "bake_steam_library", expand=True)
                row = col.row(align=True)
                row.prop(item, "gmod_model_name", expand=True)
                row = col.row(align=True)
            if not context.scene.bake_show_advanced_general_options:
                row.prop(context.scene, 'bake_show_advanced_general_options', icon=globs.ICON_ADD, emboss=True, expand=False, toggle=False, event=False)
            else:
                row.prop(context.scene, 'bake_show_advanced_general_options', icon=globs.ICON_REMOVE, emboss=True, expand=False, toggle=False, event=False)
                row = col.row(align=True)
                row.prop(context.scene, 'bake_sharpen', expand=True)
                row = col.row(align=True)
                row.prop(context.scene, 'bake_denoise', expand=True)
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
                    if context.scene.bake_illuminate_eyes:
                        multires_obj_names = []
                        for obj in Common.get_meshes_objects(check=False):
                            if obj.name not in context.view_layer.objects:
                                continue
                            if Common.is_hidden(obj):
                                 continue
                            if any(mod.type == "MULTIRES" for mod in obj.modifiers):
                                multires_obj_names.add(obj.name)

                        if multires_obj_names:
                            row = col.row(align=True)
                            row.separator()
                            row.label(text="One or more of your objects are using Multires.", icon="ERROR")
                            row = col.row(align=True)
                            row.separator()
                            row.label(text="This has issues excluding the eyes, try adding")
                            row = col.row(align=True)
                            row.separator()
                            row.label(text="'ambient occlusion' shape keys instead.")

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
        ### END ADVANCED GENERAL OPTIONS
        else: # if not bake_platforms:
            row = col.row(align=True)
            row.label(text="To get started, press 'Autodetect All' above.", icon="INFO")
            row = col.row(align=True)
            row.label(text="Then if the settings look right, press 'Copy and Bake'.", icon="BLANK1")

        col.separator()
        col.separator()
        if context.preferences.addons['cycles'].preferences.compute_device_type == 'NONE' and context.scene.bake_device == 'GPU':
            row = col.row(align=True)
            row.label(text="No render device configured in Blender settings. Bake will use CPU", icon="INFO")
        if not addon_utils.check("render_auto_tile_size")[1] and Common.version_2_93_or_older():
            row = col.row(align=True)
            row.label(text="Enabling \"Auto Tile Size\" plugin reccomended!", icon="INFO")
        row = col.row(align=True)
        row.prop(context.scene, 'bake_device', expand=True)

        # Bake button
        row = col.row(align=True)
        row.operator(Bake.BakeButton.bl_idname, icon='RENDER_STILL')

        # Warnings. Ideally these should be dynamically generated but only take up a limited number of rows
        non_bsdf_mat_names = set()
        multi_bsdf_mat_names = set()
        non_node_mat_names = set()
        non_world_scale_names = set()
        empty_material_slots = set()
        for obj in Common.get_meshes_objects(check=False):
            if obj.name not in context.view_layer.objects:
                continue
            if Common.is_hidden(obj):
                continue
            for slot in obj.material_slots:
                if slot.material:
                    if not slot.material.use_nodes:
                        non_node_mat_names.add(slot.material.name)
                    if not any(node.type == "BSDF_PRINCIPLED" for node in slot.material.node_tree.nodes):
                        non_bsdf_mat_names.add(slot.material.name)
                    if len([node for node in slot.material.node_tree.nodes if node.type == "BSDF_PRINCIPLED"]) > 1:
                        multi_bsdf_mat_names.add(slot.material.name)
                else:
                    if len(obj.material_slots) == 1:
                        empty_material_slots.add(obj.name)
            if len(obj.material_slots) == 0:
                empty_material_slots.add(obj.name)
            if any(dim != 1.0 for dim in obj.scale):
                non_world_scale_names.add(obj.name)

        if non_node_mat_names:
            row = col.row(align=True)
            row.label(text="The following materials do not use nodes!", icon="ERROR")
            row = col.row(align=True)
            row.label(text="Ensure they have Use Nodes checked in their properties or Bake will not run.", icon="BLANK1")
            for name in non_node_mat_names:
                row = col.row(align=True)
                row.label(text=name, icon="MATERIAL")
        if non_bsdf_mat_names:
            row = col.row(align=True)
            row.label(text="The following materials do not use Principled BSDF!", icon="INFO")
            row = col.row(align=True)
            row.label(text="Bake may have unexpected results.", icon="BLANK1")
            for name in non_bsdf_mat_names:
                row = col.row(align=True)
                row.separator()
                row.label(text=name, icon="MATERIAL")
        if multi_bsdf_mat_names:
            row = col.row(align=True)
            row.label(text="The following materials have multiple Principled BSDF!", icon="INFO")
            row = col.row(align=True)
            row.label(text="Bake may have unexpected results.", icon="BLANK1")
            for name in multi_bsdf_mat_names:
                row = col.row(align=True)
                row.separator()
                row.label(text=name, icon="MATERIAL")
        if empty_material_slots:
            row = col.row(align=True)
            row.label(text="The following objects have no material.", icon="INFO")
            row = col.row(align=True)
            row.label(text="Please assign one before continuing.", icon="BLANK1")
            for name in empty_material_slots:
                row = col.row(align=True)
                row.separator()
                row.label(text=name, icon="OBJECT_DATA")
        if non_world_scale_names:
            row = col.row(align=True)
            row.label(text="The following objects do not have scale applied", icon="INFO")
            row = col.row(align=True)
            row.label(text="The resulting islands will be inversely scaled.", icon="BLANK1")
            for name in non_world_scale_names:
                row = col.row(align=True)
                row.separator()
                row.label(text=name + ": " + "{:.1f}".format(1.0/bpy.data.objects[name].scale[0]) + "x", icon="OBJECT_DATA")

