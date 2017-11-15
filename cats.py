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

import bpy
import random
import math
import mathutils
import numpy as np
from math import radians
from mathutils import Vector, Matrix


class AutoAtlasButton(bpy.types.Operator):
    bl_idname = 'auto.atlas'
    bl_label = 'Make atlas'

    def generateRandom(self, prefix='', suffix=''):
        return prefix + str(random.randrange(9999999999)) + suffix

    def execute(self, context):
        unhide_all()

        if not bpy.data.is_saved:
            self.report({'ERROR'}, 'You must save your blender file first, please save it to your assets folder so unity can discover the generated atlas file.')
            return {'CANCELLED'}

        bpy.context.scene.objects.active = bpy.data.objects[context.scene.mesh_name_atlas]
        bpy.data.objects[context.scene.mesh_name_atlas].select = True

        # Check uv index
        newUVindex = len(bpy.context.object.data.uv_textures) - 1
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

        # Check if the texture size is divisable by 512
        if not int(context.scene.texture_size) % 512 == 0:
            self.report({'ERROR'}, 'The texture size: ' + str(context.scene.texture_size) + ' is not divisable by 512.')
            return {'CANCELLED'}

        # Check if the texture size is over 4096
        if int(context.scene.texture_size) > 4096:
            self.report({'ERROR'}, 'The texture size: ' + str(context.scene.texture_size) + ' should not be more then 4096.')
            return {'CANCELLED'}

        # Add a UVMap
        bpy.ops.mesh.uv_texture_add()

        # Active object should be rendered
        bpy.context.object.hide_render = False

        # Go into edit mode, deselect and select all
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_all(action='SELECT')

        # Try to UV smart project
        bpy.ops.uv.smart_project(angle_limit=float(context.scene.angle_limit), island_margin=float(context.scene.island_margin))

        # Get or define the image file
        image_name = self.generateRandom('AtlasBake')
        if image_name in bpy.data.images:
            img = bpy.data.images[image_name]
        else:
            img = bpy.ops.image.new(name=image_name, alpha=True, width=int(context.scene.texture_size), height=int(context.scene.texture_size))

        img = bpy.data.images[image_name]

        # Set uv mapping to active image
        for uvface in bpy.context.object.data.uv_textures.active.data:
            uvface.image = img

        # Time to bake
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        bpy.data.scenes["Scene"].render.bake_type = "TEXTURE"
        bpy.data.screens['UV Editing'].areas[1].spaces[0].image = img
        bpy.ops.object.bake_image()

        # Lets save the generated atlas
        filename = self.generateRandom('//GeneratedAtlasBake', '.png')
        img.filepath_raw = filename
        img.file_format = 'PNG'
        img.save()

        # Deselect all and switch to object mode
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Delete all materials
        for ob in bpy.context.selected_editable_objects:
            ob.active_material_index = 0
            for i in range(len(ob.material_slots)):
                bpy.ops.object.material_slot_remove({'object': ob})

        # Create material slot
        matslot = bpy.ops.object.material_slot_add()
        new_mat = bpy.data.materials.new(name=self.generateRandom('AtlasBakedMat'))
        bpy.context.object.active_material = new_mat

        # Create texture slot from material slot and use generated atlas
        tex = bpy.data.textures.new(self.generateRandom('AtlasBakedTex'), 'IMAGE')
        tex.image = bpy.data.images.load(filename)
        slot = new_mat.texture_slots.add()
        slot.texture = tex

        # Remove orignal uv map and replace with generated
        uv_textures = bpy.context.object.data.uv_textures
        uv_textures.remove(uv_textures['UVMap'])
        uv_textures[0].name = 'UVMap'

        bpy.ops.mmd_tools.set_shadeless_glsl_shading()

        self.report({'INFO'}, 'Auto Atlas finished!')

        return{'FINISHED'}


