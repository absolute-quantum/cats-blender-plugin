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
# Edits by: GiveMeAllYourCats

import bpy

import tools.common
import tools.translate

mmd_tools_installed = True
try:
    from mmd_tools import utils
    from mmd_tools.translations import DictionaryEnum
except ImportError:
    mmd_tools_installed = False

bone_list = ['ControlNode', 'ParentNode', 'Center', 'CenterTip', 'Groove', 'Waist', 'LowerBody2', 'Eyes', 'EyesTip',
             'LowerBodyTip', 'UpperBody2Tip', 'GrooveTip', 'NeckTip']
bone_list_with = ['_shadow_', '_dummy_', 'Dummy_', 'WaistCancel', 'LegIKParent', 'LegIK', 'LegIKTip', 'ToeTipIK',
                  'ToeTipIKTip', 'ShoulderP_', 'EyeTip_', 'ThumbTip_', 'IndexFingerTip_', 'MiddleFingerTip_',
                  'RingFingerTip_', 'LittleFingerTip_', 'HandDummy_', 'HandTip_', 'ShoulderC_', 'SleeveShoulderIK_']
bone_list_rename = {
    'hips': 'Hips',
    'spine': 'Spine',
    'chest': 'Chest',
    'neck': 'Neck',
    'head': 'Head',
    'LowerBody': 'Hips',
    'Lowerbody': 'Hips',
    'Lower body': 'Hips',
    'Lower Body': 'Hips',
    'Leg_L': 'Left leg',
    'left foot': 'Left leg',
    'Left foot': 'Left leg',
    'Leg_R': 'Right leg',
    'right foot': 'Right leg',
    'Right foot': 'Right leg',
    'Knee_L': 'Left knee',
    'Knee_R': 'Right knee',
    'Ankle_L': 'Left ankle',
    'Ankle_R': 'Right ankle',
    'ToeTip_L': 'Left toe',
    'ToeTip_R': 'Right toe',
    'UpperBody': 'Spine',
    'Upperbody': 'Spine',
    'Upper body': 'Spine',
    'Upper Body': 'Spine',
    'UpperBody2': 'Chest',
    'Upperbody2': 'Chest',
    'Upper body 2': 'Chest',
    'Upper Body 2': 'Chest',
    'Waist upper 2': 'Chest',
    'Waist Upper 2': 'Chest',
    'UpperBody3': 'NewChest',
    'Upperbody3': 'NewChest',
    'Upper body 3': 'NewChest',
    'Upper Body 3': 'NewChest',
    'Waist upper 3': 'NewChest',
    'Shoulder_L': 'Left shoulder',
    'Shoulder_R': 'Right shoulder',
    'Arm_L': 'Left arm',
    'Arm_R': 'Right arm',
    'Elbow_L': 'Left elbow',
    'Elbow_R': 'Right elbow',
    'Wrist_L': 'Left wrist',
    'Wrist_R': 'Right wrist'
}
bone_list_rename_unknown_side = {
    'Shoulder': 'shoulder',
    'Shoulder_001': 'shoulder'
}
bone_list_parenting = {
    'Spine': 'Hips',
    'Chest': 'Spine',
    'Neck': 'Chest',
    'Head': 'Neck',
    'Left shoulder': 'Chest',
    'Right shoulder': 'Chest',
    'Left arm': 'Left shoulder',
    'Right arm': 'Right shoulder',
    'Left elbow': 'Left arm',
    'Right elbow': 'Right arm',
    'Left wrist': 'Left elbow',
    'Right wrist': 'Right elbow',
    'Left knee': 'Left leg',
    'Right knee': 'Right leg',
    'Left ankle': 'Left knee',
    'Right ankle': 'Right knee',
    'Left toe': 'Left ankle',
    'Right toe': 'Right ankle',
}
bone_list_weight = {
    'LegD_L': 'Left leg',
    'LegD_R': 'Right leg',
    'KneeD_L': 'Left knee',
    'KneeD_R': 'Right knee',
    'AnkleD_L': 'Left ankle',
    'AnkleD_R': 'Right ankle',
    'LegTipEX_L': 'Left toe',
    'LegTipEX_R': 'Right toe',
    'Left foot D': 'Left leg',
    'Right foot D': 'Right leg',
    'Left knee D': 'Left knee',
    'Right knee D': 'Right knee',

    'ShoulderC_R': 'Right shoulder',
    'SleeveShoulderIK_R': 'Right shoulder',
    'Right shoulder weight': 'Right shoulder',

    'ShoulderC_L': 'Left shoulder',
    'SleeveShoulderIK_L': 'Left shoulder',
    'Left shoulder weight': 'Left shoulder',

    'ArmTwist_R': 'Right arm',
    'ArmTwist1_R': 'Right arm',
    'ArmTwist2_R': 'Right arm',
    'ArmTwist3_R': 'Right arm',
    'Right arm twist': 'Right arm',
    'Right arm torsion': 'Right arm',
    'Right arm torsion 1': 'Right arm',
    'Right arm tight': 'Right arm',
    'Right arm tight 1': 'Right arm',
    'Right arm tight 2': 'Right arm',
    'Right arm tight 3': 'Right arm',

    'ArmTwist_L': 'Left arm',
    'ArmTwist1_L': 'Left arm',
    'ArmTwist2_L': 'Left arm',
    'ArmTwist3_L': 'Left arm',
    'Left arm twist': 'Left arm',
    'Left arm torsion': 'Left arm',
    'Left arm torsion 1': 'Left arm',
    'Left arm tight': 'Left arm',
    'Left arm tight 1': 'Left arm',
    'Left arm tight 2': 'Left arm',
    'Left arm tight 3': 'Left arm',
    'ElbowAux+_L': 'Left arm',

    'HandTwist_R': 'Right elbow',
    'HandTwist1_R': 'Right elbow',
    'HandTwist2_R': 'Right elbow',
    'HandTwist3_R': 'Right elbow',
    'Right Hand 1': 'Right elbow',
    'Right Hand 2': 'Right elbow',
    'Right Hand 3': 'Right elbow',
    'Right hand 1': 'Right elbow',
    'Right hand 2': 'Right elbow',
    'Right hand 3': 'Right elbow',
    'Right hand twist': 'Right elbow',
    'Right hand twist 1': 'Right elbow',
    'Right hand twist 2': 'Right elbow',
    'Right Hand Thread 3': 'Right elbow',
    'ElbowAux+_R': 'Left arm',

    'HandTwist_L': 'Left elbow',
    'HandTwist1_L': 'Left elbow',
    'HandTwist2_L': 'Left elbow',
    'HandTwist3_L': 'Left elbow',
    'Left Hand 1': 'Left elbow',
    'Left Hand 2': 'Left elbow',
    'Left Hand 3': 'Left elbow',
    'Left hand 1': 'Left elbow',
    'Left hand 2': 'Left elbow',
    'Left hand 3': 'Left elbow',
    'Left hand twist': 'Left elbow',
    'Left hand twist 1': 'Left elbow',
    'Left hand twist 2': 'Left elbow',
    'Left Hand Thread 3': 'Left elbow',
}
dont_delete_these_bones = {
    'Hips', 'Spine', 'Chest', 'Neck', 'Head',
    'Left leg', 'Left knee', 'Left ankle', 'Left toe',
    'Right leg', 'Right knee', 'Right ankle', 'Right toe',
    'Left shoulder', 'Left arm', 'Left elbow', 'Left wrist',
    'Right shoulder', 'Right arm', 'Right elbow', 'Right wrist'
}


