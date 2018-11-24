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

import os
import bpy
import random
import webbrowser
import tools.common
import addon_utils
from tools.common import version_2_79_or_older
from tools.register import register_wrap


addon_name = "Shotariya-don"
min_version = [1, 1, 6]


ICON_URL = 'URL'
if version_2_79_or_older():
    ICON_URL = 'LOAD_FACTORY'


@register_wrap
class AutoAtlasNewButton(bpy.types.Operator):
    bl_idname = 'atlas.generate'
    bl_label = 'Create Atlas'
    bl_description = 'Generates a texture atlas.' \
                     '\n' \
                     '\nGenerate the Material List to select what you want to combine.' \
                     '\nOtherwise this will combine all materials.' \
                     '\n' \
                     '\nThis is a shortcut to shotariyas plugin.' \
                     '\nIf you want more options, use the plugin tab "shotariya"'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if not tools.common.version_2_79_or_older():
            self.report({'ERROR'}, 'This function is not yet compatible with Blender 2.8!')
            return {'CANCELLED'}
            # TODO

        # Check if shotariyas plugin is correctly set up
        if not shotariya_installed():
            return {'CANCELLED'}

        # Check if there are meshes in the model
        if not tools.common.get_meshes_objects():
            tools.common.show_error(2.8, ['No model with meshes found!'])
            return {'CANCELLED'}

        # Check if all textures are found and count the materials/textures to check if it is already atlased
        missing_textures = []
        material_list = []
        texture_list = []
        empty_tex_count = 0
        if len(context.scene.material_list) == 0:
            for mesh in tools.common.get_meshes_objects():
                for mat_slot in mesh.material_slots:
                    if mat_slot and mat_slot.material:
                        mat = mat_slot.material
                        if mat.name not in material_list:
                            material_list.append(mat.name)

                        tex_slot = mat.texture_slots[0]
                        if tex_slot and tex_slot.texture:
                            if tex_slot.texture.name not in texture_list:
                                texture_list.append(tex_slot.texture.name)

                            tex_path = bpy.path.abspath(tex_slot.texture.image.filepath)
                            if not os.path.isfile(tex_path) and tex_path not in missing_textures:
                                missing_textures.append(tex_path)
                        else:
                            texture_list.append('Empty' + str(empty_tex_count))
                            empty_tex_count += 1
        else:
            for item in context.scene.material_list:
                mat = item.material
                if item.material.add_to_atlas:
                    material_list.append(mat.name)

                    tex_slot = mat.texture_slots[0]
                    if tex_slot and tex_slot.texture:
                        if tex_slot.texture.name not in texture_list:
                            texture_list.append(tex_slot.texture.name)

                        tex_path = bpy.path.abspath(tex_slot.texture.image.filepath)
                        if not os.path.isfile(tex_path) and tex_path not in missing_textures:
                            missing_textures.append(tex_path)
                    else:
                        texture_list.append('Empty' + str(empty_tex_count))
                        empty_tex_count += 1

        # Check if there is an atlas already
        if len(material_list) == 0:
            if len(context.scene.material_list) == 0:
                tools.common.show_error(2.3, ['No materials found!'])
            else:
                tools.common.show_error(2.3, ['No materials selected!'])
            return {'CANCELLED'}

        # Check if there is an atlas already
        if len(material_list) == 1:
            tools.common.show_error(5, ['No need to create an atlas, there is already only one material.'])
            return {'CANCELLED'}

        # Check if there are too few items selected in the list
        if len(context.scene.material_list) > 0:
            checked_mats_count = 0
            for item in context.scene.material_list:
                if item.material.add_to_atlas:
                    checked_mats_count += 1

            if checked_mats_count <= 1:
                tools.common.show_error(3.2, ['Please select more than one material.'])
                return {'CANCELLED'}

        # Check if too few textures are selected
        if len(texture_list) <= 1:
            if len(context.scene.material_list) > 0:
                tools.common.show_error(4.1, ['You only selected materials with the same texture.',
                                              'You need multiple textures to generate an atlas.'])
            else:
                tools.common.show_error(3.4, ['All materials are using the same texture.',
                                              'There is no need to create an atlas.'])
            return {'CANCELLED'}

        # Check if there are missing textures
        if missing_textures:
            longest_line = 'Use "File > External Data > Find Missing Files" to fix this.'
            message = ['Could not find the following textures:']
            for index, missing_texture in enumerate(missing_textures):
                if index < 5:
                    line = ' - ' + missing_texture
                    message.append(line)
                    if len(line) > len(longest_line):
                        longest_line = line

                else:
                    message.append('...and ' + str(len(missing_textures) - 5) + ' more.')
                    break
            message.append('')
            message.append('Use "File > External Data > Find Missing Files" to fix this.')  # TODO: Check this in 2.8

            width = 0
            for char in longest_line:
                width += 0.095

            tools.common.show_error(width, message)
            return {'CANCELLED'}

        # Check if Blend file is saved
        if not bpy.data.is_saved:
            tools.common.show_error(4.5, ['You have to save this Blender file first!',
                                          'The generated atlas will be saved to the same location.'])
            return {'CANCELLED'}

        # Getting the directory of the currently saved blend file
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)

        # Saves all the file names in the current directory for later comparison
        files = []
        for file in os.listdir(directory):
            files.append(file)

        # Filling the list with textures and concurrently checking if shotaiyas plugin is installed
        tools.common.set_default_stage()
        bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='GENERATE_TEX')

        # Sets the folder for saving the generated textures
        bpy.ops.shotariya.tex_folder('EXEC_DEFAULT', filepath=directory)

        # Deselects all textures and then selects only the ones from the current model
        bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='CLEAR_TEX')
        if len(context.scene.material_list) == 0:
            for mesh in tools.common.get_meshes_objects():
                for mat_slot in mesh.material_slots:
                    if mat_slot:
                        bpy.data.materials[mat_slot.material.name].to_tex = True
        else:
            for item in context.scene.material_list:
                if item.material.add_to_atlas:
                    bpy.data.materials[item.material.name].to_tex = True

        # Generating the textures of UVs with bounds greater than 1
        try:
            bpy.ops.shotariya.gen_tex('INVOKE_DEFAULT')
        except RuntimeError as e:
            print(str(e))
            pass

        # Filling the list with the materials and setting the folder to save the created atlas
        bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='GENERATE_MAT')
        bpy.ops.shotariya.combined_folder('EXEC_DEFAULT', filepath=directory)

        # Deselects all materials and then selects only the ones from the current model
        bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='CLEAR_MAT')
        if len(context.scene.material_list) == 0:
            for mesh in tools.common.get_meshes_objects():
                for mat_slot in mesh.material_slots:
                    if mat_slot:
                        bpy.data.materials[mat_slot.material.name].to_combine = True
        else:
            for item in context.scene.material_list:
                if item.material.add_to_atlas:
                    bpy.data.materials[item.material.name].to_combine = True

        # Generating the atlas
        error = None
        try:
            bpy.ops.shotariya.gen_mat('INVOKE_DEFAULT')
        except RuntimeError as e:
            error = str(e).replace('Error: ', '')

        # Deleting generated textures and searching for generated atlas
        atlas_name = None
        for file in os.listdir(directory):
            if file not in files:
                if file.endswith('_uv.png'):
                    os.remove(os.path.join(directory, file))
                    print('Deleted', file)
                if file.startswith('combined_image_'):
                    atlas_name = file

        # Update material list
        if len(context.scene.material_list) > 0:
            bpy.ops.atlas.gen_mat_list('INVOKE_DEFAULT')

        # Check if the atlas was successfully generated
        if not error and not atlas_name:
            error = 'You only selected materials that are using the same texture. These materials were combined.'

        # Finish
        tools.common.set_default_stage()
        if error:
            self.report({'ERROR'}, error)
        else:
            self.report({'INFO'}, 'Auto Atlas finished! Atlas saved as "' + atlas_name + '"')
        return {'FINISHED'}