class CreateEyesButton(bpy.types.Operator):
    bl_idname = 'create.eyes'
    bl_label = 'Create eye tracking'

    def bone_exists(self, bone):
        try:
            bpy.context.object.data.edit_bones[bone]
        except:
            self.report({'ERROR'}, 'The bone: ' + str(bone) + ' was not found')
            return False
        return True

    def set_to_center_mass(self, bone, center_mass_bone):
        bone.head = (bpy.context.object.data.edit_bones[center_mass_bone].head + bpy.context.object.data.edit_bones[center_mass_bone].tail) / 2
        bone.tail = (bpy.context.object.data.edit_bones[center_mass_bone].head + bpy.context.object.data.edit_bones[center_mass_bone].tail) / 2

    def find_center_vector_of_vertex_group(self, mesh_name, vertex_group):
        mesh = bpy.data.objects[mesh_name]

        group_lookup = {g.index: g.name for g in mesh.vertex_groups}
        verts = {name: [] for name in group_lookup.values()}
        for v in bpy.context.object.data.vertices:
            for g in v.groups:
                verts[group_lookup[g.group]].append(v)

        # Find the average vector point of the vertex cluster
        divide_by = len(verts[vertex_group])
        total = Vector()

        if divide_by == 0:
            return False

        for vertice in verts[vertex_group]:
            total += vertice.co

        average = total / divide_by

        return average

    def copy_vertex_group(self, mesh, vertex_group, rename_to):
        # iterate through the vertex group
        vertex_group_index = 0
        for group in bpy.data.objects[mesh].vertex_groups:
            # Find the vertex group
            if group.name == vertex_group:
                # Copy the group and rename
                bpy.data.objects[mesh].vertex_groups.active_index = vertex_group_index
                new_vertex_group = bpy.ops.object.vertex_group_copy()
                bpy.data.objects[mesh].vertex_groups[vertex_group + '_copy'].name = rename_to
                break

            vertex_group_index += 1

    def fix_eye_position(self, mesh_name, old_eyebone, eyebone):
        # Verify that the new eye bone is in the correct position
        # by comparing the old eye vertex group average vector location
        coords_eye = self.find_center_vector_of_vertex_group(mesh_name, old_eyebone)

        if coords_eye is False:
            return False

        vector_difference = Vector(np.subtract(coords_eye, eyebone.tail))

        # We want to have the eye bone ATLEAST behind the eye, not infront
        if vector_difference[1] > 0.01:
            # Check if the bone is too much behind the eye
            if vector_difference[1] < 0.4:
                eyebone.head[1] = eyebone.head[1] - 0.2
                eyebone.tail[1] = eyebone.tail[1] - 0.2

                return self.fix_eye_position(old_eyebone, eyebone)

            # Check if the bone is infront the eye, this is always bad
            if vector_difference[1] > 0:
                eyebone.head[1] = eyebone.head[1] + 0.2
                eyebone.tail[1] = eyebone.tail[1] + 0.2

                return self.fix_eye_position(old_eyebone, eyebone)

    def execute(self, context):
        unhide_all()

        # Select the armature
        for object in bpy.context.scene.objects:
            if object.type == 'ARMATURE':
                armature_object = object

        bpy.context.scene.objects.active = armature_object
        armature_object.select = True

        # Why does two times edit works?
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='EDIT')

        # Find the existing left eye bone
        if self.bone_exists(context.scene.eye_left) is False:
            return {'CANCELLED'}

        # Find the existing right eye bone
        if self.bone_exists(context.scene.eye_right) is False:
            return {'CANCELLED'}

        # Find the existing head bone
        if self.bone_exists(context.scene.head) is False:
            return {'CANCELLED'}

        # Create the new eye bones
        new_left_eye = bpy.context.object.data.edit_bones.new('LeftEye')
        new_right_eye = bpy.context.object.data.edit_bones.new('RightEye')

        # Parent them correctly
        new_left_eye.parent = bpy.context.object.data.edit_bones[context.scene.head]
        new_right_eye.parent = bpy.context.object.data.edit_bones[context.scene.head]

        # Use center of mass from old eye bone to place new eye bone in
        self.set_to_center_mass(new_right_eye, context.scene.eye_right)
        self.set_to_center_mass(new_left_eye, context.scene.eye_left)

        # Set the eye bone up straight
        new_right_eye.tail[2] = new_right_eye.head[2] + 0.3
        new_left_eye.tail[2] = new_left_eye.head[2] + 0.3

        # Switch to mesh
        bpy.context.scene.objects.active = bpy.data.objects[context.scene.mesh_name_eye]

        bpy.ops.object.mode_set(mode='OBJECT')

        # Make sure the bones are positioned correctly
        # not too far away from eye vertex (behind and infront)
        if context.scene.experimental_eye_fix:
            self.fix_eye_position(context.scene.mesh_name_eye, context.scene.eye_right, new_right_eye)
            self.fix_eye_position(context.scene.mesh_name_eye, context.scene.eye_left, new_left_eye)

        # Copy the existing eye vertex group to the new one
        self.copy_vertex_group(context.scene.mesh_name_eye, context.scene.eye_right, 'RightEye')
        self.copy_vertex_group(context.scene.mesh_name_eye, context.scene.eye_left, 'LeftEye')

        # Copy shape key mixes from user defined shape keys and rename them to the correct liking of VRC
        copy_shape_key(context.scene.mesh_name_eye, context.scene.wink_left, 'vrc.blink_left', 1)
        copy_shape_key(context.scene.mesh_name_eye, context.scene.wink_right, 'vrc.blink_right', 2)
        copy_shape_key(context.scene.mesh_name_eye, context.scene.lowerlid_left, 'vrc.lowerlid_left', 3)
        copy_shape_key(context.scene.mesh_name_eye, context.scene.lowerlid_right, 'vrc.lowerlid_right', 4)

        self.report({'INFO'}, 'Created eye tracking!')

        bpy.ops.object.editmode_toggle()

        return{'FINISHED'}


