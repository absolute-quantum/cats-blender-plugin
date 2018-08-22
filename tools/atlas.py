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


class AutoAtlasNewButton(bpy.types.Operator):
    bl_idname = 'auto.atlas_new'
    bl_label = 'Create Atlas'
    bl_description = 'Generates a texture atlas for this model.' \
                     '\n' \
                     '\nThis is a shortcut to shotariyas plugin.' \
                     '\nIf you want more options, use the plugin tab "shotariya"'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        # Checking if shotaiyas plugin is installed. If it is not installed, open a popup with a link to it
        try:
            bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='CLEAR_MAT')
        except AttributeError:
            bpy.ops.install.shotariya('INVOKE_DEFAULT')
            return {'CANCELLED'}

        # Check if there are meshes
        if not tools.common.get_meshes_objects():
            self.report({'ERROR'}, 'No model with meshes was found!')
            return {'CANCELLED'}

        # Check if Blend file is saved
        if not bpy.data.is_saved:
            tools.common.show_error(6.5, ['You have to save this Blender file first!',
                                          'Please save it to your assets folder so Unity can discover the generated atlas file.'])
            return {'CANCELLED'}

        # Getting the directory of the currently saved blend file
        filepath = bpy.data.filepath
        directory = os.path.dirname(filepath)

        # Saves all the files in the current directory for later comparison
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
        for mesh in tools.common.get_meshes_objects():
            for mat_slot in mesh.material_slots:
                if mat_slot:
                    bpy.data.materials[mat_slot.material.name].to_tex = True

        # Generating the textures of UVs with bounds greater than 1
        try:
            bpy.ops.shotariya.gen_tex('INVOKE_DEFAULT')
        except RuntimeError:
            pass

        # Filling the list with the materials and setting the folder to save the created atlas
        bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='GENERATE_MAT')
        bpy.ops.shotariya.combined_folder('EXEC_DEFAULT', filepath=directory)

        # Deselects all materials and then selects only the ones from the current model
        bpy.ops.shotariya.list_actions('INVOKE_DEFAULT', action='CLEAR_MAT')
        for mesh in tools.common.get_meshes_objects():
            for mat_slot in mesh.material_slots:
                if mat_slot:
                    bpy.data.materials[mat_slot.material.name].to_combine = True

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

        # Check if the atlas was successfully generated
        if not error and not atlas_name:
            error = 'Generated atlas could not be found!'

        # Finish
        tools.common.set_default_stage()
        if error:
            self.report({'ERROR'}, error)
        else:
            self.report({'INFO'}, 'Auto Atlas finished! Atlas saved as "' + atlas_name + '"')
        return {'FINISHED'}


class InstallShotariya(bpy.types.Operator):
    bl_idname = "install.shotariya"
    bl_label = 'Material Combiner is not installed or enabled!'

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

        row = col.row(align=True)
        row.scale_y = 0.75
        row.label("The plugin 'Material Combiner' by shotariya is required for this function.")
        col.separator()
        row = col.row(align=True)
        row.label("If it is not enabled please enable it in your User Preferences.")
        row.scale_y = 0.75
        row = col.row(align=True)
        row.label("If it is not installed please download and install it manually.")
        row.scale_y = 0.75
        col.separator()
        row = col.row(align=True)
        row.operator('download.shotariya', icon='LOAD_FACTORY')
        col.separator()


class ShotariyaButton(bpy.types.Operator):
    bl_idname = 'download.shotariya'
    bl_label = 'Download Material Combiner'

    def execute(self, context):
        webbrowser.open('https://vrcat.club/threads/material-combiner-blender-addon-1-1-3.2255/')

        self.report({'INFO'}, 'Material Combiner link opened')
        return {'FINISHED'}


