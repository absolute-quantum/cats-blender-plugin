# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: GiveMeAllYourCats
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: Hotox

import bpy
import webbrowser
import addon_utils

from . import common as Common
from .register import register_wrap
from .. import globs
from ..translations import t


# addon_name = "Shotariya-don"
# min_version = [1, 1, 6]


@register_wrap
class EnableSMC(bpy.types.Operator):
    bl_idname = 'cats_atlas.enable_smc'
    bl_label = t('EnableSMC.label')
    bl_description = t('EnableSMC.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        # disable all wrong versions
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == "Shotariya-don":
                if addon_utils.check(mod.__name__)[0]:
                    try:
                        bpy.ops.wm.addon_disable(module=mod.__name__)
                    except:
                        pass
                    continue
            if mod.bl_info['name'] == "Shotariya's Material Combiner":
                if mod.bl_info['version'] < (2, 1, 1, 2) and addon_utils.check(mod.__name__)[0]:
                    try:
                        bpy.ops.wm.addon_disable(module=mod.__name__)
                    except:
                        pass
                    continue

        # then enable correct version
        for mod in addon_utils.modules():
            if mod.bl_info['name'] == "Shotariya's Material Combiner":
                if mod.bl_info['version'] < (2, 1, 1, 2):
                    continue
                if not addon_utils.check(mod.__name__)[0]:
                    bpy.ops.wm.addon_enable(module=mod.__name__)
                    break
        self.report({'INFO'}, t('EnableSMC.success'))
        return {'FINISHED'}


# @register_wrap
# class AutoAtlasNewButton(bpy.types.Operator):
#     bl_idname = 'cats_atlas.generate_atlas'
#     bl_label = 'Create Atlas'
#     bl_description = 'Generates a texture atlas.' \
#                      '\n' \
#                      '\nGenerate the Material List to select what you want to combine.' \
#                      '\nOtherwise this will combine all materials.' \
#                      '\n' \
#                      '\nThis is a shortcut to shotariyas plugin.' \
#                      '\nIf you want more options, use the plugin tab "shotariya"'
#     bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
#
#     def execute(self, context):
#         if not Common.version_2_79_or_older():
#             self.report({'ERROR'}, 'This function is not yet compatible with Blender 2.8!')
#             return {'CANCELLED'}
#             # TODO
#
#         # Check if shotariyas plugin is correctly set up
#         print('show error from button')
#         if not shotariya_installed(show_error=True):
#             return {'CANCELLED'}
#
#         # Check if there are meshes in the model
#         if not Common.get_meshes_objects():
#             Common.show_error(2.8, ['No model with meshes found!'])
#             return {'CANCELLED'}
#
#         # Check if all textures are found and count the materials/textures to check if it is already atlased
#         missing_textures = []
#         material_list = []
#         texture_list = []
#         empty_tex_count = 0
#         if len(context.scene.material_list) == 0:
#             for mesh in Common.get_meshes_objects():
#                 for mat_slot in mesh.material_slots:
#                     if mat_slot and mat_slot.material:
#                         mat = mat_slot.material
#                         if mat.name not in material_list:
#                             material_list.append(mat.name)
#
#                         tex_slot = mat.texture_slots[0]
#                         if tex_slot and tex_slot.texture:
#                             if tex_slot.texture.name not in texture_list:
#                                 texture_list.append(tex_slot.texture.name)
#
#                             tex_path = bpy.path.abspath(tex_slot.texture.image.filepath)
#                             if not os.path.isfile(tex_path) and tex_path not in missing_textures:
#                                 missing_textures.append(tex_path)
#                         else:
#                             texture_list.append('Empty' + str(empty_tex_count))
#                             empty_tex_count += 1
#         else:
#             for item in context.scene.material_list:
#                 mat = item.material
#                 if item.material.add_to_atlas:
#                     material_list.append(mat.name)
#
#                     tex_slot = mat.texture_slots[0]
#                     if tex_slot and tex_slot.texture:
#                         if tex_slot.texture.name not in texture_list:
#                             texture_list.append(tex_slot.texture.name)
#
#                         tex_path = bpy.path.abspath(tex_slot.texture.image.filepath)
#                         if not os.path.isfile(tex_path) and tex_path not in missing_textures:
#                             missing_textures.append(tex_path)
#                     else:
#                         texture_list.append('Empty' + str(empty_tex_count))
#                         empty_tex_count += 1
#
#         # Check if there is an atlas already
#         if len(material_list) == 0:
#             if len(context.scene.material_list) == 0:
#                 Common.show_error(2.3, ['No materials found!'])
#             else:
#                 Common.show_error(2.3, ['No materials selected!'])
#             return {'CANCELLED'}
#
#         # Check if there is an atlas already
#         if len(material_list) == 1:
#             Common.show_error(5, ['No need to create an atlas, there is already only one material.'])
#             return {'CANCELLED'}
#
#         # Check if there are too few items selected in the list
#         if len(context.scene.material_list) > 0:
#             checked_mats_count = 0
#             for item in context.scene.material_list:
#                 if item.material.add_to_atlas:
#                     checked_mats_count += 1
#
#             if checked_mats_count <= 1:
#                 Common.show_error(3.2, ['Please select more than one material.'])
#                 return {'CANCELLED'}
#
#         # Check if too few textures are selected
#         if len(texture_list) <= 1:
#             if len(context.scene.material_list) > 0:
#                 Common.show_error(4.1, ['You only selected materials with the same texture.',
#                                               'You need multiple textures to generate an atlas.'])
#             else:
#                 Common.show_error(3.4, ['All materials are using the same texture.',
#                                               'There is no need to create an atlas.'])
#             return {'CANCELLED'}
#
#         # Check if there are missing textures
#         if missing_textures:
#             longest_line = 'Use "File > External Data > Find Missing Files" to fix this.'
#             message = ['Could not find the following textures:']
#             for index, missing_texture in enumerate(missing_textures):
#                 if index < 5:
#                     line = ' - ' + missing_texture
#                     message.append(line)
#                     if len(line) > len(longest_line):
#                         longest_line = line
#
#                 else:
#                     message.append('...and ' + str(len(missing_textures) - 5) + ' more.')
#                     break
#             message.append('')
#             message.append('Use "File > External Data > Find Missing Files" to fix this.')  # TODO: Check this in 2.8
#
#             width = 0
#             for char in longest_line:
#                 width += 0.095
#
#             Common.show_error(width, message)
#             return {'CANCELLED'}
#
#         # Check if Blend file is saved
#         if not bpy.data.is_saved:
#             Common.show_error(4.5, ['You have to save this Blender file first!',
#                                           'The generated atlas will be saved to the same location.'])
#             return {'CANCELLED'}
#
#         # Getting the directory of the currently saved blend file
#         filepath = bpy.data.filepath
#         directory = os.path.dirname(filepath)
#
#         # Saves all the file names in the current directory for later comparison
#         files = []
#         for file in os.listdir(directory):
#             files.append(file)
#
#         # Filling the list with textures and concurrently checking if shotaiyas plugin is installed
#         Common.set_default_stage()
#         bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='GENERATE_TEX')
#
#         # Sets the folder for saving the generated textures
#         bpy.ops.shotariya.tex_folder('EXEC_DEFAULT', filepath=directory)
#
#         # Deselects all textures and then selects only the ones from the current model
#         bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='CLEAR_TEX')
#         if len(context.scene.material_list) == 0:
#             for mesh in Common.get_meshes_objects():
#                 for mat_slot in mesh.material_slots:
#                     if mat_slot:
#                         bpy.data.materials[mat_slot.material.name].to_tex = True
#         else:
#             for item in context.scene.material_list:
#                 if item.material.add_to_atlas:
#                     bpy.data.materials[item.material.name].to_tex = True
#
#         # Generating the textures of UVs with bounds greater than 1
#         try:
#             bpy.ops.shotariya.gen_tex('INVOKE_DEFAULT')
#         except RuntimeError as e:
#             print(str(e))
#             pass
#
#         # Filling the list with the materials and setting the folder to save the created atlas
#         bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='GENERATE_MAT')
#         bpy.ops.shotariya.combined_folder('EXEC_DEFAULT', filepath=directory)
#
#         # Deselects all materials and then selects only the ones from the current model
#         bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='CLEAR_MAT')
#         if len(context.scene.material_list) == 0:
#             for mesh in Common.get_meshes_objects():
#                 for mat_slot in mesh.material_slots:
#                     if mat_slot:
#                         bpy.data.materials[mat_slot.material.name].to_combine = True
#         else:
#             for item in context.scene.material_list:
#                 if item.material.add_to_atlas:
#                     bpy.data.materials[item.material.name].to_combine = True
#
#         # Generating the atlas
#         error = None
#         try:
#             bpy.ops.shotariya.gen_mat('INVOKE_DEFAULT')
#         except RuntimeError as e:
#             error = str(e).replace('Error: ', '')
#
#         # Deleting generated textures and searching for generated atlas
#         atlas_name = None
#         for file in os.listdir(directory):
#             if file not in files:
#                 if file.endswith('_uv.png'):
#                     os.remove(os.path.join(directory, file))
#                     print('Deleted', file)
#                 if file.startswith('combined_image_'):
#                     atlas_name = file
#
#         # Update material list
#         if len(context.scene.material_list) > 0:
#             bpy.ops.cats_atlas.gen_mat_list('INVOKE_DEFAULT')
#
#         # Check if the atlas was successfully generated
#         if not error and not atlas_name:
#             error = 'You only selected materials that are using the same texture. These materials were combined.'
#
#         # Finish
#         Common.set_default_stage()
#         if error:
#             self.report({'ERROR'}, error)
#         else:
#             self.report({'INFO'}, 'Auto Atlas finished! Atlas saved as "' + atlas_name + '"')
#         return {'FINISHED'}


# @register_wrap
# class MaterialsGroup(bpy.types.PropertyGroup):
#     material = bpy.props.PointerProperty(
#         name='Material',
#         type=bpy.types.Material
#     )


# @register_wrap
# class GenerateMaterialListButton(bpy.types.Operator):
#     bl_idname = 'cats_atlas.gen_mat_list'
#     bl_label = 'Generate Material List'
#     bl_description = 'This generates the material list.' \
#                      '\nUse this to select which materials you want to combine.' \
#                      '\nOtherwise all materials will be combined'
#     bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
#
#     def execute(self, context):
#         if not Common.version_2_79_or_older():
#             self.report({'ERROR'}, 'This function is not yet compatible with Blender 2.8!')
#             return {'CANCELLED'}
#             # TODO
#
#         print("show error from button 2")
#         if not shotariya_installed():
#             return {'CANCELLED'}
#
#         # Check if there are meshes
#         if not Common.get_meshes_objects():
#             Common.show_error(2.8, ['No model with meshes found!'])
#             return {'CANCELLED'}
#
#         scene = context.scene
#         scene.material_list.clear()
#         scene.clear_materials = True
#         scene.material_list_index = 0
#
#         for mesh in Common.get_meshes_objects():
#             if not mesh.data.uv_layers.active:
#                 continue
#
#             Common.clean_material_names(mesh)
#
#             for mat_slot in mesh.material_slots:
#                 if mat_slot and mat_slot.material:
#                     mat = mat_slot.material
#                     mat.add_to_atlas = True
#
#                     item = scene.material_list.add()
#                     item.id = len(scene.material_list)
#                     item.name = mat.name
#                     item.material = mat
#                     item.add_to_atlas = mat.add_to_atlas
#                     scene.material_list_index = (len(scene.material_list) - 1)
#         return {'FINISHED'}


@register_wrap
class AtlasHelpButton(bpy.types.Operator):
    bl_idname = 'cats_atlas.help'
    bl_label = t('AtlasHelpButton.label')
    bl_description = t('AtlasHelpButton.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('AtlasHelpButton.URL'))
        self.report({'INFO'}, t('AtlasHelpButton.success'))
        return {'FINISHED'}


# @register_wrap
# class ClearMaterialListButton(bpy.types.Operator):
#     bl_idname = 'cats_atlas.clear_mat_list'
#     bl_label = 'Clear Material List'
#     bl_description = 'Clears the material list'
#     bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
#
#     def execute(self, context):
#         context.scene.material_list.clear()
#         return {'FINISHED'}


# def update_material_list(self, context):
#     print('Update mat list')
#     if len(context.scene.material_list) > 0:
#         bpy.ops.cats_atlas.gen_mat_list()
#     print('UPDATED MAT LIST')


@register_wrap
class InstallShotariya(bpy.types.Operator):
    bl_idname = "cats_atlas.install_shotariya_popup"
    bl_label = t('InstallShotariya.label')
    bl_options = {'INTERNAL'}

    action = bpy.props.EnumProperty(
        items=(('INSTALL', '', ''),
               ('ENABLE', '', ''),
               ('VERSION', '', '')))

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 5.3)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if self.action == 'INSTALL':
            row = col.row(align=True)
            row.label(text=t('InstallShotariya.error.install1'))
            row.scale_y = 0.75
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('InstallShotariya.error.install2'))
            col.separator()
            row = col.row(align=True)
            row.label(text=t('InstallShotariya.error.install3'))
            row.scale_y = 0.75
            col.separator()
            row = col.row(align=True)
            row.operator(ShotariyaButton.bl_idname, icon=globs.ICON_URL)
            col.separator()

        elif self.action == 'ENABLE':
            row = col.row(align=True)
            row.label(text=t('InstallShotariya.error.enable1'))
            row.scale_y = 0.75
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('InstallShotariya.error.enable2'))
            col.separator()
            row = col.row(align=True)
            row.label(text=t('InstallShotariya.error.enable3'))
            row.scale_y = 0.75
            col.separator()

        elif self.action == 'VERSION':
            row = col.row(align=True)
            row.label(text=t('InstallShotariya.error.version1'))
            row.scale_y = 0.75
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('InstallShotariya.error.version2'))
            col.separator()
            row = col.row(align=True)
            row.label(text=t('InstallShotariya.error.version3'))
            row.scale_y = 0.75
            col.separator()
            row = col.row(align=True)
            row.operator(ShotariyaButton.bl_idname, icon=globs.ICON_URL)
            col.separator()


