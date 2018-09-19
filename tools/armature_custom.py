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

import copy
import bpy
import webbrowser
import tools.common
import tools.armature_bones as Bones


class MergeArmature(bpy.types.Operator):
    bl_idname = 'armature_custom.merge_armatures'
    bl_label = 'Merge Armatures'
    bl_description = "Merges the selected merge armature into the base armature." \
                     "\nYou should fix both armatures with Cats first." \
                     "\nOnly move the mesh of the merge armature to the desired position, the bones will be moved automatically"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(tools.common.get_armature_objects()) > 1

    def execute(self, context):
        # Set default stage
        tools.common.set_default_stage()
        tools.common.unselect_all()

        # Get both armatures
        base_armature_name = bpy.context.scene.merge_armature_into
        merge_armature_name = bpy.context.scene.merge_armature
        base_armature = bpy.data.objects[base_armature_name]
        merge_armature = bpy.data.objects[merge_armature_name]

        if not merge_armature:
            tools.common.show_error(5.2, ['The armature "' + merge_armature_name + '" could not be found.'])
            return {'FINISHED'}
        if not base_armature:
            tools.common.show_error(5.2, ['The armature "' + base_armature_name + '" could not be found.'])
            return {'FINISHED'}

        if merge_armature.parent or base_armature.parent:
            if context.scene.merge_same_bones:
                if merge_armature.parent:
                    tools.common.select(merge_armature.parent)
                    bpy.ops.object.delete()
                    bpy.context.scene.objects.unlink(merge_armature.parent)
                    bpy.data.objects.remove(merge_armature.parent)
                if base_armature.parent:
                    tools.common.select(base_armature.parent)
                    bpy.ops.object.delete()
                    bpy.context.scene.objects.unlink(base_armature.parent)
                    bpy.data.objects.remove(base_armature.parent)
            else:
                tools.common.show_error(6.2,
                                        ['Please use the "Fix Model" feature on the selected armatures first!',
                                         'Make sure to select the armature you want to fix above the "Fix Model" button!',
                                         'After that please only move the mesh (not the armature!) to the desired position.'])
                return {'FINISHED'}

        if len(tools.common.get_meshes_objects(armature_name=merge_armature_name)) == 0:
            tools.common.show_error(5.2, ['The armature "' + merge_armature_name + '" does not have any meshes.'])
            return {'FINISHED'}
        if len(tools.common.get_meshes_objects(armature_name=base_armature_name)) == 0:
            tools.common.show_error(5.2, ['The armature "' + base_armature_name + '" does not have any meshes.'])
            return {'FINISHED'}

        # Merge armatures
        merge_armatures(base_armature_name, merge_armature_name, False, merge_same_bones=context.scene.merge_same_bones)

        self.report({'INFO'}, 'Armatures successfully joined.')
        return {'FINISHED'}


class AttachMesh(bpy.types.Operator):
    bl_idname = 'armature_custom.attach_mesh'
    bl_label = 'Attach Mesh'
    bl_description = "Attaches the selected mesh to the selected bone of the selected armature." \
                     "\n" \
                     "\nINFO: The mesh will only be assigned to the selected bone." \
                     "\nE.g.: A jacket won't work, because it requires multiple bones"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return len(tools.common.get_armature_objects()) > 0 and len(tools.common.get_meshes_objects(mode=1)) > 0

    def execute(self, context):
        # Set default stage
        tools.common.set_default_stage()
        tools.common.unselect_all()

        # Get armature and mesh
        mesh_name = bpy.context.scene.attach_mesh
        base_armature_name = bpy.context.scene.merge_armature_into
        attach_bone_name = bpy.context.scene.attach_to_bone
        mesh = bpy.data.objects[mesh_name]
        base_armature = bpy.data.objects[base_armature_name]

        # Create new armature
        bpy.ops.object.armature_add(location=(0, 0, 0))
        new_armature = bpy.context.active_object

        # Reparent mesh to new armature
        mesh.parent = new_armature
        mesh.parent_type = 'OBJECT'

        # Rename bone in new armature
        new_armature.data.bones.get('Bone').name = attach_bone_name

        # Switch mesh to edit mode
        tools.common.unselect_all()
        tools.common.select(mesh)
        tools.common.switch('EDIT')

        # Select and assign all vertices to new vertex group
        bpy.ops.mesh.select_all(action='SELECT')
        mesh.vertex_groups.new(attach_bone_name)
        bpy.ops.object.vertex_group_assign()

        tools.common.switch('OBJECT')

        # Create new armature modifier
        mod = mesh.modifiers.new('Armature', 'ARMATURE')
        mod.object = new_armature

        # Merge armatures
        merge_armatures(base_armature_name, new_armature.name, True, mesh_name=mesh_name)

        self.report({'INFO'}, 'Mesh successfully attached to armature.')
        return {'FINISHED'}


