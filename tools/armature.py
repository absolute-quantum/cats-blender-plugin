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

# Code author: Shotariya
# Repo: https://github.com/Grim-es/shotariya
# Code author: Neitri
# Repo: https://github.com/netri/blender_neitri_tools
# Edits by: GiveMeAllYourCats, Hotox

import bpy
import tools.common
import tools.translate
import tools.armature_bones as Bones
from mmd_tools_local.translations import DictionaryEnum

mmd_tools_installed = False
try:
    import mmd_tools
    mmd_tools_installed = True
except:
    pass


class FixArmature(bpy.types.Operator):
    bl_idname = 'armature.fix'
    bl_label = 'Fix Model'
    bl_description = 'Automatically:\n' \
                     '- Reparents bones\n' \
                     '- Removes unnecessary bones, objects, groups & constraints\n' \
                     '- Translates and renames bones & objects\n' \
                     '- Mixes weight paints\n' \
                     '- Corrects the hips\n' \
                     '- Joins meshes\n' \
                     '- Corrects shading'

    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    dictionary = bpy.props.EnumProperty(
        name='Dictionary',
        items=DictionaryEnum.get_dictionary_items,
        description='Translate names from Japanese to English using selected dictionary',
    )

    @classmethod
    def poll(cls, context):
        if tools.common.get_armature() is None:
            return False
        i = 0
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                if ob.parent is not None and ob.parent.type == 'ARMATURE':
                    i += 1
        return i > 0


    def execute(self, context):
        wm = bpy.context.window_manager
        armature = tools.common.set_default_stage()

        steps = len(bpy.data.objects) + len(armature.pose.bone_groups) + len(Bones.bone_list_rename_unknown_side) + len(Bones.bone_list_parenting) + len(Bones.bone_list_weight) + 1  # TODO
        current_step = 0
        wm.progress_begin(current_step, steps)

        # Set correct mmd shading
        if mmd_tools_installed:
            try:
                bpy.ops.mmd_tools.set_shadeless_glsl_shading()
                for obj in bpy.data.objects:
                    if obj.parent is None and obj.type == 'EMPTY':
                            obj.mmd_root.use_toon_texture = False
                            obj.mmd_root.use_sphere_texture = False
                            break
            except:
                pass

        # Remove Rigidbodies and joints
        for obj in bpy.data.objects:
            current_step += 1
            wm.progress_update(current_step)
            if obj.name == 'rigidbodies' or obj.name == 'rigidbodies.001' or obj.name == 'joints' or obj.name == 'joints.001':
                tools.common.delete_hierarchy(obj)

        # Remove empty objects
        tools.common.remove_empty()

        # Remove Bone Groups
        for group in armature.pose.bone_groups:
            current_step += 1
            wm.progress_update(current_step)
            armature.pose.bone_groups.remove(group)

        # Model should be in rest position
        armature.data.pose_position = 'REST'

        # Armature should be named correctly
        armature.name = 'Armature'
        armature.data.name = 'Armature'

        # Joins meshes into one and calls it 'Body'
        mesh = tools.common.join_meshes(context)

        # Reorders vrc shape keys to the correct order
        tools.common.repair_viseme_order(mesh.name)

        # Armature should be selected and in edit mode
        tools.common.unselect_all()
        tools.common.select(armature)
        tools.common.switch('EDIT')

        # Translate bones with dictionary
        tools.translate.translate_bones(self.dictionary)

        # Rename bones
        for bone in armature.data.edit_bones:
            bone.name = bone.name[:1].upper() + bone.name[1:]

        for bone_new, bones_old in Bones.bone_rename.items():
            if '\Left' in bone_new or '\L' in bone_new:
                bones = [[bone_new.replace('\Left', 'Left').replace('\left', 'left').replace('\L', 'L').replace('\l', 'l'), ''],
                         [bone_new.replace('\Left', 'Right').replace('\left', 'right').replace('\L', 'R').replace('\l', 'r'), '']]
            else:
                bones = [[bone_new, '']]
            for bone_old in bones_old:
                if '\Left' in bone_new or '\L' in bone_new:
                    bones[0][1] = bone_old.replace('\Left', 'Left').replace('\left', 'left').replace('\L', 'L').replace('\l', 'l')
                    bones[1][1] = bone_old.replace('\Left', 'Right').replace('\left', 'right').replace('\L', 'R').replace('\l', 'r')
                else:
                    bones[0][1] = bone_old

                for bone in bones:  # bone[0] = new name, bone[1] = old name
                    if bone[1] in armature.data.edit_bones or bone[1].lower() in armature.data.edit_bones:
                        bone2 = armature.data.edit_bones.get(bone[1])
                        if bone2 is not None:
                            bone2.name = bone[0]

        # Check if it is a mixamo model
        mixamo = False
        for bone in armature.data.edit_bones:
            if not mixamo and 'Mixamo' in bone.name:
                mixamo = True
                break

        # Rename bones which don't have a side and try to detect it automatically
        for key, value in Bones.bone_list_rename_unknown_side.items():
            current_step += 1
            wm.progress_update(current_step)

            for bone in armature.data.edit_bones:
                parent = bone.parent
                if parent is None:
                    continue
                if parent.name == key or parent.name == key.lower():
                    if 'right' in bone.name.lower():
                        parent.name = 'Right ' + value
                        break
                    elif 'left' in bone.name.lower():
                        parent.name = 'Left ' + value
                        break

                parent = parent.parent
                if parent is None:
                    continue
                if parent.name == key or parent.name == key.lower():
                    if 'right' in bone.name.lower():
                        parent.name = 'Right ' + value
                        break
                    elif 'left' in bone.name.lower():
                        parent.name = 'Left ' + value
                        break

        # Remove un-needed bones and disconnect them
        for bone in armature.data.edit_bones:
            if bone.name in Bones.bone_list or bone.name.startswith(tuple(Bones.bone_list_with)):
                if bone.parent is not None:
                    Bones.bone_list_weight[bone.name] = bone.parent.name
                else:
                    armature.data.edit_bones.remove(bone)
            else:
                bone.use_connect = False

        # Make Hips top parent and reparent other top bones to hips
        if 'Hips' in armature.data.edit_bones:
            hips = armature.data.edit_bones.get('Hips')
            hips.parent = None
            for bone in armature.data.edit_bones:
                if bone.parent is None:
                    bone.parent = hips

        # Set head roll to 0 degrees for eye tracking
        if 'Head' in armature.data.edit_bones:
            armature.data.edit_bones.get('Head').roll = 0

        # == FIXING OF SPECIAL BONE CASES ==

        # Create missing Chest # TODO bleeding
        if 'Chest' not in armature.data.edit_bones:
            if 'Spine' in armature.data.edit_bones:
                if 'Neck' in armature.data.edit_bones:
                    chest = armature.data.edit_bones.new('Chest')
                    spine = armature.data.edit_bones.get('Spine')
                    neck = armature.data.edit_bones.get('Neck')

                    # Set new Chest bone to new position
                    chest.tail = neck.head
                    chest.head = spine.head
                    chest.head[2] = spine.head[2] + (neck.head[2] - spine.head[2]) / 2
                    chest.head[1] = spine.head[1] + (neck.head[1] - spine.head[1]) / 2

                    # Adjust spine bone position
                    spine.tail = chest.head

                    # Reparent bones to include new chest
                    chest.parent = spine

                    for bone in armature.data.edit_bones:
                        if bone.parent == spine:
                            bone.parent = chest

        # Remove third chest
        if 'NewChest' in armature.data.edit_bones:
            if 'Chest' in armature.data.edit_bones:
                if 'Spine' in armature.data.edit_bones:
                    new_chest = armature.data.edit_bones.get('NewChest')
                    old_chest = armature.data.edit_bones.get('Chest')
                    spine = armature.data.edit_bones.get('Spine')

                    # Check if NewChest is empty
                    if tools.common.isEmptyGroup(new_chest.name):
                        armature.data.edit_bones.remove(new_chest)
                    else:
                        # Rename chests
                        old_chest.name = 'ChestOld'
                        new_chest.name = 'Chest'

                        # Adjust spine bone position
                        spine.tail[0] += old_chest.tail[0] - old_chest.head[0]
                        spine.tail[1] += old_chest.tail[1] - old_chest.head[1]
                        spine.tail[2] += old_chest.tail[2] - old_chest.head[2]

                        # Move weight paint to spine
                        tools.common.unselect_all()
                        tools.common.switch('OBJECT')
                        tools.common.select(mesh)

                        vg = mesh.vertex_groups.get(old_chest.name)
                        if vg is not None:
                            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
                            bpy.context.object.modifiers['VertexWeightMix'].vertex_group_a = spine.name
                            bpy.context.object.modifiers['VertexWeightMix'].vertex_group_b = old_chest.name
                            bpy.context.object.modifiers['VertexWeightMix'].mix_mode = 'ADD'
                            bpy.context.object.modifiers['VertexWeightMix'].mix_set = 'B'
                            bpy.ops.object.modifier_apply(modifier='VertexWeightMix')
                            mesh.vertex_groups.remove(vg)

                        tools.common.unselect_all()
                        tools.common.select(armature)
                        tools.common.switch('EDIT')

                        # Delete old chest bone
                        # New Check is necessary because switch to object mode in between

                        old_chest = armature.data.edit_bones.get('ChestOld')
                        armature.data.edit_bones.remove(old_chest)

        # Hips bone should be fixed as per specification from the SDK code
        if not mixamo:
            if 'Hips' in armature.data.edit_bones:
                if 'Left leg' in armature.data.edit_bones:
                    if 'Right leg' in armature.data.edit_bones:
                        hip_bone = armature.data.edit_bones.get('Hips')
                        left_leg = armature.data.edit_bones.get('Left leg')
                        right_leg = armature.data.edit_bones.get('Right leg')
                        right_knee = armature.data.edit_bones.get('Right knee')
                        left_knee = armature.data.edit_bones.get('Left knee')
                        spine = armature.data.edit_bones.get('Spine')
                        chest = armature.data.edit_bones.get('Chest')
                        neck = armature.data.edit_bones.get('Neck')
                        head = armature.data.edit_bones.get('Head')

                        full_body_tracking = False

                        # Fixing the hips
                        if not full_body_tracking:
                            # Hips should have x value of 0 in both head and tail
                            hip_bone.head[0] = 0
                            hip_bone.tail[0] = 0

                            # Make sure the hips bone (tail and head tip) is aligned with the legs Y
                            hip_bone.head[1] = right_leg.head[1]
                            hip_bone.tail[1] = right_leg.head[1]

                            # Flip the hips bone and make sure the hips bone is not below the legs bone
                            hip_bone_length = abs(hip_bone.tail[2] - hip_bone.head[2])
                            hip_bone.head[2] = right_leg.head[2]
                            hip_bone.tail[2] = hip_bone.head[2] + hip_bone_length

                        elif spine is not None and chest is not None and neck is not None and head is not None:
                            bones = [hip_bone, spine, chest, neck, head]
                            for bone in bones:
                                bone_length = abs(bone.tail[2] - bone.head[2])
                                bone.tail[0] = bone.head[0]
                                bone.tail[1] = bone.head[1]
                                bone.tail[2] = bone.head[2] + bone_length

                        # Fixing legs
                        if right_knee is not None and left_knee is not None:
                            # Make sure the upper legs tail are the same x/y values as the lower leg tail x/y
                            right_leg.tail[0] = right_knee.head[0]
                            left_leg.tail[0] = left_knee.head[0]
                            right_leg.head[1] = right_knee.head[1]
                            left_leg.head[1] = left_knee.head[1]

                            # Make sure the leg bones are setup straight. (head should be same X as tail)
                            left_leg.head[0] = left_leg.tail[0]
                            right_leg.head[0] = right_leg.tail[0]

                            # Make sure the left legs (head tip) have the same Y values as right leg (head tip)
                            left_leg.head[1] = right_leg.head[1]

                        # Roll should be disabled on legs and hips
                        left_leg.roll = 0
                        right_leg.roll = 0
                        hip_bone.roll = 0

        # Reparent all bones to be correct for unity mapping and vrc itself
        for key, value in Bones.bone_list_parenting.items():
            current_step += 1
            wm.progress_update(current_step)

            if key in armature.data.edit_bones and value in armature.data.edit_bones:
                armature.data.edit_bones.get(key).parent = armature.data.edit_bones.get(value)

        # Weights should be mixed
        tools.common.unselect_all()
        tools.common.switch('OBJECT')
        tools.common.select(mesh)

        for key, value in Bones.bone_list_weight.items():
            current_step += 1
            wm.progress_update(current_step)
            vg = mesh.vertex_groups.get(key)
            if vg is None:
                vg = mesh.vertex_groups.get(key.lower())
                if vg is None:
                    continue
            vg2 = mesh.vertex_groups.get(value)
            if vg2 is None:
                continue
            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
            bpy.context.object.modifiers['VertexWeightMix'].vertex_group_a = value
            bpy.context.object.modifiers['VertexWeightMix'].vertex_group_b = key
            bpy.context.object.modifiers['VertexWeightMix'].mix_mode = 'ADD'
            bpy.context.object.modifiers['VertexWeightMix'].mix_set = 'B'
            bpy.ops.object.modifier_apply(modifier='VertexWeightMix')
            mesh.vertex_groups.remove(vg)

        tools.common.unselect_all()
        tools.common.select(armature)
        tools.common.switch('EDIT')

        # Bone constraints should be deleted
        # if context.scene.remove_constraints:
        delete_bone_constraints()

        # Removes unused vertex groups
        tools.common.remove_unused_vertex_groups()

        # Zero weight bones should be deleted
        if context.scene.remove_zero_weight:
            delete_zero_weight()

        # At this point, everything should be fixed and now we validate and give errors if needed

        # The bone hierarchy needs to be validated
        hierarchy_check_hips = check_hierarchy([
            ['Hips', 'Spine', 'Chest', 'Neck', 'Head'],
            ['Hips', 'Left leg', 'Left knee', 'Left ankle'],
            ['Hips', 'Right leg', 'Right knee', 'Right ankle'],
            ['Chest', 'Left shoulder', 'Left arm', 'Left elbow', 'Left wrist'],
            ['Chest', 'Right shoulder', 'Right arm', 'Right elbow', 'Right wrist']
        ])

        current_step += 1
        wm.progress_update(current_step)

        wm.progress_end()

        if hierarchy_check_hips['result'] is False:
            self.report({'ERROR'}, hierarchy_check_hips['message'])
            return {'FINISHED'}

        self.report({'INFO'}, 'Model fixed.')
        return {'FINISHED'}


