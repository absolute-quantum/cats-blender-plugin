# MIT License

# Copyright (c) 2020 GiveMeAllYourCats

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
# Edits by: Feilen

import bpy

from . import common as Common
from .register import register_wrap
from ..translations import t

@register_wrap
class BakeButton(bpy.types.Operator):
    bl_idname = 'cats_bake.bake'
    bl_label = 'Copy and Bake (SLOW!)'
    bl_description = "Perform the bake. Warning, this performs an actual render!\n" \
                     "This will create a copy of your avatar to leave the original alone.\n" \
                     "Depending on your machine, this could take an hour or more."
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        #if not meshes or len(meshes) == 0:
        #    return False
        return True

    # "Bake pass" function. Run a single bake to "<bake_name>.png" against all selected objects.
    # When baking selected to active, only bake two objects at a time.
    def bake_pass(self, context, bake_name, bake_type, bake_pass_filter, objects, bake_size, bake_samples, bake_ray_distance, background_color, clear, bake_margin, bake_active=None, bake_multires=False, normal_space='TANGENT'):
        bpy.ops.object.select_all(action='DESELECT')
        if bake_active is not None:
            bake_active.select_set(True)
            context.view_layer.objects.active = bake_active

        print("Baking " + bake_name + " for objects: " + ",".join([obj.name for obj in objects]))

        if "SCRIPT_" + bake_name + ".png" not in bpy.data.images:
            bpy.ops.image.new(name="SCRIPT_" + bake_name + ".png", width=bake_size[0], height=bake_size[1], color=background_color,
                generated_type="BLANK", alpha=True)
        image = bpy.data.images["SCRIPT_" + bake_name + ".png"]
        if clear:
            image.alpha_mode = "NONE"
            image.generated_color = background_color
            image.generated_width=bake_size[0]
            image.generated_height=bake_size[1]
            image.pixels[:] = background_color * bake_size[0] * bake_size[1]
            image.scale(bake_size[0], bake_size[1])
            if bake_type == 'NORMAL' or bake_type == 'ROUGHNESS':
                image.colorspace_settings.name = 'Non-Color'
            if bake_type == 'DIFFUSE': # For packing smoothness to alpha
                image.alpha_mode = 'CHANNEL_PACKED'

        # Select only objects we're baking
        for obj in objects:
            obj.select_set(True)

        # For all materials in use, change any value node labeled "bake_<bake_name>" to 1.0, then back to 0.0.
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material:
                    for node in obj.active_material.node_tree.nodes:
                        if node.label == "bake_" + bake_name:
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
            #pass_filter=bake_pass_filter,
            use_clear= clear and bake_type == 'NORMAL',
            #uv_layer="SCRIPT",
            use_selected_to_active=(bake_active != None),
            cage_extrusion=bake_ray_distance,
            normal_space=normal_space
        )
        # For all materials in use, change any value node labeled "bake_<bake_name>" to 1.0, then back to 0.0.
        for obj in objects:
            for slot in obj.material_slots:
                if slot.material:
                    for node in obj.active_material.node_tree.nodes:
                        if node.label == "bake_" + bake_name:
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
        meshes = Common.get_meshes_objects()
        if not meshes or len(meshes) == 0:
            self.report({'ERROR'}, "No meshes found!")
            return {'FINISHED'}
        if context.scene.render.engine != 'CYCLES':
            self.report({'ERROR'}, "You need to set your render engine to Cycles first!")
            return {'FINISHED'}
#        saved_data = Common.SavedData()
        # TODO: Check if any UV islands are self-overlapping, emit an error
        self.perform_bake(context)
        return {'FINISHED'}
