# MIT License

# Copyright (c) 2020 Feilen

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

# Code author: Feilen

import os
import bpy
import math
import webbrowser
import numpy as np
import subprocess
import shutil
import threading
from contextlib import contextmanager
from typing import NamedTuple
from itertools import chain
from time import perf_counter

from . import common as Common
from .register import register_wrap
from .translations import t


@register_wrap
class BakeTutorialButton(bpy.types.Operator):
    bl_idname = 'cats_bake.tutorial'
    bl_label = t('cats_bake.tutorial_button.label')
    bl_description = t('cats_bake.tutorial_button.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('cats_bake.tutorial_button.URL'))

        self.report({'INFO'}, t('cats_bake.tutorial_button.success'))
        return {'FINISHED'}

def autodetect_passes(self, context, item, tricount, platform, use_phong=False):
    item.max_tris = tricount
    # Autodetect passes based on BSDF node inputs
    bsdf_nodes = []
    objects = [obj for obj in Common.get_meshes_objects(check=False) if not Common.is_hidden(obj) or not context.scene.bake_ignore_hidden]
    for obj in objects:
        for slot in obj.material_slots:
            if slot.material:
                if not slot.material.use_nodes or not slot.material.node_tree:
                    self.report({'ERROR'}, t('cats_bake.warn_missing_nodes'))
                    return {'FINISHED'}
                tree = slot.material.node_tree
                for node in tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        bsdf_nodes.append(node)

    # Decimate if we're over the limit
    total_tricount = sum([Common.get_tricount(obj) for obj in objects])
    item.use_decimation = total_tricount > tricount

    # Diffuse: on if >1 unique color input or if any has non-default base color input on bsdf
    context.scene.bake_pass_diffuse = (any([node.inputs["Base Color"].is_linked for node in bsdf_nodes])
                                       or len(set([node.inputs["Base Color"].default_value[:] for node in bsdf_nodes])) > 1)

    # Smoothness: similar to diffuse
    context.scene.bake_pass_smoothness = (any([node.inputs["Roughness"].is_linked for node in bsdf_nodes])
                                          or len(set([node.inputs["Roughness"].default_value for node in bsdf_nodes])) > 1)

    # Emit: similar to diffuse
    context.scene.bake_pass_emit = (any([node.inputs["Emission"].is_linked for node in bsdf_nodes])
                                    or len(set([node.inputs["Emission"].default_value[:] for node in bsdf_nodes])) > 1)

    # Transparency: similar to diffuse
    context.scene.bake_pass_alpha = (any([node.inputs["Alpha"].is_linked for node in bsdf_nodes])
                                                    or len(set([node.inputs["Alpha"].default_value for node in bsdf_nodes])) > 1)

    # Metallic: similar to diffuse
    context.scene.bake_pass_metallic = (any([node.inputs["Metallic"].is_linked for node in bsdf_nodes])
                                        or len(set([node.inputs["Metallic"].default_value for node in bsdf_nodes])) > 1)

    # Normal: on if any normals connected or if decimating... so, always on for this preset
    context.scene.bake_pass_normal = (item.use_decimation
                                      or any([node.inputs["Normal"].is_linked for node in bsdf_nodes]))

    if any("Target" in obj.data.uv_layers for obj in Common.get_meshes_objects(check=False)):
        context.scene.bake_uv_overlap_correction = 'MANUAL'
    elif any(plat.use_decimation for plat in context.scene.bake_platforms) and context.scene.bake_pass_normal:
        context.scene.bake_uv_overlap_correction = 'UNMIRROR'

    # Unfortunately, though it's technically faster, this makes things ineligible as Quest fallback avatars. So leave it off.
    # Sadly this is still fairly unkind to a number of lighting situations, so we'll leave it off
    # context.scene.bake_optimize_static = platform == "DESKTOP"

    # Quest has no use for twistbones
    item.merge_twistbones = platform != "DESKTOP"

    # AO: up to user, don't override as part of this. Possibly detect if using a toon shader in the future?
    # TODO: If mesh is manifold and non-intersecting, turn on AO. Otherwise, leave it alone
    # diffuse ao: off if desktop
    item.diffuse_premultiply_ao = platform != "DESKTOP"

    # alpha packs: arrange for maximum efficiency.
    # Its important to leave Diffuse alpha alone if we're not using it, as Unity will try to use 4bpp if so
    item.diffuse_alpha_pack = "NONE"
    item.metallic_alpha_pack = "NONE"
    if platform == "DESKTOP":
        item.export_format = "FBX"
        item.image_export_format = "PNG"
        item.translate_bone_names = "NONE"
        # If 'smoothness' and 'transparency', we need to force metallic to bake so we can pack to it.
        if context.scene.bake_pass_smoothness and context.scene.bake_pass_alpha:
            context.scene.bake_pass_metallic = True
        # If we have transparency, it needs to go in diffuse alpha
        if context.scene.bake_pass_alpha:
            item.diffuse_alpha_pack = "TRANSPARENCY"
        # Smoothness to diffuse is only the most efficient when we don't have metallic or alpha
        if context.scene.bake_pass_smoothness and not context.scene.bake_pass_metallic and not context.scene.bake_pass_alpha:
            item.diffuse_alpha_pack = "SMOOTHNESS"
        if context.scene.bake_pass_metallic and context.scene.bake_pass_smoothness:
            item.metallic_alpha_pack = "SMOOTHNESS"
        item.use_lods = False
        item.use_physmodel = False
    elif platform == "QUEST":
        item.export_format = "FBX"
        item.image_export_format = "PNG"
        item.translate_bone_names = "NONE"
        item.generate_prop_bones = False
        # Diffuse vertex color bake? Only if there's already no texture inputs!
        if not any([node.inputs["Base Color"].is_linked for node in bsdf_nodes]):
            item.diffuse_vertex_colors = True

        # alpha packs: arrange for maximum efficiency.
        # Its important to leave Diffuse alpha alone if we're not using it, as Unity will try to use 4bpp if so
        item.diffuse_alpha_pack = "NONE"
        item.metallic_alpha_pack = "NONE"
        # If 'smoothness', we need to force metallic to bake so we can pack to it. (smoothness source is not configurable)
        if context.scene.bake_pass_smoothness:
            context.scene.bake_pass_metallic = True
            item.metallic_alpha_pack = "SMOOTHNESS"
        item.use_lods = False
        item.use_physmodel = False
    elif platform == "SECONDLIFE":
        item.export_format = "DAE"
        item.image_export_format = "PNG"
        item.translate_bone_names = "SECONDLIFE"
        if context.scene.bake_pass_emit:
            item.diffuse_alpha_pack = "EMITMASK"
        item.specular_setup = context.scene.bake_pass_diffuse and context.scene.bake_pass_metallic
        item.specular_alpha_pack = "SMOOTHNESS" if context.scene.bake_pass_smoothness else "NONE"
        item.diffuse_emit_overlay = context.scene.bake_pass_emit
        item.use_physmodel = True
        item.physmodel_lod = 0.1
        item.use_lods = True
        item.lods = (1.0/4, 1.0/16, 1.0/32)
    elif platform == "GMOD":
        # https://developer.valvesoftware.com/wiki/Adapting_PBR_Textures_to_Source with some adjustments
        item.export_format = "GMOD"
        item.image_export_format = "TGA"
        item.translate_bone_names = "VALVE"
        item.gmod_model_name = "Missing No"
        item.generate_prop_bones = False
        if not use_phong:
            if context.scene.bake_pass_normal:
                item.normal_alpha_pack = "SPECULAR"
                item.normal_invert_g = True
            item.specular_setup = True
            item.phong_setup = False
            item.specular_smoothness_overlay = context.scene.bake_pass_smoothness
        else:
            if context.scene.bake_pass_normal:
                item.normal_alpha_pack = "SMOOTHNESS"
                item.normal_invert_g = True
            item.specular_setup = False
            item.phong_setup = True
            item.specular_smoothness_overlay = False
        item.diffuse_emit_overlay = context.scene.bake_pass_emit
        item.diffuse_premultiply_ao = context.scene.bake_pass_ao
        item.smoothness_premultiply_ao = context.scene.bake_pass_ao and context.scene.bake_pass_smoothness
        #TBD: basetexture specular pack
        if context.scene.bake_pass_emit:
            item.diffuse_alpha_pack = "EMITMASK"
        elif context.scene.bake_pass_alpha:
            item.diffuse_alpha_pack = "TRANSPARENCY"
        else:
            item.diffuse_alpha_pack = "NONE"


@register_wrap
class BakePresetDesktop(bpy.types.Operator):
    bl_idname = 'cats_bake.preset_desktop'
    bl_label = t('cats_bake.preset_desktop.label')
    bl_description = t('cats_bake.preset_desktop.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        item = context.scene.bake_platforms.add()
        item.name = "VRChat Desktop"
        autodetect_passes(self, context, item, 32000, "DESKTOP")
        return {'FINISHED'}

@register_wrap
class BakePresetQuest(bpy.types.Operator):
    bl_idname = 'cats_bake.preset_quest'
    bl_label = t('cats_bake.preset_quest.label')
    bl_description = t('cats_bake.preset_quest.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        item = context.scene.bake_platforms.add()
        item.name = "VRChat Quest Excellent"
        autodetect_passes(self, context, item, 7500, "QUEST")
        itemgood = context.scene.bake_platforms.add()
        itemgood.name = "VRChat Quest Good"
        autodetect_passes(self, context, itemgood, 10000, "QUEST")
        return {'FINISHED'}

@register_wrap
class BakePresetSecondlife(bpy.types.Operator):
    bl_idname = 'cats_bake.preset_secondlife'
    bl_label = 'Second Life'
    bl_description = "Preset for producing a single-material Second Life Mesh avatar"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        item = context.scene.bake_platforms.add()
        item.name = "Second Life"
        autodetect_passes(self, context, item, 21844, "SECONDLIFE")
        return {'FINISHED'}

@register_wrap
class BakePresetGmod(bpy.types.Operator):
    bl_idname = 'cats_bake.preset_gmod'
    bl_label = "GMod Metallic (Experimental)"
    bl_description = "Preset for producing a compatible Garry's Mod character model"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        item = context.scene.bake_platforms.add()
        item.name = "Garrys Mod (Metallic)"
        autodetect_passes(self, context, item, 10000, "GMOD")
        return {'FINISHED'}

@register_wrap
class BakePresetGmodPhong(bpy.types.Operator):
    bl_idname = 'cats_bake.preset_gmod_phong'
    bl_label = "GMod Organic (Experimental)"
    bl_description = "Preset for producing a compatible Garry's Mod character model"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        item = context.scene.bake_platforms.add()
        item.name = "Garrys Mod (Organic)"
        autodetect_passes(self, context, item, 10000, "GMOD", use_phong=True)
        return {'FINISHED'}

@register_wrap
class BakePresetAll(bpy.types.Operator):
    bl_idname = 'cats_bake.preset_all'
    bl_label = "Autodetect All"
    bl_description = "Attempt to bake all possible output platforms. Not significantly slower than baking for any one platform"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        bpy.ops.cats_bake.preset_desktop()
        bpy.ops.cats_bake.preset_quest()
        bpy.ops.cats_bake.preset_secondlife()
        return {'FINISHED'}

@register_wrap
class BakeAddProp(bpy.types.Operator):
    bl_idname = 'cats_bake.add_prop'
    bl_label = "Force Prop"
    bl_description = "Forces selected objects to generate prop setups, regardless of bone counts."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.view_layer.objects.selected and any(obj.type == "MESH" for obj in context.view_layer.objects.selected)

    def execute(self, context):
        for obj in context.view_layer.objects.selected:
            obj['generatePropBones'] = True
        return {'FINISHED'}

@register_wrap
class BakeRemoveProp(bpy.types.Operator):
    bl_idname = 'cats_bake.remove_prop'
    bl_label = "Force Not Prop"
    bl_description = "Forces selected objects to never generate prop setups, regardless of bone counts."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.view_layer.objects.selected and any(obj.type == "MESH" for obj in context.view_layer.objects.selected)

    def execute(self, context):
        for obj in context.view_layer.objects.selected:
            obj['generatePropBones'] = False
        return {'FINISHED'}


class BakePassSettings(NamedTuple):
    name: str
    type: str
    image_resolution: int
    samples: int
    background_color: tuple[float, float, float, float]
    margin_px: int
    filter: set[str] = None
    clear: bool = True
    ray_distance: float = 0
    normal_space: str = 'TANGENT'
    solid_material_colors: dict = None
    bake_multires: bool = False


def get_pixel_buffer(image, out=None):
    """Highly efficient method to get all of an image's pixels
    'out' argument allows for re-using an existing buffer if it's the correct size and type"""
    if out is not None and out.size == len(image.pixels) and out.dtype == np.single:
        # Ensure it's flat
        out.shape = -1
        pixel_buffer = out
    else:
        pixel_buffer = np.empty(len(image.pixels), dtype=np.single)
    image.pixels.foreach_get(pixel_buffer)
    return pixel_buffer


@register_wrap
class BakeButton(bpy.types.Operator):
    bl_idname = 'cats_bake.bake'
    bl_label = t('cats_bake.bake.label')
    bl_description = t('cats_bake.bake.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        for obj in Common.get_meshes_objects(check=False):
            if obj.name not in context.view_layer.objects:
                continue
            if Common.is_hidden(obj):
                continue
            for slot in obj.material_slots:
                if slot.material:
                    if not slot.material.use_nodes:
                        return False
                else:
                    if len(obj.material_slots) == 1:
                        return False

        return context.scene.bake_platforms

    @staticmethod
    def scale_samples_by_quality(context, *, samples: int, minimum=None):
        quality = context.scene.bake_samples_quality

        # Scale by the selected quality setting
        if quality == 'LOW':
            samples = samples * 0.25
        elif quality == 'LOWEST':
            samples = 1

        if minimum is not None:
            samples = max(minimum, samples)

        # Samples cannot be less than 1
        samples = max(1, samples)
        return int(samples)

    @staticmethod
    @contextmanager
    # **kwargs are not suitable as input names can be any string
    def temp_disable_links(objects, *inputs_to_disable):
        """ContextManager to temporarily disable links to Principled BSDF inputs and optionally temporarily set different default values\n
        inputs_to_disable contains the names of the inputs and their replacement default values, specifying a
        replacement default value of None will leave the current default value unchanged\n
        inputs_to_disable can be a mix of different types:\n
        only the input name, in which case, the replacement default value is assumed to be None\n
        tuples of (input_name, replacement_default_value)\n
        dictionaries of {input_name: replacement_default_value}, each containing as many key-value pairs as you like"""
        # Parse all the arguments into one big dictionary
        inputs_to_disable_with_defaults = {}
        for input_to_disable in inputs_to_disable:
            if isinstance(input_to_disable, dict):
                inputs_to_disable_with_defaults.update(input_to_disable)
            elif isinstance(input_to_disable, tuple):
                inputs_to_disable_with_defaults[input_to_disable[0]] = input_to_disable[1]
            else:
                inputs_to_disable_with_defaults[input_to_disable] = None

        already_disabled = set()
        re_enable_data = {}
        for material in chain.from_iterable(o.data.materials for o in objects):
            if not material or material.name in already_disabled:
                continue
            else:
                already_disabled.add(material.name)
                tree = material.node_tree
                for node in tree.nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        for input_to_disable, replacement_default_value in inputs_to_disable_with_defaults.items():
                            node_input = node.inputs[input_to_disable]

                            # Get current link sockets and remove the links to them
                            old_link_sockets = []
                            if node_input.is_linked:
                                # Important to only get .links once as it takes O(len(nodetree.links)) time
                                links = node_input.links
                                for link in links:
                                    # There will probably only ever be one link, but this is able to handle multiple links
                                    old_link_sockets.append(link.from_socket)
                                    tree.links.remove(link)

                            # Optionally get and replace the current default value
                            if replacement_default_value is not None:
                                old_default_value = node_input.default_value
                                node_input.default_value = replacement_default_value
                            else:
                                old_default_value = None

                            # Save the old link sockets and old default value, so they can be restored later
                            link_data_list = re_enable_data.setdefault(material.name, [])
                            link_data_list.append((node_input, old_link_sockets, old_default_value))

        # see contextmanager for details
        try:
            yield None
        finally:
            # Restore all the links and default values that were temporarily disabled
            for material_name, link_data_list in re_enable_data.items():
                material = bpy.data.materials[material_name]
                tree = material.node_tree
                for node_input, old_link_sockets, old_default_value in link_data_list:
                    if old_default_value is not None:
                        node_input.default_value = old_default_value
                    for link_socket in old_link_sockets:
                        tree.links.new(node_input, link_socket)

    # Only works between equal data types.
    def swap_links(self, objects, input1, input2):
        already_swapped = set()
        # Find all Principled BSDF. Flip values for input1 and input2 (default_value and connection)
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material:
                    if slot.material.name in already_swapped:
                        continue
                    else:
                        already_swapped.add(slot.material.name)
                    tree = slot.material.node_tree
                    for node in tree.nodes:
                        if node.type == "BSDF_PRINCIPLED":
                            dv1 = node.inputs[input1].default_value
                            dv2 = node.inputs[input2].default_value
                            node.inputs[input2].default_value = dv1
                            node.inputs[input1].default_value = dv2

                            alpha_input = None
                            if node.inputs[input1].is_linked:
                                alpha_input = node.inputs[input1].links[0].from_socket
                                tree.links.remove(node.inputs[input1].links[0])

                            color_input = None
                            if node.inputs[input2].is_linked:
                                color_input = node.inputs[input2].links[0].from_socket
                                tree.links.remove(node.inputs[input2].links[0])

                            if color_input:
                                tree.links.new(node.inputs[input1], color_input)

                            if alpha_input:
                                tree.links.new(node.inputs[input2], alpha_input)

    # filter_node_create is a function which, given a tree, returns a tuple of
    # (input, output)
    def filter_image(self, context, image, filter_create, use_linear=False, save_srgb=False):
        # This is performed in our throwaway scene, so we don't have to keep settings
        context.scene.view_settings.view_transform = 'Raw' if use_linear else 'Standard'
        bpy.context.scene.display_settings.display_device = 'None' if use_linear else 'sRGB'
        orig_colorspace = bpy.data.images[image].colorspace_settings.name
        #if save_srgb:
        #    bpy.data.images[image].colorspace_settings.name = 'sRGB'
        # Bizarrely, getting the pixels from a render result is extremely difficult.
        # To keep things simple, we perform a render here and then reload from disk.
        bpy.data.images[image].save()
        # set up compositor
        context.scene.use_nodes = True
        tree = context.scene.node_tree
        for node in tree.nodes:
            tree.nodes.remove(node)
        image_node = tree.nodes.new(type="CompositorNodeImage")
        image_node.image = bpy.data.images[image]
        filter_input, filter_output = filter_create(context, tree)
        tree.links.new(filter_input, image_node.outputs["Image"])
        viewer_node = tree.nodes.new(type="CompositorNodeComposite")
        tree.links.new(viewer_node.inputs["Image"], filter_output)

        # rerender image
        context.scene.render.resolution_x = bpy.data.images[image].size[0]
        context.scene.render.resolution_y = bpy.data.images[image].size[1]
        context.scene.render.resolution_percentage = 100
        context.scene.render.filepath = bpy.data.images[image].filepath
        # Immediately overwrite when we do this
        bpy.ops.render.render(write_still=True, scene=context.scene.name)
        bpy.data.images[image].reload()
        bpy.data.images[image].colorspace_settings.name = orig_colorspace


    def denoise_create(context, tree):
        denoise_node = tree.nodes.new(type="CompositorNodeDenoise")
        if context.scene.bake_pass_normal:
            normal_node = tree.nodes.new(type="CompositorNodeImage")
            normal_node.image = bpy.data.images["SCRIPT_world.png"]
            tree.links.new(denoise_node.inputs["Normal"], normal_node.outputs["Image"])
        return denoise_node.inputs["Image"], denoise_node.outputs["Image"]

    def sharpen_create(context, tree):
        sharpen_node = tree.nodes.new(type="CompositorNodeFilter")
        sharpen_node.filter_type = "SHARPEN"
        sharpen_node.inputs["Fac"].default_value = 0.1
        return sharpen_node.inputs["Image"], sharpen_node.outputs["Image"]

    def set_values(self, objects, input_name, input_value):
        already_set = set()
        # Find all Principled BSDF. Flip values for input1 and input2 (default_value and connection)
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material:
                    if slot.material.name in already_set:
                        continue
                    else:
                        already_set.add(slot.material.name)
                    tree = slot.material.node_tree
                    for node in tree.nodes:
                        if node.type == "BSDF_PRINCIPLED":
                            node.inputs[input_name].default_value = input_value

    # "Bake pass" function. Run a single bake to "<bake_name>.png" against all selected objects.
    @staticmethod
    def bake_pass(context, bake_settings: BakePassSettings, objects, *, bake_active=None):
        bake_name = bake_settings.name
        bake_type = bake_settings.type
        bake_pass_filter = {} if bake_settings.filter is None else bake_settings.filter
        bake_width = bake_height = bake_settings.image_resolution
        bake_samples = bake_settings.samples
        bake_ray_distance = bake_settings.ray_distance
        background_color = bake_settings.background_color
        clear = bake_settings.clear
        bake_margin = bake_settings.margin_px
        normal_space = bake_settings.normal_space
        solidmaterialcolors = {} if bake_settings.solid_material_colors is None else bake_settings.solid_material_colors
        bake_multires = bake_settings.bake_multires

        bpy.ops.object.select_all(action='DESELECT')
        if bake_active is not None:
            bake_active.select_set(True)
            context.view_layer.objects.active = bake_active

        print("Baking " + bake_name + " for objects: " + ",".join([obj.name for obj in objects]))

        if clear:
            if "SCRIPT_" + bake_name + ".png" in bpy.data.images:
                image = bpy.data.images["SCRIPT_" + bake_name + ".png"]
                image.user_clear()
                bpy.data.images.remove(image)

            bpy.ops.image.new(name="SCRIPT_" + bake_name + ".png", width=bake_width, height=bake_height, color=background_color,
                              generated_type="BLANK", alpha=True)
            image = bpy.data.images["SCRIPT_" + bake_name + ".png"]
            image.filepath = bpy.path.abspath("//CATS Bake/" + "SCRIPT_" + bake_name + ".png")
            image.alpha_mode = "STRAIGHT"
            image.generated_color = background_color
            image.generated_width = bake_width
            image.generated_height = bake_height
            image.scale(bake_width, bake_height)
            if bake_type == 'NORMAL' or bake_type == 'ROUGHNESS':
                image.colorspace_settings.name = 'Non-Color'
            if bake_name == 'diffuse' or bake_name == 'metallic':  # For packing smoothness to alpha
                image.alpha_mode = 'CHANNEL_PACKED'
            # No dtype argument in np.tile so need to create a correctly typed array first
            background_color_array = np.array(background_color, dtype=np.single)
            image.pixels.foreach_set(np.tile(background_color_array, bake_width * bake_height))
        image = bpy.data.images["SCRIPT_" + bake_name + ".png"]

        # Select only objects we're baking
        if not objects:
            print("No objects selected!")
            return

        for obj in objects:
            obj.select_set(True)
            context.view_layer.objects.active = obj

        # For all materials in use, change any value node labeled "bake_<bake_name>" to 1.0, then back to 0.0.
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material:
                    for node in obj.active_material.node_tree.nodes:
                        if node.type == "VALUE" and node.label == "bake_" + bake_name:
                            node.outputs["Value"].default_value = 1

        # For all materials in all objects, add or repurpose an image texture node named "SCRIPT_BAKE"
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material:
                    for node in slot.material.node_tree.nodes:
                        # Assign bake node
                        tree = slot.material.node_tree
                        node = None
                        if "bake" in tree.nodes:
                            node = tree.nodes["bake"]
                        else:
                            node = tree.nodes.new("ShaderNodeTexImage")
                        node.name = "bake"
                        node.label = "Cats bake - do not use"
                        node.select = True
                        node.image = bpy.data.images["SCRIPT_" + bake_name + ".png"]
                        tree.nodes.active = node
                        node.location.x += 500
                        node.location.y -= 500

        # Run bake.
        context.scene.cycles.bake_type = bake_type
        context.scene.render.bake.use_pass_direct = "DIRECT" in bake_pass_filter
        context.scene.render.bake.use_pass_indirect = "INDIRECT" in bake_pass_filter
        context.scene.render.bake.use_pass_color = "COLOR" in bake_pass_filter
        context.scene.render.bake.use_pass_diffuse = "DIFFUSE" in bake_pass_filter
        context.scene.render.bake.use_pass_emit = "EMIT" in bake_pass_filter
        if Common.version_2_93_or_older():
            context.scene.render.bake.use_pass_ambient_occlusion = "AO" in bake_pass_filter
        if bpy.app.version >= (2, 92, 0):
            context.scene.render.bake.target = "VERTEX_COLORS" if "VERTEX_COLORS" in bake_pass_filter else "IMAGE_TEXTURES"
        context.scene.cycles.samples = bake_samples
        context.scene.render.bake.use_clear = clear and bake_type == 'NORMAL'
        context.scene.render.bake.use_selected_to_active = (bake_active != None)
        context.scene.render.bake.margin = bake_margin
        context.scene.render.use_bake_multires = bake_multires
        context.scene.render.bake.normal_space = normal_space
        bpy.ops.object.bake(type=bake_type,
                            # pass_filter=bake_pass_filter,
                            use_clear=clear and bake_type == 'NORMAL',
                            # uv_layer="SCRIPT",
                            use_selected_to_active=(bake_active != None),
                            cage_extrusion=bake_ray_distance,
                            normal_space=normal_space
                            )
        # For all materials in use, change any value node labeled "bake_<bake_name>" to 1.0, then back to 0.0.
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material:
                    for node in obj.active_material.node_tree.nodes:
                        if node.type == "VALUE" and node.label == "bake_" + bake_name:
                            node.outputs["Value"].default_value = 0


        #solid material optimization making 4X4 squares of solid color for this pass - @989onan
        if context.scene.bake_optimize_solid_materials and (not any(plat.use_decimation for plat in context.scene.bake_platforms)) and (not context.scene.bake_pass_ao) and (not context.scene.bake_pass_normal):
            #arranging old pixels and assignment to image pixels this way makes only one update per pass, so many many times faster - @989onan
            old_pixels = get_pixel_buffer(image)
            # Set shape to a 3D array of (width, height, rgba)
            old_pixels.shape = (image.size[0], image.size[1], 4)

            # lastly, slap our solid squares on top of bake atlas, to make a nice solid square without interuptions from the rest of the bake - @989onan
            #
            # in pixels
            # Thanks to @Sacred#9619 on discord for this one.
            # 0.0078125 is 1/128, so the margin is 1/256th of the bake resolution, rounded up
            margin = math.ceil(0.0078125 * context.scene.bake_resolution / 2)  # has to be the same as "pixelmargin"
            margins_in_width = bake_width // margin
            margins_in_height = bake_height // margin

            solid_material_index_lookup = {key: index for index, key in enumerate(solidmaterialcolors.keys())}

            for child in [obj for obj in objects if obj.type == "MESH"]:  # grab all mesh objects being baked
                for material in child.data.materials:
                    if material.name in solidmaterialcolors:
                        index = solid_material_index_lookup[material.name]

                        x_start = margin * (index % margins_in_width)
                        x_end_excl = x_start + margin
                        y_start = margin * (index // margins_in_height)
                        y_end_excl = y_start + margin

                        # while in pixels inside image but 4 pixel padding around our solid center square position
                        x_start = max(0, x_start)
                        x_end_excl = min(bake_width, x_end_excl)
                        y_start = max(0, y_start)
                        y_end_excl = min(bake_height, y_end_excl)

                        color = solidmaterialcolors[material.name][bake_name + "_color"]

                        # Update pixel values via 2D slice
                        old_pixels[y_start:y_end_excl, x_start:x_end_excl] = color
            old_pixels.shape = -1
            image.pixels.foreach_set(old_pixels)



    def copy_ob(self, ob, parent, collection):
        # copy ob
        copy = ob.copy()
        copy.data = ob.data.copy()
        copy.parent = parent
        copy.matrix_parent_inverse = ob.matrix_parent_inverse.copy()
        # copy particle settings
        for ps in copy.particle_systems:
            ps.settings = ps.settings.copy()
        collection.objects.link(copy)
        return copy

    def tree_copy(self, ob, parent, collection, ignore_hidden, levels=3, view_layer=None):
        def recurse(ob, parent, depth, ignore_hidden, view_layer=None):
            if depth > levels:
                return
            if Common.is_hidden(ob) and ob.type != 'ARMATURE' and ignore_hidden:
                return
            if view_layer and ob.name not in view_layer.objects:
                return
            copy = self.copy_ob(ob, parent, collection)

            for child in ob.children:
                recurse(child, copy, depth + 1, ignore_hidden, view_layer=view_layer)

            return copy

        return recurse(ob, ob.parent, 0, ignore_hidden, view_layer=view_layer)

    def execute(self, context):
        bake_start = perf_counter()

        if not [obj for obj in Common.get_meshes_objects(check=False) if not Common.is_hidden(obj) or not context.scene.bake_ignore_hidden]:
            self.report({'ERROR'}, t('cats_bake.error.no_meshes'))
            return {'FINISHED'}
        # if context.scene.render.engine != 'CYCLES':
        #     self.report({'ERROR'}, t('cats_bake.error.render_engine'))
        #     return {'FINISHED'}
        if any([obj.hide_render and not Common.is_hidden(obj) for obj in Common.get_armature().children if obj.name in context.view_layer.objects]):
            self.report({'ERROR'}, t('cats_bake.error.render_disabled'))
            return {'FINISHED'}
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "You need to save your .blend somewhere first!")
            return {'FINISHED'}

        # Change render engine to cycles and save the current one
        render_engine_tmp = context.scene.render.engine
        render_device_tmp = context.scene.cycles.device
        context.scene.render.engine = 'CYCLES'
        if context.scene.bake_device == 'GPU':
            context.scene.cycles.device = 'GPU'
        else:
            context.scene.cycles.device = 'CPU'

        # Change decimate settings, run bake, change them back
        decimation_mode = context.scene.decimation_mode
        max_tris = context.scene.max_tris
        decimate_fingers = context.scene.decimate_fingers
        decimation_remove_doubles = context.scene.decimation_remove_doubles
        decimation_animation_weighting = context.scene.decimation_animation_weighting
        decimation_animation_weighting_factor = context.scene.decimation_animation_weighting_factor

        self.perform_bake(context)

        context.scene.decimation_mode = decimation_mode
        context.scene.max_tris = max_tris
        context.scene.decimate_fingers = decimate_fingers
        context.scene.decimation_remove_doubles = decimation_remove_doubles
        context.scene.decimation_animation_weighting = decimation_animation_weighting
        context.scene.decimation_animation_weighting_factor = decimation_animation_weighting_factor

        # Change render engine back to original
        context.scene.render.engine = render_engine_tmp
        context.scene.cycles.device = render_device_tmp

        bake_end = perf_counter()

        bake_duration = bake_end - bake_start

        print(f'Bake completed in {bake_duration} seconds')

        return {'FINISHED'}

        #this samples curve to recalculate original smoothness to new smoothness
    def sample_curve_smoothness(self,sample_val):
        samplecurve = [0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000334,0.000678,0.001033,0.001400,0.001779,0.002170,0.002575,0.002993,0.003424,0.003871,0.004332,0.004808,0.005301,0.005810,0.006335,0.006878,0.007439,0.008018,0.008616,0.009233,0.009870,0.010527,0.011204,0.011903,0.012624,0.013367,0.014132,0.014920,0.015732,0.016568,0.017429,0.018314,0.019225,0.020163,0.021126,0.022117,0.023134,0.024180,0.025255,0.026358,0.027490,0.028652,0.029845,0.031068,0.032323,0.033610,0.034928,0.036280,0.037664,0.039083,0.040535,0.042022,0.043544,0.045102,0.046696,0.048327,0.049994,0.051699,0.053442,0.055224,0.057045,0.058905,0.060805,0.062745,0.064729,0.066758,0.068831,0.070948,0.073109,0.075311,0.077555,0.079841,0.082166,0.084531,0.086935,0.089377,0.091856,0.094371,0.096923,0.099510,0.102131,0.104786,0.107474,0.110195,0.112947,0.115729,0.118542,0.121385,0.124256,0.127155,0.130082,0.133035,0.136013,0.139018,0.142046,0.145098,0.148173,0.151270,0.154389,0.157529,0.160689,0.163868,0.167066,0.170282,0.173515,0.176765,0.180030,0.183310,0.186605,0.189914,0.193235,0.196569,0.199914,0.203270,0.206635,0.210011,0.213395,0.216786,0.220185,0.223591,0.227002,0.230418,0.233838,0.237263,0.240690,0.244119,0.247549,0.250980]

        #256 values in curve
        return samplecurve[round(256*sample_val)]

    #this samples for roughness map curve
    def sample_curve_roughness(self,sample_val):
        samplecurve = [0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.002133,0.004309,0.006529,0.008791,0.011097,0.013447,0.015840,0.018276,0.020756,0.023280,0.025847,0.028459,0.031114,0.033813,0.036557,0.039344,0.042176,0.045053,0.047973,0.050938,0.053948,0.057002,0.060102,0.063245,0.066434,0.069668,0.072947,0.076271,0.079640,0.083054,0.086514,0.090019,0.093570,0.097166,0.100808,0.104495,0.108229,0.112008,0.115834,0.119705,0.123623,0.127586,0.131596,0.135653,0.139756,0.143905,0.148101,0.152343,0.156633,0.160969,0.165352,0.169782,0.174259,0.178784,0.183355,0.187974,0.192640,0.197354,0.202115,0.206924,0.211781,0.216685,0.221637,0.226637,0.231685,0.236781,0.241926,0.247118,0.252359,0.257648,0.262986,0.268372,0.273807,0.279291,0.284823,0.290404,0.296035,0.301714,0.307442,0.313220,0.319046,0.324922,0.330848,0.336823,0.342847,0.348921,0.355045,0.361219,0.367443,0.373716,0.380040,0.386413,0.392837,0.399311,0.405836,0.412410,0.419036,0.425712,0.432438,0.439216,0.446181,0.453467,0.461066,0.468971,0.477176,0.485674,0.494457,0.503519,0.512853,0.522451,0.532307,0.542413,0.552764,0.563351,0.574168,0.585208,0.596464,0.607929,0.619596,0.631458,0.643508,0.655739,0.668144,0.680716,0.693449,0.706335,0.719367,0.732538,0.745842,0.759271,0.772819,0.786478,0.800241,0.814102,0.828054,0.842089,0.856201,0.870382,0.884626,0.898926,0.913275,0.927665,0.942090,0.956543,0.971017,0.985505,1.000000]

        #256 values in curve
        return samplecurve[round(256*sample_val)]

    #needed because it likes to pause blender entirely for a key input in console and we don't want that garbage - @989onan
    def compile_gmod_tga(self,steam_library_path,images_path,texturename):
        def on_timeout(process,statusdict):
            process.kill()
        #print(str([steam_library_path+"steamapps/common/GarrysMod/bin/vtex.exe", images_path+"materialsrc/"+texturename,"-mkdir", "-quiet","-game", steam_library_path+"steamapps/common/GarrysMod/garrysmod"]))
        proc = subprocess.Popen([steam_library_path+"steamapps/common/GarrysMod/bin/vtex.exe", images_path+"materialsrc/"+texturename,"-mkdir", "-quiet","-game", steam_library_path+"steamapps/common/GarrysMod/garrysmod"])
        # trigger timout and kill process in 5 seconds
        timer = threading.Timer(10, on_timeout, (proc,{'timeout':False}))
        timer.start()
        proc.wait()
        # in case we didn't hit timeout
        timer.cancel()

    def perform_bake(self, context):
        print('START BAKE')
        # TODO: diffuse, emit, alpha, metallic and smoothness all have a very slight difference between sample counts
        #       default it to something sane, but maybe add a menu later?
        # Global options
        resolution = context.scene.bake_resolution
        steam_library_path = context.scene.bake_steam_library.replace("\\", "/")
        generate_uvmap = context.scene.bake_generate_uvmap
        prioritize_face = context.scene.bake_prioritize_face
        prioritize_factor = context.scene.bake_face_scale
        uv_overlap_correction = context.scene.bake_uv_overlap_correction
        margin = 0.0078125 # we want a 1-pixel margin around each island at 256x256, so 1/256, and since it's the space between islands we multiply it by two
        pixelmargin = int(math.ceil(margin * resolution / 2))
        quick_compare = True
        apply_keys = context.scene.bake_apply_keys
        optimize_solid_materials = context.scene.bake_optimize_solid_materials
        unwrap_angle = context.scene.bake_unwrap_angle

        # TODO: Option to seperate by loose parts and bake selected to active

        # Passes
        pass_diffuse = context.scene.bake_pass_diffuse
        pass_normal = context.scene.bake_pass_normal
        pass_smoothness = context.scene.bake_pass_smoothness
        pass_ao = context.scene.bake_pass_ao
        pass_emit = context.scene.bake_pass_emit
        pass_alpha = context.scene.bake_pass_alpha
        pass_metallic = context.scene.bake_pass_metallic

        # Pass options
        illuminate_eyes = context.scene.bake_illuminate_eyes
        supersample_normals = context.scene.bake_pass_normal and any(plat.use_decimation for plat in context.scene.bake_platforms) and uv_overlap_correction == "UNMIRROR" # Bake the intermediate step at 2x resolution
        overlap_aware = False # Unreliable until UVP doesn't care about the island scale.
        emit_indirect = context.scene.bake_emit_indirect
        emit_exclude_eyes = context.scene.bake_emit_exclude_eyes
        cleanup_shapekeys = context.scene.bake_cleanup_shapekeys # Reverted and _old shapekeys
        create_disable_shapekeys = context.scene.bake_create_disable_shapekeys
        ignore_hidden = context.scene.bake_ignore_hidden

        # Filters
        sharpen_bakes = context.scene.bake_sharpen
        denoise_bakes = context.scene.bake_denoise

        #also disable optimize solid materials if other things are enabled that will break it
        optimize_solid_materials = optimize_solid_materials and (not any(plat.use_decimation for plat in context.scene.bake_platforms)) and (not pass_ao) and (not pass_normal)

        # Save reference to original armature
        armature = Common.get_armature()


        # Create an output collection
        collection = bpy.data.collections.new("CATS Bake")
        context.scene.collection.children.link(collection)

        # Tree-copy all meshes
        arm_copy = self.tree_copy(armature, None, collection, ignore_hidden, view_layer=context.view_layer)

        # Create an extra scene to render in
        orig_scene_name = context.scene.name
        bpy.ops.scene.new(type="EMPTY") # copy keeps existing settings
        context.scene.name = "CATS Scene"
        orig_scene = bpy.data.scenes[orig_scene_name]
        context.scene.collection.children.link(collection)


        # Make sure all armature modifiers target the new armature
        for child in collection.all_objects:
            for modifier in child.modifiers:
                if modifier.type == "ARMATURE":
                    modifier.object = arm_copy
                if modifier.type == "MULTIRES":
                    modifier.render_levels = modifier.total_levels

        # Copy default values from the largest diffuse BSDF
        objs_size_descending = sorted([obj for obj in collection.all_objects if obj.type == "MESH"],
                                      key=lambda obj: obj.dimensions.x * obj.dimensions.y * obj.dimensions.z,
                                      reverse=True)

        def first_bsdf(objs):
            for obj in objs_size_descending:
                for slot in obj.material_slots:
                    if slot.material:
                        tree = slot.material.node_tree
                        for node in tree.nodes:
                            if node.type == "BSDF_PRINCIPLED":
                                return node

        bsdf_original = first_bsdf(objs_size_descending)
        cats_uv_layers = []

        #first fix broken colors by adding their textures, then add the results of color only materials/solid textures to see if they need special UV treatment.
        #To detect and fix UV's for materials that are solid and don't need entire uv maps if all the textures are consistent throught. Also adds solid textures for BSDF's with default values but no texture
        solidmaterialnames = dict()

        #to store the colors for each pass for each solid material to apply to bake atlas later.
        solidmaterialcolors = dict()
        if optimize_solid_materials:
            for child in collection.all_objects:
                if child.type == "MESH":
                    for matindex,material in enumerate(child.data.materials):
                        for node in material.node_tree.nodes:
                            if node.type == "BSDF_PRINCIPLED":#For each material bsdf in every object in each material

                                diffuse_solid = True
                                diffuse_color = [0.0,0.0,0.0,1.0]
                                smoothness_solid = True
                                smoothness_color = [0.0,0.0,0.0,1.0]
                                emission_solid = False
                                emission_color = [0.0,0.0,0.0,1.0]
                                metallic_solid = True
                                metallic_color = [0.0,0.0,0.0,1.0]

                                def check_if_tex_solid(bsdfinputname,node_prinipled,executestring):
                                    node_image = node_prinipled.inputs[bsdfinputname].links[0].from_node
                                    if node_image.type != "TEX_IMAGE":  # To catch normal maps
                                        return False, (0.0, 0.0, 0.0, 1.0)  # if not image then it's some type of node chain that is too complicated so return false
                                    pixels = get_pixel_buffer(node_image.image)
                                    # Sneaky minor optimisation since there's no axis argument available in numpy.equal
                                    # Create custom dtype for viewing every four elements as a single tuple-like element
                                    rgba_dtype = np.dtype([("", pixels.dtype), ] * 4)
                                    # View the data as this custom type
                                    pixels_rgba_view = pixels.view(rgba_dtype)
                                    first_pixel = pixels_rgba_view[0]
                                    # Using the custom dtype means there's only a quarter as many elements to compare, making it slightly faster
                                    if (pixels_rgba_view == first_pixel).all():
                                        # first_pixel will be a np.void type which could cause problems, so convert to tuple before returning
                                        return True, tuple(first_pixel)
                                    else:
                                        return False, (0.0, 0.0, 0.0, 1.0)
                                #each pass below makes solid color textures or reads the texture and checks if it's solid using numpy.

                                node_prinipled = node

                                if pass_diffuse:
                                    if not node.inputs["Base Color"].is_linked:
                                        diffuse_solid = True
                                        node_image = material.node_tree.nodes.new(type="ShaderNodeTexImage")
                                        node_image.image = bpy.data.images.new("Base Color", width=8, height=8, alpha=True)
                                        node_image.location = (1101, -500)
                                        node_image.label = "Base Color"

                                        #assign to image so it's baked
                                        node_image.image.generated_color = node.inputs["Base Color"].default_value
                                        diffuse_color = node.inputs["Base Color"].default_value
                                        node_image.image.file_format = 'PNG'
                                        material.node_tree.links.new(node_image.outputs['Color'], node_prinipled.inputs['Base Color'])
                                    else:
                                        diffuse_solid,diffuse_color = check_if_tex_solid("Base Color",node_prinipled,'diffuse_color')

                                if pass_emit:
                                    if not node.inputs["Emission"].is_linked:
                                        emission_solid = True
                                        node_image = material.node_tree.nodes.new(type="ShaderNodeTexImage")
                                        node_image.image = bpy.data.images.new("Emission", width=8, height=8, alpha=True)
                                        node_image.location = (1101, -500)
                                        node_image.label = "Emission"


                                        #assign to image so it's baked
                                        node_image.image.generated_color = node.inputs["Emission"].default_value
                                        emission_color = node.inputs["Emission"].default_value
                                        node_image.image.file_format = 'PNG'
                                        material.node_tree.links.new(node_image.outputs['Color'], node_prinipled.inputs['Emission'])
                                    else:
                                        emission_solid,emission_color = check_if_tex_solid("Emission",node_prinipled,"emission_color") #emission doesn't care about other things for mat to be solid
                                if pass_smoothness:
                                    if not node.inputs["Roughness"].is_linked:
                                        smoothness_solid = True
                                        node_image = material.node_tree.nodes.new(type="ShaderNodeTexImage")
                                        node_image.image = bpy.data.images.new("Roughness", width=8, height=8, alpha=True)
                                        node_image.location = (1101, -500)
                                        node_image.label = "Roughness"


                                        #assign to image so it's baked
                                        node_image.image.generated_color = [node.inputs["Roughness"].default_value]*4
                                        smoothness_color = [node.inputs["Roughness"].default_value]*4
                                        node_image.image.file_format = 'PNG'
                                        material.node_tree.links.new(node_image.outputs['Color'], node_prinipled.inputs['Roughness'])
                                    else:
                                        if diffuse_solid: #efficency since checking if others are false is faster than always checking an entire array. Every bit counts.
                                            smoothness_solid,smoothness_color = check_if_tex_solid("Roughness",node_prinipled,"smoothness_color")
                                        else:
                                            smoothness_solid = False
                                if pass_metallic:
                                    if not node.inputs["Metallic"].is_linked:
                                        metallic_solid = True
                                        node_image = material.node_tree.nodes.new(type="ShaderNodeTexImage")
                                        node_image.image = bpy.data.images.new("Metallic", width=8, height=8, alpha=True)
                                        node_image.location = (1101, -500)
                                        node_image.label = "Metallic"


                                        #assign to image so it's baked
                                        node_image.image.generated_color = [node.inputs["Metallic"].default_value]*4
                                        metallic_color = [node.inputs["Metallic"].default_value]*4
                                        node_image.image.file_format = 'PNG'
                                        material.node_tree.links.new(node_image.outputs['Color'], node_prinipled.inputs['Metallic'])
                                    else:
                                        if smoothness_solid:  #efficency since checking if others are false is faster than always checking an entire array. Every bit counts.
                                            metallic_solid,metallic_color = check_if_tex_solid("Metallic",node_prinipled,"metallic_color")
                                        else:
                                            metallic_solid = False

                                #now we check based on all the passes if our material is solid.
                                if diffuse_solid and smoothness_solid and metallic_solid:
                                    solidmaterialnames[child.data.materials[matindex].name] = len(solidmaterialnames) #put materials into an index order because we wanna put them into a grid
                                    solidmaterialcolors[child.data.materials[matindex].name] = {"diffuse_color":diffuse_color,"emission_color":emission_color,"smoothness_color":smoothness_color,"metallic_color":metallic_color}
                                    print("Object: \""+child.name+"\" with Material: \""+child.data.materials[matindex].name+"\" is solid!")
                                elif emission_solid:
                                    solidmaterialnames[child.data.materials[matindex].name] = len(solidmaterialnames) #put materials into an index order because we wanna put them into a grid
                                    solidmaterialcolors[child.data.materials[matindex].name] = {"diffuse_color":diffuse_color,"emission_color":emission_color,"smoothness_color":smoothness_color,"metallic_color":metallic_color}
                                    print("Object: \""+child.name+"\" with Material: \""+child.data.materials[matindex].name+"\" is solid!")
                                else:
                                    print("Object: \""+child.name+"\" with Material: \""+child.data.materials[matindex].name+"\" is NOT solid!")
                                    pass #don't put an entry, and assume if there is no entry, then it isn't solid.

                                break #since we found our principled and did our stuff we can break the node scanning loop on this material.


        if generate_uvmap:
            bpy.ops.object.select_all(action='DESELECT')
            # Make copies of the currently render-active UV layer, name "CATS UV"
            for child in collection.all_objects:
                if child.type == "MESH":
                    child.select_set(True)
                    context.view_layer.objects.active = child
                    # make sure to copy the render-active UV only
                    active_uv = None
                    for uvmap in child.data.uv_layers:
                        if uvmap.active_render:
                            child.data.uv_layers.active = uvmap
                            active_uv = uvmap

                    reproject_anyway = len(child.data.uv_layers) == 0 \
                        or all(loop.uv[0] in {0, 1} and loop.uv[1] in {0, 1} for loop in active_uv.data)

                    bpy.ops.mesh.uv_texture_add()
                    child.data.uv_layers[-1].name = 'CATS UV'
                    cats_uv_layers.append('CATS UV')
                    if supersample_normals:
                        bpy.ops.mesh.uv_texture_add()
                        child.data.uv_layers[-1].name = 'CATS UV Super'
                        cats_uv_layers.append('CATS UV Super')

                    if uv_overlap_correction == "REPROJECT" or reproject_anyway:
                        for layer in cats_uv_layers:
                            idx = child.data.uv_layers.active_index
                            bpy.ops.object.select_all(action='DESELECT')
                            child.data.uv_layers[layer].active = True
                            Common.switch('EDIT')
                            for matindex,material in enumerate(child.data.materials):
                                #select each material individually and unwrap. The averaging and packing will take care of overlaps. - @989onan
                                bpy.ops.mesh.select_all(action='DESELECT')
                                child.active_material_index = matindex
                                bpy.ops.object.material_slot_select()

                                bpy.ops.uv.select_all(action='SELECT')
                                bpy.ops.uv.smart_project(angle_limit=unwrap_angle, island_margin=margin)
                            Common.switch('OBJECT')
                            child.data.uv_layers.active_index = idx
                    elif uv_overlap_correction == "UNMIRROR":
                        # TODO: issue a warning if any source images don't use 'wrap'
                        # Move uvs of all faces in +X over by (1, 0)
                        print("Un-mirroring source CATS UV data")
                        uv_layer = (child.data.uv_layers["CATS UV Super"] if
                                   supersample_normals else
                                   child.data.uv_layers["CATS UV"])
                        # Get centers of all polygons
                        poly_centers = np.empty(len(child.data.polygons) * 3, dtype=np.single)
                        child.data.polygons.foreach_get('center', poly_centers)
                        # The polygon centers are 3 dimensional vectors, which get flattened into one big array of floats
                        # Use a slice to get a view of every third value, starting from the
                        poly_centers_x_view = poly_centers[0::3]
                        # Find where the x value of the centers are greater than 0
                        x_greater_than_zero = np.greater(poly_centers_x_view, 0)

                        # Get loop total of all polygons
                        loop_totals = np.empty(len(child.data.polygons), dtype=np.uintc)
                        child.data.polygons.foreach_get('loop_total', loop_totals)

                        # Repeat the bools so there's one for each polygon loop index of each polygon
                        x_greater_than_zero_mask = np.repeat(x_greater_than_zero, loop_totals)

                        # Get uvs
                        uvs = np.empty(len(uv_layer.data) * 2, dtype=np.single)
                        uv_layer.data.foreach_get('uv', uvs)
                        # Get view of only the x components of the uvs
                        uv_x_components_view = uvs[::2]
                        # Add 1 to all the uv x components where the polygon's center's x component is greater than zero
                        uv_x_components_view[x_greater_than_zero_mask] += 1

                        # Write the updated uvs to the uv layer
                        uv_layer.data.foreach_set('uv', uvs)

                        del uv_x_components_view
                        del uvs
                        del x_greater_than_zero_mask
                        del loop_totals
                        del x_greater_than_zero
                        del poly_centers_x_view
                        del poly_centers
                    elif uv_overlap_correction == "MANUAL":
                        if "Target" in child.data.uv_layers:
                            # Copy uvs from "Target" to "CATS UV" and "CATS UV Super"
                            target_layer = child.data.uv_layers["Target"]
                            uvs = np.empty(len(target_layer.data) * 2, dtype=np.single)
                            target_layer.data.foreach_get('uv', uvs)
                            child.data.uv_layers["CATS UV"].data.foreach_set('uv', uvs)
                            if supersample_normals:
                                child.data.uv_layers["CATS UV Super"].data.foreach_set('uv', uvs)
                            del uvs

            #PLEASE DO THIS TO PREVENT PROBLEMS WITH UV EDITING LATER ON:
            bpy.data.scenes["CATS Scene"].tool_settings.use_uv_select_sync = False

            if optimize_solid_materials:
                # Thanks to @Sacred#9619 on discord for this one.
                squaremargin = pixelmargin
                n = resolution // squaremargin

                # go through the solid materials on all the meshes and scale their UV's down to 0 in a grid of rows of
                # squares so that they bake on a small separate part of the image mostly in the bottom left -@989onan
                for child in collection.all_objects:
                    if child.type == "MESH":
                        poly_material_indices = None
                        poly_loop_totals = None
                        poly_hide = None
                        uv_layers_uvs = {}
                        for matindex, material in enumerate(child.data.materials):
                            if material.name in solidmaterialnames:
                                # Only get the material indices at most once per object
                                if poly_material_indices is None:
                                    poly_material_indices = np.empty(len(child.data.polygons), dtype=np.ushort)
                                    child.data.polygons.foreach_get('material_index', poly_material_indices)
                                # Only get the polygon loop_totals at most once per object
                                if poly_loop_totals is None:
                                    poly_loop_totals = np.empty(len(child.data.polygons), dtype=np.uintc)
                                    child.data.polygons.foreach_get('loop_total', poly_loop_totals)
                                # Only get polygon hide at most once per object
                                if poly_hide is None:
                                    poly_hide = np.empty(len(child.data.polygons), dtype=bool)
                                    child.data.polygons.foreach_get('hide', poly_hide)

                                # Find which polygons are in this material
                                polygons_in_mat = np.equal(poly_material_indices, matindex)

                                # Hide the polygons so that, when uv unwrapping later, it ignores these polygons
                                poly_hide[polygons_in_mat] = True

                                # Use the loop totals to get which uvs are in this material
                                uvs_in_mat = np.repeat(polygons_in_mat, poly_loop_totals)

                                # The index of the solid material determines its location on the uv map and texture
                                index = solidmaterialnames[material.name]

                                # Thanks to @Sacred#9619 on discord for this one.
                                x = squaremargin / 2 + squaremargin * index % n
                                y = squaremargin / 2 + squaremargin * index // n

                                pivot_point = (x / resolution, y / resolution)

                                for layer_name in cats_uv_layers:
                                    # Only get the uvs for each uv layer at most once per object
                                    uvs_and_data = uv_layers_uvs.get(layer_name)
                                    if uvs_and_data is None:
                                        uv_layer_data = child.data.uv_layers[layer_name].data
                                        uvs = np.empty(len(uv_layer_data) * 2, dtype=np.single)
                                        uv_layer_data.foreach_get('uv', uvs)
                                        # Change shape to put each u and v into their own sub-arrays
                                        # This makes it so that each index gets a uv pair
                                        uvs.shape = (-1, 2)
                                        uv_layers_uvs[layer_name] = (uvs, uv_layer_data)
                                    else:
                                        uvs, _uv_layer_data = uvs_and_data
                                    # We want to scale the uvs in the current material down to zero relative to the
                                    # pivot point
                                    # This is the same as setting the uvs to that pivot point
                                    uvs[uvs_in_mat] = pivot_point
                                del uvs_in_mat
                                del polygons_in_mat
                        # Write modified uvs back to their corresponding uv_layer
                        # Deselect all the uvs for scaling uv's out the way later.
                        if uv_layers_uvs:
                            all_deselect = None
                            for uvs, uv_layer_data in uv_layers_uvs.values():
                                # Must be flat when setting
                                uvs.shape = -1
                                uv_layer_data.foreach_set('uv', uvs)
                                if all_deselect is None:
                                    # All the uv_layers will have the same number of elements, so we can reuse the same
                                    # array each time
                                    all_deselect = np.zeros(len(uv_layer_data), dtype=bool)
                                uv_layer_data.foreach_set('select', all_deselect)
                            del all_deselect
                        # Write modified poly_hide back to the polygons for scaling uv's out the way later.
                        # This and the uv deselecting also prevents the steps for averaging islands and prioritizing
                        # head size from going bad later.
                        if poly_hide is not None:
                            child.data.polygons.foreach_set('hide', poly_hide)
                        del uv_layers_uvs
                        del poly_hide
                        del poly_loop_totals
                        del poly_material_indices


            # Select all meshes. Select all UVs. Average islands scale
            Common.switch('OBJECT')
            bpy.ops.object.select_all(action='SELECT')
            for layer in cats_uv_layers:
                Common.switch('OBJECT')
                for obj in collection.all_objects:
                    if obj.type == 'MESH':
                        obj.data.uv_layers.active = obj.data.uv_layers[layer]
                        context.view_layer.objects.active = obj
                Common.switch('EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.select_all(action='SELECT')
                bpy.ops.uv.average_islands_scale()  # Use blender average so we can make our own tweaks.
                Common.switch('OBJECT')


            if prioritize_face:
                for obj in collection.all_objects:
                    if obj.type != "MESH":
                        continue

                    groups_to_look_for = ['LeftEye', 'lefteye', 'Lefteye', 'Eye.L', 'RightEye', 'righteye', 'Righteye', 'Eye.R']

                    # Get the index of each group and ignore any groups which don't exist
                    idx_to_group = {obj.vertex_groups[group].index: group for group in groups_to_look_for if group in obj.vertex_groups}

                    found_groups = []
                    # Iterate through all the groups of all the vertices, once each, until we find the groups we're
                    # looking for
                    # Using this chain lets us avoid the extra code needed to break an outer for loop from an inner for
                    # loop
                    vgroup_iter = chain.from_iterable(vert.groups for vert in obj.data.vertices)
                    if idx_to_group:
                        for v_group in vgroup_iter:
                            if v_group.group in idx_to_group and v_group.weight > 0.0:
                                # Found a group we're looking for with an acceptable weight!
                                group = idx_to_group[v_group.group]
                                print("{} found in {}".format(group, obj.name))
                                # Add it to the list
                                found_groups.append(group)
                                # Remove it from the dictionary
                                idx_to_group.pop(v_group.group)
                                # Ideally, we would process the found group immediately, but it requires going into and
                                # out of edit mode, which is likely to cause obj.data.vertices to change, which seems
                                # to cause some sort of memory corruption when trying to iterate the now stale
                                # obj.data.vertices, often crashing Blender or causing weird corruption in the bake
                                if not idx_to_group:
                                    # If there are no more groups to look for, we can stop looking
                                    break

                    context.view_layer.objects.active = obj

                    uvs = None
                    for group in found_groups:
                        bpy.ops.object.mode_set(mode='EDIT')
                        bpy.ops.uv.select_all(action='DESELECT')
                        bpy.ops.mesh.select_all(action='DESELECT')
                        # Select all vertices in it
                        obj.vertex_groups.active = obj.vertex_groups[group]
                        bpy.ops.object.vertex_group_select()
                        # Synchronize
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.mode_set(mode='EDIT')
                        # Then select all UVs
                        bpy.ops.uv.select_all(action='SELECT')
                        bpy.ops.object.mode_set(mode='OBJECT')
                        # Then for each UV (cause of the viewport thing) scale up by the selected factor

                        # Going in and out of edit mode can cause any existing reference to uv_layer to become stale and
                        # presumably point to some unrelated part of memory, so we can't maintain a single reference to
                        # the uv_layer and use it over and over again otherwise we risk randomly crashing Blender
                        uv_layer = obj.data.uv_layers["CATS UV"]

                        if uvs is None:
                            uvs = np.empty(len(uv_layer.data) * 2, dtype=np.single)
                            uv_layer.data.foreach_get('uv', uvs)
                            uvs.shape = (-1, 2)

                        # Get uv select state
                        uv_select = np.empty(len(uv_layer.data), dtype=bool)
                        uv_layer.data.foreach_get('select', uv_select)

                        # Multiply the values by prioritize_factor where the uvs are selected
                        uvs[uv_select] *= prioritize_factor
                        del uv_select

                    if uvs is not None:
                        # Flatten and update
                        # Note: This assumes that entering and exiting edit mode and selecting/deselecting parts
                        #       of the mesh and uvs cannot affect uv ordering. If sometimes the uvs get completely
                        #       messed up, try setting the updated uvs at the end of each iteration of the above for
                        #       loop instead of only once here after the for loop has finished
                        uv_layer = obj.data.uv_layers["CATS UV"]
                        uvs.shape = -1
                        uv_layer.data.foreach_set('uv', uvs)
                    del uvs


            # Pack islands. Optionally use UVPackMaster if it's available
            bpy.ops.object.select_all(action='SELECT')
            for layer in cats_uv_layers:
                for obj in collection.all_objects:
                    if obj.type == 'MESH':
                        obj.data.uv_layers.active = obj.data.uv_layers[layer]
                Common.switch('EDIT')
                if not optimize_solid_materials:
                    # keep polygons for solid materials hidden, so they don't get packed and unwrapped
                    # All other polygons will already be set as visible
                    bpy.ops.mesh.reveal()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.uv.select_all(action='SELECT')
                # detect if UVPackMaster installed and configured
                if not overlap_aware:
                    bpy.ops.uv.pack_islands(rotate=True, margin=margin)
                try:  # UVP doesn't respect margins when called like this, find out why
                    context.scene.uvp2_props.normalize_islands = False
                    context.scene.uvp2_props.lock_overlapping_mode = ('0' if
                                                                      layer == 'CATS UV Super' else
                                                                      '2')
                    context.scene.uvp2_props.pack_to_others = False
                    context.scene.uvp2_props.margin = margin
                    context.scene.uvp2_props.similarity_threshold = 3
                    context.scene.uvp2_props.precision = 1000
                    # Give UVP a static number of iterations to do TODO: make this configurable?
                    for _ in range(1, 3):
                        bpy.ops.uvpackmaster2.uv_pack()
                except AttributeError:
                    bpy.ops.uv.pack_islands(rotate=True, margin=margin)
                    pass
                Common.switch('OBJECT')

            if optimize_solid_materials:
                #unhide geometry from step before pack islands that fixed solid material uvs, then scale uv's to be short enough to avoid color squares at top right. - @989onan

                last_index = len(solidmaterialnames)

                # Thanks to @Sacred#9619 on discord for this one.
                squaremargin = pixelmargin
                n = resolution // squaremargin
                y = squaremargin / 2 + squaremargin * last_index // n

                y_scale_amount = 1-((y+(pixelmargin+squaremargin))/resolution)

                for child in collection.all_objects:
                    if child.type == "MESH":
                        poly_material_indices = np.empty(len(child.data.polygons), dtype=np.ushort)
                        child.data.polygons.foreach_get('material_index', poly_material_indices)
                        poly_loop_totals = np.empty(len(child.data.polygons), dtype=np.uintc)
                        child.data.polygons.foreach_get('loop_total', poly_loop_totals)
                        poly_hide = np.empty(len(child.data.polygons), dtype=bool)
                        child.data.polygons.foreach_get('hide', poly_hide)

                        visible_polygons = np.invert(poly_hide, out=poly_hide)
                        uvs_of_visible_polygons = np.repeat(visible_polygons, poly_loop_totals)
                        for layer in cats_uv_layers:
                            # get all polygons that aren't hidden
                            # use polygon loop totals with np.repeat to choose the uvs we want from the non-hidden polygons
                            # scale the uvs
                            # Unhide the mesh (we should only have to unhide polygons since that's the only thing we hid
                            # earlier?)
                            # Select all the uvs in each uv layer
                            # Select all the polygons, vertices and edges
                            # Only get the material indices at most once per object

                            uv_layer_data = child.data.uv_layers[layer].data
                            uvs = np.empty(len(uv_layer_data) * 2, dtype=np.single)
                            uv_layer_data.foreach_get('uv', uvs)
                            # Slice to get a view of only y coordinates
                            uvs_y = uvs[1::2]

                            # https://blender.stackexchange.com/a/75095
                            # Scale a 2D vector v, considering a scale s and a pivot point p
                            # scale y by y_scale_amount about y=1
                            uvs_y[uvs_of_visible_polygons] = uvs_y[uvs_of_visible_polygons] * y_scale_amount + (1 - y_scale_amount)

                            uv_layer_data.foreach_set('uv', uvs)
                            del uvs_y
                            del uvs

                        #unhide all mesh polygons from our material hiding for scaling
                        unhide_all = np.zeros(len(child.data.polygons), dtype=bool)
                        child.data.polygons.foreach_set('hide', unhide_all)
                        # TODO: Do we still need to select all of the mesh and select all of the uvs?
                        # lastly make our target UV map active
                        child.data.uv_layers.active = child.data.uv_layers["CATS UV"]
                        del unhide_all
                        del uvs_of_visible_polygons
                        del visible_polygons
                        del poly_hide
                        del poly_loop_totals
                        del poly_material_indices
            else:
                # even if we didn't optimise solid materials, we still need to make our target UV map active
                for obj in collection.all_objects:
                    if obj.type == 'MESH':
                        obj.data.uv_layers.active = obj.data.uv_layers["CATS UV"]

        if not os.path.exists(bpy.path.abspath("//CATS Bake/")):
            os.mkdir(bpy.path.abspath("//CATS Bake/"))

        # Gather settings for each bake pass
        white_bg = (1.0, 1.0, 1.0, 1.0)
        gray_bg = (0.5, 0.5, 0.5, 1.0)
        black_bg = (0.0, 0.0, 0.0, 1.0)
        world_normal_bg = (0.0, 0.0, 1.0, 1.0)
        tangent_normal_bg = (0.5, 0.5, 1.0, 1.0)
        if context.scene.bake_samples_quality == 'CUSTOM':
            advanced_samples = context.scene.bake_advanced_samples
            diffuse_samples = advanced_samples.diffuse
            smoothness_samples = advanced_samples.smoothness
            alpha_samples = advanced_samples.alpha
            metallic_samples = advanced_samples.metallic
            world_normal_samples = advanced_samples.normal_world
            tangent_normal_samples = advanced_samples.normal_tangent
            ao_samples = advanced_samples.ao
            emit_samples = advanced_samples.emit
            emit_indirect_samples = advanced_samples.emit_indirect
            emit_indirect_eyes_samples = advanced_samples.emit_indirect_eyes
            vertex_diffuse_samples = advanced_samples.vertex_diffuse
        else:
            # AO, particularly without denoising, often ends up rather speckled all over without at least a few samples
            ao_samples = self.scale_samples_by_quality(context, samples=512, minimum=4)
            emit_indirect_samples = self.scale_samples_by_quality(context, samples=512)
            world_normal_samples = tangent_normal_samples = self.scale_samples_by_quality(context, samples=128)
            diffuse_samples = smoothness_samples = alpha_samples = metallic_samples = emit_samples = \
                emit_indirect_eyes_samples = vertex_diffuse_samples = self.scale_samples_by_quality(context, samples=32)

        world_normal_resolution = resolution * 2 if supersample_normals else resolution

        diffuse_settings = BakePassSettings(
            "diffuse", "DIFFUSE", resolution, diffuse_samples, gray_bg, pixelmargin, filter={"COLOR"},
            solid_material_colors=solidmaterialcolors)
        smoothness_settings = BakePassSettings(
            "smoothness", "ROUGHNESS", resolution, smoothness_samples, white_bg, pixelmargin,
            solid_material_colors=solidmaterialcolors)
        alpha_settings = BakePassSettings(
            "alpha", "ROUGHNESS", resolution, alpha_samples, white_bg, pixelmargin)
        metallic_settings = BakePassSettings(
            "metallic", "ROUGHNESS", resolution, metallic_samples, black_bg, pixelmargin,
            solid_material_colors=solidmaterialcolors)
        world_normal_settings = BakePassSettings(
            "world", "NORMAL", world_normal_resolution, world_normal_samples, world_normal_bg, pixelmargin, normal_space="OBJECT",
            solid_material_colors=solidmaterialcolors)
        ao_settings = BakePassSettings(
            "ao", "AO", resolution, ao_samples, white_bg, pixelmargin, filter={"AO"})
        emit_no_indirect_settings = BakePassSettings(
            "emission", "EMIT", resolution, emit_samples, black_bg, pixelmargin)
        emit_indirect_settings = BakePassSettings(
            "emission", "COMBINED", resolution, emit_indirect_samples, black_bg, pixelmargin,
            filter={"COLOR", "DIRECT", "INDIRECT", "EMIT", "AO", "DIFFUSE"}, solid_material_colors=solidmaterialcolors)
        emit_indirect_eyes = BakePassSettings(
            "emission", "EMIT", resolution, emit_indirect_eyes_samples, black_bg, pixelmargin, clear=False,
            solid_material_colors=solidmaterialcolors)
        tangent_normal_settings = BakePassSettings(
            "normal", "NORMAL", resolution, tangent_normal_samples, tangent_normal_bg, pixelmargin,
            solid_material_colors=solidmaterialcolors)
        vertex_diffuse_settings = BakePassSettings(
            "vertex_diffuse", "DIFFUSE", 1, vertex_diffuse_samples, gray_bg, pixelmargin, filter={"COLOR", "VERTEX_COLORS"})

        # Most bake passes use all the mesh objects in collection.all_objects
        all_mesh_objects = [obj for obj in collection.all_objects if obj.type == 'MESH']

        # Bake diffuse
        if pass_diffuse:
            # Metallic can cause issues baking diffuse, so temporarily disable it and set it to 0.0
            # Alpha causes issues baking diffuse (multiplies with the diffuse intensity), so we temporarily disable its
            # link and set its value to 1.0
            with self.temp_disable_links(all_mesh_objects, {"Alpha": 1.0, "Metallic": 0.0}):
                self.bake_pass(context, diffuse_settings, all_mesh_objects)
            bpy.data.images["SCRIPT_diffuse.png"].save()

            if sharpen_bakes:
                self.filter_image(context, "SCRIPT_diffuse.png", BakeButton.sharpen_create)

        # Bake roughness, invert
        if pass_smoothness:
            # Specularity or alpha of 0 mess up 'roughness' bakes. Fix that here.
            with self.temp_disable_links(all_mesh_objects, {"Alpha": 1.0, "Specular": 0.5}):
                self.bake_pass(context, smoothness_settings, all_mesh_objects)
            image = bpy.data.images["SCRIPT_smoothness.png"]
            pixel_buffer = get_pixel_buffer(image)
            # Set shape so each pixel is grouped into an array of [r, g, b, a]
            pixel_buffer.shape = (-1, 4)
            # 2D Slice to view only the first 3 columns (rgb)
            pixel_buffer_rgb_view = pixel_buffer[:, :3]
            # Invert (one minus) all the rgb values and write the updated values back to itself
            np.subtract(1.0, pixel_buffer_rgb_view, out=pixel_buffer_rgb_view)
            # Set shape back to flat
            pixel_buffer.shape = -1
            # Set the updated pixels from the buffer
            image.pixels.foreach_set(pixel_buffer)
            if sharpen_bakes:
                self.filter_image(context, "SCRIPT_smoothness.png", BakeButton.sharpen_create, use_linear=True)
            del pixel_buffer_rgb_view
            del pixel_buffer

        # advanced: bake alpha from bsdf output
        if pass_alpha:
            # We're baking alpha via a roughness bake
            self.swap_links(all_mesh_objects, "Alpha", "Roughness")
            # Specularity or alpha of 0 mess up 'roughness' bakes. Fix that here.
            with self.temp_disable_links(all_mesh_objects, {"Alpha": 1.0, "Metallic": 0.0, "Specular": 0.5}):
                # Run the bake pass (bake roughness)
                self.bake_pass(context, alpha_settings, all_mesh_objects)

            # Revert the changes (re-flip)
            self.swap_links(all_mesh_objects, "Alpha", "Roughness")

        # advanced: bake metallic from last bsdf output
        if pass_metallic:
            # Find all Principled BSDF nodes. Flip Roughness and Metallic (default_value and connection)
            self.swap_links(all_mesh_objects, "Metallic", "Roughness")
            # Specularity or alpha of 0 mess up 'roughness' bakes. Fix that here.
            with self.temp_disable_links(all_mesh_objects, {"Alpha": 1.0, "Specular": 0.5}):
                # Run the bake pass
                self.bake_pass(context, metallic_settings, all_mesh_objects)

            # Revert the changes (re-flip)
            self.swap_links(all_mesh_objects, "Metallic", "Roughness")
            if sharpen_bakes:
                self.filter_image(context, "SCRIPT_metallic.png", BakeButton.sharpen_create)

        # TODO: advanced: bake detail mask from diffuse node setup

        # Create 'disable' shape keys, each of which shrinks their relevant mesh down to a single point
        if create_disable_shapekeys:
            # Iterate over all the mesh objects except the one with the most vertices
            for obj in sorted(all_mesh_objects, key=lambda o: len(o.data.vertices))[:-1]:
                print(obj.name)

                # If there aren't any shape keys, we need to add a Basis shape key first
                if obj.data.shape_keys is None or len(obj.data.shape_keys.key_blocks) == 0:
                    obj.shape_key_add(name="Basis")

                # Add a new shape key for disabling the object
                disable_shape = obj.shape_key_add(name="Disable " + obj.name[:-4], from_mix=True)

                # Get the flattened vertex positions
                disable_shape_cos = np.empty(len(disable_shape.data) * 3, dtype=np.single)
                disable_shape.data.foreach_get('co', disable_shape_cos)
                # Reshape into an array of [x, y, z] sub-arrays
                disable_shape_cos.shape = (-1, 3)

                # Calculate bounding box center
                # Find the min and max of each column
                min_xyz = np.amin(disable_shape_cos, axis=0)
                max_xyz = np.amax(disable_shape_cos, axis=0)

                # Bounding box center will be the mean average
                bounding_box_center = (min_xyz + max_xyz) * 0.5

                # An alternative would be to shrink to the mean point of the vertices
                # mean_point = np.mean(disable_shape_cos, axis=0)

                # Set all co to the bounding box center
                disable_shape_cos[:] = bounding_box_center

                # Re-flatten the vertex positions
                disable_shape_cos.shape = -1

                # Set the update cos for the disable shape key
                disable_shape.data.foreach_set('co', disable_shape_cos)
                del disable_shape_cos

        # Save the current values and disable (set value to zero) the shape keys of each mesh that we don't want to bake
        # into the Basis shapekey of the mesh they belong to
        # If apply_keys is True, all shape keys are applied to the Basis at their current values, so there's no need to
        # save their values
        # If apply_keys is False only shape keys ending in '_bake' are applied to the Basis at their current values, so
        # other shape keys need to have their values saved and be temporarily disabled
        shapekey_values = dict()
        if not apply_keys:
            for obj in all_mesh_objects:
                if Common.has_shapekeys(obj):
                    # Different meshes could have shape keys with the same names, so we need a sub-dict for each mesh
                    dict_for_mesh = shapekey_values.setdefault(obj.name, {})
                    # This doesn't work for keys which have different starting
                    # values... but generally that's not what you should do anyway
                    for key in obj.data.shape_keys.key_blocks:
                        # Always ignore '_bake' keys so they're baked in
                        if key.name[-5:] != '_bake':
                            dict_for_mesh[key.name] = key.value
                            key.value = 0.0

        # Bake all the shape keys
        # Apply current shape key mix and then disable all shape keys, otherwise normals bake weird
        for obj in all_mesh_objects:
            if Common.has_shapekeys(obj):
                # Add a new shape key from the current mix
                obj.shape_key_add(from_mix=True)
                # The new shape key will be the last index, set it as active so we can apply it to the basis
                obj.active_shape_key_index = len(obj.data.shape_keys.key_blocks) - 1
                # Create context override for shape_key_to_basis
                override_context = {'object': obj}
                # Apply the new mix shape key to basis
                bpy.ops.cats_shapekey.shape_key_to_basis(override_context)
                # Set the active shape key to the basis
                obj.active_shape_key_index = 0
                # Ensure all keys are now set to 0.0
                for key in obj.data.shape_keys.key_blocks:
                    key.value = 0.0

        # Joining meshes causes issues with materials. Instead. apply location for all meshes, so object and world space are the same
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        # Select all of our meshes
        for obj in all_mesh_objects:
            obj.select_set(True)
        # Apply transforms for all the objects we selected
        bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

        # Bake normals in object coordinates
        if pass_normal:
            if generate_uvmap:
                for obj in all_mesh_objects:
                    if supersample_normals:
                        obj.data.uv_layers.active = obj.data.uv_layers["CATS UV Super"]
                    else:
                        obj.data.uv_layers.active = obj.data.uv_layers["CATS UV"]
            self.bake_pass(context, world_normal_settings, all_mesh_objects)

        # Reset UV
        if generate_uvmap and supersample_normals:
            for obj in all_mesh_objects:
                obj.data.uv_layers.active = obj.data.uv_layers["CATS UV"]

        # Bake AO
        if pass_ao:
            for obj in collection.all_objects:
                if Common.has_shapekeys(obj):
                    for key in obj.data.shape_keys.key_blocks:
                        if ('ambient' in key.name.lower() and 'occlusion' in key.name.lower()) or key.name[-3:] == '_ao':
                            key.value = 1.0
            if illuminate_eyes:
                # Add modifiers that prevent LeftEye and RightEye being baked
                for obj in all_mesh_objects:
                    if "LeftEye" in obj.vertex_groups:
                        leyemask = obj.modifiers.new(type='MASK', name="leyemask")
                        leyemask.mode = "VERTEX_GROUP"
                        leyemask.vertex_group = "LeftEye"
                        leyemask.invert_vertex_group = True
                    if "RightEye" in obj.vertex_groups:
                        reyemask = obj.modifiers.new(type='MASK', name="reyemask")
                        reyemask.mode = "VERTEX_GROUP"
                        reyemask.vertex_group = "RightEye"
                        reyemask.invert_vertex_group = True
            self.bake_pass(context, ao_settings, all_mesh_objects)
            if illuminate_eyes:
                for obj in all_mesh_objects:
                    if "leyemask" in obj.modifiers:
                        obj.modifiers.remove(obj.modifiers['leyemask'])
                    if "reyemask" in obj.modifiers:
                        obj.modifiers.remove(obj.modifiers['reyemask'])

            for obj in collection.all_objects:
                if Common.has_shapekeys(obj):
                    for key in obj.data.shape_keys.key_blocks:
                        if ('ambient' in key.name.lower() and 'occlusion' in key.name.lower()) or key.name[-3:] == '_ao':
                            key.value = 0.0
            if denoise_bakes:
                self.filter_image(context, "SCRIPT_ao.png", BakeButton.denoise_create)

        # bake emit
        if pass_emit:
            if not emit_indirect:
                self.bake_pass(context, emit_no_indirect_settings, all_mesh_objects)
            else:
                # Bake indirect lighting contributions: Turn off the lights and bake all diffuse passes
                # TODO: disable scene lights?
                for obj in collection.all_objects:
                    if Common.has_shapekeys(obj):
                        for key in obj.data.shape_keys.key_blocks:
                            if ('ambient' in key.name.lower() and 'occlusion' in key.name.lower()) or key.name[-3:] == '_ao':
                                key.value = 1.0
                original_color = bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value
                bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0,0,0,1)
                self.bake_pass(context, emit_indirect_settings, all_mesh_objects)
                if emit_exclude_eyes:
                    def group_relevant(obj, groupname):
                        if groupname in obj.vertex_groups:
                            idx = obj.vertex_groups[groupname].index
                            return any( any(group.group == idx and group.weight > 0.0 for group in vert.groups)
                                    for vert in obj.data.vertices)

                    # Bake each eye on top individually
                    for obj in all_mesh_objects:
                        if group_relevant(obj, "LeftEye"):
                            leyemask = obj.modifiers.new(type='MASK', name="leyemask")
                            leyemask.mode = "VERTEX_GROUP"
                            leyemask.vertex_group = "LeftEye"
                            leyemask.invert_vertex_group = False
                    left_eye_relevant_meshes = [obj for obj in all_mesh_objects if group_relevant(obj, "LeftEye")]
                    self.bake_pass(context, emit_indirect_eyes, left_eye_relevant_meshes)
                    for obj in all_mesh_objects:
                        if "leyemask" in obj.modifiers:
                            obj.modifiers.remove(obj.modifiers["leyemask"])

                    for obj in all_mesh_objects:
                        if group_relevant(obj, "RightEye"):
                            reyemask = obj.modifiers.new(type='MASK', name="reyemask")
                            reyemask.mode = "VERTEX_GROUP"
                            reyemask.vertex_group = "RightEye"
                            reyemask.invert_vertex_group = False
                    right_eye_relevant_meshes = [obj for obj in all_mesh_objects if group_relevant(obj, "RightEye")]
                    self.bake_pass(context, emit_indirect_eyes, right_eye_relevant_meshes)
                    for obj in all_mesh_objects:
                        if "reyemask" in obj.modifiers:
                            obj.modifiers.remove(obj.modifiers["reyemask"])

                bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = original_color
                if denoise_bakes:
                    self.filter_image(context, "SCRIPT_emission.png", BakeButton.denoise_create)
                for obj in collection.all_objects:
                    if Common.has_shapekeys(obj):
                        for key in obj.data.shape_keys.key_blocks:
                            if ('ambient' in key.name.lower() and 'occlusion' in key.name.lower()) or key.name[-3:] == '_ao':
                                key.value = 0.0

        # Remove multires modifiers
        for obj in collection.all_objects:
            mods = []
            for mod in obj.modifiers:
                if mod.type == "MULTIRES":
                    mods.append(mod.name)
            for mod in mods:
                obj.modifiers.remove(obj.modifiers[mod])

        # Apply any masking modifiers before decimation
        print("Applying mask modifiers")
        for obj in collection.all_objects:
            if not any(mod.type == "MASK" and mod.show_viewport for mod in obj.modifiers):
                continue
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = obj

            vgroup_idxes = set([obj.vertex_groups[mod.vertex_group].index for mod in obj.modifiers
                            if mod.show_viewport and mod.type == 'MASK'])
            for group in vgroup_idxes:
                print("Deleting vertices from {} on obj {}".format(group, obj.name))
            Common.switch("EDIT")
            bpy.ops.mesh.select_all(action='DESELECT')
            Common.switch("OBJECT")
            for vert in obj.data.vertices:
                vert.select = any(group.group in vgroup_idxes and group.weight > 0.0 for group in vert.groups)

            Common.switch("EDIT")
            bpy.ops.mesh.delete(type="VERT")
        Common.switch("OBJECT")

        ########### BEGIN PLATFORM SPECIFIC CODE ###########
        for platform_number, platform in enumerate(context.scene.bake_platforms):
            image_extension = ""
            if platform.image_export_format == "TGA":
                image_extension = ".tga"
            elif platform.image_export_format == "PNG":
                image_extension = ".png"

            def platform_img(img_pass):
                return platform_name + " " + img_pass + image_extension
            def sanitized_name(orig_name):
                #sanitizing name since everything needs to be simple characters and "_"'s
                sanitized = ""
                for i in orig_name.lower():
                    if i.isalnum() or i == "_":
                        sanitized += i
                    else:
                        sanitized += "_"
                return sanitized.replace("_tga", ".tga")

            platform_name = platform.name
            merge_twistbones = platform.merge_twistbones
            diffuse_alpha_pack = platform.diffuse_alpha_pack
            metallic_alpha_pack = platform.metallic_alpha_pack
            diffuse_premultiply_ao = platform.diffuse_premultiply_ao
            diffuse_premultiply_opacity = platform.diffuse_premultiply_opacity
            smoothness_premultiply_ao = platform.smoothness_premultiply_ao
            smoothness_premultiply_opacity = platform.smoothness_premultiply_opacity
            use_decimation = platform.use_decimation
            optimize_static = platform.optimize_static
            preserve_seams = platform.preserve_seams
            diffuse_vertex_colors = platform.diffuse_vertex_colors
            translate_bone_names = platform.translate_bone_names
            export_format = platform.export_format
            specular_setup = platform.specular_setup
            phong_setup = platform.phong_setup
            specular_alpha_pack = platform.specular_alpha_pack
            specular_smoothness_overlay = platform.specular_smoothness_overlay
            normal_alpha_pack = platform.normal_alpha_pack
            normal_invert_g = platform.normal_invert_g
            diffuse_emit_overlay = platform.diffuse_emit_overlay
            use_physmodel = platform.use_physmodel
            physmodel_lod = platform.physmodel_lod
            use_lods = platform.use_lods
            lods = platform.lods

            # For GMOD
            gmod_model_name = platform.gmod_model_name
            sanitized_platform_name = sanitized_name(platform_name)
            sanitized_model_name = sanitized_name(gmod_model_name)
            vmtfile = "\"VertexlitGeneric\"\n{\n    \"$surfaceprop\" \"Flesh\""
            images_path = steam_library_path+"steamapps/common/GarrysMod/garrysmod/"
            target_dir = steam_library_path+"steamapps/common/GarrysMod/garrysmod/addons/"+sanitized_model_name+"_playermodel/materials/models/"+sanitized_model_name
            if export_format == "GMOD":
                os.makedirs(target_dir, 0o777, True)

            generate_prop_bones = platform.generate_prop_bones
            generate_prop_bone_max_influence_count = platform.generate_prop_bone_max_influence_count
            generate_prop_bone_max_overall = 75 # platform-specific?

            if not os.path.exists(bpy.path.abspath("//CATS Bake/" + platform_name + "/")):
                os.mkdir(bpy.path.abspath("//CATS Bake/" + platform_name + "/"))

            # for cleanliness create platform-specific copies here
            for (bakepass, bakename) in [
                (pass_diffuse, 'diffuse'),
                (pass_normal, 'normal'),
                (pass_smoothness, 'smoothness'),
                (pass_ao, 'ao'),
                (pass_emit, 'emission'),
                (pass_alpha, 'alpha'),
                (pass_metallic, 'metallic'),
                (specular_setup, 'specular'),
                (phong_setup, 'phong')
            ]:
                if not bakepass:
                    continue
                if platform_img(bakename) in bpy.data.images:
                    image = bpy.data.images[platform_img(bakename)]
                    image.user_clear()
                    bpy.data.images.remove(image)
                bpy.ops.image.new(name=platform_img(bakename), width=resolution, height=resolution,
                                  generated_type="BLANK", alpha=False)
                image = bpy.data.images[platform_img(bakename)]
                if export_format != "GMOD":
                    image.filepath = bpy.path.abspath("//CATS Bake/" + platform_name + "/" + platform_img(bakename))
                else:
                    image.filepath = bpy.path.abspath("//CATS Bake/" + platform_name + "/" + sanitized_name(platform_img(bakename)))
                image.generated_width = resolution
                image.generated_height = resolution
                image.scale(resolution, resolution)
                # already completed passes
                if bakename not in ["specular", "normal", "phong"]:
                    orig_image = bpy.data.images["SCRIPT_" + bakename+'.png']
                    pixel_buffer = get_pixel_buffer(orig_image)
                    image.pixels.foreach_set(pixel_buffer)
                    del pixel_buffer


            # Create yet another output collection
            plat_collection = bpy.data.collections.new("CATS Bake " + platform_name)
            #context.scene.collection.children.link(plat_collection)
            orig_scene.collection.children.link(plat_collection)

            # Tree-copy all meshes
            plat_arm_copy = self.tree_copy(arm_copy, None, plat_collection, ignore_hidden)

            # Create an extra scene to render in
            plat_orig_scene_name = "CATS Scene"
            bpy.ops.scene.new(type="EMPTY") # copy keeps existing settings
            context.scene.name = "CATS Scene " + platform_name
            plat_orig_scene = bpy.data.scenes[orig_scene_name]
            context.scene.collection.children.link(plat_collection)

            # Make sure all armature modifiers target the new armature
            for child in plat_collection.all_objects:
                for modifier in child.modifiers:
                    if modifier.type == "ARMATURE":
                        modifier.object = plat_arm_copy
                    if modifier.type == "MULTIRES":
                        modifier.render_levels = modifier.total_levels

            # Optionally cleanup bones if we're not going to use them
            if merge_twistbones:
                print("merging bones")
                bpy.ops.object.select_all(action='DESELECT')
                context.view_layer.objects.active = plat_arm_copy
                Common.switch("EDIT")
                bpy.ops.armature.select_all(action="DESELECT")
                bone_children = dict()
                for editbone in context.visible_bones:
                    if not editbone.parent:
                        continue
                    if not editbone.parent.name in bone_children:
                        bone_children[editbone.parent.name] = []
                    bone_children[editbone.parent.name].append(editbone.name)
                for editbone in context.visible_bones:
                    if 'twist' in editbone.name.lower() and not editbone.children:
                        editbone.select = True
                        if editbone.parent:
                            # only select if bone is alphabetically after all non-twistbones. Prevents hierarchy problems
                            if any(otherbone > editbone.name for otherbone in bone_children[editbone.parent.name]
                                   if not 'twist' in otherbone.lower()):
                                editbone.select = False
                if context.selected_editable_bones:
                    bpy.ops.cats_manual.merge_weights()
                Common.switch("OBJECT")

            if generate_prop_bones:
                # Find any mesh that's weighted to a single bone, duplicate and rename that bone, move mesh's vertex group to the new bone
                for obj in plat_collection.objects:
                    if obj.type == "MESH":
                        orig_obj_name = obj.name[:-4] if obj.name[-4] == '.' else obj.name
                        found_vertex_groups = set()
                        path_strings = []
                        for vertex in obj.data.vertices:
                            found_vertex_groups |= set([vgp.group for vgp in vertex.groups if vgp.weight > 0.00001])

                        generate_bones = found_vertex_groups and len(found_vertex_groups) <= generate_prop_bone_max_influence_count
                        if 'generatePropBones' in obj:
                            generate_bones = obj['generatePropBones']
                        if generate_bones:
                            vgroup_lookup = dict([(vgp.index, vgp.name) for vgp in obj.vertex_groups])
                            for vgp in found_vertex_groups:
                                vgroup_name = vgroup_lookup[vgp]
                                #if not plat_arm_copy.data.bones[vgroup_name].children:
                                #    #TODO: this doesn't account for props attached to something which has existing attachments
                                #    Common.switch("OBJECT")
                                #    print("Object " + obj.name + " already has no children, skipping")
                                #    continue

                                print("Object " + obj.name + " is an eligible prop on " + vgroup_name + "! Creating prop bone...")
                                # If the obj has ".001" or similar, trim it
                                newbonename = "~" + vgroup_name + "_Prop_" + orig_obj_name
                                obj.vertex_groups[vgroup_name].name = newbonename
                                context.view_layer.objects.active = plat_arm_copy
                                Common.switch("EDIT")
                                orig_bone = plat_arm_copy.data.edit_bones[vgroup_name]
                                prop_bone = plat_arm_copy.data.edit_bones.new(newbonename)
                                prop_bone.head = orig_bone.head
                                prop_bone.tail[:] = [(orig_bone.head[i] + orig_bone.tail[i]) / 2 for i in range(3)]
                                prop_bone.parent = orig_bone
                                # To create en/disable animation files
                                next_bone = prop_bone.parent
                                path_string = prop_bone.name
                                while next_bone != None:
                                    path_string = next_bone.name + "/" + path_string
                                    next_bone = next_bone.parent
                                path_string = "Armature/" + path_string
                                path_strings.append(path_string)
                                Common.switch("OBJECT")

                        # A bit of a hacky string manipulation, just create a curve for each bone based on the editor path. Output file is YAML
                        # {EDITOR_VALUE} = 1
                        # {SCALE_VALUE} = {x: 1, y: 1, z: 1}
                        with open(os.path.dirname(os.path.abspath(__file__)) + "/../extern_tools/enable.anim", 'r') as infile:
                            newname = "Enable " + orig_obj_name
                            editor_curves = ""
                            scale_curves = ""
                            for path_string in path_strings:
                                with open(os.path.dirname(os.path.abspath(__file__)) + "/../extern_tools/m_ScaleCurves.anim.part", 'r') as infilepart:
                                    scale_curves += "".join([line.replace("{PATH_STRING}", path_string).replace("{SCALE_VALUE}", "{x: 1, y: 1, z: 1}") for line in infilepart])
                                with open(os.path.dirname(os.path.abspath(__file__)) + "/../extern_tools/m_EditorCurves.anim.part", 'r') as infilepart:
                                    editor_curves += "".join([line.replace("{PATH_STRING}", path_string).replace("{EDITOR_VALUE}", "1") for line in infilepart])

                            with open(bpy.path.abspath("//CATS Bake/") + newname + ".anim", 'w') as outfile:
                                for line in infile:
                                    outfile.write(line.replace("{NAME_STRING}", newname).replace("{EDITOR_CURVES}", editor_curves).replace("{SCALE_CURVES}", scale_curves))
                        with open(os.path.dirname(os.path.abspath(__file__)) + "/../extern_tools/disable.anim", 'r') as infile:
                            newname = "Disable " + orig_obj_name
                            editor_curves = ""
                            scale_curves = ""
                            for path_string in path_strings:
                                with open(os.path.dirname(os.path.abspath(__file__)) + "/../extern_tools/m_ScaleCurves.anim.part", 'r') as infilepart:
                                    scale_curves += "".join([line.replace("{PATH_STRING}", path_string).replace("{SCALE_VALUE}", "{x: 0, y: 0, z: 0}") for line in infilepart])
                                with open(os.path.dirname(os.path.abspath(__file__)) + "/../extern_tools/m_EditorCurves.anim.part", 'r') as infilepart:
                                    editor_curves += "".join([line.replace("{PATH_STRING}", path_string).replace("{EDITOR_VALUE}", "0") for line in infilepart])

                            with open(bpy.path.abspath("//CATS Bake/") + newname + ".anim", 'w') as outfile:
                                for line in infile:
                                    outfile.write(line.replace("{NAME_STRING}", newname).replace("{EDITOR_CURVES}", editor_curves).replace("{SCALE_CURVES}", scale_curves))

            if translate_bone_names == "SECONDLIFE":
                bpy.ops.cats_manual.convert_to_secondlife()

            # Blend diffuse and AO to create Quest Diffuse (if selected)
            # Overlay emission onto diffuse, dodge metallic if specular
            if pass_diffuse:
                image = bpy.data.images[platform_img("diffuse")]
                diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
                pixel_buffer = get_pixel_buffer(diffuse_image)
                pixel_buffer.shape = (-1, 4)
                pixel_buffer_rgb_view = pixel_buffer[:, :3]
                if pass_ao and diffuse_premultiply_ao:
                    ao_image = bpy.data.images["SCRIPT_ao.png"]
                    ao_buffer = get_pixel_buffer(ao_image)
                    ao_buffer.shape = (-1, 4)
                    ao_buffer_rgb_view = ao_buffer[:, :3]
                    # Map range: set the black point up to 1-opacity
                    # pixel_rgb = pixel_rgb * ((1.0 - diffuse_premultiply_opacity) + (diffuse_premultiply_opacity * ao_rgb))
                    #
                    # ao_rgb *= diffuse_premultiply_opacity
                    np.multiply(diffuse_premultiply_opacity, ao_buffer_rgb_view, out=ao_buffer_rgb_view)
                    # ao_rgb += 1.0 - diffuse_premultiply_opacity
                    np.add(1.0 - diffuse_premultiply_opacity, ao_buffer_rgb_view, out=ao_buffer_rgb_view)
                    # pixel_rgb *= ao_rgb
                    np.multiply(pixel_buffer_rgb_view, ao_buffer_rgb_view, out=pixel_buffer_rgb_view)
                    del ao_buffer_rgb_view
                    del ao_buffer
                if specular_setup and pass_metallic:
                    metallic_image = bpy.data.images["SCRIPT_metallic.png"]
                    metallic_buffer = get_pixel_buffer(metallic_image)
                    metallic_buffer.shape = (-1, 4)
                    metallic_buffer_rgb_view = metallic_buffer[:, :3]
                    # Map range: metallic blocks diffuse light
                    # pixel_rgb = pixel_rgb * (1 - metallic_rgb)
                    #
                    # metallic_rgb = 1 - metallic_rgb
                    np.subtract(1, metallic_buffer_rgb_view, out=metallic_buffer_rgb_view)
                    # pixel_rgb *= metallic_rgb
                    np.multiply(pixel_buffer_rgb_view, metallic_buffer_rgb_view, out=pixel_buffer_rgb_view)
                    del metallic_buffer_rgb_view
                    del metallic_buffer
                if pass_emit and diffuse_emit_overlay:
                    emit_image = bpy.data.images["SCRIPT_emission.png"]
                    emit_buffer = get_pixel_buffer(emit_image)
                    emit_buffer.shape = (-1, 4)
                    emit_buffer_rgb_view = emit_buffer[:, :3]
                    # Map range: screen the emission onto diffuse
                    # pixel_rgb = 1.0 - (1.0 - emit_rgb) * (1.0 - pixel_rgb)
                    #
                    # emit_rgb = 1.0 - emit_rgb
                    np.subtract(1.0, emit_buffer_rgb_view, out=emit_buffer_rgb_view)
                    # pixel_rgb = 1.0 - pixel_rgb
                    np.subtract(1.0, pixel_buffer_rgb_view, out=pixel_buffer_rgb_view)
                    # emit_rgb *= pixel_rgb
                    np.multiply(emit_buffer_rgb_view, pixel_buffer_rgb_view, out=emit_buffer_rgb_view)
                    # pixel_rgb = 1.0 - emit_rgb
                    np.subtract(1.0, emit_buffer_rgb_view, out=pixel_buffer_rgb_view)
                    del emit_buffer_rgb_view
                    del emit_buffer

                vmtfile += "\n    \"$basetexture\" \"models/"+sanitized_model_name+"/"+sanitized_name(image.name).replace(".tga","")+"\""
                pixel_buffer.shape = -1
                image.pixels.foreach_set(pixel_buffer)
                image.save()
                del pixel_buffer_rgb_view
                del pixel_buffer

            # Preultiply AO into smoothness if selected, to avoid shine in dark areas
            if pass_smoothness and pass_ao and smoothness_premultiply_ao:
                image = bpy.data.images[platform_img("smoothness")]
                smoothness_image = bpy.data.images["SCRIPT_smoothness.png"]
                ao_image = bpy.data.images["SCRIPT_ao.png"]
                pixel_buffer = get_pixel_buffer(image)
                smoothness_buffer = get_pixel_buffer(smoothness_image)
                ao_buffer = get_pixel_buffer(ao_image)

                # Alpha is unused on quest, set to 1 to make sure unity doesn't keep it
                pixel_buffer[3::4] = 1.0

                pixel_buffer.shape = (-1, 4)
                smoothness_buffer.shape = (-1, 4)
                ao_buffer.shape = (-1, 4)
                pixel_buffer_rgb_view = pixel_buffer[:, :3]
                smoothness_buffer_rgb_view = smoothness_buffer[:, :3]
                ao_buffer_rgb_view = ao_buffer[:, :3]

                # Map range: set the black point up to 1-opacity
                # pixel_rgb = smoothness_rgb * (1.0 - smoothness_premultiply_opacity + smoothness_premultiply_opacity * ao_buffer_rgb)
                #           = smoothness_rgb * (smoothness_premultiply_opacity * ao_buffer_rgb + 1.0 - smoothness_premultiply_opacity)
                # ao_buffer_rgb *= smoothness_premultiply_opacity
                np.multiply(ao_buffer_rgb_view, smoothness_premultiply_opacity, out=ao_buffer_rgb_view)
                # ao_buffer_rgb += 1.0 - smoothness_premultiply_opacity
                np.add(ao_buffer_rgb_view, 1.0 - smoothness_premultiply_opacity, out=ao_buffer_rgb_view)
                # pixel_rgb = smoothness_rgb * ao_buffer_rgb
                np.multiply(smoothness_buffer_rgb_view, ao_buffer_rgb_view, out=pixel_buffer_rgb_view)

                pixel_buffer.shape = -1
                image.pixels.foreach_set(pixel_buffer)
                del ao_buffer_rgb_view
                del smoothness_buffer_rgb_view
                del pixel_buffer_rgb_view
                del ao_buffer
                del smoothness_buffer
                del pixel_buffer

            # Pack to diffuse alpha (if selected)
            if pass_diffuse and ((diffuse_alpha_pack == "SMOOTHNESS" and pass_smoothness) or
                                 (diffuse_alpha_pack == "TRANSPARENCY" and pass_alpha) or
                                 (diffuse_alpha_pack == "EMITMASK" and pass_emit)):
                image = bpy.data.images[platform_img("diffuse")]
                print("Packing to diffuse alpha")
                alpha_image = None
                if diffuse_alpha_pack == "SMOOTHNESS":
                    alpha_image = bpy.data.images[platform_img("smoothness")]
                    vmtfile += "\n    \"$basealphaenvmapmask\" 1"
                elif diffuse_alpha_pack == "TRANSPARENCY":
                    alpha_image = bpy.data.images["SCRIPT_alpha.png"]
                    vmtfile += "\n    \"$translucent\" 1"
                elif diffuse_alpha_pack == "EMITMASK":
                    alpha_image = bpy.data.images["SCRIPT_emission.png"]
                    # "By default, $selfillum uses the alpha channel of the base texture as a mask.
                    # If the alpha channel of your base texture is used for something else, you can specify a separate $selfillummask texture."
                    # https://developer.valvesoftware.com/wiki/Glowing_Textures
                    # TODO: independent emit if transparency "\n    \"$selfillummask\" \"models/"+sanitized_model_name+"/"+baked_emissive_image.name.replace(".tga","")+"\""
                    vmtfile += "\n    \"$selfillum\" 1"
                pixel_buffer = get_pixel_buffer(image)
                alpha_buffer = get_pixel_buffer(alpha_image)
                # Set pixel_buffer alpha to alpha_buffer grayscale
                # Reshape into sub-arrays of rgba
                alpha_buffer.shape = (-1, 4)
                # 2d slice to view only the rgb columns
                alpha_buffer_rgb_view = alpha_buffer[:, :3]
                # Grayscale = 0.299r + 0.587g + 0.114b
                rgb_to_grayscale_coefficients = [0.299, 0.587, 0.114]
                # In-place multiply the rgb columns by the grayscale coefficients
                np.multiply(alpha_buffer_rgb_view, rgb_to_grayscale_coefficients, out=alpha_buffer_rgb_view)
                # Get view of only pixel_buffer alpha
                pixel_buffer_a_view = pixel_buffer[3::4]
                # sum each rgb in alpha_buffer and store the result in the alpha channel of pixel_buffer
                np.sum(alpha_buffer_rgb_view, axis=1, out=pixel_buffer_a_view)

                image.pixels.foreach_set(pixel_buffer)

                del pixel_buffer_a_view
                del alpha_buffer_rgb_view
                del alpha_buffer
                del pixel_buffer

            # Pack to metallic alpha (if selected)
            if pass_metallic and (metallic_alpha_pack == "SMOOTHNESS" and pass_smoothness):
                image = bpy.data.images[platform_img("metallic")]
                print("Packing to metallic alpha")
                metallic_image = bpy.data.images["SCRIPT_metallic.png"]
                alpha_image = bpy.data.images[platform_img("smoothness")]
                pixel_buffer = get_pixel_buffer(metallic_image)
                alpha_buffer = get_pixel_buffer(alpha_image)
                # Set pixel_buffer alpha to alpha_buffer red
                pixel_buffer[3::4] = alpha_buffer[0::4]
                image.pixels.foreach_set(pixel_buffer)

                del alpha_buffer
                del pixel_buffer

            # Create specular map
            if specular_setup:
                # TODO: Valve has their own suggested curve ramps, which are indexed above.
                # Add an an option to apply it for a more "source-ey" specular setup
                image = bpy.data.images[platform_img("specular")]
                pixel_buffer = get_pixel_buffer(image)
                # Reshape to sub-arrays of rgba
                pixel_buffer.shape = (-1, 4)
                if pass_metallic:
                    # Use the unaltered diffuse map
                    diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
                    diffuse_buffer = get_pixel_buffer(diffuse_image)
                    diffuse_buffer.shape = (-1, 4)
                    metallic_image = bpy.data.images["SCRIPT_metallic.png"]
                    metallic_buffer = get_pixel_buffer(metallic_image)
                    metallic_buffer.shape = (-1, 4)
                    pixel_buffer_rgb_view = pixel_buffer[:, :3]
                    diffuse_buffer_rgb_view = diffuse_buffer[:, :3]
                    metallic_buffer_rgb_view = metallic_buffer[:, :3]

                    # Simple specularity: most nonmetallic objects have about 4% reflectiveness
                    # pixel_rgb = diffuse_rgb * metallic_rgb + .04 * (1-metallic_rgb)
                    #
                    # pixel_rgb = diffuse_rgb * metallic_rgb
                    np.multiply(diffuse_buffer_rgb_view, metallic_buffer_rgb_view, out=pixel_buffer_rgb_view)
                    # metallic_rgb = 1 - metallic_rgb
                    np.subtract(1, metallic_buffer_rgb_view, out=metallic_buffer_rgb_view)
                    # metallic_rgb = .04 * metallic_rgb
                    np.multiply(.04, metallic_buffer_rgb_view, out=metallic_buffer_rgb_view)
                    # pixel_rgb = pixel_rgb + metallic_rgb
                    np.add(pixel_buffer_rgb_view, metallic_buffer_rgb_view, out=pixel_buffer_rgb_view)
                    del metallic_buffer_rgb_view
                    del diffuse_buffer_rgb_view
                    del pixel_buffer_rgb_view
                    del metallic_buffer
                    del diffuse_buffer
                else:
                    # Set all rgb to 0.04
                    pixel_buffer[:, :3] = 0.04
                if specular_alpha_pack == "SMOOTHNESS" and pass_smoothness:
                    alpha_image = bpy.data.images[platform_img("smoothness")]
                    alpha_image_buffer = get_pixel_buffer(alpha_image)
                    # Change pixel buffer shape back to flat
                    pixel_buffer.shape = -1
                    # Copy red channel from alpha_image_buffer to alpha channel of pixel_buffer
                    pixel_buffer[3::4] = alpha_image_buffer[0::4]
                    # Restore pixel_buffer shape back to sub-arrays of rgba
                    pixel_buffer.shape = (-1, 4)
                    del alpha_image_buffer
                # for source games, screen(specular, smoothness) to create envmapmask
                if specular_smoothness_overlay and pass_smoothness:
                    smoothness_image = bpy.data.images[platform_img("smoothness")]
                    smoothness_buffer = get_pixel_buffer(smoothness_image)
                    smoothness_buffer.shape = (-1, 4)
                    pixel_buffer_rgb_view = pixel_buffer[:, :3]
                    smoothness_buffer_rgb_view = smoothness_buffer[:, :3]
                    # pixel_buffer_rgb = pixel_buffer_rgb * smoothness_image_buffer_rgb
                    np.multiply(pixel_buffer_rgb_view, smoothness_buffer_rgb_view, out=pixel_buffer_rgb_view)
                    del smoothness_buffer_rgb_view
                    del smoothness_buffer
                pixel_buffer.shape = -1
                image.pixels.foreach_set(pixel_buffer)
                del pixel_buffer

            # Phong texture (R: smoothness, G: metallic, pack smoothness * AO to normalmap alpha as mask)
            if phong_setup and pass_smoothness:
                image = bpy.data.images[platform_img("phong")]
                pixel_buffer = get_pixel_buffer(image)
                # Use the unaltered smoothness
                smoothness_image = bpy.data.images["SCRIPT_smoothness.png"]
                smoothness_buffer = get_pixel_buffer(smoothness_image)
                # Copy red channel from smoothness_buffer to red channel of pixel_buffer
                pixel_buffer[0::4] = smoothness_buffer[0::4]

                if pass_normal:
                    # Has to be specified first!
                    vmtfile += "\n    \"$bumpmap\" \"models/"+sanitized_model_name+"/"+sanitized_name(platform_img("normal")).replace(".tga","")+"\""
                vmtfile += "\n    \"$phong\" 1"
                vmtfile += "\n    \"$phongboost\" 1.0"
                vmtfile += "\n    \"$phongfresnelranges\" \"[0 0.5 1.0\"]"
                vmtfile += "\n    \"$phongexponenttexture\" \"models/"+sanitized_model_name+"/"+sanitized_name(image.name).replace(".tga","")+"\""

                if pass_metallic:
                    # Use the unaltered metallic
                    metallic_image = bpy.data.images["SCRIPT_metallic.png"]
                    metallic_buffer = get_pixel_buffer(metallic_image, out=smoothness_buffer)
                    # Copy green channel from metallic_buffer to green channel of pixel_buffer
                    pixel_buffer[1::4] = metallic_buffer[1::4]
                    vmtfile += "\n    \"$phongalbedotint\" 1"
                    del metallic_buffer

                image.pixels.foreach_set(pixel_buffer)
                del smoothness_buffer
                del pixel_buffer

            print("Decimating")

            # Physmodel does a couple extra things like ensuring doubles are removed, wire display
            if use_physmodel:
                new_arm = self.tree_copy(plat_arm_copy, None, plat_collection, ignore_hidden, view_layer=context.view_layer)
                for obj in new_arm.children:
                    obj.display_type = "WIRE"
                context.scene.max_tris = platform.max_tris * physmodel_lod
                context.scene.decimate_fingers = False
                context.scene.decimation_remove_doubles = True
                context.scene.decimation_animation_weighting = context.scene.bake_animation_weighting
                context.scene.decimation_animation_weighting_factor = context.scene.bake_animation_weighting_factor
                bpy.ops.cats_decimation.auto_decimate(armature_name=new_arm.name, preserve_seams=False, seperate_materials=False)
                for obj in new_arm.children:
                    obj.name = "LODPhysics"
                new_arm.name = "ArmatureLODPhysics"

            if use_lods:
                for idx, lod in enumerate(lods):
                    new_arm = self.tree_copy(plat_arm_copy, None, plat_collection, ignore_hidden, view_layer=context.view_layer)
                    context.scene.max_tris = platform.max_tris * lod
                    context.scene.decimate_fingers = False
                    context.scene.decimation_remove_doubles = platform.remove_doubles
                    context.scene.decimation_animation_weighting = context.scene.bake_animation_weighting
                    context.scene.decimation_animation_weighting_factor = context.scene.bake_animation_weighting_factor
                    bpy.ops.cats_decimation.auto_decimate(armature_name=new_arm.name, preserve_seams=preserve_seams, seperate_materials=False)
                    for obj in new_arm.children:
                        obj.name = "LOD" + str(idx + 1)
                    new_arm.name = "ArmatureLOD" + str(idx + 1)

            if use_decimation:
                # Decimate. If 'preserve seams' is selected, forcibly preserve seams (seams from islands, deselect seams)
                if context.scene.bake_loop_decimate:
                    context.scene.decimation_mode = "LOOP"
                else:
                    context.scene.decimation_mode = "SMART"
                context.scene.max_tris = platform.max_tris
                context.scene.decimate_fingers = False
                context.scene.decimation_remove_doubles = platform.remove_doubles
                context.scene.decimation_animation_weighting = context.scene.bake_animation_weighting
                context.scene.decimation_animation_weighting_factor = context.scene.bake_animation_weighting_factor
                bpy.ops.cats_decimation.auto_decimate(armature_name=plat_arm_copy.name, preserve_seams=preserve_seams, seperate_materials=False)
            else:
                # join meshes here if we didn't decimate
                Common.join_meshes(armature_name=plat_arm_copy.name, repair_shape_keys=False)

            # Remove all other materials if we've done at least one bake pass
            for obj in plat_collection.all_objects:
                if obj.type == 'MESH':
                    context.view_layer.objects.active = obj
                    while len(obj.material_slots) > 0:
                        obj.active_material_index = 0  # select the top material
                        bpy.ops.object.material_slot_remove()

            # Apply generated material (object normals -> normal map -> BSDF normal and other textures)
            mat = bpy.data.materials.get("CATS Baked " + platform_name)
            if mat is not None:
                bpy.data.materials.remove(mat, do_unlink=True)
            # create material
            mat = bpy.data.materials.new(name="CATS Baked " + platform_name)
            mat.use_nodes = True
            mat.use_backface_culling = True
            # add a normal map and image texture to connect the world texture, if it exists
            tree = mat.node_tree
            bsdfnode = next(node for node in tree.nodes if node.type == "BSDF_PRINCIPLED")
            if bsdf_original is not None:
                for bsdfinput in bsdfnode.inputs:
                    bsdfinput.default_value = bsdf_original.inputs[bsdfinput.identifier].default_value
            if pass_normal:
                normaltexnode = tree.nodes.new("ShaderNodeTexImage")
                normaltexnode.image = bpy.data.images["SCRIPT_world.png"]
                # If not supersampling, sample SCRIPT_WORLD 1:1 so we don't blur it
                if not supersample_normals:
                    normaltexnode.interpolation = "Closest"
                normaltexnode.location.x -= 500
                normaltexnode.location.y -= 200

                normalmapnode = tree.nodes.new("ShaderNodeNormalMap")
                normalmapnode.space = "OBJECT"
                normalmapnode.location.x -= 200
                normalmapnode.location.y -= 200

                tree.links.new(normalmapnode.inputs["Color"], normaltexnode.outputs["Color"])
                tree.links.new(bsdfnode.inputs["Normal"], normalmapnode.outputs["Normal"])

                for obj in plat_collection.all_objects:
                    if obj.type == "MESH" and generate_uvmap:
                        if supersample_normals:
                            obj.data.uv_layers["CATS UV Super"].active_render = True
                        else:
                            obj.data.uv_layers["CATS UV"].active_render = True
            for child in plat_collection.all_objects:
                if child.type == "MESH":
                    child.data.materials.append(mat)

            if pass_normal:
                # Bake tangent normals
                self.bake_pass(context, tangent_normal_settings,
                               [obj for obj in plat_collection.all_objects if obj.type == "MESH" and not "LOD" in obj.name])
                image = bpy.data.images[platform_img("normal")]
                image.colorspace_settings.name = 'Non-Color'
                normal_image = bpy.data.images["SCRIPT_normal.png"]
                # Copy normal_image.pixels to image.pixels
                normal_buffer = get_pixel_buffer(normal_image)
                image.pixels.foreach_set(normal_buffer)
                vmtfile += "\n    \"$bumpmap\" \"models/"+sanitized_model_name+"/"+sanitized_name(image.name).replace(".tga","")+"\""
                pixel_buffer = None
                if normal_alpha_pack != "NONE":
                    print("Packing to normal alpha")
                    if normal_alpha_pack == "SPECULAR":
                        alpha_image = bpy.data.images[platform_img("specular")]
                        vmtfile += "\n    \"$normalmapalphaenvmapmask\" 1"
                        vmtfile += "\n    \"$envmap\" env_cubemap"
                    else:  # normal_alpha_pack == "SMOOTHNESS":
                        # 'There must be a Phong mask. The alpha channel of a bump map acts as a Phong mask by default.'
                        alpha_image = bpy.data.images[platform_img("smoothness")]
                    vmtfile += "\n    \"$normalmapalphaenvmapmask\" 1"
                    vmtfile += "\n    \"$envmap\" env_cubemap"
                    # Get image pixels
                    pixel_buffer = get_pixel_buffer(image, out=normal_buffer)
                    pixel_buffer_a_view = pixel_buffer[3::4]

                    # Get alpha_image pixels
                    alpha_buffer = get_pixel_buffer(alpha_image)
                    # Reshape into sub-arrays of rgba
                    alpha_buffer.shape = (-1, 4)
                    # 2d slice to view only the rgb columns
                    alpha_buffer_rgb_view = alpha_buffer[:, :3]
                    # Grayscale = 0.299r + 0.587g + 0.114b
                    rgb_to_grayscale_coefficients = [0.299, 0.587, 0.114]
                    # In-place multiply the rgb columns by the grayscale coefficients
                    np.multiply(alpha_buffer_rgb_view, rgb_to_grayscale_coefficients, out=alpha_buffer_rgb_view)

                    # sum each rgb in alpha_buffer and store the result in the alpha channel of pixel_buffer
                    np.sum(alpha_buffer_rgb_view, axis=1, out=pixel_buffer_a_view)
                    del alpha_buffer_rgb_view
                    del alpha_buffer
                    del pixel_buffer_a_view
                if normal_invert_g:
                    if pixel_buffer is None:
                        pixel_buffer = get_pixel_buffer(image, out=normal_buffer)
                    pixel_buffer_g_view = pixel_buffer[1::4]
                    np.subtract(1.0, pixel_buffer_g_view, out=pixel_buffer_g_view)
                    del pixel_buffer_g_view
                if pixel_buffer is not None:
                    # Write any modifications back to the image
                    image.pixels.foreach_set(pixel_buffer)
                del pixel_buffer
                del normal_buffer

            # Remove old UV maps (if we created new ones)
            if generate_uvmap:
                for child in plat_collection.all_objects:
                    if child.type == "MESH":
                        uv_layers = [layer.name for layer in child.data.uv_layers]
                        while uv_layers:
                            layer = uv_layers.pop()
                            if layer != "CATS UV Super" and layer != "CATS UV" and layer != "Detail Map":
                                print("Removing UV {}".format(layer))
                                child.data.uv_layers.remove(child.data.uv_layers[layer])
                for obj in plat_collection.all_objects:
                    if obj.type == 'MESH':
                        obj.data.uv_layers.active = obj.data.uv_layers["CATS UV"]

            # Re-enable keys that were disabled instead of being applied to the Basis
            if not apply_keys:
                for obj in plat_collection.all_objects:
                    if obj.name in shapekey_values:
                        values_dict = shapekey_values[obj.name]
                        for key in obj.data.shape_keys.key_blocks:
                            if key.name in values_dict:
                                key.value = values_dict[key.name]


            # Remove CATS UV Super
            if generate_uvmap and supersample_normals:
                for child in plat_collection.all_objects:
                    if child.type == "MESH":
                        uv_layers = [layer.name for layer in child.data.uv_layers]
                        while uv_layers:
                            layer = uv_layers.pop()
                            if layer == "CATS UV Super":
                                print("Removing UV {}".format(layer))
                                child.data.uv_layers.remove(child.data.uv_layers[layer])

            # Always remove existing vertex colors here
            for obj in plat_collection.all_objects:
                if obj.type == "MESH":
                    if obj.data.vertex_colors is not None and len(obj.data.vertex_colors) > 0:
                        while len(obj.data.vertex_colors) > 0:
                            context.view_layer.objects.active = obj
                            bpy.ops.mesh.vertex_color_remove()

            # Update generated material to preview all of our passes
            if pass_normal:
                normaltexnode.image = bpy.data.images[platform_img("normal")]
                normalmapnode.space = "TANGENT"
                normaltexnode.interpolation = "Linear"
            if pass_diffuse:
                diffusetexnode = tree.nodes.new("ShaderNodeTexImage")
                diffusetexnode.image = bpy.data.images[platform_img("diffuse")]
                diffusetexnode.location.x -= 300
                diffusetexnode.location.y += 500

                # If AO, blend in AO.
                if pass_ao and not diffuse_premultiply_ao:
                    # AO -> Math (* ao_opacity + (1-ao_opacity)) -> Mix (Math, diffuse) -> Color
                    aotexnode = tree.nodes.new("ShaderNodeTexImage")
                    aotexnode.image = bpy.data.images[platform_img("ao")]
                    aotexnode.location.x -= 700
                    aotexnode.location.y += 800

                    multiplytexnode = tree.nodes.new("ShaderNodeMath")
                    multiplytexnode.operation = "MULTIPLY_ADD"
                    multiplytexnode.inputs[1].default_value = diffuse_premultiply_opacity
                    multiplytexnode.inputs[2].default_value = 1.0 - diffuse_premultiply_opacity
                    multiplytexnode.location.x -= 400
                    multiplytexnode.location.y += 700
                    tree.links.new(multiplytexnode.inputs[0], aotexnode.outputs["Color"])

                    mixnode = tree.nodes.new("ShaderNodeMixRGB")
                    mixnode.blend_type = "MULTIPLY"
                    mixnode.inputs["Fac"].default_value = 1.0
                    mixnode.location.x -= 200
                    mixnode.location.y += 700
                    tree.links.new(mixnode.inputs["Color1"], multiplytexnode.outputs["Value"])
                    tree.links.new(mixnode.inputs["Color2"], diffusetexnode.outputs["Color"])

                    tree.links.new(bsdfnode.inputs["Base Color"], mixnode.outputs["Color"])
                else:
                    tree.links.new(bsdfnode.inputs["Base Color"], diffusetexnode.outputs["Color"])
            if pass_metallic:
                metallictexnode = tree.nodes.new("ShaderNodeTexImage")
                metallictexnode.image = bpy.data.images[platform_img("metallic")]
                metallictexnode.location.x -= 300
                metallictexnode.location.y += 200
                tree.links.new(bsdfnode.inputs["Metallic"], metallictexnode.outputs["Color"])
            if pass_smoothness:
                if pass_diffuse and (diffuse_alpha_pack == "SMOOTHNESS"):
                    invertnode = tree.nodes.new("ShaderNodeInvert")
                    diffusetexnode.location.x -= 200
                    invertnode.location.x -= 200
                    invertnode.location.y += 200
                    tree.links.new(invertnode.inputs["Color"], diffusetexnode.outputs["Alpha"])
                    tree.links.new(bsdfnode.inputs["Roughness"], invertnode.outputs["Color"])
                elif pass_metallic and (metallic_alpha_pack == "SMOOTHNESS"):
                    invertnode = tree.nodes.new("ShaderNodeInvert")
                    metallictexnode.location.x -= 200
                    invertnode.location.x -= 200
                    invertnode.location.y += 100
                    tree.links.new(invertnode.inputs["Color"], metallictexnode.outputs["Alpha"])
                    tree.links.new(bsdfnode.inputs["Roughness"], invertnode.outputs["Color"])
                else:
                    smoothnesstexnode = tree.nodes.new("ShaderNodeTexImage")
                    smoothnesstexnode.image = bpy.data.images[platform_img("smoothness")]
                    invertnode = tree.nodes.new("ShaderNodeInvert")
                    tree.links.new(invertnode.inputs["Color"], smoothnesstexnode.outputs["Color"])
                    tree.links.new(bsdfnode.inputs["Roughness"], invertnode.outputs["Color"])
            if pass_alpha:
                if pass_diffuse and (diffuse_alpha_pack == "TRANSPARENCY"):
                    tree.links.new(bsdfnode.inputs["Alpha"], diffusetexnode.outputs["Alpha"])
                else:
                    alphatexnode = tree.nodes.new("ShaderNodeTexImage")
                    alphatexnode.image = bpy.data.images[platform_img("alpha")]
                    tree.links.new(bsdfnode.inputs["Alpha"], alphatexnode.outputs["Color"])
                mat.blend_method = 'CLIP'
            if pass_emit:
                emittexnode = tree.nodes.new("ShaderNodeTexImage")
                emittexnode.image = bpy.data.images[platform_img("emission")]
                emittexnode.location.x -= 800
                emittexnode.location.y -= 150
                tree.links.new(bsdfnode.inputs["Emission"], emittexnode.outputs["Color"])

            # Rebake diffuse to vertex colors: Incorperates AO
            if pass_diffuse and diffuse_vertex_colors:
                plat_collection_meshes = [obj for obj in plat_collection.all_objects if obj.type == "MESH"]
                for obj in plat_collection_meshes:
                    context.view_layer.objects.active = obj
                    bpy.ops.mesh.vertex_color_add()

                with self.temp_disable_links(plat_collection_meshes, {"Alpha": 1.0, "Metallic": 0.0}):
                    self.bake_pass(context, vertex_diffuse_settings, plat_collection_meshes)

                # TODO: If we're not baking anything else in, remove all UV maps entirely

                # Update material preview
                #tree.nodes.remove(diffusetexnode)
                diffusevertnode = tree.nodes.new("ShaderNodeVertexColor")
                diffusevertnode.layer_name = "Col"
                diffusevertnode.location.x -= 300
                diffusevertnode.location.y += 500
                tree.links.new(bsdfnode.inputs["Base Color"], diffusevertnode.outputs["Color"])

            # Try to only output what you'll end up importing into unity.
            context.scene.render.image_settings.file_format = 'TARGA' if export_format == "GMOD" else 'PNG'
            context.scene.render.image_settings.color_mode = 'RGBA'
            for (bakepass, bakeconditions) in [
                ("diffuse", pass_diffuse and not diffuse_vertex_colors),
                ("smoothness", pass_smoothness and (diffuse_alpha_pack != "SMOOTHNESS") and (metallic_alpha_pack != "SMOOTHNESS") and (specular_alpha_pack != "SMOOTHNESS") and (normal_alpha_pack != "SMOOTHNESS") and not specular_smoothness_overlay),
                ("ao", pass_ao and not diffuse_premultiply_ao),
                ("emission", pass_emit and not diffuse_alpha_pack == "EMITMASK"),
                ("alpha", pass_alpha and (diffuse_alpha_pack != "TRANSPARENCY")),
                ("metallic", pass_metallic and not specular_setup and not phong_setup),
                ("specular", specular_setup and normal_alpha_pack != "SPECULAR"),
                ("phong", phong_setup),
                ("normal", pass_normal)
            ]:
                if not bakeconditions:
                    continue
                image = bpy.data.images[platform_img(bakepass)]
                image.save_render(bpy.path.abspath(image.filepath), scene=context.scene)
                if export_format == "GMOD":
                    image.filepath_raw = images_path+"materialsrc/"+sanitized_name(image.name)
                    image.save_render(image.filepath_raw,scene=context.scene)
                    self.compile_gmod_tga(steam_library_path,images_path,sanitized_name(image.name))
                    if os.path.isfile(target_dir+"/"+sanitized_name(image.name).replace(".tga",".vtf")):
                        os.remove(target_dir+"/"+sanitized_name(image.name).replace(".tga",".vtf"))
                    shutil.move(images_path+"materials/"+sanitized_name(image.name).replace(".tga",".vtf"), target_dir)

            if cleanup_shapekeys:
                for mesh in plat_collection.all_objects:
                    if mesh.type == 'MESH' and mesh.data.shape_keys is not None:
                        names = [key.name for key in mesh.data.shape_keys.key_blocks]
                        for name in names:
                            if name[-4:] == "_old" or name[-11:] == " - Reverted":
                                mesh.shape_key_remove(key=mesh.data.shape_keys.key_blocks[name])

            # '_bake' shapekeys are always applied and removed.
            for mesh in plat_collection.all_objects:
                if mesh.type == 'MESH' and mesh.data.shape_keys is not None:
                    names = [key.name for key in mesh.data.shape_keys.key_blocks]
                    for name in names:
                        if name[-5:] == "_bake":
                            mesh.shape_key_remove(key=mesh.data.shape_keys.key_blocks[name])


            if optimize_static:
                for mesh in plat_collection.all_objects:
                    if mesh.type == 'MESH' and mesh.data.shape_keys is not None:
                        context.view_layer.objects.active = mesh
                        bpy.ops.cats_manual.optimize_static_shapekeys()

            # Export the model to the bake dir
            export_groups = [
                ("Bake", ["Body", "Armature", "Static"])
            ]
            if use_physmodel:
                    export_groups.append(("LODPhysics", ["LODPhysics", "ArmatureLODPhysics"]))
            if use_lods:
                for idx, _ in enumerate(lods):
                    export_groups.append(("LOD" + str(idx + 1), ["LOD" + str(idx + 1), "ArmatureLOD" + str(idx + 1)]))


            # Create groups to export... One for the main, one each for each LOD
            for obj in plat_collection.all_objects:
                if not "LOD" in obj.name:
                    if obj.type == "MESH" and obj.name != "Static":
                        obj.name = "Body"
                    elif obj.type == "ARMATURE":
                        obj.name = "Armature"

            # Remove all materials for export - blender will try to embed materials but it doesn't work with our setup
            #exception is Gmod because Gmod needs textures to be applied to work - @989onan
            if export_format != "GMOD":
                for obj in plat_collection.all_objects:
                    if obj.type == 'MESH':
                        context.view_layer.objects.active = obj
                        while len(obj.material_slots) > 0:
                            obj.active_material_index = 0  # select the top material
                            bpy.ops.object.material_slot_remove()

            for export_group in export_groups:
                bpy.ops.object.select_all(action='DESELECT')
                for obj in plat_collection.all_objects:
                    if obj.name in export_group[1]:
                        obj.select_set(True)
                if export_format == "FBX":
                    bpy.ops.export_scene.fbx(filepath=bpy.path.abspath("//CATS Bake/" + platform_name + "/" + export_group[0] + ".fbx"), check_existing=False, filter_glob='*.fbx',
                                             use_selection=True,
                                             use_active_collection=False, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_ALL',
                                             bake_space_transform=False, object_types={'ARMATURE', 'MESH'},
                                             use_mesh_modifiers=False, use_mesh_modifiers_render=False, mesh_smooth_type='OFF', use_subsurf=False,
                                             use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=False, primary_bone_axis='Y',
                                             secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True,
                                             path_mode='AUTO',
                                             embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True,
                                             axis_forward='-Z', axis_up='Y')
                elif export_format == "DAE":
                    bpy.ops.wm.collada_export(filepath=bpy.path.abspath("//CATS Bake/" + platform_name + "/" + export_group[0] + ".dae"), check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False,
                                              filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False,
                                              filter_collada=True, filter_alembic=False, filter_usd=False, filter_volume=False, filter_folder=True,
                                              filter_blenlib=False, filemode=8, display_type='DEFAULT', prop_bc_export_ui_section='main',
                                              apply_modifiers=False, export_mesh_type=0, export_mesh_type_selection='view', export_global_forward_selection='Y',
                                              export_global_up_selection='Z', apply_global_orientation=False, selected=True, include_children=False,
                                              include_armatures=True, include_shapekeys=False, deform_bones_only=False, include_animations=True, include_all_actions=True,
                                              export_animation_type_selection='sample', sampling_rate=1, keep_smooth_curves=False, keep_keyframes=False, keep_flat_curves=False,
                                              active_uv_only=False, use_texture_copies=False, triangulate=True, use_object_instantiation=True, use_blender_profile=True,
                                              sort_by_name=False, export_object_transformation_type=0, export_object_transformation_type_selection='matrix',
                                              export_animation_transformation_type=0, open_sim=False,
                                              limit_precision=False, keep_bind_info=False)
                elif export_format == "GMOD":
                    #compile model. (TAKES JUST AS LONG AS BAKE OR MORE)
                    bpy.ops.cats_importer.export_gmod_addon(steam_library_path=steam_library_path,gmod_model_name=gmod_model_name,platform_name=platform_name)
            # Reapply cats material
            if export_format != "GMOD":
                for child in plat_collection.all_objects:
                    if child.type == "MESH":
                        if len(child.material_slots) == 0:
                            child.data.materials.append(mat)
                        else:
                            child.material_slots[0].material = mat

            if optimize_static:
                with open(os.path.dirname(os.path.abspath(__file__)) + "/../extern_tools/BakeFixer.cs", 'r') as infile:
                    with open(bpy.path.abspath("//CATS Bake/" + platform_name + "/") + "BakeFixer.cs", 'w') as outfile:
                        for line in infile:
                            outfile.write(line)
            # Delete our duplicate scene
            bpy.ops.scene.delete()

            if export_format == "GMOD":
                vmtfile += "\n}"
                vmtfiledir = open(target_dir+"/cats_baked_"+sanitized_platform_name+".vmt","w")
                vmtfiledir.write(vmtfile)
                vmtfiledir.close()
                collection = bpy.data.collections["CATS Bake"]
            # Move armature so we can see it
            if quick_compare and export_format != "GMOD":
                for obj in plat_collection.objects:
                    if obj.type == "ARMATURE":
                        obj.location.x += armature.dimensions.x * (1 + platform_number)
                for idx, _ in enumerate(lods):
                    if "ArmatureLOD" + str(idx + 1) in plat_collection.objects:
                        plat_collection.objects["ArmatureLOD" + str(idx + 1)].location.z += armature.dimensions.z * (1 + idx)

        # Delete our duplicate scene and the platform-agnostic CATS Bake
        bpy.ops.scene.delete()

        for obj in collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

        bpy.data.collections.remove(collection)

        #clean unused data
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        self.report({'INFO'}, t('cats_bake.info.success'))

        print("BAKE COMPLETE!")
