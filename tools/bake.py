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
import webbrowser

from . import common as Common
from .register import register_wrap
from ..translations import t


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


def autodetect_passes(self, context, tricount, is_desktop):
    context.scene.bake_max_tris = tricount
    context.scene.bake_resolution = 2048 if is_desktop else 1024
    # Autodetect passes based on BSDF node inputs
    bsdf_nodes = []
    objects = Common.get_meshes_objects()
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
    context.scene.bake_use_decimation = total_tricount > tricount
    context.scene.bake_uv_overlap_correction = 'UNMIRROR' if context.scene.bake_use_decimation else "NONE"

    # Diffuse: on if >1 unique color input or if any has non-default base color input on bsdf
    context.scene.bake_pass_diffuse = (any([node.inputs["Base Color"].is_linked for node in bsdf_nodes])
                                       or len(set([node.inputs["Base Color"].default_value for node in bsdf_nodes])) > 1)

    # Smoothness: similar to diffuse
    context.scene.bake_pass_smoothness = (any([node.inputs["Roughness"].is_linked for node in bsdf_nodes])
                                          or len(set([node.inputs["Roughness"].default_value for node in bsdf_nodes])) > 1)

    # Emit: similar to diffuse
    context.scene.bake_pass_emit = (any([node.inputs["Emission"].is_linked for node in bsdf_nodes])
                                    or len(set([node.inputs["Emission"].default_value for node in bsdf_nodes])) > 1)

    # Transparency: similar to diffuse
    context.scene.bake_pass_alpha = is_desktop and (any([node.inputs["Alpha"].is_linked for node in bsdf_nodes])
                                                    or len(set([node.inputs["Alpha"].default_value for node in bsdf_nodes])) > 1)

    # Metallic: similar to diffuse
    context.scene.bake_pass_metallic = (any([node.inputs["Metallic"].is_linked for node in bsdf_nodes])
                                        or len(set([node.inputs["Metallic"].default_value for node in bsdf_nodes])) > 1)

    # Normal: on if any normals connected or if decimating... so, always on for this preset
    context.scene.bake_pass_normal = (context.scene.bake_use_decimation
                                      or any([node.inputs["Normal"].is_linked for node in bsdf_nodes]))

    # Apply transforms: on if more than one mesh TODO: with different materials?
    context.scene.bake_normal_apply_trans = len(objects) > 1

    # AO: up to user, don't override as part of this. Possibly detect if using a toon shader in the future?
    # TODO: If mesh is manifold and non-intersecting, turn on AO. Otherwise, leave it alone
    # diffuse ao: off if desktop
    context.scene.bake_pass_questdiffuse = not is_desktop

    # alpha packs: arrange for maximum efficiency.
    # Its important to leave Diffuse alpha alone if we're not using it, as Unity will try to use 4bpp if so
    context.scene.bake_diffuse_alpha_pack = "NONE"
    context.scene.bake_metallic_alpha_pack = "NONE"
    if is_desktop:
        # If 'smoothness' and 'transparency', we need to force metallic to bake so we can pack to it.
        if context.scene.bake_pass_smoothness and context.scene.bake_pass_alpha:
            context.scene.bake_pass_metallic = True
        # If we have transparency, it needs to go in diffuse alpha
        if context.scene.bake_pass_alpha:
            context.scene.bake_diffuse_alpha_pack = "TRANSPARENCY"
        # Smoothness to diffuse is only the most efficient when we don't have metallic or alpha
        if context.scene.bake_pass_smoothness and not context.scene.bake_pass_metallic and not context.scene.bake_pass_alpha:
            context.scene.bake_diffuse_alpha_pack = "SMOOTHNESS"
        if context.scene.bake_pass_metallic and context.scene.bake_pass_smoothness:
            context.scene.bake_metallic_alpha_pack = "SMOOTHNESS"
    else:
        # alpha packs: arrange for maximum efficiency.
        # Its important to leave Diffuse alpha alone if we're not using it, as Unity will try to use 4bpp if so
        context.scene.bake_diffuse_alpha_pack = "NONE"
        context.scene.bake_metallic_alpha_pack = "NONE"
        # If 'smoothness', we need to force metallic to bake so we can pack to it. (smoothness source is not configurable)
        if context.scene.bake_pass_smoothness:
            context.scene.bake_pass_metallic = True
            context.scene.bake_metallic_alpha_pack = "SMOOTHNESS"


