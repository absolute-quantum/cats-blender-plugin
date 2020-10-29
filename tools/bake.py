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

        print("Baking objects: " + ",".join([obj.name for obj in objects]))

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
        self.perform_bake(context)
        return {'FINISHED'}
#        saved_data = Common.SavedData()
#
#        if context.scene.decimation_mode != 'CUSTOM':
#            mesh = Common.join_meshes(repair_shape_keys=False)
#            Common.separate_by_materials(context, mesh)
#
#
#        Common.join_meshes()
#
#        saved_data.load()

    def perform_bake(self, context):
        print('START BAKE')
        # Global options
        resolution = context.scene.bake_resolution
        use_decimation = context.scene.bake_use_decimation
        generate_uvmap = context.scene.bake_generate_uvmap
        prioritize_face = context.scene.bake_prioritize_face
        margin = 0.01

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
            # Make copies of the currently render-active UV layer, name "CATS UV"
            for child in collection.all_objects:
                if child.type == "MESH":
                    child.select_set(True)
                    bpy.context.view_layer.objects.active = child
                    bpy.ops.mesh.uv_texture_add()
                    child.data.uv_layers[-1].name = 'CATS UV'

            # Select all meshes. Select all UVs. Average islands scale
            bpy.context.view_layer.objects.active = next(child for child in arm_copy.children if child.type == "MESH")
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.select_all(action='SELECT')
            bpy.ops.uv.average_islands_scale() # Use blender average so we can make our own tweaks.
            bpy.ops.object.mode_set(mode='OBJECT')

            # TODO: Select all islands belonging to 'Head', 'LeftEye' and 'RightEye', separate islands, enlarge by 200% if selected
            # TODO: Look at all bones hierarchically from 'Head' and select those

            # Pack islands. Optionally use UVPackMaster if it's available
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.select_all(action='SELECT')
            if False: #TODO: detect if UVPackMaster installed and configured
                context.scene.uvp2_props.normalize_islands = False
                context.scene.uvp2_props.lock_overlapping_mode = '0' if use_decimation else '2'
                context.scene.uvp2_props.pack_to_others = False
                context.scene.uvp2_props.margin = margin
                context.scene.uvp2_props.similarity_threshold = 3
                context.scene.uvp2_props.precision = 500
                bpy.ops.uvpackmaster2.uv_pack()
            else:
                bpy.ops.uv.pack_islands(rotate=True, margin=margin)

        # TODO: ensure render engine is set to Cycles

        # Bake diffuse
        if pass_diffuse:
            self.bake_pass(context, "diffuse", "DIFFUSE", {"COLOR"}, [obj for obj in collection.all_objects if obj.type == "MESH"],
                SCRIPT_BAKE_SIZE, 1, 0, [0.5,0.5,0.5,1.0], True, int(margin * resolution / 2))

        # Bake roughness, invert
        if pass_smoothness:
            self.bake_pass(context, "smoothness", "ROUGHNESS", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                SCRIPT_BAKE_SIZE, 1, 0, [0.0,0.0,0.0,1.0], True, int(margin * resolution / 2))
            image = bpy.data.images["SCRIPT_smoothness.png"]
            for idx, pixel in enumerate(image.pixels):
                # invert r, g, b, but not a
                if (idx % 4) != 3:
                    pixel = 1.0 - pixel

        # Pack smoothness to diffuse alpha (if selected)
        if smoothness_diffusepack and pass_diffuse and pass_smoothness:
            diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
            smoothness_image = bpy.data.images["SCRIPT_smoothness.png"]
            for idx, pixel in enumerate(diffuse_image.pixels):
                if (idx % 4) == 3:
                    pixel = smoothness_image.pixels[idx - 3]


        # TODO: bake emit

        # TODO: advanced: bake alpha from diffuse node setup

        # TODO: advanced: bake metallic from diffuse node setup

        # TODO: advanced: bake detail mask from diffuse node setup

        # Bake AO
        if pass_ao:
            # TODO: Disable rendering of all objects in the scene except these ones.
            bake_pass("ao", "AO", {"AO"}, [obj for obj in collection.all_objects if and obj.type == "MESH"],
                SCRIPT_BAKE_SIZE, 512, 0, [1.0,1.0,1.0,1.0], True, int(margin * resolution / 2))
            # TODO: Re-enable rendering

        # Bake eyes AO to full brightness if selected

        # Blend diffuse and AO to create Quest Diffuse (if selected)
        if pass_diffuse and pass_ao and pass_questdiffuse:
            if "SCRIPT_questdiffuse.png" not in bpy.data.images:
                bpy.ops.image.new(name="SCRIPT_questdiffuse.png", width=resolution, height=resolution, color=background_color,
                    generated_type="BLANK", alpha=False)
            image = bpy.data.images["SCRIPT_questdiffuse.png"]
            diffuse_image = bpy.data.images["SCRIPT_diffuse.png"]
            ao_image = bpy.data.images["SCRIPT_ao.png"]
            image.generated_color = background_color
            image.generated_width=resolution
            image.generated_height=resolution
            image.scale(resolution, resolution)
            for idx, pixel in image.pixels:
                if (idx % 4 != 3):
                    pixel = diffuse_image.pixels[idx] * (1.0 - questdiffuse_opacity) * (questdiffuse_opacity * ao_image.pixels[idx])
                else:
                    pixel = diffuse_image.pixels[idx]

        # Bake highres normals
        if not use_decimate:
            # Just bake the traditional way
            if pass_normal:
                self.bake_pass(context, "normal", "NORMAL", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                    SCRIPT_BAKE_SIZE, 128, 0, [0.5,0.5,1.0,1.0], True, int(margin * resolution / 2))
        else:
            # Join meshes
            Common.join_meshes(armature=arm_copy.name, repair_shape_keys=False)

            # Bake normals in object coordinates
            bake_pass("world", "NORMAL", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                      SCRIPT_BAKE_SIZE, 128, 0, [0.5, 0.5, 1.0, 1.0], True, int(margin * resolution / 2), normal_space="OBJECT")

            # Decimate
            bpy.ops.cats_decimate.auto_decimate()

        # Remove all other materials
        while len(bpy.context.object.material_slots) > 0:
            bpy.context.object.active_material_index = 0 #select the top material
            bpy.ops.object.material_slot_remove()

        # Apply generated material (object normals -> normal map -> BSDF normal and other textures)

        # Remove old UV maps (if we created new ones)
        if generate_uvmap:
            for uv_layer in child.data.uv_layers:
                if uv_layer.name != "CATS UV" and uv_layer.name != "Detail Map":
                    child.data.uv_layers.remove(uv_layer)

        # Bake tangent normals
        if use_decimate and pass_normal:
            self.bake_pass(context, "normal", "NORMAL", set(), [obj for obj in collection.all_objects if obj.type == "MESH"],
                 SCRIPT_BAKE_SIZE, 128, 0, [0.5,0.5,1.0,1.0], True, int(margin * resolution / 2))


        # Update generated material to show tangents
