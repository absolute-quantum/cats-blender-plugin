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

# Code author: Hotox
# Repo: https://github.com/michaeldegroot/cats-blender-plugin

import bpy
import copy
import webbrowser

from . import common as Common
from . import armature_bones as Bones
from .register import register_wrap
from ..translations import t


@register_wrap
class MergeArmature(bpy.types.Operator):
    bl_idname = 'cats_custom.merge_armatures'
    bl_label = t('MergeArmature.label')
    bl_description = t('MergeArmature.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(Common.get_armature_objects()) > 1

    def execute(self, context):
        saved_data = Common.SavedData()

        # Set default stage
        Common.set_default_stage()
        Common.unselect_all()

        # Get both armatures
        base_armature_name = bpy.context.scene.merge_armature_into
        merge_armature_name = bpy.context.scene.merge_armature
        base_armature = Common.get_objects()[base_armature_name]
        merge_armature = Common.get_objects()[merge_armature_name]

        if not merge_armature:
            saved_data.load()
            Common.show_error(5.2, [t('MergeArmature.error.notFound', name=merge_armature_name)])
            return {'CANCELLED'}
        if not base_armature:
            saved_data.load()
            Common.show_error(5.2, [t('MergeArmature.error.notFound', name=base_armature_name)])
            return {'CANCELLED'}

        merge_parent = merge_armature.parent
        base_parent  = base_armature.parent
        if merge_parent or base_parent:
            if context.scene.merge_same_bones:
                if merge_parent:
                    for i in [0, 1, 2]:
                        if merge_parent.scale[i] != 1 or merge_parent.location[i] != 0 or merge_parent.rotation_euler[i] != 0:
                            saved_data.load()
                            Common.show_error(6.5, t('MergeArmature.error.checkTransforms'))
                            return {'CANCELLED'}
                    Common.delete(merge_armature.parent)

                if base_parent:
                    for i in [0, 1, 2]:
                        if base_parent.scale[i] != 1 or base_parent.location[i] != 0 or base_parent.rotation_euler[i] != 0:
                            saved_data.load()
                            Common.show_error(6.5, t('MergeArmature.error.checkTransforms'))
                            return {'CANCELLED'}
                    Common.delete(base_armature.parent)
            else:
                saved_data.load()
                Common.show_error(6.2, t('MergeArmature.error.pleaseFix'))
                return {'CANCELLED'}

        # if len(Common.get_meshes_objects(armature_name=merge_armature_name)) == 0:
        #     saved_data.load()
        #     Common.show_error(5.2, ['The armature "' + merge_armature_name + '" does not have any meshes.'])
        #     return {'CANCELLED'}
        # if len(Common.get_meshes_objects(armature_name=base_armature_name)) == 0:
        #     saved_data.load()
        #     Common.show_error(5.2, ['The armature "' + base_armature_name + '" does not have any meshes.'])
        #     return {'CANCELLED'}

        # Merge armatures
        merge_armatures(base_armature_name, merge_armature_name, False, merge_same_bones=context.scene.merge_same_bones)

        saved_data.load()

        self.report({'INFO'}, t('MergeArmature.success'))
        return {'FINISHED'}


@register_wrap
class AttachMesh(bpy.types.Operator):
    bl_idname = 'cats_custom.attach_mesh'
    bl_label = t('AttachMesh.label')
    bl_description = t('AttachMesh.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(Common.get_armature_objects()) > 0 and len(Common.get_meshes_objects(mode=1, check=False)) > 0

    def execute(self, context):
        saved_data = Common.SavedData()

        # Set default stage
        Common.set_default_stage()
        Common.unselect_all()

        # Get armature and mesh
        mesh_name = bpy.context.scene.attach_mesh
        base_armature_name = bpy.context.scene.merge_armature_into
        attach_bone_name = bpy.context.scene.attach_to_bone
        mesh = Common.get_objects()[mesh_name]

        # Create new armature
        bpy.ops.object.armature_add(location=(0, 0, 0))
        new_armature = bpy.context.active_object

        # Reparent mesh to new armature
        mesh.parent = new_armature
        mesh.parent_type = 'OBJECT'

        # Rename bone in new armature
        new_armature.data.bones.get('Bone').name = attach_bone_name

        # Switch mesh to edit mode
        Common.unselect_all()
        Common.set_active(mesh)
        Common.switch('EDIT')

        # Delete all previous vertex groups
        if mesh.vertex_groups:
            bpy.ops.object.vertex_group_remove(all=True)

        # Select and assign all vertices to new vertex group
        bpy.ops.mesh.select_all(action='SELECT')
        mesh.vertex_groups.new(name=attach_bone_name)
        bpy.ops.object.vertex_group_assign()

        Common.switch('OBJECT')

        # Create new armature modifier
        mod = mesh.modifiers.new('Armature', 'ARMATURE')
        mod.object = new_armature

        # Merge armatures
        merge_armatures(base_armature_name, new_armature.name, True, mesh_name=mesh_name)

        saved_data.load()

        self.report({'INFO'}, t('AttachMesh.success'))
        return {'FINISHED'}


@register_wrap
class CustomModelTutorialButton(bpy.types.Operator):
    bl_idname = 'cats_custom.tutorial'
    bl_label = t('CustomModelTutorialButton.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('CustomModelTutorialButton.URL'))

        self.report({'INFO'}, t('CustomModelTutorialButton.success'))
        return {'FINISHED'}


def merge_armatures(base_armature_name, merge_armature_name, mesh_only, mesh_name=None, merge_same_bones=False):
    tolerance = 0.00008726647  # around 0.005 degrees
    base_armature = Common.get_objects()[base_armature_name]
    merge_armature = Common.get_objects()[merge_armature_name]

    # Fixes bones disappearing, prevents bones from having their tail and head at the exact same position
    x_cord, y_cord, z_cord, fbx = Common.get_bone_orientations(base_armature)
    Common.fix_zero_length_bones(base_armature, x_cord, y_cord, z_cord)
    x_cord, y_cord, z_cord, fbx = Common.get_bone_orientations(merge_armature)
    Common.fix_zero_length_bones(merge_armature, x_cord, y_cord, z_cord)

    # Get all meshes and join if neccessary
    if bpy.context.scene.merge_armatures_join_meshes:
        meshes_base = [Common.join_meshes(armature_name=base_armature_name, apply_transformations=False)]
        meshes_merge = [Common.join_meshes(armature_name=merge_armature_name, apply_transformations=False)]
    else:
        meshes_base = Common.get_meshes_objects(armature_name=base_armature_name)
        meshes_merge = Common.get_meshes_objects(armature_name=merge_armature_name)

    # Make sure the list is really empty if it should be
    if len(meshes_base) == 1 and not meshes_base[0]:
        meshes_base = []
    if len(meshes_merge) == 1 and not meshes_merge[0]:
        meshes_merge = []

    # Applies transforms of the base armature and mesh
    Common.apply_transforms(armature_name=base_armature_name)

    # Applies the transforms to the merge armature and mesh
    print(meshes_merge)
    if (len(meshes_merge) != 1 or not bpy.context.scene.merge_armatures_join_meshes or bpy.context.scene.apply_transforms) and not mesh_only:
        Common.apply_transforms(armature_name=merge_armature_name)
    else:
        mesh_merge = meshes_merge[0]
        # Check if merge armature is rotated. Because the code can handle everything except rotations
        for i in [0, 1, 2]:
            if abs(merge_armature.rotation_euler[i]) > tolerance or abs(mesh_merge.rotation_euler[i]) > tolerance:

                if merge_armature.location[i] != 0 or abs(merge_armature.rotation_euler[i]) > tolerance or merge_armature.scale[i] != 1:

                    # Reset wrong merge armature rotations
                    for i2 in [0, 1, 2]:
                        merge_armature.location[i2] = 0
                        merge_armature.rotation_euler[i2] = 0
                        merge_armature.scale[i2] = 1

                    Common.unselect_all()
                    Common.set_active(mesh_merge)

                    Common.show_error(7.5, t('merge_armatures.error.transformReset'))
                    return

        # Save the transforms of the merge armature
        old_loc = [merge_armature.location[0], merge_armature.location[1], merge_armature.location[2]]
        old_scale = [merge_armature.scale[0], merge_armature.scale[1], merge_armature.scale[2]]

        # Apply transformation from mesh to armature
        for i in [0, 1, 2]:
            merge_armature.location[i] = (mesh_merge.location[i] * old_scale[i]) + old_loc[i]
            merge_armature.rotation_euler[i] = mesh_merge.rotation_euler[i]
            merge_armature.scale[i] = mesh_merge.scale[i] * old_scale[i]

        # Reset all transformations on merge mesh
        for i in [0, 1, 2]:
            mesh_merge.location[i] = 0
            mesh_merge.rotation_euler[i] = 0
            mesh_merge.scale[i] = 1

        # Apply all transforms of merge armature and mesh
        Common.apply_transforms(armature_name=merge_armature_name)

    # Go into edit mode
    Common.unselect_all()
    Common.set_active(merge_armature)
    Common.switch('EDIT')

    # Create new bone
    bones_to_merge = copy.deepcopy(Bones.dont_delete_these_main_bones)
    found = False
    root_name = ''
    for bone in bones_to_merge:
        if bone in merge_armature.data.edit_bones and 'Eye' not in bone:
            found = True
            print('AUTO MERGE!')
            break

    if not found and not merge_same_bones:
        print('CUSTOM MERGE!')
        root_name = bpy.context.scene.attach_to_bone
        root = merge_armature.data.edit_bones.get(root_name)
        if root:
            root.name += '_Old'
        root = merge_armature.data.edit_bones.new(root_name)
        root.tail[2] += 0.1

        # Make new root top parent and reparent other top bones to root
        root.parent = None
        for bone2 in merge_armature.data.edit_bones:
            if not bone2.parent:
                bone2.parent = root
        bones_to_merge.append(root.name)

    # Rename all the bones of the merge armature
    mesh_only_bone_name = ''
    for bone in merge_armature.data.edit_bones:
        bone.name = bone.name + '.merge'
        if mesh_only:
            mesh_only_bone_name = bone.name

    # Go back into object mode
    Common.set_default_stage()
    Common.unselect_all()

    # Select armature in correct way
    Common.set_active(base_armature)
    Common.select(merge_armature)

    # Join the armatures
    if bpy.ops.object.join.poll():
        bpy.ops.object.join()

    # Set new armature
    bpy.context.scene.armature = base_armature_name
    armature = Common.get_armature(armature_name=base_armature_name)

    # Clean up shape keys
    for mesh_base in meshes_base:
        Common.clean_shapekeys(mesh_base)
    for mesh_merge in meshes_merge:
        Common.clean_shapekeys(mesh_merge)

    # Join the meshes
    if bpy.context.scene.merge_armatures_join_meshes:
        meshes_merged = [Common.join_meshes(armature_name=base_armature_name, apply_transformations=False)]
    else:
        meshes_merged = meshes_base + meshes_merge
        for mesh in meshes_merged:
            mesh.parent = base_armature
            Common.repair_mesh(mesh, base_armature_name)
    if len(meshes_merged) == 1 and not meshes_merged[0]:
        meshes_merged = []

    # Go into edit mode
    Common.unselect_all()
    Common.set_active(armature)
    Common.switch('EDIT')

    # Reparent all bones
    if merge_same_bones:
        bones_to_merge = []
        for bone in armature.data.edit_bones:
            if bone.name.endswith('.merge'):
                new_bone = armature.data.edit_bones.get(bone.name.replace('.merge', ''))
                if new_bone:
                    bone.parent = new_bone
                    bones_to_merge.append(new_bone.name)
    else:
        # Merge base bones
        for bone_name in bones_to_merge:
            old = bone_name + '.merge'
            new = bone_name
            if old in armature.data.edit_bones and new in armature.data.edit_bones:
                armature.data.edit_bones.get(old).parent = armature.data.edit_bones.get(new)

        # Merge all bones that have the exact same position and name
        for bone in armature.data.edit_bones:
            if bone.name.endswith('.merge'):
                new_bone = armature.data.edit_bones.get(bone.name.replace('.merge', ''))
                if new_bone and new_bone.name not in bones_to_merge \
                        and round(bone.head[0], 4) == round(new_bone.head[0], 4)\
                        and round(bone.head[1], 4) == round(new_bone.head[1], 4)\
                        and round(bone.head[2], 4) == round(new_bone.head[2], 4):
                    bone.parent = new_bone
                    bones_to_merge.append(new_bone.name)

    # Remove all unused bones, constraints and vertex groups
    Common.set_default_stage()
    if not mesh_only:
        Common.delete_bone_constraints(armature_name=base_armature_name)
        if bpy.context.scene.merge_armatures_remove_zero_weight_bones:
            Common.remove_unused_vertex_groups(ignore_main_bones=True)
            if Common.get_meshes_objects(armature_name=base_armature_name):
                Common.delete_zero_weight(armature_name=base_armature_name, ignore=root_name)
        Common.set_default_stage()

    # Merge bones into existing bones
    if not mesh_only:
        to_delete = []
        for bone_name in bones_to_merge:
            bone_base = bone_name
            bone_merge = bone_name + '.merge'

            for mesh_merged in meshes_merged:
                Common.set_active(mesh_merged)
                vg_base = mesh_merged.vertex_groups.get(bone_base)
                vg_merge = mesh_merged.vertex_groups.get(bone_merge)

                if not vg_base:
                    mesh_merged.vertex_groups.new(name=bone_base)
                if not vg_merge:
                    mesh_merged.vertex_groups.new(name=bone_merge)

                Common.mix_weights(mesh_merged, bone_merge, bone_base)
            to_delete.append(bone_merge)

        Common.set_active(armature)
        Common.switch('EDIT')

        for bone_name in to_delete:
            bone = armature.data.edit_bones.get(bone_name)
            bone_base = armature.data.edit_bones.get(bone_name.replace('.merge', ''))
            if bone and bone_base:
                armature.data.edit_bones.remove(bone)

        Common.switch('OBJECT')

        # Remove ".merge" from all non duplicate bones
        for bone in armature.pose.bones:
            new_name = bone.name.replace('.merge', '')
            if new_name not in armature.pose.bones:
                bone.name = new_name

    # If mesh_only then rename the only bone to mesh name
    elif mesh_name:
        bone = armature.pose.bones.get(mesh_only_bone_name)
        if not bone:
            Common.show_error(5.8, t('merge_armatures.error.pleaseUndo'))
            return
        armature.pose.bones.get(mesh_only_bone_name).name = mesh_name

    # Go into edit mode
    Common.unselect_all()
    Common.set_active(armature)
    Common.switch('EDIT')

    # Set new bone positions
    # for bone_name in replace_bones:
    #     if bone_name in armature.data.edit_bones and bone_name + '.merge' in armature.data.edit_bones:
    #         bone = armature.data.edit_bones.get(bone_name)
    #         bone_merged = armature.data.edit_bones.get(bone_name + '.merge')
    #
    #         bone.name = bone.name + '_Old'
    #         bone_merged.name = bone_merged.name.replace('.merge', '')
    #
    #         bone_merged.parent = bone.parent
    #         bone.parent = bone_merged

    # Fix bone connections (just for design)
    Common.correct_bone_positions(armature_name=base_armature_name)

    # Remove all unused bones, constraints and vertex groups
    Common.set_default_stage()
    if not mesh_only:
        if bpy.context.scene.merge_armatures_remove_zero_weight_bones:
            Common.remove_unused_vertex_groups()
            if Common.get_meshes_objects(armature_name=base_armature_name):
                Common.delete_zero_weight(armature_name=base_armature_name, ignore=root_name)
            Common.set_default_stage()

    # Fix armature name
    Common.fix_armature_names(armature_name=base_armature_name)
