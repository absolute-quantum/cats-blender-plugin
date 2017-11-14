# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

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
    bl_label  = 'Make atlas'

    def execute(self, context):
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
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        
        # Try to UV smart project
        bpy.ops.uv.smart_project(angle_limit = float(context.scene.angle_limit), island_margin = float(context.scene.island_margin))
        
        # Get or define the image file
        image_name = generateRandom('AtlasBake')
        if image_name in bpy.data.images:
            img = bpy.data.images[image_name]
        else:
            img = bpy.ops.image.new(name = image_name, alpha = True, width = int(context.scene.texture_size), height = int(context.scene.texture_size))
            
        img = bpy.data.images[image_name]
        
        # Set uv mapping to active image
        for uvface in bpy.context.object.data.uv_textures.active.data:
            uvface.image = img
        
        # Time to bake
        bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
        bpy.data.scenes["Scene"].render.bake_type = "TEXTURE"
        bpy.data.screens['UV Editing'].areas[1].spaces[0].image = img
        bpy.ops.object.bake_image()
        
        # Lets save the generated atlas
        filename = generateRandom('//GeneratedAtlasBake', '.png')
        
        # TODO: cannot use alpha? gets a black image render
        # confirm in unity if this is a problem
        
        # img.use_alpha  = True
        # img.alpha_mode = 'STRAIGHT'
        
        img.filepath_raw = filename
        img.file_format  = 'PNG'
        img.save()
        
        # Deselect all and switch to object mode
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Delete all materials
        for ob in bpy.context.selected_editable_objects:
            ob.active_material_index = 0
            for i in range(len(ob.material_slots)):
                bpy.ops.object.material_slot_remove({'object': ob})
        
        # Create material slot
        matslot             = bpy.ops.object.material_slot_add()
        new_mat             = bpy.data.materials.new(name = generateRandom('AtlasBakedMat'))
        bpy.context.object.active_material = new_mat
        
        # Create texture slot from material slot and use generated atlas
        tex          = bpy.data.textures.new(generateRandom('AtlasBakedTex'), 'IMAGE')
        tex.image    = bpy.data.images.load(filename)
        slot         = new_mat.texture_slots.add()
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
                
    def find_center_vector_of_vertex_group(self, vertex_group):
        group_lookup = {g.index: g.name for g in bpy.context.object.vertex_groups}
        verts = {name: [] for name in group_lookup.values()}
        for v in bpy.context.object.data.vertices:
            for g in v.groups:
                verts[group_lookup[g.group]].append(v)
        
        # Find the average vector point of the vertex cluster
        divide_by = len(verts[vertex_group])
        total = Vector()
        
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
            
    def fix_eye_position(self, old_eyebone, eyebone, i = 0):
        i += 1
        
        if i > 60:
            return
        
        # Verify that the new eye bone is in the correct position
        # by comparing the old eye vertex group average vector location
        coords_eye = self.find_center_vector_of_vertex_group(old_eyebone)
        vector_difference = Vector(np.subtract(coords_eye, eyebone.tail))
        
        # Check if the bone is too much behind the eye 
        if vector_difference[1] < 0:
            print('bone', eyebone, 'behind, moving -0.3', vector_difference)
            eyebone.head[1] = eyebone.head[1] - 0.3
            eyebone.tail[1] = eyebone.tail[1] - 0.3
            
            return self.fix_eye_position(old_eyebone, eyebone, i)
        
        # Check if the bone is too much infront the eye 
        if vector_difference[1] > 0:
            print('bone', eyebone, 'infront, moving +0.3', vector_difference)
            eyebone.head[1] = eyebone.head[1] + 0.3
            eyebone.tail[1] = eyebone.tail[1] + 0.3
            
            return self.fix_eye_position(old_eyebone, eyebone, i)
 
    def execute(self, context):
        # Select the armature
        for object in bpy.context.scene.objects:
            if object.type == 'ARMATURE':
                armature_object = object
                
        bpy.context.scene.objects.active = armature_object
        armature_object.select = True
        
        # Why does two times edit works?
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        
        # Find the existing left eye bone
        if self.bone_exists(context.scene.eye_left) == False:
            return {'CANCELLED'}
        
        # Find the existing right eye bone
        if self.bone_exists(context.scene.eye_right) == False:
            return {'CANCELLED'}
        
        # Find the existing head bone
        if self.bone_exists(context.scene.head) == False:
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
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Make sure the bones are positioned correctly
        # not too far away from eye vertex (behind and infront)
        self.fix_eye_position(context.scene.eye_right, new_right_eye)
        self.fix_eye_position(context.scene.eye_left, new_left_eye)
        
        # Copy the existing eye vertex group to the new one
        self.copy_vertex_group(context.scene.mesh_name_eye, context.scene.eye_right, 'RightEye')
        self.copy_vertex_group(context.scene.mesh_name_eye, context.scene.eye_left, 'LeftEye')

        self.report({'INFO'}, 'Created eye tracking!')
        
        return{'FINISHED'}
        