@register_wrap
class BakePresetDesktop(bpy.types.Operator):
    bl_idname = 'cats_bake.preset_desktop'
    bl_label = t('cats_bake.preset_desktop.label')
    bl_description = t('cats_bake.preset_desktop.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        autodetect_passes(self, context, 32000, True)
        return {'FINISHED'}


@register_wrap
class BakePresetQuest(bpy.types.Operator):
    bl_idname = 'cats_bake.preset_quest'
    bl_label = t('cats_bake.preset_quest.label')
    bl_description = t('cats_bake.preset_quest.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        autodetect_passes(self, context, 5000, False)
        return {'FINISHED'}


@register_wrap
class BakeButton(bpy.types.Operator):
    bl_idname = 'cats_bake.bake'
    bl_label = t('cats_bake.bake.label')
    bl_description = t('cats_bake.bake.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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
                  normal_space='TANGENT'):
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
        for obj in objects:
            obj.select_set(True)

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
        if bake_type == 'DIFFUSE':
            context.scene.render.bake.use_pass_direct = False
            context.scene.render.bake.use_pass_indirect = False
            context.scene.render.bake.use_pass_color = True
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

    def tree_copy(self, ob, parent, collection, levels=3):
        def recurse(ob, parent, depth):
            if depth > levels:
                return
            copy = self.copy_ob(ob, parent, collection)

            for child in ob.children:
                recurse(child, copy, depth + 1)

            return copy

        return recurse(ob, ob.parent, 0)

    def execute(self, context):
        if not Common.get_meshes_objects():
            self.report({'ERROR'}, t('cats_bake.error.no_meshes'))
            return {'FINISHED'}
        # if context.scene.render.engine != 'CYCLES':
        #     self.report({'ERROR'}, t('cats_bake.error.render_engine'))
        #     return {'FINISHED'}
        if any([obj.hide_render for obj in Common.get_armature().children]):
            self.report({'ERROR'}, t('cats_bake.error.render_disabled'))
            return {'FINISHED'}
        # TODO: Check if any UV islands are self-overlapping, emit a warning

        # Change render engine to cycles and save the current one
        render_engine_tmp = context.scene.render.engine
        context.scene.render.engine = 'CYCLES'

        # Change decimate settings, run bake, change them back
        decimation_mode = context.scene.decimation_mode
        max_tris = context.scene.max_tris
        decimate_fingers = context.scene.decimate_fingers
        decimation_remove_doubles = context.scene.decimation_remove_doubles
        decimation_animation_weighting = context.scene.decimation_animation_weighting
        decimation_animation_weighting_factor = context.scene.decimation_animation_weighting_factor

        context.scene.decimation_mode = "SMART"
        context.scene.max_tris = context.scene.bake_max_tris
        context.scene.decimate_fingers = False
        context.scene.decimation_remove_doubles = True
        context.scene.decimation_animation_weighting = context.scene.bake_animation_weighting
        context.scene.decimation_animation_weighting_factor = context.scene.bake_animation_weighting_factor
        self.perform_bake(context)

        context.scene.decimation_mode = decimation_mode
        context.scene.max_tris = max_tris
        context.scene.decimate_fingers = decimate_fingers
        context.scene.decimation_remove_doubles = decimation_remove_doubles
        context.scene.decimation_animation_weighting = decimation_animation_weighting
        context.scene.decimation_animation_weighting_factor = decimation_animation_weighting_factor

        # Change render engine back to original
        context.scene.render.engine = render_engine_tmp

        return {'FINISHED'}

    def perform_bake(self, context):
        print('START BAKE')
        # TODO: diffuse, emit, alpha, metallic and smoothness all have a very slight difference between sample counts
        #       default it to something sane, but maybe add a menu later?
        # Global options
        resolution = context.scene.bake_resolution
        use_decimation = context.scene.bake_use_decimation
        preserve_seams = context.scene.bake_preserve_seams
        generate_uvmap = context.scene.bake_generate_uvmap
        prioritize_face = context.scene.bake_prioritize_face
        prioritize_factor = context.scene.bake_face_scale
        uv_overlap_correction = context.scene.bake_uv_overlap_correction
        margin = 0.01
        quick_compare = context.scene.bake_quick_compare

        # TODO: Option to seperate by loose parts and bake selected to active

        # Passes
        pass_diffuse = context.scene.bake_pass_diffuse
        pass_normal = context.scene.bake_pass_normal
        pass_smoothness = context.scene.bake_pass_smoothness
        pass_ao = context.scene.bake_pass_ao
        pass_questdiffuse = context.scene.bake_pass_questdiffuse
        pass_emit = context.scene.bake_pass_emit
        pass_alpha = context.scene.bake_pass_alpha
        pass_metallic = context.scene.bake_pass_metallic

        # Pass options
        illuminate_eyes = context.scene.bake_illuminate_eyes
        questdiffuse_opacity = context.scene.bake_questdiffuse_opacity
        normal_apply_trans = context.scene.bake_normal_apply_trans
        diffuse_alpha_pack = context.scene.bake_diffuse_alpha_pack
        metallic_alpha_pack = context.scene.bake_metallic_alpha_pack

        # Create an output collection
        collection = bpy.data.collections.new("CATS Bake")
        context.scene.collection.children.link(collection)

        # Tree-copy all meshes
        armature = Common.set_default_stage()
        arm_copy = self.tree_copy(armature, None, collection)

        # Make sure all armature modifiers target the new armature
        for child in collection.all_objects:
            for modifier in child.modifiers:
                if modifier.type == "ARMATURE":
                    modifier.object = arm_copy

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

        if generate_uvmap:
            # TODO: automagically detect if meshes even have a uv map, smart UV project them if not

            bpy.ops.object.select_all(action='DESELECT')
            # Make copies of the currently render-active UV layer, name "CATS UV"
            for child in collection.all_objects:
                if child.type == "MESH":
                    child.select_set(True)
                    context.view_layer.objects.active = child
                    bpy.ops.mesh.uv_texture_add()
                    child.data.uv_layers[-1].name = 'CATS UV'
                    if uv_overlap_correction == "REPROJECT":
                        idx = child.data.uv_layers.active_index
                        child.data.uv_layers.active_index = len(child.data.uv_layers) - 1
                        bpy.ops.object.editmode_toggle()
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.uv.select_all(action='SELECT')
                        bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.01)
                        bpy.ops.object.editmode_toggle()
                        child.data.uv_layers.active_index = idx
                    elif uv_overlap_correction == "UNMIRROR":
                        # TODO: issue a warning if any source images don't use 'wrap'
                        # Select all faces in +X
                        print("Un-mirroring source CATS UV data")
                        uv_layer = child.data.uv_layers["CATS UV"].data
                        for poly in child.data.polygons:
                            if poly.center[0] > 0:
                                for loop in poly.loop_indices:
                                    uv_layer[loop].uv.x += 1

            # TODO: cleanup, all editmode_toggle -> common.switch

            # Select all meshes. Select all UVs. Average islands scale
            context.view_layer.objects.active = next(child for child in arm_copy.children if child.type == "MESH")
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.average_islands_scale()  # Use blender average so we can make our own tweaks.
            Common.switch('OBJECT')

            # Select all islands belonging to 'Head' and children and enlarge them
            if prioritize_face and "Head" in arm_copy.data.bones:
                selected_group_names = ["Head"]
                selected_group_names.extend([bone.name for bone in arm_copy.data.bones["Head"].children_recursive])
                print("Prioritizing vertex groups: " + (", ".join(selected_group_names)))

                for obj in collection.all_objects:
                    if obj.type != "MESH":
                        continue
                    context.view_layer.objects.active = obj
                    Common.switch('EDIT')
                    bpy.ops.uv.select_all(action='DESELECT')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    for group in selected_group_names:
                        if group in obj.vertex_groups:
                            # Select all vertices in it
                            obj.vertex_groups.active = obj.vertex_groups[group]
                            bpy.ops.object.vertex_group_select()
                    # Synchronize
                    Common.switch('OBJECT')
                    Common.switch('EDIT')
                    # Then select all UVs
                    bpy.ops.uv.select_all(action='SELECT')
                    # Then for each UV (cause of the viewport thing) scale up by the selected factor
                    Common.switch('OBJECT')
                    uv_layer = obj.data.uv_layers["CATS UV"].data
                    for poly in obj.data.polygons:
                        for loop in poly.loop_indices:
                            if uv_layer[loop].select:
                                uv_layer[loop].uv.x *= prioritize_factor
                                uv_layer[loop].uv.y *= prioritize_factor

            # Pack islands. Optionally use UVPackMaster if it's available
            Common.switch('EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.pack_islands(rotate=True, margin=margin)
            # detect if UVPackMaster installed and configured
            try:  # UVP doesn't respect margins when called like this, find out why
                context.scene.uvp2_props.normalize_islands = False
                context.scene.uvp2_props.lock_overlapping_mode = '0' if use_decimation else '2'
                context.scene.uvp2_props.pack_to_others = False
                context.scene.uvp2_props.margin = margin
                context.scene.uvp2_props.similarity_threshold = 3
                context.scene.uvp2_props.precision = 1000
                # Give UVP a static number of iterations to do TODO: make this configurable?
                for _ in range(1, 10):
                    bpy.ops.uvpackmaster2.uv_pack()
            except AttributeError:
                pass

        # TODO: Option to apply current shape keys, otherwise normals bake weird

        # Bake diffuse
        Common.switch('OBJECT')
        if pass_diffuse:
            # Metallic can cause issues baking diffuse, so we put it somewhere typically unused
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic Rotation")
            self.set_values([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", 0.0)

            self.bake_pass(context, "diffuse", "DIFFUSE", {"COLOR"}, [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 32, 0, [0.5, 0.5, 0.5, 1.0], True, int(margin * resolution / 2))

            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic Rotation")

        # Bake roughness, invert
        if pass_smoothness:
            self.bake_pass(context, "smoothness", "ROUGHNESS", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 32, 0, [1.0, 1.0, 1.0, 1.0], True, int(margin * resolution / 2))
            image = bpy.data.images["SCRIPT_smoothness.png"]
            pixel_buffer = list(image.pixels)
            for idx in range(0, len(image.pixels)):
                # invert r, g, b, but not a
                if (idx % 4) != 3:
                    pixel_buffer[idx] = 1.0 - pixel_buffer[idx]
            image.pixels[:] = pixel_buffer

        # bake emit
        if pass_emit:
            self.bake_pass(context, "emission", "EMIT", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 32, 0, [0, 0, 0, 1.0], True, int(margin * resolution / 2))

        # advanced: bake alpha from bsdf output
        if pass_alpha:
            # when baking alpha as roughness, the -real- alpha needs to be set to 1 to avoid issues
            # this will clobber whatever's in Anisotropic Rotation!
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", "Roughness")
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", "Anisotropic Rotation")
            self.set_values([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", 1.0)
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic")
            self.set_values([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", 0)

            # Run the bake pass (bake roughness)
            self.bake_pass(context, "alpha", "ROUGHNESS", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 32, 0, [1, 1, 1, 1.0], True, int(margin * resolution / 2))

            # Revert the changes (re-flip)
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Anisotropic")
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", "Anisotropic Rotation")
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Alpha", "Roughness")

        # advanced: bake metallic from last bsdf output
        if pass_metallic:
            # Find all Principled BSDF nodes. Flip Roughness and Metallic (default_value and connection)
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Roughness")

            # Run the bake pass
            self.bake_pass(context, "metallic", "ROUGHNESS", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 32, 0, [0, 0, 0, 1.0], True, int(margin * resolution / 2))

            # Revert the changes (re-flip)
            self.swap_links([obj for obj in collection.all_objects if obj.type == "MESH"], "Metallic", "Roughness")

        # Pack to diffuse alpha (if selected)
        if pass_diffuse and ((diffuse_alpha_pack == "SMOOTHNESS" and pass_smoothness) or
                             (diffuse_alpha_pack == "TRANSPARENCY" and pass_alpha)):
            print("Packing to diffuse alpha")
            diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
            alpha_image = None
            if diffuse_alpha_pack == "SMOOTHNESS":
                alpha_image = bpy.data.images["SCRIPT_smoothness.png"]
            elif diffuse_alpha_pack == "TRANSPARENCY":
                alpha_image = bpy.data.images["SCRIPT_alpha.png"]
            pixel_buffer = list(diffuse_image.pixels)
            alpha_buffer = alpha_image.pixels[:]
            for idx in range(3, len(pixel_buffer), 4):
                pixel_buffer[idx] = alpha_buffer[idx - 3]
            diffuse_image.pixels[:] = pixel_buffer

        # Pack to metallic alpha (if selected)
        if pass_metallic and (metallic_alpha_pack == "SMOOTHNESS" and pass_smoothness):
            print("Packing to metallic alpha")
            metallic_image = bpy.data.images["SCRIPT_metallic.png"]
            alpha_image = bpy.data.images["SCRIPT_smoothness.png"]
            pixel_buffer = list(metallic_image.pixels)
            alpha_buffer = alpha_image.pixels[:]
            for idx in range(3, len(pixel_buffer), 4):
                pixel_buffer[idx] = alpha_buffer[idx - 3]
            metallic_image.pixels[:] = pixel_buffer

        # TODO: advanced: bake detail mask from diffuse node setup

        # TODO: specularity? would allow specular setups on pre-existing avatars

        # Bake AO
        if pass_ao:
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
                           (resolution, resolution), 512, 0, [1.0, 1.0, 1.0, 1.0], True, int(margin * resolution / 2))
            if illuminate_eyes:
                if "leyemask" in obj.modifiers:
                    obj.modifiers.remove(leyemask)
                if "reyemask" in obj.modifiers:
                    obj.modifiers.remove(reyemask)

        # Blend diffuse and AO to create Quest Diffuse (if selected)
        if pass_diffuse and pass_ao and pass_questdiffuse:
            if "SCRIPT_questdiffuse.png" in bpy.data.images:
                image = bpy.data.images["SCRIPT_questdiffuse.png"]
                image.user_clear()
                bpy.data.images.remove(image)
            bpy.ops.image.new(name="SCRIPT_questdiffuse.png", width=resolution, height=resolution,
                              generated_type="BLANK", alpha=False)
            image = bpy.data.images["SCRIPT_questdiffuse.png"]
            image.filepath = bpy.path.abspath("//CATS Bake/" + "SCRIPT_questdiffuse.png")
            diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
            ao_image = bpy.data.images["SCRIPT_ao.png"]
            image.generated_width = resolution
            image.generated_height = resolution
            image.scale(resolution, resolution)
            pixel_buffer = list(image.pixels)
            diffuse_buffer = diffuse_image.pixels[:]
            ao_buffer = ao_image.pixels[:]
            for idx in range(0, len(image.pixels)):
                if (idx % 4 != 3):
                    # Map range: set the black point up to 1-opacity
                    pixel_buffer[idx] = diffuse_buffer[idx] * ((1.0 - questdiffuse_opacity) + (questdiffuse_opacity * ao_buffer[idx]))
                else:
                    # Alpha is unused on quest, set to 1 to make sure unity doesn't keep it
                    pixel_buffer[idx] = 1.0
            image.pixels[:] = pixel_buffer

        # Bake highres normals
        if not use_decimation:
            # Just bake the traditional way
            if pass_normal:
                self.bake_pass(context, "normal", "NORMAL", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                               (resolution, resolution), 128, 0, [0.5, 0.5, 1.0, 1.0], True, int(margin * resolution / 2))
        else:
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
            # TODO: 32-bit floats so we don't lose detail
            if pass_normal:
                self.bake_pass(context, "world", "NORMAL", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                               (resolution, resolution), 128, 0, [0.5, 0.5, 1.0, 1.0], True, int(margin * resolution / 2), normal_space="OBJECT")

            # Decimate. If 'preserve seams' is selected, forcibly preserve seams (seams from islands, deselect seams)
            bpy.ops.cats_decimation.auto_decimate(armature_name=arm_copy.name, preserve_seams=preserve_seams, seperate_materials=False)

        # join meshes here if we didn't decimate
        if not use_decimation:
            Common.join_meshes(armature_name=arm_copy.name, repair_shape_keys=False)

        # Remove all other materials
        while len(context.object.material_slots) > 0:
            context.object.active_material_index = 0  # select the top material
            bpy.ops.object.material_slot_remove()

        # Apply generated material (object normals -> normal map -> BSDF normal and other textures)
        mat = bpy.data.materials.get("CATS Baked")
        if mat is not None:
            bpy.data.materials.remove(mat, do_unlink=True)
        # create material
        mat = bpy.data.materials.new(name="CATS Baked")
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
            if use_decimation:
                normaltexnode.image = bpy.data.images["SCRIPT_world.png"]
            normaltexnode.location.x -= 500
            normaltexnode.location.y -= 200

            normalmapnode = tree.nodes.new("ShaderNodeNormalMap")
            normalmapnode.space = "OBJECT"
            normalmapnode.location.x -= 200
            normalmapnode.location.y -= 200

            tree.links.new(normalmapnode.inputs["Color"], normaltexnode.outputs["Color"])
            tree.links.new(bsdfnode.inputs["Normal"], normalmapnode.outputs["Normal"])
        for child in collection.all_objects:
            if child.type == "MESH":
                child.data.materials.append(mat)

        # Remove old UV maps (if we created new ones)
        if generate_uvmap:
            for child in collection.all_objects:
                if child.type == "MESH":
                    uv_layers = child.data.uv_layers[:]
                    while uv_layers:
                        layer = uv_layers.pop()
                        if layer.name != "CATS UV" and layer.name != "Detail Map":
                            print("Removing UV {}".format(layer.name))
                            child.data.uv_layers.remove(layer)

        # Bake tangent normals
        if use_decimation and pass_normal:
            self.bake_pass(context, "normal", "NORMAL", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                           (resolution, resolution), 128, 0, [0.5, 0.5, 1.0, 1.0], True, int(margin * resolution / 2))

        # Update generated material to preview all of our passes
        if pass_normal:
            normaltexnode.image = bpy.data.images["SCRIPT_normal.png"]
            normalmapnode.space = "TANGENT"
        if pass_diffuse:
            diffusetexnode = tree.nodes.new("ShaderNodeTexImage")
            diffusetexnode.image = bpy.data.images["SCRIPT_diffuse.png"]
            diffusetexnode.location.x -= 300
            diffusetexnode.location.y += 500
            # If AO, blend in AO.
            if pass_ao:
                # AO -> Math (* ao_opacity + (1-ao_opacity)) -> Mix (Math, diffuse) -> Color
                aotexnode = tree.nodes.new("ShaderNodeTexImage")
                aotexnode.image = bpy.data.images["SCRIPT_ao.png"]
                aotexnode.location.x -= 700
                aotexnode.location.y += 800

                multiplytexnode = tree.nodes.new("ShaderNodeMath")
                multiplytexnode.operation = "MULTIPLY_ADD"
                multiplytexnode.inputs[1].default_value = questdiffuse_opacity
                multiplytexnode.inputs[2].default_value = 1.0 - questdiffuse_opacity
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
            metallictexnode.image = bpy.data.images["SCRIPT_metallic.png"]
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
                smoothnesstexnode.image = bpy.data.images["SCRIPT_smoothness.png"]
                invertnode = tree.nodes.new("ShaderNodeInvert")
                tree.links.new(invertnode.inputs["Color"], smoothnesstexnode.outputs["Color"])
                tree.links.new(bsdfnode.inputs["Roughness"], invertnode.outputs["Color"])
        if pass_alpha:
            if pass_diffuse and (diffuse_alpha_pack == "TRANSPARENCY"):
                tree.links.new(bsdfnode.inputs["Alpha"], diffusetexnode.outputs["Alpha"])
            else:
                alphatexnode = tree.nodes.new("ShaderNodeTexImage")
                alphatexnode.image = bpy.data.images["SCRIPT_alpha.png"]
                tree.links.new(bsdfnode.inputs["Alpha"], alphatexnode.outputs["Color"])
            mat.blend_method = 'CLIP'
        if pass_emit:
            emittexnode = tree.nodes.new("ShaderNodeTexImage")
            emittexnode.image = bpy.data.images["SCRIPT_emission.png"]
            emittexnode.location.x -= 800
            emittexnode.location.y -= 150
            tree.links.new(bsdfnode.inputs["Emission"], emittexnode.outputs["Color"])

        # TODO: Optionally cleanup bones as a last step
        # Select all bones which don't fuzzy match a whitelist (Chest, Head, etc) and do Merge Weights to parent on them
        # For now, just add a note saying you should merge bones manually

        # Export the model to the bake dir
        bpy.ops.object.select_all(action='DESELECT')
        for obj in collection.all_objects:
            obj.select_set(True)
            if obj.type == "MESH":
                obj.name = "Body"
            elif obj.type == "ARMATURE":
                obj.name = "Armature"
        if not os.path.exists(bpy.path.abspath("//CATS Bake/")):
            os.mkdir(bpy.path.abspath("//CATS Bake/"))
        bpy.ops.export_scene.fbx(filepath=bpy.path.abspath("//CATS Bake/Bake.fbx"), check_existing=False, filter_glob='*.fbx',
                                 use_selection=True,
                                 use_active_collection=False, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE',
                                 bake_space_transform=False, object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'},
                                 use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF', use_subsurf=False,
                                 use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y',
                                 secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True,
                                 bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True,
                                 bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, path_mode='AUTO',
                                 embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True,
                                 axis_forward='-Z', axis_up='Y')

        # Try to only output what you'll end up importing into unity.
        if pass_diffuse:
            bpy.data.images["SCRIPT_diffuse.png"].save()
        if pass_normal:
            bpy.data.images["SCRIPT_normal.png"].save()
        if pass_smoothness and (diffuse_alpha_pack != "SMOOTHNESS") and (metallic_alpha_pack != "SMOOTHNESS"):
            bpy.data.images["SCRIPT_smoothness.png"].save()
        if pass_ao:
            bpy.data.images["SCRIPT_ao.png"].save()
        if pass_diffuse and pass_ao and pass_questdiffuse:
            bpy.data.images["SCRIPT_questdiffuse.png"].save()
        if pass_emit:
            bpy.data.images["SCRIPT_emission.png"].save()
        if pass_alpha and (diffuse_alpha_pack != "TRANSPARENCY"):
            bpy.data.images["SCRIPT_alpha.png"].save()
        if pass_metallic:
            bpy.data.images["SCRIPT_metallic.png"].save()

        self.report({'INFO'}, t('cats_bake.info.success'))

        # Move armature so we can see it
        if quick_compare:
            arm_copy.location.x += arm_copy.dimensions.x

        print("BAKE COMPLETE!")