class AutoAtlasButton(bpy.types.Operator):
    bl_idname = 'auto.atlas'
    bl_label = 'Create Atlas'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if context.scene.mesh_name_atlas == "":
            return False
        return True

    def generateRandom(self, prefix='', suffix=''):
        return prefix + str(random.randrange(9999999999)) + suffix

    def execute(self, context):
        if not bpy.data.is_saved:
            tools.common.show_error(6.5, ['You have to save your Blender file first!',
                                          'Please save it to your assets folder so unity can discover the generated atlas file.'])
            return {'CANCELLED'}

        tools.common.set_default_stage()

        atlas_mesh = bpy.data.objects[context.scene.mesh_name_atlas]
        atlas_mesh.hide = False
        tools.common.select(atlas_mesh)

        # Check uv index
        newUVindex = len(atlas_mesh.data.uv_textures) - 1
        if newUVindex >= 1:
            tools.common.show_error(4.5, ['You have more then one UVMap, please combine them.'])
            return {'CANCELLED'}

        # Disable all texture slots for all materials except the first texture slot
        if context.scene.one_texture:
            for ob in bpy.context.selected_editable_objects:
                for mat_slot in ob.material_slots:
                    for i in range(len(mat_slot.material.texture_slots)):
                        if i is not 0:
                            bpy.data.materials[mat_slot.name].use_textures[i] = False

        # Add a UVMap
        bpy.ops.mesh.uv_texture_add()

        # Active object should be rendered
        atlas_mesh.hide_render = False

        # Go into edit mode, deselect and select all
        tools.common.switch('EDIT')
        tools.common.switch('EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='SELECT')

        if bpy.ops.mesh.reveal.poll():
            bpy.ops.mesh.reveal()

        # Define the image file
        image_name = self.generateRandom('AtlasBake')
        bpy.ops.image.new(name=image_name, alpha=True, width=int(context.scene.texture_size), height=int(context.scene.texture_size))
        img = bpy.data.images[image_name]

        # Set image settings
        filename = self.generateRandom('//GeneratedAtlasBake', '.png')
        img.use_alpha = True
        img.alpha_mode = 'STRAIGHT'
        img.filepath_raw = filename
        img.file_format = 'PNG'

        # Switch to new image for the uv edit
        if bpy.data.screens['UV Editing'].areas[1].spaces[0]:
            bpy.data.screens['UV Editing'].areas[1].spaces[0].image = img

        # Set uv mapping to active image
        for uvface in atlas_mesh.data.uv_textures.active.data:
            uvface.image = img

        # Try to UV smart project
        bpy.ops.uv.smart_project(angle_limit=float(context.scene.angle_limit), island_margin=float(context.scene.island_margin), user_area_weight=float(context.scene.area_weight))

        # Pack islands
        if context.scene.pack_islands:
            bpy.ops.uv.pack_islands(margin=0.001)

        # Time to bake
        tools.common.switch('EDIT')
        context.scene.render.bake_type = "TEXTURE"
        bpy.ops.object.bake_image()

        # Lets save the generated atlas
        img.save()

        # Deselect all and switch to object mode
        bpy.ops.mesh.select_all(action='DESELECT')
        tools.common.switch('OBJECT')

        # Delete all materials
        for ob in bpy.context.selected_editable_objects:
            ob.active_material_index = 0
            for i in range(len(ob.material_slots)):
                bpy.ops.object.material_slot_remove({'object': ob})

        # Create material slot
        bpy.ops.object.material_slot_add()
        new_mat = bpy.data.materials.new(name=self.generateRandom('AtlasBakedMat'))
        atlas_mesh.active_material = new_mat

        # Create texture slot from material slot and use generated atlas
        tex = bpy.data.textures.new(self.generateRandom('AtlasBakedTex'), 'IMAGE')
        tex.image = bpy.data.images.load(filename)
        slot = new_mat.texture_slots.add()
        slot.texture = tex

        # Remove orignal uv map and replace with generated
        uv_textures = atlas_mesh.data.uv_textures
        uv_textures.remove(uv_textures['UVMap'])
        uv_textures[0].name = 'UVMap'

        # Make sure alpha works, thanks Tupper :D!
        for mat_slot in atlas_mesh.material_slots:
            if mat_slot is not None:
                for tex_slot in bpy.data.materials[mat_slot.name].texture_slots:
                    if tex_slot is not None:
                        tex_slot.use_map_alpha = True
                mat_slot.material.use_transparency = True
                mat_slot.material.transparency_method = 'MASK'
                mat_slot.material.alpha = 0

        self.report({'INFO'}, 'Auto Atlas finished!')

        return {'FINISHED'}