def generateRandom(prefix = '', suffix = ''):
    return prefix + str(random.randrange(9999999999)) + suffix

class ToolPanel(bpy.types.Panel):
    bl_label       = 'Cats\'s VRC Blender Plugin'
    bl_idname      = '3D_VIEW_TS_vrc'
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category    = 'CATS'

    def draw(self, context):
        layout = self.layout
 
        layout.label(' > Auto Atlas')
        row = layout.row(align = True)
        
        row.prop(context.scene, 'island_margin')
        row = layout.row(align = True)
        
        row.prop(context.scene, 'angle_limit')
        row = layout.row(align = True)
        
        row.prop(context.scene, 'texture_size')
        row = layout.row(align = True)
        
        row.prop(context.scene, 'mesh_name_atlas')
        row = layout.row(align = True)
        
        row.prop(context.scene, 'one_texture')

        row = layout.row(align = True)
        row.operator('auto.atlas')
        
        layout.label('')
        layout.label(' > Eye Tracking')
        row = layout.row(align = True)
        row.prop(context.scene, 'mesh_name_eye')
        row = layout.row(align = True)
        row.prop(context.scene, 'head')
        row = layout.row(align = True)
        row.prop(context.scene, 'eye_left')
        row = layout.row(align = True)
        row.prop(context.scene, 'eye_right')
        row = layout.row(align = True)
        row.operator('create.eyes')
        
        layout.label('')
        row = layout.row(align = True)
        row.label('Created by GiveMeAllYourCats')
        row = layout.row(align = True)
        row.label('For the VRC community <3')
        
def get_meshes(self, context):
    choices = []
    
    for object in bpy.context.scene.objects:
        if object.type == 'MESH':
            choices.append((object.name, object.name, object.name))

    bpy.types.Object.Enum = sorted(choices)
    return bpy.types.Object.Enum
        
def get_bones(self, context):
    choices = []
    
    for bone in bpy.data.armatures[0].bones:
        choices.append((bone.name, bone.name, bone.name))

    bpy.types.Object.Enum = sorted(choices)

    return bpy.types.Object.Enum

def get_texture_sizes(self, context):
    bpy.types.Object.Enum = [("1024", "1024", "1024"), ("2048", "2048", "2048"), ("4096", "4096", "4096")]
    
    return bpy.types.Object.Enum
        
def register():
    bpy.utils.register_class(ToolPanel)
    bpy.utils.register_class(AutoAtlasButton)
    bpy.utils.register_class(CreateEyesButton)
    
    bpy.types.Scene.island_margin = bpy.props.FloatProperty (
        name = 'Margin',
        description = 'Margin to reduce bleed of adjacent islands',
        default = 0.01
    )
    
    bpy.types.Scene.angle_limit = bpy.props.FloatProperty (
        name = 'Angle',
        description = 'Lower for more projection groups, higher for less distortion',
        default = 82.0
    )
    
    bpy.types.Scene.texture_size = bpy.props.EnumProperty (
        name = 'Texture size',
        description = 'Lower for faster bake time, higher for more detail.',
        items = get_texture_sizes
    )
      
    bpy.types.Scene.one_texture = bpy.props.BoolProperty(
        name = 'Disable multiple textures',
        description = 'Texture baking and multiple textures per material can look weird in the end result. Check this box if you are experiencing this.',
        default = True
    ) 
      
    bpy.types.Scene.mesh_name_eye = bpy.props.EnumProperty(
        name  = 'Mesh name',
        description = 'The mesh with the eyes vertex groups',
        items = get_meshes
    )
      
    bpy.types.Scene.mesh_name_atlas = bpy.props.EnumProperty(
        name  = 'Target mesh',
        description = 'The mesh that you want to create a atlas from',
        items = get_meshes
    )
      
    bpy.types.Scene.head = bpy.props.EnumProperty(
        name = 'Head name',
        description = 'Head bone name',
        items = get_bones,
    )
      
    bpy.types.Scene.eye_left = bpy.props.EnumProperty(
        name = 'Left eye name',
        description = 'Eye bone left name',
        items = get_bones,
    )
      
    bpy.types.Scene.eye_right = bpy.props.EnumProperty(
        name = 'Right eye name',
        description = 'Eye bone right name',
        items = get_bones,
    )

def unregister():
    bpy.utils.unregister_class(ToolPanel)
    bpy.utils.unregister_class(AutoAtlasButton)
    bpy.utils.unregister_class(CreateEyesButton)

if __name__ == '__main__':
    register()