def delete_hierarchy(obj):
    names = {obj.name}

    def get_child_names(objz):
        for child in objz.children:
            names.add(child.name)
            if child.children:
                get_child_names(child)

    get_child_names(obj)
    objects = bpy.data.objects
    [setattr(objects[n], 'select', True) for n in names]

    bpy.ops.object.delete()


class FixArmature(bpy.types.Operator):
    bl_idname = 'armature.fix'
    bl_label = 'Fix armature'
    bl_description = "Fixes the armature by:\n" \
                     + "- Reparenting bones\n" \
                     + "- Removing unnecessary bones\n" \
                     + "- Renaming objects and bones\n" \
                     + "- Mixing weight paints\n" \
                     + "- Rotating the hips\n" \
                     + "- Joining all meshes\n" \
                     + "- Removing rigidbodies and joints\n" \
                     + "- Deleting unused vertex groups"

    bl_options = {'REGISTER', 'UNDO'}

    tries = 0

    if mmd_tools_installed:
        dictionary = bpy.props.EnumProperty(
            name='Dictionary',
            items=DictionaryEnum.get_dictionary_items,
            description='Translate names from Japanese to English using selected dictionary',
        )

    def execute(self, context):
        self.tries += 1

        if mmd_tools_installed is False:
            self.report({'ERROR'}, 'mmd_tools is not installed, this feature is disabled')
            return {'CANCELLED'}

        # preservestate = tools.common.PreserveState()
        # preservestate.save()

        # bpy.ops.object.hide_view_clear()
        tools.common.unselect_all()
        bpy.ops.object.mode_set(mode='OBJECT')
        armature = tools.common.get_armature()
        mesh = None

        # Empty objects should be removed
        tools.common.remove_empty()

        # Rigidbodies and joints should be removed
        for obj in bpy.data.objects:
            if obj.name == 'rigidbodies' or obj.name == 'joints':
                delete_hierarchy(obj)
                bpy.data.objects.remove(obj)

        # Model should be in rest position
        armature.data.pose_position = 'REST'

        # Armature should be named correctly
        armature.name = 'Armature'
        armature.data.name = 'Armature'

        # Meshes should be combined
        tools.common.unselect_all()
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                tools.common.select(ob)
        bpy.ops.object.join()

        # Mesh should be renamed to Body
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                ob.name = 'Body'
                mesh = ob
                break

        # Armature should be selected and in edit mode
        tools.common.unselect_all()
        tools.common.select(armature)
        bpy.ops.object.mode_set(mode='EDIT')

        # Translate bones with dictionary
        translator = DictionaryEnum.get_translator(self.dictionary)
        for bone in armature.data.bones:
            bone.name = utils.convertNameToLR(bone.name, True)
            bone.name = translator.translate(bone.name)


        # Rename bones
        for key, value in bone_list_rename.items():
            if key in armature.data.edit_bones:
                armature.data.edit_bones.get(key).name = value

        # Rename bones which don't have a side and try to detect it automatically
        for key, value in bone_list_rename_unknown_side.items():
            for bone in armature.data.edit_bones:
                parent = bone.parent
                if parent is None:
                    continue
                if parent.name == key:
                    if 'right' in bone.name.lower():
                        parent.name = 'Right ' + value
                        break
                    elif 'left' in bone.name.lower():
                        parent.name = 'Left ' + value
                        break

                parent = parent.parent
                if parent is None:
                    continue
                if parent.name == key:
                    if 'right' in bone.name.lower():
                        parent.name = 'Right ' + value
                        break
                    elif 'left' in bone.name.lower():
                        parent.name = 'Left ' + value
                        break

        # Remove un-needed bones
        for bone in armature.data.edit_bones:
            if bone.name in bone_list or bone.name.startswith(tuple(bone_list_with)):
                armature.data.edit_bones.remove(bone)

        # Disconnect all bones
        for bone in armature.data.edit_bones:
            bone.use_connect = False

        # Make Hips top parent and reparent other top bones to hips
        if 'Hips' in armature.data.edit_bones:
            hips = armature.data.edit_bones.get('Hips')
            hips.parent = None
            for bone in armature.data.edit_bones:
                if bone.parent is None:
                    bone.parent = hips

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

                    # Rename chests
                    old_chest.name = 'ChestOld'
                    new_chest.name = 'Chest'

                    # Adjust spine bone position
                    spine.tail[0] += old_chest.tail[0] - old_chest.head[0]
                    spine.tail[1] += old_chest.tail[1] - old_chest.head[1]
                    spine.tail[2] += old_chest.tail[2] - old_chest.head[2]

                    # Move weight paint to spine
                    tools.common.unselect_all()
                    bpy.ops.object.mode_set(mode='OBJECT')
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
                    bpy.ops.object.mode_set(mode='EDIT')

                    # Delete old chest bone
                    # New Check is necessary because switch to object mode in between

                    old_chest = armature.data.edit_bones.get('ChestOld')
                    armature.data.edit_bones.remove(old_chest)

        # Hips bone should be fixed as per specification from the SDK code
        if 'Hips' in armature.data.edit_bones:
            if 'Left leg' in armature.data.edit_bones:
                if 'Right leg' in armature.data.edit_bones:
                    hip_bone = armature.data.edit_bones.get('Hips')
                    left_leg = armature.data.edit_bones.get('Left leg')
                    right_leg = armature.data.edit_bones.get('Right leg')

                    # Make sure the left legs (head tip) have the same Y values as right leg (head tip)
                    left_leg.head[1] = right_leg.head[1]

                    # Make sure the hips bone (tail and head tip) is aligned with the legs Y
                    hip_bone.head[1] = right_leg.head[1]
                    hip_bone.tail[1] = right_leg.head[1]

                    # Flip the hips bone and make sure the hips bone is not below the legs bone
                    hip_bone_length = abs(hip_bone.tail[2] - hip_bone.head[2])
                    hip_bone.head[2] = right_leg.head[2]
                    hip_bone.tail[2] = hip_bone.head[2] + hip_bone_length

        # Reparent all bones to be correct for unity mapping and vrc itself
        for key, value in bone_list_parenting.items():
            if key in armature.data.edit_bones and value in armature.data.edit_bones:
                armature.data.edit_bones.get(key).parent = armature.data.edit_bones.get(value)

        # Weights should be mixed
        tools.common.unselect_all()
        bpy.ops.object.mode_set(mode='OBJECT')
        tools.common.select(mesh)

        for key, value in bone_list_weight.items():
            vg = mesh.vertex_groups.get(key)
            vg2 = mesh.vertex_groups.get(value)
            if vg is None or vg2 is None:
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
        bpy.ops.object.mode_set(mode='EDIT')

        # Bone constraints should be deleted
        if context.scene.remove_constraints:
            delete_bone_constraints()

        # Removes unused vertex groups
        tools.common.remove_unused_vertex_groups()

        # Zero weight bones should be deleted
        # TODO: doesn't seem to be working at first glance
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

        if hierarchy_check_hips['result'] is False:
            # if this is first try with an error then retry. This fixes the bonetranslation.blend error
            # TODO: figure out why?
            if self.tries == 1:
                return self.execute(context)
            elif self.tries == 2:
                self.tries = 0

            self.report({'ERROR'}, hierarchy_check_hips['message'])
            return {'FINISHED'}

        # preservestate.load()

        self.report({'INFO'}, 'Armature fixed.')
        return {'FINISHED'}