#        saved_data.load()

    def perform_bake(self, context):
        print('START BAKE')
        # Global options
        resolution = context.scene.bake_resolution
        use_decimation = context.scene.bake_use_decimation
        preserve_seams = context.scene.bake_preserve_seams
        generate_uvmap = context.scene.bake_generate_uvmap
        prioritize_face = context.scene.bake_prioritize_face
        prioritize_factor = 2.0
        margin = 0.01

        # TODO: Option to seperate by loose parts and bake selected to active

        # Passes
        pass_diffuse = context.scene.bake_pass_diffuse
        pass_normal = context.scene.bake_pass_normal
        pass_smoothness = context.scene.bake_pass_smoothness
        pass_ao = context.scene.bake_pass_ao
        pass_questdiffuse = context.scene.bake_pass_questdiffuse

        # Pass options
        illuminate_eyes = context.scene.bake_illuminate_eyes
        questdiffuse_opacity = context.scene.bake_questdiffuse_opacity
        smoothness_diffusepack = context.scene.bake_smoothness_diffusepack

         # Create an output collection
        collection = bpy.data.collections.new("CATS Bake")
        context.scene.collection.children.link(collection)

        # Tree-copy all meshes
        armature = Common.get_armature()
        arm_copy = self.tree_copy(armature, None, collection)

        # Make sure all armature modifiers target the new armature
        for child in collection.all_objects:
            for modifier in child.modifiers:
                if modifier.type == "ARMATURE":
                    modifier.object = arm_copy

        if generate_uvmap:
            bpy.ops.object.select_all(action='DESELECT')
            # Make copies of the currently render-active UV layer, name "CATS UV"
            for child in collection.all_objects:
                if child.type == "MESH":
                    child.select_set(True)
                    context.view_layer.objects.active = child
                    bpy.ops.mesh.uv_texture_add()
                    child.data.uv_layers[-1].name = 'CATS UV'

            # Select all meshes. Select all UVs. Average islands scale
            context.view_layer.objects.active = next(child for child in arm_copy.children if child.type == "MESH")
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.average_islands_scale() # Use blender average so we can make our own tweaks.
            bpy.ops.object.mode_set(mode='OBJECT')

            # Select all islands belonging to 'Head', 'LeftEye' and 'RightEye', separate islands, enlarge by 200% if selected
            # TODO: Look at all bones hierarchically from 'Head' and select those
            for obj in collection.all_objects:
                if obj.type != "MESH":
                    continue
                context.view_layer.objects.active = obj
                for group in ["Head", "LeftEye", "RightEye"]:
                    if group in obj.vertex_groups:
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
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.select_all(action='SELECT')
            try: # detect if UVPackMaster installed and configured
                context.scene.uvp2_props.normalize_islands = False
                context.scene.uvp2_props.lock_overlapping_mode = '0' if use_decimation else '2'
                context.scene.uvp2_props.pack_to_others = False
                context.scene.uvp2_props.margin = margin
                context.scene.uvp2_props.similarity_threshold = 3
                context.scene.uvp2_props.precision = 500
                bpy.ops.uvpackmaster2.uv_pack()
            except AttributeError:
                bpy.ops.uv.pack_islands(rotate=True, margin=margin)

        # Bake diffuse
        Common.switch('OBJECT')
        if pass_diffuse:
            self.bake_pass(context, "diffuse", "DIFFUSE", {"COLOR"}, [obj for obj in collection.all_objects if obj.type == "MESH"],
                (resolution, resolution), 1, 0, [0.5,0.5,0.5,1.0], True, int(margin * resolution / 2))

        # Bake roughness, invert
        if pass_smoothness:
            self.bake_pass(context, "smoothness", "ROUGHNESS", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                (resolution, resolution), 1, 0, [1.0,1.0,1.0,1.0], True, int(margin * resolution / 2))
            image = bpy.data.images["SCRIPT_smoothness.png"]
            pixel_buffer = list(image.pixels)
            for idx in range(0, len(image.pixels)):
                # invert r, g, b, but not a
                if (idx % 4) != 3:
                    pixel_buffer[idx] = 1.0 - pixel_buffer[idx]
            image.pixels[:] = pixel_buffer


        # Pack smoothness to diffuse alpha (if selected)
        if smoothness_diffusepack and pass_diffuse and pass_smoothness:
            print("Packing smoothness to diffuse alpha")
            diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
            smoothness_image = bpy.data.images["SCRIPT_smoothness.png"]
            pixel_buffer = list(diffuse_image.pixels)
            smoothness_buffer = smoothness_image.pixels[:]
            for idx in range(3, len(pixel_buffer), 4):
                pixel_buffer[idx] = smoothness_buffer[idx - 3]
            diffuse_image.pixels[:] = pixel_buffer


        # TODO: bake emit

        # TODO: advanced: bake alpha from diffuse node setup

        # TODO: advanced: bake metallic from diffuse node setup

        # TODO: advanced: bake detail mask from diffuse node setup

        # Bake AO
        if pass_ao:
            # TODO: Add modifiers that prevent LeftEye and RightEye being baked
            # TODO: Disable rendering of all objects in the scene except these ones.
            self.bake_pass(context, "ao", "AO", {"AO"}, [obj for obj in collection.all_objects if obj.type == "MESH"],
                (resolution, resolution), 512, 0, [1.0,1.0,1.0,1.0], True, int(margin * resolution / 2))
            # TODO: Re-enable rendering

        # Blend diffuse and AO to create Quest Diffuse (if selected)
        if pass_diffuse and pass_ao and pass_questdiffuse:
            if "SCRIPT_questdiffuse.png" not in bpy.data.images:
                bpy.ops.image.new(name="SCRIPT_questdiffuse.png", width=resolution, height=resolution,
                    generated_type="BLANK", alpha=False)
            image = bpy.data.images["SCRIPT_questdiffuse.png"]
            diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
            ao_image = bpy.data.images["SCRIPT_ao.png"]
            image.generated_width=resolution
            image.generated_height=resolution
            image.scale(resolution, resolution)
            pixel_buffer = list(image.pixels)
            diffuse_buffer = diffuse_image.pixels[:]
            ao_buffer = ao_image.pixels[:]
            for idx in range(0, len(image.pixels)):
                if (idx % 4 != 3):
                    # Map range: set the black point up to 1-opacity
                    pixel_buffer[idx] = diffuse_buffer[idx] * ((1.0 - questdiffuse_opacity) + (questdiffuse_opacity * ao_buffer[idx]))
                else:
                    # Just copy alpha
                    pixel_buffer[idx] = diffuse_buffer[idx]
            image.pixels[:] = pixel_buffer


        # Bake highres normals
        if not use_decimation:
            # Just bake the traditional way
            if pass_normal:
                self.bake_pass(context, "normal", "NORMAL", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                    (resolution, resolution), 128, 0, [0.5,0.5,1.0,1.0], True, int(margin * resolution / 2))
        else:
            # Join meshes
            Common.join_meshes(armature_name=arm_copy.name, repair_shape_keys=False)

            # Bake normals in object coordinates
            if pass_normal:
                self.bake_pass(context, "world", "NORMAL", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                      (resolution, resolution), 128, 0, [0.5, 0.5, 1.0, 1.0], True, int(margin * resolution / 2), normal_space="OBJECT")

            # Decimate. If 'preserve seams' is selected, forcibly preserve seams (seams from islands, deselect seams)
            bpy.ops.cats_decimation.auto_decimate(armature_name=arm_copy.name, preserve_seams=preserve_seams, seperate_materials=False)

        # Remove all other materials
        while len(context.object.material_slots) > 0:
            context.object.active_material_index = 0 #select the top material
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
        bsdfnode.inputs["Specular"].default_value = 0
        if pass_normal:
            normaltexnode = tree.nodes.new("ShaderNodeTexImage")
            if use_decimation:
               normaltexnode.image = bpy.data.images["SCRIPT_world.png"]

            normalmapnode = tree.nodes.new("ShaderNodeNormalMap")
            normalmapnode.space = "OBJECT"

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
                 (resolution, resolution), 128, 0, [0.5,0.5,1.0,1.0], True, int(margin * resolution / 2))

        # Update generated material to preview all of our passes
        if pass_normal:
            normaltexnode.image = bpy.data.images["SCRIPT_normal.png"]
            normalmapnode.space = "TANGENT"
        if pass_diffuse:
            diffusetexnode = tree.nodes.new("ShaderNodeTexImage")
            diffusetexnode.image = bpy.data.images["SCRIPT_diffuse.png"]
            tree.links.new(bsdfnode.inputs["Base Color"], diffusetexnode.outputs["Color"])
        if pass_smoothness:
            if smoothness_diffusepack and pass_diffuse:
                invertnode = tree.nodes.new("ShaderNodeInvert")
                tree.links.new(invertnode.inputs["Color"], diffusetexnode.outputs["Alpha"])
                tree.links.new(bsdfnode.inputs["Roughness"], invertnode.outputs["Color"])
            else:
                smoothnesstexnode = tree.nodes.new("ShaderNodeTexImage")
                smoothnesstexnode.image = bpy.data.images["SCRIPT_smoothness.png"]
                invertnode = tree.nodes.new("ShaderNodeInvert")
                tree.links.new(invertnode.inputs["Color"], smoothnesstexnode.outputs["Color"])
                tree.links.new(bsdfnode.inputs["Roughness"], invertnode.outputs["Color"])

        # Move armature so we can see it
        arm_copy.location.x += arm_copy.dimensions.x