class CustomModelTutorialButton(bpy.types.Operator):
    bl_idname = 'armature_custom.button'
    bl_label = 'Go to Documentation'

    def execute(self, context):
        webbrowser.open('https://github.com/michaeldegroot/cats-blender-plugin#custom-model-creation')

        self.report({'INFO'}, 'Documentation')
        return {'FINISHED'}


def merge_armatures(base_armature_name, merge_armature_name, mesh_only, mesh_name=None, merge_same_bones=False):
    tolerance = 0.00008726647  # around 0.005 degrees
    base_armature = bpy.data.objects[base_armature_name]
    merge_armature = bpy.data.objects[merge_armature_name]

    # Join meshes in both armatures
    mesh_base = tools.common.join_meshes(armature_name=base_armature_name, apply_transformations=False)
    mesh_merge = tools.common.join_meshes(armature_name=merge_armature_name, apply_transformations=False)

    # Applies transforms an the base armature and mesh
    tools.common.unselect_all()
    tools.common.select(base_armature)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    tools.common.unselect_all()
    tools.common.select(mesh_base)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # # Check for transform on base armature, reset if not default
    # for i in [0, 1, 2]:
    #     if base_armature.location[i] != 0 \
    #             or abs(base_armature.rotation_euler[i]) > tolerance \
    #             or base_armature.scale[i] != 1 \
    #             or mesh_base.location[i] != 0 \
    #             or abs(mesh_base.rotation_euler[i]) > tolerance \
    #             or mesh_base.scale[i] != 1:
    #
    #         # Reset all wrong transforms
    #         for i2 in [0, 1, 2]:
    #             base_armature.location[i2] = 0
    #             base_armature.rotation_euler[i2] = 0
    #             base_armature.scale[i2] = 1
    #             mesh_base.location[i2] = 0
    #             mesh_base.rotation_euler[i2] = 0
    #             mesh_base.scale[i2] = 1
    #
    #         # Check if merge armature also needs it's transforms to be reset (ignore the tolerance here, just reset it)
    #         if merge_armature.location[i] != 0 or merge_armature.rotation_euler[i] != 0 or merge_armature.scale[i] != 1:
    #             if merge_armature.rotation_euler[i] != 0 or mesh_merge.rotation_euler[i] != 0:
    #                 for i2 in [0, 1, 2]:
    #                     merge_armature.location[i2] = 0
    #                     merge_armature.rotation_euler[i2] = 0
    #                     merge_armature.scale[i2] = 1
    #
    #         # Hide armatures and select the mesh
    #         merge_armature.hide = True
    #         base_armature.hide = True
    #         tools.common.unselect_all()
    #         tools.common.select(mesh_merge)
    #         bpy.context.space_data.transform_manipulators = {'TRANSLATE'}
    #
    #         # Show error messages
    #         if mesh_only:
    #             # remove the temporary armature from the new mesh
    #             bpy.data.objects.remove(merge_armature)
    #             mesh_merge.name = mesh_name
    #
    #             tools.common.show_error(8,
    #                                     ["The transforms of your base armature and base mesh don't have the default values!",
    #                                      '',
    #                                      "Only move the mesh you want to attach to the desired position.",
    #                                      '',
    #                                      'The transforms of the base armature got reset for you and the mesh you have to modify got selected.',
    #                                      'Please start from here or undo this operation.'])
    #         else:
    #             tools.common.show_error(8.1,
    #                                     ["The transforms of your base armature and base mesh don't have the default values!",
    #                                      '',
    #                                      'Maybe you mixed up the base and merge armatures?',
    #                                      'Only move the mesh of the merge armature to the desired position. The bones will be placed automatically.',
    #                                      '',
    #                                      'The transforms of the armatures got reset for you and the mesh you have to modify got selected.',
    #                                      'Please start from here or undo this operation.'])
    #         return

    # Check if merge armature is rotated. Because the code can handle everything except rotations
    for i in [0, 1, 2]:
        if abs(merge_armature.rotation_euler[i]) > tolerance or abs(mesh_merge.rotation_euler[i]) > tolerance:

            if merge_armature.location[i] != 0 or abs(merge_armature.rotation_euler[i]) > tolerance or merge_armature.scale[i] != 1:

                # Reset wrong merge armature rotations
                for i2 in [0, 1, 2]:
                    merge_armature.location[i2] = 0
                    merge_armature.rotation_euler[i2] = 0
                    merge_armature.scale[i2] = 1

                tools.common.unselect_all()
                tools.common.select(mesh_merge)

                tools.common.show_error(7.5,
                                        ['If you want to rotate the new part, only modify the mesh instead of the armature!',
                                         '',
                                         'The transforms of the merge armature got reset and the mesh you have to modify got selected.',
                                         'Now place this selected mesh where and how you want it to be and then merge the armatures again.',
                                         "If you don't want that, undo this operation."])
                return

    # Save the transforms of the merge armature
    old_loc = [merge_armature.location[0], merge_armature.location[1], merge_armature.location[2]]
    old_scale = [merge_armature.scale[0], merge_armature.scale[1], merge_armature.scale[2]]

    # Apply transformation from mesh to armature
    for i in [0, 1, 2]:
        merge_armature.location[i] = (mesh_merge.location[i] * old_scale[i]) + old_loc[i]
        merge_armature.rotation_euler[i] = mesh_merge.rotation_euler[i]
        merge_armature.scale[i] = mesh_merge.scale[i] * old_scale[i]

    tools.common.set_default_stage()
    # Apply all transformations on mesh
    tools.common.unselect_all()
    tools.common.select(mesh_merge)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Apply all transformations on armature
    tools.common.unselect_all()
    tools.common.select(merge_armature)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Reset all transformations on mesh
    for i in [0, 1, 2]:
        mesh_merge.location[i] = old_loc[i]
        mesh_merge.rotation_euler[i] = 0
        mesh_merge.scale[i] = old_scale[i]

    # Apply all transformations on mesh again
    tools.common.unselect_all()
    tools.common.select(mesh_merge)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Go into edit mode
    tools.common.unselect_all()
    tools.common.select(merge_armature)
    tools.common.switch('EDIT')

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
    tools.common.set_default_stage()
    tools.common.unselect_all()

    # Select armature in correct way
    tools.common.select(base_armature)
    merge_armature.select = True

    # Join the armatures
    if bpy.ops.object.join.poll():
        bpy.ops.object.join()

    # Set new armature
    bpy.context.scene.armature = base_armature_name
    armature = tools.common.get_armature(armature_name=base_armature_name)

    # Join the meshes
    mesh_merge = tools.common.join_meshes(armature_name=base_armature_name, apply_transformations=False)

    # Clean up shape keys
    tools.common.clean_shapekeys(mesh_merge)

    # Go into edit mode
    tools.common.unselect_all()
    tools.common.select(armature)
    tools.common.switch('EDIT')

    # Reparent all bones
    if merge_same_bones:
        for bone in armature.data.edit_bones:
            if bone.name.endswith('.merge'):
                new_bone = armature.data.edit_bones.get(bone.name.replace('.merge', ''))
                if new_bone:
                    bone.parent = new_bone
    else:
        for bone_name in bones_to_merge:
            old = bone_name + '.merge'
            new = bone_name
            if old in armature.data.edit_bones and new in armature.data.edit_bones:
                armature.data.edit_bones.get(old).parent = armature.data.edit_bones.get(new)

    # Remove all unused bones, constraints and vertex groups
    tools.common.set_default_stage()
    tools.common.delete_bone_constraints(armature_name=base_armature_name)
    tools.common.remove_unused_vertex_groups(ignore_main_bones=True)
    tools.common.delete_zero_weight(armature_name=base_armature_name, ignore=root_name)
    tools.common.set_default_stage()

    # Merge bones into existing bones
    tools.common.select(mesh_merge)
    replace_bones = []
    if not mesh_only:
        if merge_same_bones:
            print('MERGE SAME BONES!')
            to_delete = []
            for bone in armature.pose.bones:
                if not bone.name.endswith('.merge'):
                    continue

                bone_base = armature.pose.bones.get(bone.name.replace('.merge', ''))
                bone_merge = armature.pose.bones.get(bone.name)

                if not bone_base or not bone_merge:
                    continue

                print(bone_base.name, bone_merge.name)

                vg_base = mesh_merge.vertex_groups.get(bone_base.name)
                vg_merge = mesh_merge.vertex_groups.get(bone_merge.name)

                if vg_base and vg_merge:
                    tools.common.mix_weights(mesh_merge, vg_merge.name, vg_base.name)

                to_delete.append(bone_merge.name)

            tools.common.select(armature)
            tools.common.switch('EDIT')

            for bone_name in to_delete:
                bone = armature.data.edit_bones.get(bone_name)
                if bone:
                    armature.data.edit_bones.remove(bone)

            tools.common.switch('OBJECT')

        else:
            for bone_name in bones_to_merge:
                bone_base = bone_name
                bone_merge = bone_name + '.merge'

                vg_base = mesh_merge.vertex_groups.get(bone_base)
                vg2 = mesh_merge.vertex_groups.get(bone_merge)

                if not vg_base:
                    if vg2:
                        # vg2.name = bone_base
                        replace_bones.append(bone_base)
                        continue
                if not vg2:
                    continue

                tools.common.mix_weights(mesh_merge, bone_merge, bone_base)

        # Remove ".merge" from all non duplicate bones
        for bone in armature.pose.bones:
            new_name = bone.name.replace('.merge', '')
            if new_name not in armature.pose.bones:
                bone.name = new_name

    # If mesh_only then rename the only bone to mesh name
    elif mesh_name:
        bone = armature.pose.bones.get(mesh_only_bone_name)
        if not bone:
            tools.common.show_error(5.8, ['Something went wrong! Please undo, check your selections and try again.'])
            return
        armature.pose.bones.get(mesh_only_bone_name).name = mesh_name

    # Go into edit mode
    tools.common.unselect_all()
    tools.common.select(armature)
    tools.common.switch('EDIT')

    # Set new bone positions
    for bone_name in replace_bones:
        if bone_name in armature.data.edit_bones and bone_name + '.merge' in armature.data.edit_bones:
            bone = armature.data.edit_bones.get(bone_name)
            bone_merged = armature.data.edit_bones.get(bone_name + '.merge')

            bone.name = bone.name + '_Old'
            bone_merged.name = bone_merged.name.replace('.merge', '')

            bone_merged.parent = bone.parent
            bone.parent = bone_merged

    # Fix bone connections (just for design)
    tools.common.correct_bone_positions(armature_name=base_armature_name)

    # Remove all unused bones, constraints and vertex groups
    tools.common.set_default_stage()
    tools.common.remove_unused_vertex_groups()
    tools.common.delete_zero_weight(armature_name=base_armature_name, ignore=root_name)
    tools.common.set_default_stage()

    # Fix armature name
    tools.common.fix_armature_names(armature_name=base_armature_name)