def check_hierarchy(correct_hierarchy_array):
    armature = tools.common.get_armature()
    error = None

    for correct_hierarchy in correct_hierarchy_array:
        for index, item in enumerate(correct_hierarchy):
            # NOTE:  armature.data.bones is being used instead of armature.data.edit_bones because of a failed test (edit_bones array empty for some reason)
            if item not in armature.data.bones:
                error = {'result': False, 'message': item + ' was not found in the hierarchy, this will cause problems!'}
                break

            bone = armature.data.bones.get(item)

            if index == 0:
                # first level items do not need to be parent checked
                pass
            if bone.name == 'Hips':
                # Hips don't have to be checked
                pass
            else:
                prevbone = None
                try:
                    prevbone = armature.data.bones.get(correct_hierarchy[index - 1])
                except KeyError:
                    error = {'result': False, 'message': correct_hierarchy[index - 1] + ' bone does not exist, this might cause problems!'}

                if error is None:
                    if bone.parent is None:
                        error = {'result': False, 'message': bone.name + ' is not parented at all, this will cause problems!'}
                    # else: # TODO this part is buggy, should be fixed!
                    #     print("Debug: " + bone.parent.name + " " + prevbone.name)
                    #     if bone.parent.name != prevbone.name:
                    #         error = {'result': False, 'message': bone.parent.name + ' is not parented to ' + prevbone.name + ', this will cause problems!'}
                    #         print("Debug2: " + bone.parent.name + " " + prevbone.name)

    if error is None:
        return_value = {'result': True}
    else:
        return_value = error

    return return_value