def unhide_all():
    for object in bpy.data.objects:
        object.hide = False


def copy_shape_key(target_mesh, shapekey_name, rename_to, new_index):
    mesh = bpy.data.objects[target_mesh]

    # first set value to 0 for all shape keys, so we don't mess up
    for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
        shapekey.value = 0

    for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
        if shapekey_name == shapekey.name:
            mesh.active_shape_key_index = index
            shapekey.value = 1
            mesh.shape_key_add(name=rename_to, from_mix=True)
            shapekey.value = 0

            # Select the created shapekey
            mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1

            # Re-adjust index position
            position_correct = False
            while position_correct is False:
                bpy.ops.object.shape_key_move(type='DOWN')

                if mesh.active_shape_key_index == new_index:
                    position_correct = True


class AutoVisemeButton(bpy.types.Operator):
    bl_idname = 'auto.viseme'
    bl_label = 'Create visemes'

    def mix_shapekey(self, target_mesh, shapekey_data, new_index, rename_to):
        mesh = bpy.data.objects[target_mesh]

        # first set value to 0 for all shape keys, so we don't mess up
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            shapekey.value = 0

        for shapekey_data_context in shapekey_data:
            selector = shapekey_data_context[0]
            shapekey_value = shapekey_data_context[1]

            for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                if selector == shapekey.name:
                    mesh.active_shape_key_index = index
                    shapekey.value = shapekey_value

        mesh.shape_key_add(name=rename_to, from_mix=True)
        bpy.ops.object.shape_key_clear()

        # Select the created shapekey
        mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1

        # Re-adjust index position
        position_correct = False
        while position_correct is False:
            bpy.ops.object.shape_key_move(type='DOWN')

            if mesh.active_shape_key_index == new_index:
                position_correct = True

    def execute(self, context):
        unhide_all()

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects.active = bpy.data.objects[context.scene.mesh_name_viseme]
        bpy.data.objects[context.scene.mesh_name_viseme].select = True

        # VISEME AA
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_a), (1)]
        ], 5, 'vrc.v_aa')

        # VISEME CH
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_ch), (1)]
        ], 6, 'vrc.v_ch')

        # VISEME DD
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_ch), (0.7)],
            [(context.scene.mouth_a), (0.3)]
        ], 7, 'vrc.v_dd')

        # VISEME EE
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_ch), (0.7)],
            [(context.scene.mouth_o), (0.3)]
        ], 8, 'vrc.v_ee')

        # VISEME FF
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_ch), (0.4)],
            [(context.scene.mouth_a), (0.2)]
        ], 9, 'vrc.v_ff')

        # VISEME IH
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_ch), (0.2)],
            [(context.scene.mouth_a), (0.5)]
        ], 10, 'vrc.v_ih')

        # VISEME KK
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_ch), (0.1)],
            [(context.scene.mouth_a), (0.2)]
        ], 11, 'vrc.v_kk')

        # VISEME NN
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_ch), (0.7)],
        ], 12, 'vrc.v_nn')

        # VISEME OH
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_o), (0.8)],
            [(context.scene.mouth_a), (0.2)],
        ], 13, 'vrc.v_oh')

        # VISEME OU
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_o), (0.2)],
            [(context.scene.mouth_a), (0.8)],
        ], 14, 'vrc.v_ou')

        # VISEME PP
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_o), (0.7)],
        ], 15, 'vrc.v_pp')

        # VISEME RR
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_o), (0.3)],
            [(context.scene.mouth_ch), (0.5)],
        ], 16, 'vrc.v_rr')

        # VISEME SIL
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_o), (0.001)],
        ], 17, 'vrc.v_sil')

        # VISEME SS
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_o), (0.8)],
        ], 18, 'vrc.v_ss')

        # VISEME TH
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_o), (0.15)],
            [(context.scene.mouth_a), (0.4)],
        ], 19, 'vrc.v_th')

        # VISEME E
        self.mix_shapekey(context.scene.mesh_name_viseme, [
            [(context.scene.mouth_ch), (0.7)],
            [(context.scene.mouth_o), (0.3)]
        ], 20, 'vrc.v_e')

        self.report({'INFO'}, 'Created mouth visemes!')

        return{'FINISHED'}


