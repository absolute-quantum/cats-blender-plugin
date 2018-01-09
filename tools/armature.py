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
import copy

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

        # Add rename bones to reweight bones
        temp_reweight_bones = copy.deepcopy(Bones.bone_reweight)
        temp_list_reweight_bones = copy.deepcopy(Bones.bone_list_weight)
        temp_list_reparent_bones = copy.deepcopy(Bones.bone_list_parenting)
        for key, value in Bones.bone_rename.items():
            if key == 'Spine':
                continue
            list = temp_reweight_bones.get(key)
            if not list:
                temp_reweight_bones[key] = value
            else:
                for name in value:
                    if name not in list:
                        temp_reweight_bones.get(key).append(name)

        # Count objects for loading bar
        steps = 0
        for key, value in Bones.bone_rename.items():
            if '\Left' in key or '\L' in key:
                steps += 2 * len(value)
            else:
                steps += len(value)
        for key, value in temp_reweight_bones.items():
            if '\Left' in key or '\L' in key:
                steps += 2 * len(value)
            else:
                steps += len(value)
        steps += len(temp_list_reweight_bones)  # + len(Bones.bone_list_parenting)

        # mmd_tools specific operations
        if mmd_tools_installed:

            # Set correct mmd shading
            try:
                bpy.ops.mmd_tools.set_shadeless_glsl_shading()
                for obj in bpy.data.objects:
                    if obj.parent is None and obj.type == 'EMPTY':
                        obj.mmd_root.use_toon_texture = False
                        obj.mmd_root.use_sphere_texture = False
                        break
            except AttributeError:
                pass

            # Convert mmd bone morph into shape keys
            try:
                mmd_root = armature.parent.mmd_root
                if len(mmd_root.bone_morphs) > 0:

                    current_step = 0
                    wm.progress_begin(current_step, len(mmd_root.bone_morphs))


                    for index, morph in enumerate(mmd_root.bone_morphs):
                        current_step += 1
                        wm.progress_update(current_step)
                        armature.parent.mmd_root.active_morph = index
                        bpy.ops.mmd_tools.view_bone_morph()
                        mesh = tools.common.get_meshes_objects()[0]
                        tools.common.select(mesh)

                        mod = mesh.modifiers.new(morph.name, 'ARMATURE')
                        mod.object = armature
                        bpy.ops.object.modifier_apply(apply_as='SHAPE', modifier=mod.name)
                    wm.progress_end()
            except AttributeError:
                pass

        # Set better bone view
        armature.data.draw_type = 'OCTAHEDRAL'
        armature.draw_type = 'WIRE'
        armature.show_x_ray = True

        # Remove Rigidbodies and joints
        for obj in bpy.data.objects:
            if 'rigidbodies' in obj.name or 'joints' in obj.name:
                tools.common.delete_hierarchy(obj)

        # Remove empty objects
        tools.common.remove_empty()

        # Remove Bone Groups
        for group in armature.pose.bone_groups:
            armature.pose.bone_groups.remove(group)

        # Model should be in rest position
        armature.data.pose_position = 'REST'

        # Armature should be named correctly
        armature.name = 'Armature'
        armature.data.name = 'Armature'

        # Joins meshes into one and calls it 'Body'
        mesh = tools.common.join_meshes(context)

        # Correct pivot position
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # Reorders vrc shape keys to the correct order
        tools.common.repair_viseme_order(mesh.name)

        # Translate bones with dictionary
        tools.translate.translate_bones(self.dictionary)

        # Armature should be selected and in edit mode
        tools.common.unselect_all()
        tools.common.select(armature)
        tools.common.switch('EDIT')

        # Count steps for loading bar again
        steps += len(armature.data.edit_bones)
        for bone in armature.data.edit_bones:
            if bone.name in Bones.bone_list or bone.name.startswith(tuple(Bones.bone_list_with)):
                if bone.parent is not None:
                    steps += 1
                else:
                    steps -= 1

        # Start loading bar
        current_step = 0
        wm.progress_begin(current_step, steps)

        # Rename bones
        for bone in armature.data.edit_bones:
            current_step += 1
            wm.progress_update(current_step)
            name = ''
            for i, s in enumerate(bone.name.split(' ')):
                if i != 0:
                    name += ' '
                name += s[:1].upper() + s[1:]
            bone.name = name

        spines = []
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
                    current_step += 1
                    wm.progress_update(current_step)

                    name = ''
                    if bone[1] in armature.data.edit_bones:
                        name = bone[1]
                    elif bone[1].lower() in armature.data.edit_bones:
                        name = bone[1].lower()

                    if name == '':
                        continue

                    if bone_new == 'Spine':
                        spines.append(name)
                        continue

                    if name != '' and bone[0] not in armature.data.edit_bones:
                        bone2 = armature.data.edit_bones.get(name)
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
                    temp_list_reweight_bones[bone.name] = bone.parent.name
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

        # Fix all spines!
        spine_count = len(spines)
        if spine_count == 0:
            pass

        elif spine_count == 1:  # Create missing Chest
            if 'Neck' in armature.data.edit_bones:
                print('BONE CREATION')
                spine = armature.data.edit_bones.get(spines[0])
                chest = armature.data.edit_bones.new('Chest')
                neck = armature.data.edit_bones.get('Neck')

                # Correct the names
                spine.name = 'Spine'
                chest.name = 'Chest'

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

        elif spine_count == 2:  # Everything correct, just rename them
            print('NORMAL')
            armature.data.edit_bones.get(spines[0]).name = 'Spine'
            armature.data.edit_bones.get(spines[1]).name = 'Chest'

        elif spine_count > 2:  # Merge spines
            print('MASS MERGING')
            spine = armature.data.edit_bones.get(spines[0])
            chest = armature.data.edit_bones.get(spines[spine_count - 1])

            # Correct names
            spine.name = 'Spine'
            chest.name = 'Chest'

            # Adjust spine bone position
            spine.tail = chest.head

            # Add all redundant spines to the merge list
            for spine in spines[1:spine_count-1]:
                print(spine)
                temp_list_reweight_bones[spine] = 'Spine'

        # Correct arm bone positions for better looking
        if 'Left arm' in armature.data.edit_bones:
            if 'Left elbow' in armature.data.edit_bones:
                if 'Left wrist' in armature.data.edit_bones:
                    arm = armature.data.edit_bones.get('Left arm')
                    elbow = armature.data.edit_bones.get('Left elbow')
                    wrist = armature.data.edit_bones.get('Left wrist')
                    arm.tail = elbow.head
                    elbow.tail = wrist.head

        # Correct arm bone positions for better looking
        if 'Right arm' in armature.data.edit_bones:
            if 'Right elbow' in armature.data.edit_bones:
                if 'Right wrist' in armature.data.edit_bones:
                    arm = armature.data.edit_bones.get('Right arm')
                    elbow = armature.data.edit_bones.get('Right elbow')
                    wrist = armature.data.edit_bones.get('Right wrist')
                    arm.tail = elbow.head
                    elbow.tail = wrist.head

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

        # Mixing the weights
        tools.common.unselect_all()
        tools.common.switch('OBJECT')
        tools.common.select(mesh)

        for bone_new, bones_old in temp_reweight_bones.items():
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
                    current_step += 1
                    wm.progress_update(current_step)
                    vg = mesh.vertex_groups.get(bone[1])
                    if vg is None:
                        vg = mesh.vertex_groups.get(bone[1].lower())
                        if vg is None:
                            continue
                    # print(bone[1] + " to1 " + bone[0])
                    # If important vertex group is not there create it
                    if mesh.vertex_groups.get(bone[0]) is None:
                        if bone[0] in Bones.dont_delete_these_bones and bone[0] in armature.data.bones:
                            bpy.ops.object.vertex_group_add()
                            mesh.vertex_groups.active.name = bone[0]
                            if mesh.vertex_groups.get(bone[0]) is None:
                                continue
                        else:
                            continue

                    bone_tmp = armature.data.bones.get(bone[1])
                    if bone_tmp:
                        for child in bone_tmp.children:
                            temp_list_reparent_bones[child.name] = bone[0]

                    print(bone[1] + " to2 " + bone[0])
                    mod = mesh.modifiers.new("VertexWeightMix", 'VERTEX_WEIGHT_MIX')
                    mod.vertex_group_a = bone[0]
                    mod.vertex_group_b = bone[1]
                    mod.mix_mode = 'ADD'
                    mod.mix_set = 'B'
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                    mesh.vertex_groups.remove(vg)

        # Old mixing weights. Still important
        for key, value in temp_list_reweight_bones.items():
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

            bone_tmp = armature.data.bones.get(bone[1])
            if bone_tmp:
                for child in bone_tmp.children:
                    temp_list_reparent_bones[child.name] = bone[0]

            if key == value:
                print('BUG: ' + key + ' tried to mix weights with itself!')

            mod = mesh.modifiers.new("VertexWeightMix", 'VERTEX_WEIGHT_MIX')
            mod.vertex_group_a = value
            mod.vertex_group_b = key
            mod.mix_mode = 'ADD'
            mod.mix_set = 'B'
            bpy.ops.object.modifier_apply(modifier=mod.name)
            mesh.vertex_groups.remove(vg)

        tools.common.unselect_all()
        tools.common.select(armature)
        tools.common.switch('EDIT')

        # Reparent all bones to be correct for unity mapping and vrc itself
        for key, value in temp_list_reparent_bones.items():
            # current_step += 1
            # wm.progress_update(current_step)
            if key in armature.data.edit_bones and value in armature.data.edit_bones:
                armature.data.edit_bones.get(key).parent = armature.data.edit_bones.get(value)

        # Bone constraints should be deleted
        # if context.scene.remove_constraints:
        delete_bone_constraints()

        # Removes unused vertex groups
        tools.common.remove_unused_vertex_groups()

        # Zero weight bones should be deleted
        if context.scene.remove_zero_weight:
            delete_zero_weight()

        # # This is code for testing
        # print('18 LOOKING FOR BONES!!!')
        # if 'Breast_L' in tools.common.get_armature().pose.bones:
        #     print('THEY ARE THERE!')
        # return {'FINISHED'}

        # At this point, everything should be fixed and now we validate and give errors if needed

        # The bone hierarchy needs to be validated
        hierarchy_check_hips = check_hierarchy(False, [
            ['Hips', 'Spine', 'Chest', 'Neck', 'Head'],
            ['Hips', 'Left leg', 'Left knee', 'Left ankle'],
            ['Hips', 'Right leg', 'Right knee', 'Right ankle'],
            ['Chest', 'Left shoulder', 'Left arm', 'Left elbow', 'Left wrist'],
            ['Chest', 'Right shoulder', 'Right arm', 'Right elbow', 'Right wrist']
        ])

        wm.progress_end()

        if hierarchy_check_hips['result'] is False:
            self.report({'ERROR'}, hierarchy_check_hips['message'])
            return {'FINISHED'}

        self.report({'INFO'}, 'Model successfully fixed.')
        return {'FINISHED'}


def check_hierarchy(check_parenting, correct_hierarchy_array):
    armature = tools.common.set_default_stage()
    missing = ''

    for correct_hierarchy in correct_hierarchy_array:  # For each hierarchy array
        if len(missing) > 0 and missing[-3:] != ' - ':
            missing += '\n - '

        for index, bone in enumerate(correct_hierarchy):  # For each hierarchy bone item
            if bone not in missing and bone not in armature.data.bones:
                missing += bone + ', '

    if len(missing) > 0:
        return {'result': False, 'message': 'The following bones were not found: \n - ' +
                                            missing[:-2] + '\n' +
                                            "Make sure that this is a MMD or Mixamo model and DO NOT use PMXEditor (use the original .pmx/.pmd instead)!"}

    if check_parenting:
        for correct_hierarchy in correct_hierarchy_array:  # For each hierachy array
            previous = None
            for index, bone in enumerate(correct_hierarchy):  # For each hierarchy bone item
                if index > 0:
                    previous = correct_hierarchy[index - 1]

                if bone in armature.data.bones:
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
    tools.common.switch('POSE')

    for bone in armature.pose.bones:
        if len(bone.constraints) > 0:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)

    tools.common.switch('EDIT')