@register_wrap
class MaterialsGroup(bpy.types.PropertyGroup):
    material = bpy.props.PointerProperty(
        name='Material',
        type=bpy.types.Material
    )


@register_wrap
class GenerateMaterialListButton(bpy.types.Operator):
    bl_idname = 'atlas.gen_mat_list'
    bl_label = 'Generate Material List'
    bl_description = 'This generates the material list.' \
                     '\nUse this to select which materials you want to combine.' \
                     '\nOtherwise all materials will be combined'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        if not tools.common.version_2_79_or_older():
            self.report({'ERROR'}, 'This function is not yet compatible with Blender 2.8!')
            return {'CANCELLED'}
            # TODO

        if not shotariya_installed():
            return {'CANCELLED'}

        # Check if there are meshes
        if not tools.common.get_meshes_objects():
            tools.common.show_error(2.8, ['No model with meshes found!'])
            return {'CANCELLED'}

        scene = context.scene
        scene.material_list.clear()
        scene.clear_materials = True
        scene.material_list_index = 0

        for mesh in tools.common.get_meshes_objects():
            if not mesh.data.uv_layers.active:
                continue

            tools.common.clean_material_names(mesh)

            for mat_slot in mesh.material_slots:
                if mat_slot and mat_slot.material:
                    mat = mat_slot.material
                    mat.add_to_atlas = True

                    item = scene.material_list.add()
                    item.id = len(scene.material_list)
                    item.name = mat.name
                    item.material = mat
                    item.add_to_atlas = mat.add_to_atlas
                    scene.material_list_index = (len(scene.material_list) - 1)
        return {'FINISHED'}


@register_wrap
class AtlasHelpButton(bpy.types.Operator):
    bl_idname = 'atlas.help'
    bl_label = 'Generate Material List'
    bl_description = 'Open Useful Atlas Tips'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open('https://github.com/michaeldegroot/cats-blender-plugin/#texture-atlas')
        self.report({'INFO'}, 'Atlas Help opened.')
        return {'FINISHED'}