class ToolPanel(bpy.types.Panel):
    bl_label = 'Cats\'s MMD2VRC Blender Plugin'
    bl_idname = '3D_VIEW_TS_vrc'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'CATS'

    def draw(self, context):
        layout = self.layout

        layout.label(' > Auto Atlas')
        row = layout.row(align=True)

        row.prop(context.scene, 'island_margin')
        row = layout.row(align=True)

        row.prop(context.scene, 'angle_limit')
        row = layout.row(align=True)

        row.prop(context.scene, 'texture_size')
        row = layout.row(align=True)

        row.prop(context.scene, 'mesh_name_atlas')
        row = layout.row(align=True)

        row.prop(context.scene, 'one_texture')

        row = layout.row(align=True)
        row.operator('auto.atlas')

        layout.label('')
        layout.label(' > Auto Eye Tracking')
        row = layout.row(align=True)
        row.prop(context.scene, 'mesh_name_eye')
        row = layout.row(align=True)
        row.prop(context.scene, 'head')
        row = layout.row(align=True)
        row.prop(context.scene, 'eye_left')
        row = layout.row(align=True)
        row.prop(context.scene, 'eye_right')
        row = layout.row(align=True)
        row.prop(context.scene, 'wink_left')
        row = layout.row(align=True)
        row.prop(context.scene, 'wink_right')
        row = layout.row(align=True)
        row.prop(context.scene, 'lowerlid_left')
        row = layout.row(align=True)
        row.prop(context.scene, 'lowerlid_right')
        row = layout.row(align=True)
        row.prop(context.scene, 'experimental_eye_fix')
        row = layout.row(align=True)
        row.operator('create.eyes')

        layout.label('')
        layout.label(' > Auto Visemes')
        row = layout.row(align=True)
        row.prop(context.scene, 'mesh_name_viseme')
        row = layout.row(align=True)
        row.prop(context.scene, 'mouth_a')
        row = layout.row(align=True)
        row.prop(context.scene, 'mouth_o')
        row = layout.row(align=True)
        row.prop(context.scene, 'mouth_ch')
        row = layout.row(align=True)
        row.operator('auto.viseme')

        layout.label('')
        row = layout.row(align=True)
        row.label('Created by GiveMeAllYourCats')
        row = layout.row(align=True)
        row.label('For the VRC community <3')


