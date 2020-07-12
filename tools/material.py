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

from . import common as Common
from .register import register_wrap
from ..translations import t


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
                for i, tex_slot in enumerate(mat_slot.material.texture_slots):
                    if i > 0 and tex_slot:
                        mat_slot.material.use_textures[i] = False

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
                for i, tex_slot in enumerate(mat_slot.material.texture_slots):
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

                mat_slot.material.transparency_method = 'Z_TRANSPARENCY'
                mat_slot.material.alpha = 1

                for tex_slot in mat_slot.material.texture_slots:
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

    combined_tex = {}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return len(Common.get_meshes_objects(check=False)) > 0

    def assignmatslots(self, ob, matlist):
        scn = bpy.context.scene
        ob_active = Common.get_active()
        Common.set_active(ob)

        for s in ob.material_slots:
            bpy.ops.object.material_slot_remove()

        i = 0
        for m in matlist:
            mat = bpy.data.materials[m]
            ob.data.materials.append(mat)
            i += 1

        Common.set_active(ob_active)

    def cleanmatslots(self):
        objs = bpy.context.selected_editable_objects

        for ob in objs:
            if ob.type == 'MESH':
                mats = ob.material_slots.keys()

                usedMatIndex = []
                faceMats = []
                me = ob.data
                for f in me.polygons:
                    faceindex = f.material_index
                    if faceindex >= len(mats):
                        continue

                    currentfacemat = mats[faceindex]
                    faceMats.append(currentfacemat)

                    found = 0
                    for m in usedMatIndex:
                        if m == faceindex:
                            found = 1

                    if found == 0:
                        usedMatIndex.append(faceindex)

                ml = []
                mnames = []
                for u in usedMatIndex:
                    ml.append(mats[u])
                    mnames.append(mats[u])

                self.assignmatslots(ob, ml)

                i = 0
                for f in me.polygons:
                    if i >= len(faceMats):
                        continue
                    matindex = mnames.index(faceMats[i])
                    f.material_index = matindex
                    i += 1

    # Iterates over each material slot and hashes combined image filepaths and material settings
    # Then uses this hash as the dict keys and material data as values
    def generate_combined_tex(self):
        self.combined_tex = {}
        for ob in Common.get_meshes_objects():
            for index, mat_slot in enumerate(ob.material_slots):
                hash_this = ''

                if Common.version_2_79_or_older():
                    if mat_slot.material:
                        for tex_index, mtex_slot in enumerate(mat_slot.material.texture_slots):
                            if mtex_slot:
                                if mat_slot.material.use_textures[tex_index]:
                                    if hasattr(mtex_slot.texture, 'image') and bpy.data.materials[mat_slot.name].use_textures[tex_index] and mtex_slot.texture.image:
                                        hash_this += mtex_slot.texture.image.filepath   # Filepaths makes the hash unique
                        hash_this += str(mat_slot.material.alpha)           # Alpha setting on material makes the hash unique
                        hash_this += str(mat_slot.material.diffuse_color)   # Diffuse color makes the hash unique
                        # hash_this += str(mat_slot.material.specular_color)  # Specular color makes the hash unique  # Specular Color is no used by Unity

                    # print('---------------------------------------------------')
                    # print(mat_slot.name, hash_this)

                    # Now create or add to the dict key that has this hash value
                    if hash_this not in self.combined_tex:
                        self.combined_tex[hash_this] = []
                    self.combined_tex[hash_this].append({'mat': mat_slot.name, 'index': index})

                else:
                    hash_this = ''
                    ignore_nodes = ['Material Output', 'mmd_tex_uv', 'Cats Export Shader']

                    if mat_slot.material and mat_slot.material.node_tree:
                        # print('MAT: ', mat_slot.material.name)
                        nodes = mat_slot.material.node_tree.nodes
                        for node in nodes:

                            # Skip certain known nodes
                            ignore_this_node = False
                            for name in ignore_nodes:
                                if name in node.name or name in node.label:
                                    ignore_this_node = True
                                    break
                            if ignore_this_node:
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
                                hash_this += node.name\
                                             + str(node.inputs['Diffuse Color'].default_value[:])\
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

                    # Now create or add to the dict key that has this hash value
                    if hash_this not in self.combined_tex:
                        self.combined_tex[hash_this] = []
                    self.combined_tex[hash_this].append({'mat': mat_slot.name, 'index': index})

        # for key, value in self.combined_tex.items():
        #     print(key)
        #     for mat in value:
        #         print(mat)

    def execute(self, context):
        print('COMBINE MATERIALS!')
        saved_data = Common.SavedData()

        Common.set_default_stage()
        self.generate_combined_tex()
        Common.switch('OBJECT')
        i = 0

        for index, mesh in enumerate(Common.get_meshes_objects()):

            Common.unselect_all()
            Common.set_active(mesh)
            for file in self.combined_tex:  # for each combined mat slot of scene object
                combined_textures = self.combined_tex[file]

                # Combining material slots that are similar with only themselves are useless
                if len(combined_textures) <= 1:
                    continue
                i += len(combined_textures)

                # print('NEW', file, combined_textures, len(combined_textures))
                Common.switch('EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')

                # print('UNSELECT ALL')
                for mat in mesh.material_slots:  # for each scene object material slot
                    for tex in combined_textures:
                        if mat.name == tex['mat']:
                            mesh.active_material_index = tex['index']
                            bpy.ops.object.material_slot_select()
                            # print('SELECT', tex['mat'], tex['index'])

                bpy.ops.object.material_slot_assign()
                # print('ASSIGNED TO SLOT INDEX', bpy.context.object.active_material_index)
                bpy.ops.mesh.select_all(action='DESELECT')

            Common.unselect_all()
            Common.set_active(mesh)
            Common.switch('OBJECT')
            self.cleanmatslots()

            # Clean material names
            Common.clean_material_names(mesh)

            # print('CLEANED MAT SLOTS')

        # Update the material list of the Material Combiner
        Common.update_material_list()

        saved_data.load()

        if i == 0:
            self.report({'INFO'}, t('CombineMaterialsButton.error.noChanges'))
        else:
            self.report({'INFO'}, t('CombineMaterialsButton.success', number=str(i)))

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