def check_hierarchy(correct_hierarchy_array):
    armature = tools.common.set_default_stage()

    for correct_hierarchy in correct_hierarchy_array:  # For each hierachy array
        previous = None
        for index, bone in enumerate(correct_hierarchy):  # For each hierarchy bone item
            if index > 0:
                previous = correct_hierarchy[index - 1]

            # NOTE: armature.data.bones is being used instead of armature.data.edit_bones because of a failed test (edit_bones array empty for some reason)
            if bone not in armature.data.bones:
                return {'result': False, 'message': bone + ' was not found in the hierarchy, this will cause problems!'}

            bone = armature.data.bones[bone]

            # If a previous item was found
            if previous is not None:
                # And there is no parent, then we have a problem mkay
                if bone.parent is None:
                    return {'result': False, 'message': bone.name + ' is not parented at all, this will cause problems!'}
                # Previous needs to be the parent of the current item
                if previous != bone.parent.name:
                    return {'result': False, 'message': bone.name + ' is not parented to ' + previous + ', this will cause problems!'}

    return {'result': True}


def delete_zero_weight():
    armature = tools.common.get_armature()
    tools.common.switch('EDIT')

    bone_names_to_work_on = set([bone.name for bone in armature.data.edit_bones])

    bone_name_to_edit_bone = dict()
    for edit_bone in armature.data.edit_bones:
        bone_name_to_edit_bone[edit_bone.name] = edit_bone

    vertex_group_names_used = set()
    vertex_group_name_to_objects_having_same_named_vertex_group = dict()
    for objects in armature.children:
        vertex_group_id_to_vertex_group_name = dict()
        for vertex_group in objects.vertex_groups:
            vertex_group_id_to_vertex_group_name[vertex_group.index] = vertex_group.name
            if vertex_group.name not in vertex_group_name_to_objects_having_same_named_vertex_group:
                vertex_group_name_to_objects_having_same_named_vertex_group[vertex_group.name] = set()
            vertex_group_name_to_objects_having_same_named_vertex_group[vertex_group.name].add(objects)
        for vertex in objects.data.vertices:
            for group in vertex.groups:
                if group.weight > 0:
                    vertex_group_names_used.add(vertex_group_id_to_vertex_group_name.get(group.group))

    not_used_bone_names = bone_names_to_work_on - vertex_group_names_used

    for bone_name in not_used_bone_names:
        if bone_name not in Bones.dont_delete_these_bones:
            armature.data.edit_bones.remove(bone_name_to_edit_bone[bone_name])  # delete bone
            if bone_name in vertex_group_name_to_objects_having_same_named_vertex_group:
                for objects in vertex_group_name_to_objects_having_same_named_vertex_group[bone_name]:  # delete vertex groups
                    vertex_group = objects.vertex_groups.get(bone_name)
                    if vertex_group is not None:
                        objects.vertex_groups.remove(vertex_group)


def delete_bone_constraints():
    armature = tools.common.get_armature()

    bones = set([bone.name for bone in armature.pose.bones])

    tools.common.switch('POSE')
    bone_name_to_pose_bone = dict()
    for bone in armature.pose.bones:
        bone_name_to_pose_bone[bone.name] = bone

    for bone_name in bones:
        bone = bone_name_to_pose_bone[bone_name]
        if len(bone.constraints) > 0:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)

    tools.common.switch('EDIT')