def register():
    bpy.utils.register_class(ToolPanel)
    bpy.utils.register_class(AutoAtlasButton)
    bpy.utils.register_class(CreateEyesButton)
    bpy.utils.register_class(AutoVisemeButton)

    def get_armature():
        armature_name = ''
        for object in bpy.data.objects:
            if object.type == 'ARMATURE':
                return object.data

    def get_meshes(self, context):
        choices = []

        for object in bpy.context.scene.objects:
            if object.type == 'MESH':
                choices.append((object.name, object.name, object.name))

        bpy.types.Object.Enum = sorted(choices)
        return bpy.types.Object.Enum

    def get_bones(self, context):
        choices = []

        for bone in get_armature().bones:
            choices.append((bone.name, bone.name, bone.name))

        bpy.types.Object.Enum = sorted(choices)

        return bpy.types.Object.Enum

    def get_shapekeys(self, context):
        choices = []

        for shapekey in bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys.key_blocks:
            choices.append((shapekey.name, shapekey.name, shapekey.name))

        bpy.types.Object.Enum = sorted(choices)

        return bpy.types.Object.Enum

    def get_texture_sizes(self, context):
        bpy.types.Object.Enum = [
            ("1024", "1024 (low)", "1024"),
            ("2048", "2048 (medium)", "2048"),
            ("4096", "4096 (high)", "4096")
        ]

        return bpy.types.Object.Enum

    bpy.types.Scene.island_margin = bpy.props.FloatProperty(
        name='Margin',
        description='Margin to reduce bleed of adjacent islands',
        default=0.01
    )

    bpy.types.Scene.angle_limit = bpy.props.FloatProperty(
        name='Angle',
        description='Lower for more projection groups, higher for less distortion',
        default=82.0
    )

    bpy.types.Scene.texture_size = bpy.props.EnumProperty(
        name='Texture size',
        description='Lower for faster bake time, higher for more detail.',
        items=get_texture_sizes
    )

    bpy.types.Scene.one_texture = bpy.props.BoolProperty(
        name='Disable multiple textures',
        description='Texture baking and multiple textures per material can look weird in the end result. Check this box if you are experiencing this.',
        default=True
    )

    bpy.types.Scene.mesh_name_eye = bpy.props.EnumProperty(
        name='Mesh',
        description='The mesh with the eyes vertex groups',
        items=get_meshes
    )

    bpy.types.Scene.mesh_name_atlas = bpy.props.EnumProperty(
        name='Target mesh',
        description='The mesh that you want to create a atlas from',
        items=get_meshes
    )

    bpy.types.Scene.head = bpy.props.EnumProperty(
        name='Head',
        description='Head bone name',
        items=get_bones,
    )

    bpy.types.Scene.eye_left = bpy.props.EnumProperty(
        name='Left eye',
        description='Eye bone left name',
        items=get_bones,
    )

    bpy.types.Scene.eye_right = bpy.props.EnumProperty(
        name='Right eye',
        description='Eye bone right name',
        items=get_bones,
    )

    bpy.types.Scene.wink_right = bpy.props.EnumProperty(
        name='Blink right',
        description='The name of the shape key that controls wink right',
        items=get_shapekeys,
    )

    bpy.types.Scene.wink_left = bpy.props.EnumProperty(
        name='Blink left',
        description='The name of the shape key that controls wink left',
        items=get_shapekeys,
    )

    bpy.types.Scene.lowerlid_right = bpy.props.EnumProperty(
        name='Lowerlid right',
        description='The name of the shape key that controls lowerlid right',
        items=get_shapekeys,
    )

    bpy.types.Scene.lowerlid_left = bpy.props.EnumProperty(
        name='Lowerlid left',
        description='The name of the shape key that controls lowerlid left',
        items=get_shapekeys,
    )

    bpy.types.Scene.experimental_eye_fix = bpy.props.BoolProperty(
        name='Experimental eye fix',
        description='Script will try to verify the newly created eye bones to be located in the correct position, this works by checking the location of the old eye vertex group. It is very useful for models that have over-extended eye bones that point out of the head',
        default=False
    )

    bpy.types.Scene.mesh_name_viseme = bpy.props.EnumProperty(
        name='Mesh',
        description='The mesh with the mouth shape keys',
        items=get_meshes
    )

    bpy.types.Scene.mouth_a = bpy.props.EnumProperty(
        name='Viseme A',
        description='The name of the shape key that controls the mouth movement that looks like someone is saying A',
        items=get_shapekeys,
    )

    bpy.types.Scene.mouth_o = bpy.props.EnumProperty(
        name='Viseme OH',
        description='The name of the shape key that controls the mouth movement that looks like someone is saying OH',
        items=get_shapekeys,
    )

    bpy.types.Scene.mouth_ch = bpy.props.EnumProperty(
        name='Viseme CH',
        description='The name of the shape key that controls the mouth movement that looks like someone is saying CH',
        items=get_shapekeys,
    )


def unregister():
    bpy.utils.unregister_class(ToolPanel)
    bpy.utils.unregister_class(AutoAtlasButton)
    bpy.utils.unregister_class(CreateEyesButton)
    bpy.utils.unregister_class(AutoVisemeButton)

if __name__ == '__main__':
    register()
