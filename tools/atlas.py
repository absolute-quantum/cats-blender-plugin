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
# Edits by: GiveMeAllYourCats

import bpy
import tools.common
import random


class AutoAtlasButton(bpy.types.Operator):
    bl_idname = 'auto.atlas'
    bl_label = 'Create atlas'
    bl_options = {'REGISTER', 'UNDO'}

    def generateRandom(self, prefix='', suffix=''):
        return prefix + str(random.randrange(9999999999)) + suffix

    def execute(self, context):
        # PreserveState = tools.common.PreserveState()
        # PreserveState.save()

        tools.common.unhide_all()

        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'You must save your blender file first, please save it to your assets folder so unity can discover the generated atlas file.')
            return {'CANCELLED'}

        atlas_mesh = bpy.data.objects[context.scene.mesh_name_atlas]

        for obj in bpy.context.selected_objects:
            obj.select = False

        bpy.context.scene.objects.active = atlas_mesh
        atlas_mesh.select = True

        # Check uv index
        newUVindex = len(atlas_mesh.data.uv_textures) - 1
        if (newUVindex >= 1):
            self.report({'ERROR'}, 'You have more then one UVMap, please combine them.')
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
        bpy.data.scenes["Scene"].render.bake_type = "TEXTURE"
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

        try:
            bpy.ops.mmd_tools.set_shadeless_glsl_shading()
        except:
            print('mmd_tools probably not activated.')

        self.report({'INFO'}, 'Auto Atlas finished!')

        # PreserveState.load()

        return{'FINISHED'}
