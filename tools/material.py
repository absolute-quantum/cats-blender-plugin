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

# Code author: Michael Williamson
# Repo: https://github.com/scorpion81/blender-addons/blob/master/space_view3d_materials_utils.py
# Edits by: GiveMeAllYourCats

import os
import bpy
import numpy as np

from . import common as Common
from .register import register_wrap
from .translations import t


@register_wrap
class OneTexPerMatButton(bpy.types.Operator):
    bl_idname = 'cats_material.one_tex'
    bl_label = t('OneTexPerMatButton.label')
    bl_description = t('OneTexPerMatButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return len(Common.get_meshes_objects(check=False)) > 0

    def execute(self, context):
        # Common.unify_materials()
        # Common.add_principled_shader()
        # return {'FINISHED'}
        if not Common.version_2_79_or_older():
            self.report({'ERROR'}, t('ToolsMaterial.error.notCompatible'))
            return {'CANCELLED'}
            # TODO

        saved_data = Common.SavedData()

        Common.set_default_stage()

        for mesh in Common.get_meshes_objects():
            for mat_slot in mesh.material_slots:
                mat = mat_slot.material
                if mat:
                    for i, tex_slot in enumerate(mat.texture_slots):
                        if i > 0 and tex_slot:
                            mat.use_textures[i] = False

        saved_data.load()

        self.report({'INFO'}, t('OneTexPerMatButton.success'))
        return{'FINISHED'}


@register_wrap
class OneTexPerMatOnlyButton(bpy.types.Operator):
    bl_idname = 'cats_material.one_tex_only'
    bl_label = t('OneTexPerMatOnlyButton.label')
    bl_description = t('OneTexPerMatOnlyButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return len(Common.get_meshes_objects(check=False)) > 0

    def execute(self, context):
        if not Common.version_2_79_or_older():
            self.report({'ERROR'}, t('ToolsMaterial.error.notCompatible'))
            return {'CANCELLED'}
            # TODO

        saved_data = Common.SavedData()

        Common.set_default_stage()

        for mesh in Common.get_meshes_objects():
            for mat_slot in mesh.material_slots:
                mat = mat_slot.material
                if mat:
                    for i, tex_slot in enumerate(mat.texture_slots):
                        if i > 0 and tex_slot:
                            tex_slot.texture = None

        saved_data.load()

        self.report({'INFO'}, t('OneTexPerXButton.success'))
        return{'FINISHED'}


@register_wrap
class StandardizeTextures(bpy.types.Operator):
    bl_idname = 'cats_material.standardize_textures'
    bl_label = t('StandardizeTextures.label')
    bl_description = t('StandardizeTextures.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return len(Common.get_meshes_objects(check=False)) > 0

    def execute(self, context):
        if not Common.version_2_79_or_older():
            self.report({'ERROR'}, t('ToolsMaterial.error.notCompatible'))
            return {'CANCELLED'}
            # TODO

        saved_data = Common.SavedData()

        Common.set_default_stage()

        for mesh in Common.get_meshes_objects():
            for mat_slot in mesh.material_slots:
                mat = mat_slot.material
                if mat:
                    mat.transparency_method = 'Z_TRANSPARENCY'
                    mat.alpha = 1

                    for tex_slot in mat.texture_slots:
                        if tex_slot:
                            tex_slot.use_map_alpha = True
                            tex_slot.use_map_color_diffuse = True
                            tex_slot.blend_type = 'MULTIPLY'

        saved_data.load()

        self.report({'INFO'}, t('StandardizeTextures.success'))
        return{'FINISHED'}


@register_wrap
class CombineMaterialsButton(bpy.types.Operator):
    bl_idname = 'cats_material.combine_mats'
    bl_label = t('CombineMaterialsButton.label')
    bl_description = t('CombineMaterialsButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return len(Common.get_meshes_objects(check=False)) > 0

    @staticmethod
    def combine_exact_duplicate_mats(ob, unique_sorted_mat_indices):
        mat_names = ob.material_slots.keys()

        # Find duplicate materials and get the first index of the material slot with that same material
        mat_first_occurrence = {}
        # Note that empty material slots use '' as the material name
        for i, mat_name in enumerate(mat_names):
            if mat_name not in mat_first_occurrence:
                # This is the first time we've seen this material, add it to the first occurrence dict with the current
                # index
                mat_first_occurrence[mat_name] = i
            else:
                # We've seen this material already, find its occurrences (if any) in the unique mat indices array and
                # set it to the index of the first occurrence of this material
                unique_sorted_mat_indices[unique_sorted_mat_indices == i] = mat_first_occurrence[mat_name]

        return unique_sorted_mat_indices

    @staticmethod
    def remove_unused_mat_slots(ob, used_mat_indices):
        # Remove unused material slots
        # material_slot_remove_unused was added in 2.81
        # Unfortunately, material_slot_remove_unused completely ignores context overrides as of Blender 2.91, instead
        # getting the object(s) to operate on directly from the context's view_layer, otherwise we would use it in
        # Blender 2.91 and newer too.
        if (2, 81) <= bpy.app.version < (2, 91):
            context_override = {'active_object': ob}
            bpy.ops.object.material_slot_remove_unused(context_override)
        else:
            # Context override so that we don't need to set the object as the active object to run the operator on it
            context_override = {'object': ob}
            # Convert to a set to remove any duplicates and for quick checking of whether a material index is used
            used_mat_indices = set(used_mat_indices)
            # Iterate through the material slots, removing any which are not used
            # We iterate in reverse order, so that removing a material slot doesn't change the indices of any material
            # slots we are yet to iterate
            for i in reversed(range(len(ob.material_slots))):
                if i not in used_mat_indices:
                    ob.active_material_index = i
                    bpy.ops.object.material_slot_remove(context_override)

    @staticmethod
    def generate_mat_hash(mat):
        hash_this = ''
        if mat:
            if Common.version_2_79_or_older():
                for tex_index, mtex_slot in enumerate(mat.texture_slots):
                    if mtex_slot:
                        if mat.use_textures[tex_index]:
                            if hasattr(mtex_slot.texture, 'image') and mat.use_textures[tex_index] and mtex_slot.texture.image:
                                hash_this += mtex_slot.texture.image.filepath  # Filepaths makes the hash unique
                hash_this += str(mat.alpha)  # Alpha setting on material makes the hash unique
                hash_this += str(mat.diffuse_color)  # Diffuse color makes the hash unique
                # hash_this += str(mat.specular_color)  # Specular color makes the hash unique  # Specular Color is no used by Unity

                return hash_this
            else:
                ignore_nodes = {'Material Output', 'mmd_tex_uv', 'Cats Export Shader'}
                if mat.use_nodes and mat.node_tree:
                    # print('MAT: ', mat.name)
                    nodes = mat.node_tree.nodes
                    for node in nodes:

                        # Skip certain known nodes
                        if node.name in ignore_nodes or node.label in ignore_nodes:
                            continue

                        # Add images to hash and skip toon and shpere textures
                        if node.type == 'TEX_IMAGE':
                            image = node.image
                            if 'toon' in node.name or 'sphere' in node.name:
                                nodes.remove(node)
                                continue
                            if not image:
                                nodes.remove(node)
                                continue
                            # print('  ', node.name)
                            # print('    ', image.name)
                            hash_this += node.name + image.name
                            continue
                        # Skip nodes with no input
                        if not node.inputs:
                            continue

                        # On MMD models only add diffuse and transparency to the hash
                        if node.name == 'mmd_shader':
                            # print('  ', node.name)
                            # print('    ', node.inputs['Diffuse Color'].default_value[:])
                            # print('    ', node.inputs['Alpha'].default_value)
                            hash_this += node.name \
                                         + str(node.inputs['Diffuse Color'].default_value[:]) \
                                         + str(node.inputs['Alpha'].default_value)
                            continue

                        # Add all other nodes to the hash
                        # print('  ', node.name)
                        hash_this += node.name
                        for input, value in node.inputs.items():
                            if hasattr(value, 'default_value'):
                                try:
                                    # print('    ', input, value.default_value[:])
                                    hash_this += str(value.default_value[:])
                                except TypeError:
                                    # print('    ', input, value.default_value)
                                    hash_this += str(value.default_value)
                            else:
                                # print('    ', input, 'name:', value.name)
                                hash_this += value.name
                else:
                    # Materials almost always use nodes, but on the off chance that a material doesn't, create the hash
                    # based on the non-node properties
                    hash_this += str(mat.diffuse_color[:])
                    hash_this += str(mat.metallic)
                    hash_this += str(mat.roughness)
                    hash_this += str(mat.specular_intensity)

        return hash_this

    def execute(self, context):
        print('COMBINE MATERIALS!')
        saved_data = Common.SavedData()

        Common.set_default_stage()
        Common.switch('OBJECT')
        num_combined = 0

        # Hashes of all found materials
        mat_hashes = {}
        # The first material found for each hash
        first_mats_by_hash = {}
        for mesh in Common.get_meshes_objects():
            # Generate material hashes and re-assign material slots to the first found material that produces the same
            # hash
            for mat_name, mat_slot in mesh.material_slots.items():
                mat = mat_slot.material

                # Get the material hash, generating it if needed
                if mat_name not in mat_hashes:
                    mat_hash = self.generate_mat_hash(mat)
                    mat_hashes[mat_name] = mat_hash
                else:
                    mat_hash = mat_hashes[mat_name]

                # If a material with the same hash has already been found, re-assign the material slot to the previously
                # found material, otherwise, add the material to the dictionary of first found materials
                if mat_hash in first_mats_by_hash:
                    replacement_material = first_mats_by_hash[mat_hash]
                    # The replacement_material material could be the current material if the current material was also
                    # used on another mesh that was iterated before this mesh.
                    if mat != replacement_material:
                        mat_slot.material = replacement_material
                        num_combined += 1
                else:
                    first_mats_by_hash[mat_hash] = mat

            # Combine exact duplicate materials within the same mesh
            # Get polygon material indices
            polygons = mesh.data.polygons
            material_indices = np.empty(len(polygons), dtype=np.ushort)
            polygons.foreach_get('material_index', material_indices)

            # Find unique sorted material indices and get the inverse array to reconstruct the material indices array
            unique_sorted_material_indices, unique_inverse = np.unique(material_indices, return_inverse=True)
            # Working with only the unique material indices means we don't need to operate on the entire array
            combined_material_indices = self.combine_exact_duplicate_mats(mesh, unique_sorted_material_indices)

            # Update the material indices
            polygons.foreach_set('material_index', combined_material_indices[unique_inverse])

            # Remove any unused material slots
            self.remove_unused_mat_slots(mesh, combined_material_indices)

            # Clean material names
            Common.clean_material_names(mesh)

            # print('CLEANED MAT SLOTS')

        # Update the material list of the Material Combiner
        Common.update_material_list()

        saved_data.load()

        if num_combined == 0:
            self.report({'INFO'}, t('CombineMaterialsButton.error.noChanges'))
        else:
            self.report({'INFO'}, t('CombineMaterialsButton.success', number=str(num_combined)))

        return{'FINISHED'}


@register_wrap
class ConvertAllToPngButton(bpy.types.Operator):
    bl_idname = 'cats_material.convert_all_to_png'
    bl_label = t('ConvertAllToPngButton.label')
    bl_description = t('ConvertAllToPngButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # Inspired by:
    # https://cdn.discordapp.com/attachments/387450722410561547/526638724570677309/BlenderImageconvert.png

    @classmethod
    def poll(cls, context):
        return bpy.data.images

    def execute(self, context):
        images_to_convert = self.get_convert_list()

        if images_to_convert:
            current_step = 0
            wm = bpy.context.window_manager
            wm.progress_begin(current_step, len(images_to_convert))

            for image in images_to_convert:
                self.convert(image)
                current_step += 1
                wm.progress_update(current_step)

            wm.progress_end()

        self.report({'INFO'}, t('ConvertAllToPngButton.success', number=str(len(images_to_convert))))
        return {'FINISHED'}

    def get_convert_list(self):
        images_to_convert = []
        for image in bpy.data.images:
            # Get texture path and check if the file should be converted
            tex_path = bpy.path.abspath(image.filepath)
            if tex_path.endswith(('.png', '.spa', '.sph')) or not os.path.isfile(tex_path):
                print('IGNORED:', image.name, tex_path)
                continue
            images_to_convert.append(image)
        return images_to_convert

    def convert(self, image):
        # Set the new image file name
        image_name = image.name
        print(image_name)
        image_name_new = ''
        for s in image_name.split('.')[0:-1]:
            image_name_new += s + '.'
        image_name_new += 'png'
        print(image_name_new)

        # Set the new image file path
        tex_path = bpy.path.abspath(image.filepath)
        print(tex_path)
        tex_path_new = ''
        for s in tex_path.split('.')[0:-1]:
            tex_path_new += s + '.'
        tex_path_new += 'png'
        print(tex_path_new)

        # Save the Color Management View Transform and change it to Standard, as any other would screw with the colors
        view_transform = bpy.context.scene.view_settings.view_transform
        bpy.context.scene.view_settings.view_transform = 'Default' if Common.version_2_79_or_older() else 'Standard'

        # Save the image as a new png file
        scene = bpy.context.scene
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.image_settings.color_depth = '16'
        scene.render.image_settings.compression = 100
        image.save_render(tex_path_new, scene=scene)  # TODO: FInd out how to use image.save here, to prevent anything from changing the colors

        # Change the view transform back
        bpy.context.scene.view_settings.view_transform = view_transform

        # Exchange the old image in blender for the new one
        bpy.data.images[image_name].filepath = tex_path_new
        bpy.data.images[image_name].name = image_name_new

        return True