@register_wrap
class ClearMaterialListButton(bpy.types.Operator):
    bl_idname = 'atlas.clear_mat_list'
    bl_label = 'Clear Material List'
    bl_description = 'Clears the material list'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        context.scene.material_list.clear()
        return {'FINISHED'}


def update_material_list(self, context):
    if len(context.scene.material_list) > 0:
        bpy.ops.atlas.gen_mat_list()
    print('UPDATED MAT LIST')


@register_wrap
class InstallShotariya(bpy.types.Operator):
    bl_idname = "install.shotariya"
    bl_label = 'Error while loading Material Combiner:'

    action = bpy.props.EnumProperty(
        items=(('INSTALL', '', ''),
               ('ENABLE', '', ''),
               ('VERSION', '', '')))

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 5.3, height=-550)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if self.action == 'INSTALL':
            row = col.row(align=True)
            row.label(text="Material Combiner is not installed!")
            row.scale_y = 0.75
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="The plugin 'Material Combiner' by shotariya is required for this function.")
            col.separator()
            row = col.row(align=True)
            row.label(text="Please download and install it manually:")
            row.scale_y = 0.75
            col.separator()
            row = col.row(align=True)
            row.operator('download.shotariya', icon=ICON_URL)
            col.separator()

        elif self.action == 'ENABLE':
            row = col.row(align=True)
            row.label(text="Material Combiner is not enabled!")
            row.scale_y = 0.75
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="The plugin 'Material Combiner' by shotariya is required for this function.")
            col.separator()
            row = col.row(align=True)
            row.label(text="Please enable it in your User Preferences.")
            row.scale_y = 0.75
            col.separator()

        elif self.action == 'VERSION':
            row = col.row(align=True)
            row.label(text="Material Combiner is outdated!")
            row.scale_y = 0.75
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="The latest version is required for this function.")
            col.separator()
            row = col.row(align=True)
            row.label(text="Please download and install it manually:")
            row.scale_y = 0.75
            col.separator()
            row = col.row(align=True)
            row.operator('download.shotariya', icon=ICON_URL)
            col.separator()


@register_wrap
class ShotariyaButton(bpy.types.Operator):
    bl_idname = 'download.shotariya'
    bl_label = 'Download Material Combiner'

    def execute(self, context):
        webbrowser.open('https://vrcat.club/threads/material-combiner-blender-addon-1-1-3.2255/')

        self.report({'INFO'}, 'Material Combiner link opened')
        return {'FINISHED'}


@register_wrap
class CheckMaterialListButton(bpy.types.Operator):
    bl_idname = 'atlas.check_mat_list'
    bl_label = 'Check/Uncheck Materials'
    bl_description = 'Checks or unchecks the whole material list'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        scene = context.scene
        scene.clear_materials = not scene.clear_materials
        for item in scene.material_list:
            item.material.add_to_atlas = scene.clear_materials
        return {'FINISHED'}


def shotariya_installed():
    installed = False
    correct_version = False

    for mod2 in addon_utils.modules():
        if mod2.bl_info.get('name') == addon_name:
            installed = True

            if mod2.bl_info.get('version') >= min_version:
                correct_version = True

    if not installed:
        bpy.ops.install.shotariya('INVOKE_DEFAULT', action='INSTALL')
        print(addon_name + " not installed.")
        return False

    if not correct_version:
        bpy.ops.install.shotariya('INVOKE_DEFAULT', action='VERSION')
        print(addon_name + " has wrong version.")
        return False

    try:
        bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='CLEAR_MAT')
        bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='ALL_MAT')
    except AttributeError:
        print(addon_name + " not enabled.")
        bpy.ops.install.shotariya('INVOKE_DEFAULT', action='ENABLE')
        return False

    print(addon_name + " was successfully found!!!")
    return True

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
#             tools.common.show_error(6.5, ['You have to save your Blender file first!',
#                                           'Please save it to your assets folder so unity can discover the generated atlas file.'])
#             return {'CANCELLED'}
#
#         tools.common.set_default_stage()
#
#         atlas_mesh = bpy.data.objects[context.scene.mesh_name_atlas]
#         atlas_mesh.hide = False
#         tools.common.select(atlas_mesh)
#
#         # Check uv index
#         newUVindex = len(atlas_mesh.data.uv_textures) - 1
#         if newUVindex >= 1:
#             tools.common.show_error(4.5, ['You have more then one UVMap, please combine them.'])
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
#         tools.common.switch('EDIT')
#         tools.common.switch('EDIT')
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
#         tools.common.switch('EDIT')
#         context.scene.render.bake_type = "TEXTURE"
#         bpy.ops.object.bake_image()
#
#         # Lets save the generated atlas
#         img.save()
#
#         # Deselect all and switch to object mode
#         bpy.ops.mesh.select_all(action='DESELECT')
#         tools.common.switch('OBJECT')
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
