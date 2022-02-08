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

def autodetect_passes(self, context, item, tricount, platform):
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

    # Apply transforms: on if more than one mesh TODO: with different materials?
    context.scene.bake_normal_apply_trans = len(objects) > 1

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
        item.translate_bone_names = "NONE"
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
        """
        https://developer.valvesoftware.com/wiki/Adapting_PBR_Textures_to_Source
        TBD: We probably want to produce a VMT that at least gives breadcrumbs for how to import. Passes we need:
        $basetexture: premultiplied albedo. Source also reccomends dodging the base texture with the roughness map: albedo * curve(roughness, 127->0, 191->16, 255->64)
        $envmapmask: single-channel specularity map. Anything with $bumpmap must use $basealphaenvmapmask instead (or $normalmapalphaenvmapmask)
        for source we also need to invert the roughness and apply a curve from 1-roughness, 108->0 208->112 (in srgb)
        $bumpmap: normals, needs Y (green) channel flipped
        $emissiveblendenabled and $emissiveblendbasetexture: emit
        """



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
    bl_label = "Garry's Mod"
    bl_description = "Preset for producing a compatible Garry's Mod character model"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        item = context.scene.bake_platforms.add()
        item.name = "Garry's Mod"
        autodetect_passes(self, context, item, 10000, "GMOD")
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
        #bpy.ops.cats_bake.preset_gmod()
        bpy.ops.cats_bake.preset_secondlife()
        return {'FINISHED'}

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
    def bake_pass(self, context, bake_name, bake_type, bake_pass_filter, objects, bake_size, bake_samples, bake_ray_distance, background_color, clear, bake_margin, bake_active=None, bake_multires=False,
                  normal_space='TANGENT',solidmaterialcolors=dict()):
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

            bpy.ops.image.new(name="SCRIPT_" + bake_name + ".png", width=bake_size[0], height=bake_size[1], color=background_color,
                              generated_type="BLANK", alpha=True)
            image = bpy.data.images["SCRIPT_" + bake_name + ".png"]
            image.filepath = bpy.path.abspath("//CATS Bake/" + "SCRIPT_" + bake_name + ".png")
            image.alpha_mode = "STRAIGHT"
            image.generated_color = background_color
            image.generated_width = bake_size[0]
            image.generated_height = bake_size[1]
            image.scale(bake_size[0], bake_size[1])
            if bake_type == 'NORMAL' or bake_type == 'ROUGHNESS':
                image.colorspace_settings.name = 'Non-Color'
            if bake_name == 'diffuse' or bake_name == 'metallic':  # For packing smoothness to alpha
                image.alpha_mode = 'CHANNEL_PACKED'
            image.pixels[:] = background_color * bake_size[0] * bake_size[1]
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
            old_pixels = image.pixels[:]

            #lastly, slap our solid squares on top of bake atlas, to make a nice solid square without interuptions from the rest of the bake - @989onan
            for child in [obj for obj in objects if obj.type == "MESH"]: #grab all mesh objects being baked
                for matindex,material in enumerate(child.data.materials):
                    if material.name in solidmaterialcolors:
                        index = list(solidmaterialcolors.keys()).index(material.name)
                        old_pixels = list(old_pixels)

                        #in pixels
                        #Thanks to @Sacred#9619 on discord for this one.
                        margin = int(math.ceil(0.0078125 * context.scene.bake_resolution / 2)) #has to be the same as "pixelmargin"
                        n = int( bake_size[0]/margin )
                        n2 = int( bake_size[1]/margin )
                        X = margin/2 + margin * int( index % n )
                        Y = margin/2 + margin * int( index / n2 )
                        square_center_coord = [X,Y]

                        color = solidmaterialcolors[material.name][bake_name+"_color"]
                        #while in pixels inside image but 4 pixel padding around our solid center square position
                        for x in range(max(0,int(square_center_coord[0]-(margin/2))),min(bake_size[0], int(square_center_coord[0]+(margin/2)))):
                            for y in range(max(0,int(square_center_coord[1]-(margin/2))),min(bake_size[1], int(square_center_coord[1]+(margin/2)))):
                                for channel,rgba in enumerate(color):
                                    #since the array is one dimensional, (kinda like old minecraft schematics) we have to convert 2d cords to 1d cords, then multiply by 4 since there are 4 channels, then add current channel.
                                    old_pixels[(((y*bake_size[0])+x)*4)+channel] = rgba
            image.pixels[:] = old_pixels[:]



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

        return {'FINISHED'}

    def perform_bake(self, context):
        print('START BAKE')
        # TODO: diffuse, emit, alpha, metallic and smoothness all have a very slight difference between sample counts
        #       default it to something sane, but maybe add a menu later?
        # Global options
        resolution = context.scene.bake_resolution
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
        normal_apply_trans = context.scene.bake_normal_apply_trans
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
                                    if node_image.type != "TEX_IMAGE": #To catch normal maps
                                        return [False,[0.0,0.0,0.0,1.0]] #if not image then it's some type of node chain that is too complicated so return false
                                    old_pixels = node_image.image.pixels[:]
                                    solidimagepixels = np.tile(old_pixels[0:4], int(len(old_pixels)/4))
                                    if np.array_equal(solidimagepixels,old_pixels):
                                        return [True,old_pixels[0:4]]
                                    return [False,[0.0,0.0,0.0,1.0]]
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
                    reproject_anyway = (len(child.data.uv_layers) == 0 or
                                        all(set(loop.uv[:]).issubset({0,1}) for loop in active_uv.data))
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
                        # Select all faces in +X
                        print("Un-mirroring source CATS UV data")
                        uv_layer = (child.data.uv_layers["CATS UV Super"].data if
                                   supersample_normals else
                                   child.data.uv_layers["CATS UV"].data)
                        for poly in child.data.polygons:
                            if poly.center[0] > 0:
                                for loop in poly.loop_indices:
                                    uv_layer[loop].uv.x += 1
                    elif uv_overlap_correction == "MANUAL":
                        if "Target" in child.data.uv_layers:
                            for idx, loop in enumerate(child.data.uv_layers["Target"].data):
                                child.data.uv_layers["CATS UV"].data[idx].uv = loop.uv
                                if supersample_normals:
                                    child.data.uv_layers["CATS UV Super"].data[idx].uv = loop.uv

            #PLEASE DO THIS TO PREVENT PROBLEMS WITH UV EDITING LATER ON:
            bpy.data.scenes["CATS Scene"].tool_settings.use_uv_select_sync = False


            if optimize_solid_materials:
                #go through the solid materials on all the meshes and scale their UV's down to 0 in a grid of rows of squares so that they bake on a small separate part of the image mostly in the top left -@989onan
                for child in collection.all_objects:
                    if child.type == "MESH":
                        for matindex,material in enumerate(child.data.materials):
                            if material.name in solidmaterialnames:
                                for layer in cats_uv_layers:
                                    print("processing solid material: \""+material.name+"\" on layer: \""+layer+"\" on object: \""+child.name+"\"")
                                    idx = child.data.uv_layers.active_index
                                    child.data.uv_layers[layer].active = True
                                    Common.switch('EDIT')
                                    #deselect all geometry and uv, select material that we are on that is solid, and then select all on visible UV. This will isolate the solid material UV's on this layer and object.

                                    bpy.ops.mesh.select_all(action='SELECT') #select all mesh
                                    bpy.ops.uv.select_all(action='DESELECT') #deselect all UV
                                    bpy.ops.mesh.select_all(action='DESELECT') #deselect all mesh

                                    bpy.ops.mesh.select_mode(type="FACE")
                                    child.active_material_index = matindex
                                    bpy.ops.object.material_slot_select() #select our material on mesh
                                    bpy.ops.uv.select_all(action='SELECT') #select all uv

                                    #https://blender.stackexchange.com/a/75095
                                    #Scale a 2D vector v, considering a scale s and a pivot point p
                                    def Scale2D( v, s, p ):
                                        return ( p[0] + s[0]*(v[0] - p[0]), p[1] + s[1]*(v[1] - p[1]) )

                                    Common.switch('OBJECT')#idk why this has to be here but it breaks without it - @989onan
                                    index = solidmaterialnames[material.name]


                                    #Thanks to @Sacred#9619 on discord for this one.
                                    squaremargin = pixelmargin
                                    n = int( resolution/squaremargin )
                                    X = squaremargin/2 + squaremargin * int( index % n )
                                    Y = squaremargin/2 + squaremargin * int( index / n )

                                    uv_layer = child.data.uv_layers[layer].data
                                    for poly in child.data.polygons:
                                        for loop in poly.loop_indices:
                                            if uv_layer[loop].select: #make sure that it is selected (only visible will be selected in this case)
                                                #Here we scale the UV's down to 0 starting at the bottom left corner and going up row by row of solid materials.
                                                uv_layer[loop].uv = Scale2D( uv_layer[loop].uv, (0,0), ((X/resolution),(Y/resolution))  )
                                    Common.switch('EDIT')
                                    #deselect UV's and hide mesh for scaling uv's out the way later. this also prevents the steps for averaging islands and prioritizing head size from going bad later.
                                    bpy.ops.uv.select_all(action='DESELECT')
                                    bpy.ops.mesh.hide(unselected=False)

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
                    context.view_layer.objects.active = obj
                    for group in ['LeftEye', 'lefteye', 'Lefteye', 'Eye.L', 'RightEye', 'righteye', 'Righteye', 'Eye.R']:
                        if group in obj.vertex_groups:
                            vgroup_idx = obj.vertex_groups[group].index
                            if any(any(v_group.group == vgroup_idx and v_group.weight > 0.0 for v_group in vert.groups) for vert in obj.data.vertices):
                                print("{} found in {}".format(group, obj.name))
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
                                uv_layer = obj.data.uv_layers["CATS UV"].data
                                for poly in obj.data.polygons:
                                    for loop in poly.loop_indices:
                                        if uv_layer[loop].select:
                                            uv_layer[loop].uv.x *= prioritize_factor
                                            uv_layer[loop].uv.y *= prioritize_factor


            # Pack islands. Optionally use UVPackMaster if it's available
            bpy.ops.object.select_all(action='SELECT')
            for layer in cats_uv_layers:
                for obj in collection.all_objects:
                    if obj.type == 'MESH':
                        obj.data.uv_layers.active = obj.data.uv_layers[layer]
                Common.switch('EDIT')
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
                for child in collection.all_objects:
                    if child.type == "MESH":
                        for layer in cats_uv_layers:
                            idx = child.data.uv_layers.active_index
                            child.data.uv_layers[layer].active = True
                            Common.switch('EDIT')

                            bpy.ops.mesh.select_all(action='SELECT')
                            bpy.ops.uv.select_all(action='SELECT')

                            #https://blender.stackexchange.com/a/75095
                            #Scale a 2D vector v, considering a scale s and a pivot point p
                            def Scale2D( v, s, p ):
                                return ( p[0] + s[0]*(v[0] - p[0]), p[1] + s[1]*(v[1] - p[1]) )

                            last_index = len(solidmaterialnames)

                            #Thanks to @Sacred#9619 on discord for this one.
                            squaremargin = pixelmargin
                            n = int( resolution/squaremargin )
                            Y = squaremargin/2 + squaremargin * int( last_index / n )

                            Common.switch('OBJECT')#idk why this has to be here but it breaks without it - @989onan
                            for poly in child.data.polygons:
                                for loop in poly.loop_indices:
                                    uv_layer = child.data.uv_layers[layer].data
                                    if uv_layer[loop].select: #make sure that it is selected (only visible will be selected in this case)
                                        #scale UV upwards so square stuff below can fit for solid colors
                                        uv_layer[loop].uv = Scale2D( uv_layer[loop].uv, (1,1-((Y+(pixelmargin+squaremargin))/resolution)), (0,1) )

                        #unhide all mesh polygons from our material hiding for scaling
                        for layer in cats_uv_layers:
                            idx = child.data.uv_layers.active_index
                            child.data.uv_layers[layer].active = True
                            Common.switch('EDIT')
                            bpy.ops.mesh.select_all(action='SELECT')
                            bpy.ops.uv.select_all(action='SELECT')
                            bpy.ops.mesh.reveal(select=True)
                            Common.switch('OBJECT') #below will error if it isn't in object because of poll error

            #lastly make our target UV map active
            for obj in collection.all_objects:
                if obj.type == 'MESH':
                    obj.data.uv_layers.active = obj.data.uv_layers["CATS UV"]

        if not os.path.exists(bpy.path.abspath("//CATS Bake/")):
            os.mkdir(bpy.path.abspath("//CATS Bake/"))

        # Bake diffuse
        if pass_diffuse:
            # Metallic can cause issues baking diffuse, so we put it somewhere typically unused
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic Rotation")
            self.set_values([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", 0.0)

            self.bake_pass(context, "diffuse", "DIFFUSE", {"COLOR"}, [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 32, 0, [0.5, 0.5, 0.5, 1.0], True, pixelmargin, solidmaterialcolors=solidmaterialcolors)

            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic Rotation")
            bpy.data.images["SCRIPT_diffuse.png"].save()

            if sharpen_bakes:
                self.filter_image(context, "SCRIPT_diffuse.png", BakeButton.sharpen_create)

        # Bake roughness, invert
        if pass_smoothness:
            # Specularity of 0 messes up 'roughness' bakes. Fix that here.
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Specular", "Transmission Roughness")
            self.set_values([obj for obj in collection.all_objects if obj.type == "MESH"], "Specular", 0.5)
            self.bake_pass(context, "smoothness", "ROUGHNESS", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 32, 0, [1.0, 1.0, 1.0, 1.0], True, pixelmargin, solidmaterialcolors=solidmaterialcolors)
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Specular", "Transmission Roughness")
            image = bpy.data.images["SCRIPT_smoothness.png"]
            pixel_buffer = list(image.pixels)
            for idx in range(0, len(image.pixels)):
                # invert r, g, b, but not a
                if (idx % 4) != 3:
                    pixel_buffer[idx] = 1.0 - pixel_buffer[idx]
            image.pixels[:] = pixel_buffer
            if sharpen_bakes:
                self.filter_image(context, "SCRIPT_smoothness.png", BakeButton.sharpen_create, use_linear=True)

        # advanced: bake alpha from bsdf output
        if pass_alpha:
            # when baking alpha as roughness, the -real- alpha needs to be set to 1 to avoid issues
            # this will clobber whatever's in Anisotropic Rotation!
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", "Roughness")
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", "Anisotropic Rotation")
            self.set_values([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", 1.0)
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic")
            self.set_values([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", 0)
            # Specularity of 0 messes up 'roughness' bakes. Fix that here.
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Specular", "Transmission Roughness")
            self.set_values([obj for obj in collection.all_objects if obj.type == "MESH"], "Specular", 0.5)


            # Run the bake pass (bake roughness)
            self.bake_pass(context, "alpha", "ROUGHNESS", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 32, 0, [1, 1, 1, 1.0], True, pixelmargin)

            # Revert the changes (re-flip)
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic")
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", "Anisotropic Rotation")
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", "Roughness")
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Specular", "Transmission Roughness")


        # advanced: bake metallic from last bsdf output
        if pass_metallic:
            # Find all Principled BSDF nodes. Flip Roughness and Metallic (default_value and connection)
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Roughness")
            # Specularity of 0 messes up 'roughness' bakes. Fix that here.
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Specular", "Transmission Roughness")
            self.set_values([obj for obj in collection.all_objects if obj.type == "MESH"], "Specular", 0.5)

            # Run the bake pass
            self.bake_pass(context, "metallic", "ROUGHNESS", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 32, 0, [0, 0, 0, 1.0], True, pixelmargin, solidmaterialcolors=solidmaterialcolors)

            # Revert the changes (re-flip)
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Roughness")
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Specular", "Transmission Roughness")
            if sharpen_bakes:
                self.filter_image(context, "SCRIPT_metallic.png", BakeButton.sharpen_create)

       # TODO: advanced: bake detail mask from diffuse node setup

        # TODO: specularity? would allow specular setups on pre-existing avatars


        # Create 'disable' shape keys, each of which shrinks their relevant mesh down to a single point
        if create_disable_shapekeys:
            for obj in sorted(filter(lambda o: o.type == "MESH", collection.all_objects),
                              key=lambda o: len(o.data.vertices))[:-1]:
                print(obj.name)
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj
                if obj.data.shape_keys is None or len(obj.data.shape_keys.key_blocks) == 0:
                    bpy.ops.object.shape_key_add(from_mix=True)
                    obj.data.shape_keys.key_blocks[-1].name = "Basis"
                bpy.ops.object.shape_key_add(from_mix=True)
                obj.data.shape_keys.key_blocks[-1].name = "Disable " + obj.name[:-4]
                Common.switch("EDIT")
                bpy.ops.transform.resize(value=(0,0,0))
                Common.switch("OBJECT")

        Common.switch('OBJECT')

        # Save and disable shape keys
        shapekey_values = dict()
        if not apply_keys:
            for obj in collection.all_objects:
                if Common.has_shapekeys(obj):
                    # This doesn't work for keys which have different starting
                    # values... but generally that's not what you should do anyway
                    for key in obj.data.shape_keys.key_blocks:
                        # Always ignore '_bake' keys so they're baked in
                        if key.name[-5:] != '_bake':
                            shapekey_values[key.name] = key.value
                            key.value = 0.0

        # Option to apply current shape keys, otherwise normals bake weird
        # If true, apply all shapekeys and remove '_bakeme' keys
        # Otherwise, only apply '_bakeme' keys
        Common.switch('EDIT')
        Common.switch('OBJECT')
        for name in [ob.name for ob in collection.all_objects]:
            obj = collection.all_objects[name]
            if obj.type == "MESH" and Common.has_shapekeys(obj):
                obj.select_set(True)
                context.view_layer.objects.active = obj
                bpy.ops.object.shape_key_add(from_mix=True)
                bpy.ops.cats_shapekey.shape_key_to_basis()
                obj.active_shape_key_index = 0

        # Bake highres normals
        if not normal_apply_trans:
            # Join meshes
            Common.join_meshes(armature_name=arm_copy.name, repair_shape_keys=False)
        else:
            for obj in collection.all_objects:
                # Joining meshes causes issues with materials. Instead. apply location for all meshes, so object and world space are the same
                if obj.type == "MESH":
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    context.view_layer.objects.active = obj
                    bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)

        # Bake normals in object coordinates
        if pass_normal:
            for obj in collection.all_objects:
                if obj.type == 'MESH' and generate_uvmap:
                    if supersample_normals:
                        obj.data.uv_layers.active = obj.data.uv_layers["CATS UV Super"]
                    else:
                        obj.data.uv_layers.active = obj.data.uv_layers["CATS UV"]
            bake_size = ((resolution * 2, resolution * 2) if
                         supersample_normals else
                         (resolution, resolution))
            self.bake_pass(context, "world", "NORMAL", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                           bake_size, 128, 0, [0.5, 0.5, 1.0, 1.0], True, pixelmargin, normal_space="OBJECT",solidmaterialcolors=solidmaterialcolors)

        # Reset UV
        for obj in collection.all_objects:
             if obj.type == 'MESH' and generate_uvmap and supersample_normals:
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
                for obj in collection.all_objects:
                    if obj.type == "MESH" and "LeftEye" in obj.vertex_groups:
                        leyemask = obj.modifiers.new(type='MASK', name="leyemask")
                        leyemask.mode = "VERTEX_GROUP"
                        leyemask.vertex_group = "LeftEye"
                        leyemask.invert_vertex_group = True
                    if obj.type == "MESH" and "RightEye" in obj.vertex_groups:
                        reyemask = obj.modifiers.new(type='MASK', name="reyemask")
                        reyemask.mode = "VERTEX_GROUP"
                        reyemask.vertex_group = "RightEye"
                        reyemask.invert_vertex_group = True
            self.bake_pass(context, "ao", "AO", {"AO"}, [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 512, 0, [1.0, 1.0, 1.0, 1.0], True, pixelmargin)
            if illuminate_eyes:
                for obj in collection.all_objects:
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
                self.bake_pass(context, "emission", "EMIT", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                               (resolution, resolution), 32, 0, [0, 0, 0, 1.0], True, pixelmargin)
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
                self.bake_pass(context, "emission", "COMBINED", {"COLOR", "DIRECT", "INDIRECT", "EMIT", "AO", "DIFFUSE"}, [obj for obj in collection.all_objects if obj.type == "MESH"],
                               (resolution, resolution), 512, 0, [0.0, 0.0, 0.0, 1.0], True, pixelmargin, solidmaterialcolors=solidmaterialcolors)
                if emit_exclude_eyes:
                    def group_relevant(obj, groupname):
                        if obj.type == "MESH" and groupname in obj.vertex_groups:
                            idx = obj.vertex_groups[groupname].index
                            return any( any(group.group == idx and group.weight > 0.0 for group in vert.groups)
                                    for vert in obj.data.vertices)

                    # Bake each eye on top individually
                    for obj in collection.all_objects:
                        if group_relevant(obj, "LeftEye"):
                            leyemask = obj.modifiers.new(type='MASK', name="leyemask")
                            leyemask.mode = "VERTEX_GROUP"
                            leyemask.vertex_group = "LeftEye"
                            leyemask.invert_vertex_group = False
                    self.bake_pass(context, "emission", "EMIT", set(), [obj for obj in collection.all_objects if group_relevant(obj, "LeftEye")],
                               (resolution, resolution), 32, 0, [0, 0, 0, 1.0], False, pixelmargin, solidmaterialcolors=solidmaterialcolors)
                    for obj in collection.all_objects:
                        if "leyemask" in obj.modifiers:
                            obj.modifiers.remove(obj.modifiers["leyemask"])

                    for obj in collection.all_objects:
                        if group_relevant(obj, "RightEye"):
                            reyemask = obj.modifiers.new(type='MASK', name="reyemask")
                            reyemask.mode = "VERTEX_GROUP"
                            reyemask.vertex_group = "RightEye"
                            reyemask.invert_vertex_group = False
                    self.bake_pass(context, "emission", "EMIT", set(), [obj for obj in collection.all_objects if group_relevant(obj, "RightEye")],
                               (resolution, resolution), 32, 0, [0, 0, 0, 1.0], False, pixelmargin, solidmaterialcolors=solidmaterialcolors)
                    for obj in collection.all_objects:
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
            Common.switch("OBJECT")
            bpy.ops.object.select_all(action='DESELECT')
            context.view_layer.objects.active = obj

            for mod in obj.modifiers:
                if mod.show_viewport and mod.type == 'MASK':
                    Common.switch("OBJECT")
                    vgroup_idx = obj.vertex_groups[mod.vertex_group].index
                    for vert in obj.data.vertices:
                        vert.select = any(group.group == vgroup_idx and group.weight > 0.0 for group in vert.groups)
                    Common.switch("EDIT")
                    bpy.ops.mesh.delete(type="VERT")

        ########### BEGIN PLATFORM SPECIFIC CODE ###########
        for platform_number, platform in enumerate(context.scene.bake_platforms):
            def platform_img(img_pass):
                return platform_name + " " + img_pass

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
            specular_alpha_pack = platform.specular_alpha_pack
            diffuse_emit_overlay = platform.diffuse_emit_overlay
            use_physmodel = platform.use_physmodel
            physmodel_lod = platform.physmodel_lod
            use_lods = platform.use_lods
            lods = platform.lods
            generate_prop_bones = platform.generate_prop_bones
            generate_prop_bone_max_influence_count = platform.generate_prop_bone_max_influence_count
            generate_prop_bone_max_overall = 75 # platform-specific?

            if not os.path.exists(bpy.path.abspath("//CATS Bake/" + platform_name + "/")):
                os.mkdir(bpy.path.abspath("//CATS Bake/" + platform_name + "/"))

            # for cleanliness create platform-specific copies here
            for (bakepass, bakename) in [
                (pass_diffuse, 'diffuse.png'),
                (pass_normal, 'normal.png'),
                (pass_smoothness, 'smoothness.png'),
                (pass_ao, 'ao.png'),
                (pass_emit, 'emission.png'),
                (pass_alpha, 'alpha.png'),
                (pass_metallic, 'metallic.png'),
                (specular_setup, 'specular.png'),
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
                image.filepath = bpy.path.abspath("//CATS Bake/" + platform_name + "/" + platform_img(bakename))
                image.generated_width = resolution
                image.generated_height = resolution
                image.scale(resolution, resolution)
                # already completed passes
                if bakename not in ["specular.png", "normal.png"]:
                    orig_image = bpy.data.images["SCRIPT_" + bakename]
                    image.pixels[:] = orig_image.pixels[:]

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

                        if found_vertex_groups and len(found_vertex_groups) <= generate_prop_bone_max_influence_count:
                            vgroup_lookup = dict([(vgp.index, vgp.name) for vgp in obj.vertex_groups])
                            for vgp in found_vertex_groups:
                                vgroup_name = vgroup_lookup[vgp]

                                print("Object " + obj.name + " is an eligible prop on " + vgroup_name + "! Creating prop bone...")
                                # If the obj has ".001" or similar, trim it
                                newbonename = "~" + vgroup_name + "_Prop_" + orig_obj_name
                                obj.vertex_groups[vgroup_name].name = newbonename
                                context.view_layer.objects.active = plat_arm_copy
                                Common.switch("EDIT")
                                orig_bone = plat_arm_copy.data.edit_bones[vgroup_name]
                                if not orig_bone.children:
                                    #TODO: this doesn't account for props attached to something which has existing attachments
                                    Common.switch("OBJECT")
                                    print("Object " + obj.name + " already has no children, skipping")
                                    continue
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
                image = bpy.data.images[platform_img("diffuse.png")]
                diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
                pixel_buffer = list(diffuse_image.pixels)
                if pass_ao and diffuse_premultiply_ao:
                    ao_image = bpy.data.images["SCRIPT_ao.png"]
                    ao_buffer = ao_image.pixels[:]
                    for idx in range(0, len(image.pixels)):
                        if (idx % 4 != 3):
                            # Map range: set the black point up to 1-opacity
                            pixel_buffer[idx] = pixel_buffer[idx] * ((1.0 - diffuse_premultiply_opacity) + (diffuse_premultiply_opacity * ao_buffer[idx]))
                if specular_setup and pass_metallic:
                    metallic_image = bpy.data.images["SCRIPT_metallic.png"]
                    metallic_buffer = metallic_image.pixels[:]
                    for idx in range(0, len(image.pixels)):
                        if (idx % 4 != 3):
                            # Map range: metallic blocks diffuse light
                            pixel_buffer[idx] = pixel_buffer[idx] * (1 - metallic_buffer[idx])
                if pass_emit and diffuse_emit_overlay:
                    emit_image = bpy.data.images["SCRIPT_emission.png"]
                    emit_buffer = emit_image.pixels[:]
                    for idx in range(0, len(image.pixels)):
                        if (idx % 4 != 3):
                            # Map range: screen the emission onto diffuse
                            pixel_buffer[idx] = 1.0 - ((1.0 - emit_buffer[idx]) * (1.0 - pixel_buffer[idx]))

                image.pixels[:] = pixel_buffer
                image.save()

            # Preultiply AO into smoothness if selected, to avoid shine in dark areas
            if pass_smoothness and pass_ao and smoothness_premultiply_ao:
                image = bpy.data.images[platform_img("smoothness.png")]
                smoothness_image = bpy.data.images["SCRIPT_smoothness.png"]
                ao_image = bpy.data.images["SCRIPT_ao.png"]
                pixel_buffer = list(image.pixels)
                smoothness_buffer = smoothness_image.pixels[:]
                ao_buffer = ao_image.pixels[:]
                for idx in range(0, len(image.pixels)):
                    if (idx % 4 != 3):
                        # Map range: set the black point up to 1-opacity
                        pixel_buffer[idx] = smoothness_buffer[idx] * ((1.0 - smoothness_premultiply_opacity) + (smoothness_premultiply_opacity * ao_buffer[idx]))
                    else:
                        # Alpha is unused on quest, set to 1 to make sure unity doesn't keep it
                        pixel_buffer[idx] = 1.0
                image.pixels[:] = pixel_buffer

            # Pack to diffuse alpha (if selected)
            if pass_diffuse and ((diffuse_alpha_pack == "SMOOTHNESS" and pass_smoothness) or
                                 (diffuse_alpha_pack == "TRANSPARENCY" and pass_alpha) or
                                 (diffuse_alpha_pack == "EMITMASK" and pass_emit)):
                image = bpy.data.images[platform_img("diffuse.png")]
                print("Packing to diffuse alpha")
                alpha_image = None
                if diffuse_alpha_pack == "SMOOTHNESS":
                    alpha_image = bpy.data.images[platform_img("smoothness.png")]
                elif diffuse_alpha_pack == "TRANSPARENCY":
                    alpha_image = bpy.data.images["SCRIPT_alpha.png"]
                elif diffuse_alpha_pack == "EMITMASK":
                    alpha_image = bpy.data.images["SCRIPT_emission.png"]
                pixel_buffer = list(image.pixels)
                alpha_buffer = alpha_image.pixels[:]
                for idx in range(3, len(pixel_buffer), 4):
                    pixel_buffer[idx] = (alpha_buffer[idx - 3] * 0.299) + (alpha_buffer[idx - 2] * 0.587) + (alpha_buffer[idx - 1] * 0.114)
                image.pixels[:] = pixel_buffer

            # Pack to metallic alpha (if selected)
            if pass_metallic and (metallic_alpha_pack == "SMOOTHNESS" and pass_smoothness):
                image = bpy.data.images[platform_img("metallic.png")]
                print("Packing to metallic alpha")
                metallic_image = bpy.data.images["SCRIPT_metallic.png"]
                alpha_image = bpy.data.images[platform_img("smoothness.png")]
                pixel_buffer = list(metallic_image.pixels)
                alpha_buffer = alpha_image.pixels[:]
                for idx in range(3, len(pixel_buffer), 4):
                    pixel_buffer[idx] = alpha_buffer[idx - 3]
                image.pixels[:] = pixel_buffer

            # Create specular map
            if specular_setup:
                image = bpy.data.images[platform_img("specular.png")]
                pixel_buffer = list(image.pixels)
                if pass_metallic:
                    # Use the unaltered diffuse map
                    diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
                    diffuse_buffer = diffuse_image.pixels[:]
                    metallic_image = bpy.data.images["SCRIPT_metallic.png"]
                    metallic_buffer = metallic_image.pixels[:]
                    for idx in range(0, len(image.pixels)):
                        if (idx % 4 != 3):
                            # Simple specularity: most nonmetallic objects have about 4% reflectiveness
                            pixel_buffer[idx] = (diffuse_buffer[idx] * metallic_buffer[idx]) + (.04 * (1-metallic_buffer[idx]))
                else:
                    for idx in range(0, len(image.pixels)):
                        if (idx % 4 != 3):
                            pixel_buffer[idx] = 0.04
                if specular_alpha_pack == "SMOOTHNESS" and pass_smoothness:
                    alpha_image = bpy.data.images[platform_img("smoothness.png")]
                    alpha_image_buffer = alpha_image.pixels[:]
                    for idx in range(0, len(image.pixels)):
                        if (idx % 4 == 3):
                            pixel_buffer[idx] = alpha_image_buffer[idx - 3]

                image.pixels[:] = pixel_buffer

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
                self.bake_pass(context, "normal", "NORMAL", set(), [obj for obj in plat_collection.all_objects if obj.type == "MESH" and not "LOD" in obj.name],
                               (resolution, resolution), 128, 0, [0.5, 0.5, 1.0, 1.0], True, pixelmargin, solidmaterialcolors=solidmaterialcolors)
                image = bpy.data.images[platform_img("normal.png")]
                image.colorspace_settings.name = 'Non-Color'
                normal_image = bpy.data.images["SCRIPT_normal.png"]
                image.pixels[:] = normal_image.pixels[:]
                image.save()

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

            # Reapply keys
            if not apply_keys:
                for obj in plat_collection.all_objects:
                    if Common.has_shapekeys(obj):
                        for key in obj.data.shape_keys.key_blocks:
                            if key.name in shapekey_values:
                                key.value = shapekey_values[key.name]


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
                normaltexnode.image = bpy.data.images[platform_img("normal.png")]
                normalmapnode.space = "TANGENT"
                normaltexnode.interpolation = "Linear"
            if pass_diffuse:
                diffusetexnode = tree.nodes.new("ShaderNodeTexImage")
                diffusetexnode.image = bpy.data.images[platform_img("diffuse.png")]
                diffusetexnode.location.x -= 300
                diffusetexnode.location.y += 500

                # If AO, blend in AO.
                if pass_ao and not diffuse_premultiply_ao:
                    # AO -> Math (* ao_opacity + (1-ao_opacity)) -> Mix (Math, diffuse) -> Color
                    aotexnode = tree.nodes.new("ShaderNodeTexImage")
                    aotexnode.image = bpy.data.images[platform_img("ao.png")]
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
                metallictexnode.image = bpy.data.images[platform_img("metallic.png")]
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
                    smoothnesstexnode.image = bpy.data.images[platform_img("smoothness.png")]
                    invertnode = tree.nodes.new("ShaderNodeInvert")
                    tree.links.new(invertnode.inputs["Color"], smoothnesstexnode.outputs["Color"])
                    tree.links.new(bsdfnode.inputs["Roughness"], invertnode.outputs["Color"])
            if pass_alpha:
                if pass_diffuse and (diffuse_alpha_pack == "TRANSPARENCY"):
                    tree.links.new(bsdfnode.inputs["Alpha"], diffusetexnode.outputs["Alpha"])
                else:
                    alphatexnode = tree.nodes.new("ShaderNodeTexImage")
                    alphatexnode.image = bpy.data.images[platform_img("alpha.png")]
                    tree.links.new(bsdfnode.inputs["Alpha"], alphatexnode.outputs["Color"])
                mat.blend_method = 'CLIP'
            if pass_emit:
                emittexnode = tree.nodes.new("ShaderNodeTexImage")
                emittexnode.image = bpy.data.images[platform_img("emission.png")]
                emittexnode.location.x -= 800
                emittexnode.location.y -= 150
                tree.links.new(bsdfnode.inputs["Emission"], emittexnode.outputs["Color"])

            # Rebake diffuse to vertex colors: Incorperates AO
            if pass_diffuse and diffuse_vertex_colors:
                for obj in plat_collection.all_objects:
                    if obj.type == "MESH":
                        context.view_layer.objects.active = obj
                        bpy.ops.mesh.vertex_color_add()

                self.swap_links([obj for obj in plat_collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic Rotation")
                self.set_values([obj for obj in plat_collection.all_objects if obj.type == "MESH"], "Metallic", 0.0)
                self.bake_pass(context, "vertex_diffuse", "DIFFUSE", {"COLOR", "VERTEX_COLORS"}, [obj for obj in plat_collection.all_objects if obj.type == "MESH"],
                               (1, 1), 32, 0, [0.5, 0.5, 0.5, 1.0], True, pixelmargin)
                self.swap_links([obj for obj in plat_collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic Rotation")

                # TODO: If we're not baking anything else in, remove all UV maps entirely

                # Update material preview
                #tree.nodes.remove(diffusetexnode)
                diffusevertnode = tree.nodes.new("ShaderNodeVertexColor")
                diffusevertnode.layer_name = "Col"
                diffusevertnode.location.x -= 300
                diffusevertnode.location.y += 500
                tree.links.new(bsdfnode.inputs["Base Color"], diffusevertnode.outputs["Color"])

            # TODO: specular_setup
            # specularity: diffuse * metallic + (.04 * (1-metallic))
            # diffuse: diffuse * (1-metallic)
            # preapplied emit: diffuse + emit as 'screen': 1-(1-emit)*(1-diffuse)
            # emissive mask: emit as grayscale -> alpha channel

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

            # Reapply cats material
            for child in plat_collection.all_objects:
                if child.type == "MESH":
                    if len(child.material_slots) == 0:
                        child.data.materials.append(mat)
                    else:
                        child.material_slots[0].material = mat

            # Try to only output what you'll end up importing into unity.
            context.scene.render.image_settings.color_mode = 'RGBA'
            if pass_diffuse and not diffuse_vertex_colors:
                image = bpy.data.images[platform_img("diffuse.png")]
                image.save_render(bpy.path.abspath(image.filepath), scene=context.scene)
            if pass_smoothness and (diffuse_alpha_pack != "SMOOTHNESS") and (metallic_alpha_pack != "SMOOTHNESS") and (specular_alpha_pack != "SMOOTHNESS"):
                image = bpy.data.images[platform_img("smoothness.png")]
                image.save_render(bpy.path.abspath(image.filepath), scene=context.scene)
            if pass_ao and not diffuse_premultiply_ao:
                image = bpy.data.images[platform_img("ao.png")]
                image.save_render(bpy.path.abspath(image.filepath), scene=context.scene)
            if pass_emit and not diffuse_alpha_pack == "EMITMASK":
                image = bpy.data.images[platform_img("emission.png")]
                image.save_render(bpy.path.abspath(image.filepath), scene=context.scene)
            if pass_alpha and (diffuse_alpha_pack != "TRANSPARENCY"):
                image = bpy.data.images[platform_img("alpha.png")]
                image.save_render(bpy.path.abspath(image.filepath), scene=context.scene)
            if pass_metallic and not specular_setup:
                image = bpy.data.images[platform_img("metallic.png")]
                image.save_render(bpy.path.abspath(image.filepath), scene=context.scene)
            if specular_setup:
                image = bpy.data.images[platform_img("specular.png")]
                image.save_render(bpy.path.abspath(image.filepath), scene=context.scene)
            if optimize_static:
                with open(os.path.dirname(os.path.abspath(__file__)) + "/../extern_tools/BakeFixer.cs", 'r') as infile:
                    with open(bpy.path.abspath("//CATS Bake/" + platform_name + "/") + "BakeFixer.cs", 'w') as outfile:
                        for line in infile:
                            outfile.write(line)

            # Delete our duplicate scene
            bpy.ops.scene.delete()

            # Move armature so we can see it
            if quick_compare:
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
        self.report({'INFO'}, t('cats_bake.info.success'))

        print("BAKE COMPLETE!")