def delete_zero_weight():
    armature = tools.common.get_armature()

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
                    vertex_group_names_used.add(vertex_group_id_to_vertex_group_name[group.group])

    not_used_bone_names = bone_names_to_work_on - vertex_group_names_used

    for bone_name in not_used_bone_names:
        if bone_name not in dont_delete_these_bones:
            armature.data.edit_bones.remove(bone_name_to_edit_bone[bone_name])  # delete bone
            if bone_name in vertex_group_name_to_objects_having_same_named_vertex_group:
                for objects in vertex_group_name_to_objects_having_same_named_vertex_group[bone_name]:  # delete vertex groups
                    vertex_group = objects.vertex_groups.get(bone_name)
                    if vertex_group is not None:
                        objects.vertex_groups.remove(vertex_group)


def delete_bone_constraints():
    armature = tools.common.get_armature()

    bones = set([bone.name for bone in armature.pose.bones])

    bpy.ops.object.mode_set(mode='POSE')
    bone_name_to_pose_bone = dict()
    for bone in armature.pose.bones:
        bone_name_to_pose_bone[bone.name] = bone

    for bone_name in bones:
        bone = bone_name_to_pose_bone[bone_name]
        if len(bone.constraints) > 0:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)

    bpy.ops.object.mode_set(mode='EDIT')