@register_wrap
class ShotariyaButton(bpy.types.Operator):
    bl_idname = 'cats_atlas.download_shotariya'
    bl_label = t('ShotariyaButton.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('ShotariyaButton.URL'))

        self.report({'INFO'}, 'ShotariyaButton.success')
        return {'FINISHED'}


# @register_wrap
# class CheckMaterialListButton(bpy.types.Operator):
#     bl_idname = 'cats_atlas.check_mat_list'
#     bl_label = 'Check/Uncheck Materials'
#     bl_description = 'Checks or unchecks the whole material list'
#     bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
#
#     def execute(self, context):
#         scene = context.scene
#         scene.clear_materials = not scene.clear_materials
#         for item in scene.material_list:
#             item.material.add_to_atlas = scene.clear_materials
#         return {'FINISHED'}


# def shotariya_installed(show_error=False):
#     print("show error!")
#     installed = False
#     correct_version = False
#
#     for mod2 in addon_utils.modules():
#         if mod2.bl_info.get('name') == addon_name:
#             installed = True
#
#             if mod2.bl_info.get('version') >= min_version:
#                 correct_version = True
#
#     if not installed:
#         if show_error:
#             bpy.ops.cats_atlas.install_shotariya_popup('INVOKE_DEFAULT', action='INSTALL')
#         print(addon_name + " not installed.")
#         return False
#
#     if not correct_version:
#         if show_error:
#             bpy.ops.cats_atlas.install_shotariya_popup('INVOKE_DEFAULT', action='VERSION')
#         print(addon_name + " has wrong version.")
#         return False
#
#     try:
#         bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='CLEAR_MAT')
#         bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='ALL_MAT')
#     except AttributeError:
#         if show_error:
#             bpy.ops.cats_atlas.install_shotariya_popup('INVOKE_DEFAULT', action='ENABLE')
#         print(addon_name + " not enabled.")
#         return False
#
#     print(addon_name + " was successfully found!!!")
#     return True

# @register_wrap
# class AutoAtlasButton(bpy.types.Operator):
#     bl_idname = 'auto.atlas'
#     bl_label = 'Create Atlas'
#     bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
#
#     @classmethod
#     def poll(cls, context):
#         if context.scene.mesh_name_atlas == "":
#             return False
#         return True
#
#     def generateRandom(self, prefix='', suffix=''):
#         return prefix + str(random.randrange(9999999999)) + suffix
#
#     def execute(self, context):
#         if not bpy.data.is_saved:
#             Common.show_error(6.5, ['You have to save your Blender file first!',
#                                           'Please save it to your assets folder so unity can discover the generated atlas file.'])
#             return {'CANCELLED'}
#
#         Common.set_default_stage()
#
#         atlas_mesh = Common.get_objects()[context.scene.mesh_name_atlas]
#         atlas_mesh.hide = False
#         Common.select(atlas_mesh)
#
#         # Check uv index
#         newUVindex = len(atlas_mesh.data.uv_textures) - 1
#         if newUVindex >= 1:
#             Common.show_error(4.5, ['You have more then one UVMap, please combine them.'])
#             return {'CANCELLED'}
#
#         # Disable all texture slots for all materials except the first texture slot
#         if context.scene.one_texture:
#             for ob in bpy.context.selected_editable_objects:
#                 for mat_slot in ob.material_slots:
#                     for i in range(len(mat_slot.material.texture_slots)):
#                         if i is not 0:
#                             bpy.data.materials[mat_slot.name].use_textures[i] = False
#
#         # Add a UVMap
#         bpy.ops.mesh.uv_texture_add()
#
#         # Active object should be rendered
#         atlas_mesh.hide_render = False
#
#         # Go into edit mode, deselect and select all
#         Common.switch('EDIT')
#         Common.switch('EDIT')
#         bpy.ops.mesh.select_all(action='DESELECT')
#         bpy.ops.mesh.select_all(action='SELECT')
#
#         if bpy.ops.mesh.reveal.poll():
#             bpy.ops.mesh.reveal()
#
#         # Define the image file
#         image_name = self.generateRandom('AtlasBake')
#         bpy.ops.image.new(name=image_name, alpha=True, width=int(context.scene.texture_size), height=int(context.scene.texture_size))
#         img = bpy.data.images[image_name]
#
#         # Set image settings
#         filename = self.generateRandom('//GeneratedAtlasBake', '.png')
#         img.use_alpha = True
#         img.alpha_mode = 'STRAIGHT'
#         img.filepath_raw = filename
#         img.file_format = 'PNG'
#
#         # Switch to new image for the uv edit
#         if bpy.data.screens['UV Editing'].areas[1].spaces[0]:
#             bpy.data.screens['UV Editing'].areas[1].spaces[0].image = img
#
#         # Set uv mapping to active image
#         for uvface in atlas_mesh.data.uv_textures.active.data:
#             uvface.image = img
#
#         # Try to UV smart project
#         bpy.ops.uv.smart_project(angle_limit=float(context.scene.angle_limit), island_margin=float(context.scene.island_margin), user_area_weight=float(context.scene.area_weight))
#
#         # Pack islands
#         if context.scene.pack_islands:
#             bpy.ops.uv.pack_islands(margin=0.001)
#
#         # Time to bake
#         Common.switch('EDIT')
#         context.scene.render.bake_type = "TEXTURE"
#         bpy.ops.object.bake_image()
#
#         # Lets save the generated atlas
#         img.save()
#
#         # Deselect all and switch to object mode
#         bpy.ops.mesh.select_all(action='DESELECT')
#         Common.switch('OBJECT')
#
#         # Delete all materials
#         for ob in bpy.context.selected_editable_objects:
#             ob.active_material_index = 0
#             for i in range(len(ob.material_slots)):
#                 bpy.ops.object.material_slot_remove({'object': ob})
#
#         # Create material slot
#         bpy.ops.object.material_slot_add()
#         new_mat = bpy.data.materials.new(name=self.generateRandom('AtlasBakedMat'))
#         atlas_mesh.active_material = new_mat
#
#         # Create texture slot from material slot and use generated atlas
#         tex = bpy.data.textures.new(self.generateRandom('AtlasBakedTex'), 'IMAGE')
#         tex.image = bpy.data.images.load(filename)
#         slot = new_mat.texture_slots.add()
#         slot.texture = tex
#
#         # Remove orignal uv map and replace with generated
#         uv_textures = atlas_mesh.data.uv_textures
#         uv_textures.remove(uv_textures['UVMap'])
#         uv_textures[0].name = 'UVMap'
#
#         # Make sure alpha works, thanks Tupper :D!
#         for mat_slot in atlas_mesh.material_slots:
#             if mat_slot is not None:
#                 for tex_slot in bpy.data.materials[mat_slot.name].texture_slots:
#                     if tex_slot is not None:
#                         tex_slot.use_map_alpha = True
#                 mat_slot.material.use_transparency = True
#                 mat_slot.material.transparency_method = 'MASK'
#                 mat_slot.material.alpha = 0
#
#         self.report({'INFO'}, 'Auto Atlas finished!')
#
#         return {'FINISHED'}


# @register_wrap
# class ShapekeyList(bpy.types.UIList):
#     # The draw_item function is called for each item of the collection that is visible in the list.
#     #   data is the RNA object containing the collection,
#     #   item is the current drawn item of the collection,
#     #   icon is the "computed" icon for the item (as an integer, because some objects like materials or textures
#     #   have custom icons ID, which are not available as enum items).
#     #   active_data is the RNA object containing the active property for the collection (i.e. integer pointing to the
#     #   active item of the collection).
#     #   active_propname is the name of the active property (use 'getattr(active_data, active_propname)').
#     #   index is index of the current item in the collection.
#     #   flt_flag is the result of the filtering process for this item.
#     #   Note: as index and flt_flag are optional arguments, you do not have to use/declare them here if you don't
#     #         need them.
#     def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
#         layout.label(text=item.name, translate=False, icon='SHAPEKEY_DATA')
#         # split.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')
#
#
# class Uilist_actions(bpy.types.Operator):
#     bl_idname = "custom.list_action"
#     bl_label = "List Action"
