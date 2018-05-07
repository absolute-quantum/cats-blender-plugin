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

import math
from mathutils import Matrix

mmd_tools_installed = False
try:
    import mmd_tools_local
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
                     '- Merges weight paints\n' \
                     '- Corrects the hips\n' \
                     '- Joins meshes\n' \
                     '- Converts morphs into shapes\n' \
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

        if len(tools.common.get_armature_objects()) == 0:
            return False

        return True

    def execute(self, context):
        if len(tools.common.get_meshes_objects()) == 0:
            self.report({'ERROR'}, 'No mesh inside the armature found!')
            return {'CANCELLED'}

        wm = bpy.context.window_manager
        armature = tools.common.set_default_stage()

        # Check if bone matrix == world matrix, important for xps models
        x_cord = 0
        y_cord = 1
        z_cord = 2
        fbx = False
        for index, bone in enumerate(armature.pose.bones):
            if index == 5:
                bone_pos = bone.matrix
                world_pos = armature.matrix_world * bone.matrix
                if abs(bone_pos[0][0]) != abs(world_pos[0][0]):
                    z_cord = 1
                    y_cord = 2
                    fbx = True
                    break

        # Add rename bones to reweight bones
        temp_rename_bones = copy.deepcopy(Bones.bone_rename)
        temp_reweight_bones = copy.deepcopy(Bones.bone_reweight)
        temp_list_reweight_bones = copy.deepcopy(Bones.bone_list_weight)
        temp_list_reparent_bones = copy.deepcopy(Bones.bone_list_parenting)

        for key, value in Bones.bone_rename_fingers.items():
            temp_rename_bones[key] = value

        for key, value in temp_rename_bones.items():
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
        for key, value in temp_rename_bones.items():
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

        # Get Double Entries
        print('DOUBLE ENTRIES:')
        print('RENAME:')
        list = []
        for key, value in temp_rename_bones.items():
            for name in value:
                if name not in list:
                    list.append(name)
                else:
                    print(key + " | " + name)
        print('REWEIGHT:')
        list = []
        for key, value in temp_reweight_bones.items():
            for name in value:
                if name not in list:
                    list.append(name)
                else:
                    print(key + " | " + name)
        print('DOUBLES END')

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
            except (AttributeError, RuntimeError):
                pass

        # mmd_tools specific operations
        shading_is_set = False
        if mmd_tools_installed:

            # Set correct mmd shading
            try:
                bpy.ops.mmd_tools.set_shadeless_glsl_shading()
                for obj in bpy.data.objects:
                    if obj.parent is None and obj.type == 'EMPTY':
                        obj.mmd_root.use_toon_texture = False
                        obj.mmd_root.use_sphere_texture = False
                        break
                shading_is_set = True
            except (AttributeError, RuntimeError):
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

        if not shading_is_set:
            try:
                bpy.ops.xps_tools.set_shadeless_glsl_shading()
            except (AttributeError, RuntimeError):
                pass

        # Set better bone view
        armature.data.draw_type = 'OCTAHEDRAL'
        armature.draw_type = 'WIRE'
        armature.show_x_ray = True
        armature.data.show_bone_custom_shapes = False

        # Disable backface culling
        if context.area:
            context.area.spaces[0].show_backface_culling = False

        # Remove Rigidbodies and joints
        for obj in bpy.data.objects:
            if 'rigidbodies' in obj.name or 'joints' in obj.name:
                tools.common.delete_hierarchy(obj)

        # Remove empty mmd object and unused objects
        tools.common.remove_empty()
        tools.common.remove_unused_objects()

        # Joins meshes into one and calls it 'Body'
        mesh = tools.common.join_meshes()
        # tools.common.select(armature)
        #
        # # Correct pivot position
        # try:
        #     # bpy.ops.view3d.snap_cursor_to_center()
        #     bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)
        #     bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        # except RuntimeError:
        #     pass

        tools.common.unselect_all()
        tools.common.select(mesh)

        # # Correct pivot position
        # try:
        #     # bpy.ops.view3d.snap_cursor_to_center()
        #     bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)
        #     bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        # except RuntimeError:
        #     pass

        # Reorders vrc shape keys to the correct order
        tools.common.repair_viseme_order(mesh.name)

        # Translate bones with dictionary
        tools.translate.translate_bones(self.dictionary)

        # Armature should be selected and in edit mode
        tools.common.unselect_all()
        tools.common.select(armature)
        tools.common.switch('EDIT')

        # Show all hidden verts and faces
        if bpy.ops.mesh.reveal.poll():
            bpy.ops.mesh.reveal()

        # Remove Bone Groups
        for group in armature.pose.bone_groups:
            armature.pose.bone_groups.remove(group)

        # Model should be in rest position
        armature.data.pose_position = 'REST'

        # Count steps for loading bar again and reset the layers
        steps += len(armature.data.edit_bones)
        for bone in armature.data.edit_bones:
            if bone.name in Bones.bone_list or bone.name.startswith(tuple(Bones.bone_list_with)):
                if bone.parent is not None:
                    steps += 1
                else:
                    steps -= 1
            bone.layers[0] = True

        # Start loading bar
        current_step = 0
        wm.progress_begin(current_step, steps)

        # Standardize bone names
        for bone in armature.data.edit_bones:
            current_step += 1
            wm.progress_update(current_step)

            name_split = bone.name.split('"')
            if len(name_split) > 3:
                name = name_split[1]
            else:
                name = bone.name

            name = name[:1].upper() + name[1:]

            name = name.replace(' ', '_')\
                .replace('-', '_')\
                .replace('.', '_')\
                .replace('____', '_')\
                .replace('___', '_')\
                .replace('__', '_')\
                .replace('ValveBiped_', '')\
                .replace('Bip1_', 'Bip_')\
                .replace('Bip01_', 'Bip_')\
                .replace('Bip001_', 'Bip_')\
                .replace('Character1_', '')\
                .replace('HLP_', '')\
                .replace('JD_', '')\
                .replace('JU_', '')\

            upper_name = ''
            for i, s in enumerate(name.split('_')):
                if i != 0:
                    upper_name += '_'
                upper_name += s[:1].upper() + s[1:]
            name = upper_name

            if name[-2:] == 'S0':
                name = name[:-2]

            # Remove '_01_' from beginning
            if name[0] == '_' and name[3] == '_' and name[1].isdigit() and name[2].isdigit():
                name = name[4:]

            # Remove '_01_' from beginning
            if name.startswith('C_'):
                name = name[2:]

            bone.name = name

        # Add conflicting bone names to new list
        conflicting_bones = []
        for names in Bones.bone_list_conflicting_names:
            if '\Left' not in names[1] and '\L' not in names[1]:
                conflicting_bones.append(names)
                continue

            names0 = []
            name1 = ''
            name2 = ''
            for name0 in names[0]:
                names0.append(name0.replace('\Left', 'Left').replace('\left', 'left').replace('\L', 'L').replace('\l', 'l'))
            if '\Left' in names[1] or '\L' in names[1]:
                name1 = names[1].replace('\Left', 'Left').replace('\left', 'left').replace('\L', 'L').replace('\l', 'l')
            if '\Left' in names[2] or '\L' in names[2]:
                name2 = names[2].replace('\Left', 'Left').replace('\left', 'left').replace('\L', 'L').replace('\l', 'l')
            conflicting_bones.append((names0, name1, name2))

            for name0 in names[0]:
                names0.append(name0.replace('\Left', 'Right').replace('\left', 'right').replace('\L', 'R').replace('\l', 'r'))
            if '\Left' in names[1] or '\L' in names[1]:
                name1 = names[1].replace('\Left', 'Right').replace('\left', 'right').replace('\L', 'R').replace('\l', 'r')
            if '\Left' in names[2] or '\L' in names[2]:
                name2 = names[2].replace('\Left', 'Right').replace('\left', 'right').replace('\L', 'R').replace('\l', 'r')
            conflicting_bones.append((names0, name1, name2))

        # Resolve conflicting bone names
        for names in conflicting_bones:
            if names[1] in armature.data.edit_bones:
                found_all = True
                for name in names[0]:
                    if name not in armature.data.edit_bones:
                        found_all = False
                        break
                if found_all:
                    armature.data.edit_bones.get(names[1]).name = names[2]

        # Standardize bone names again (new duplicate bones have ".001" in it)
        for bone in armature.data.edit_bones:
            bone.name = bone.name.replace('.', '_')

        # Rename all the bones
        spines = []
        spine_parts = []
        for bone_new, bones_old in temp_rename_bones.items():
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

                    # If spine bone, then don't rename for now, and ignore spines with no children
                    bone2 = armature.data.edit_bones.get(name)
                    if bone_new == 'Spine':
                        if len(bone2.children) > 0:
                            spines.append(name)
                        else:
                            spine_parts.append(name)
                        continue

                    # Rename the bone
                    if bone[0] not in armature.data.edit_bones:
                        if bone2 is not None:
                            bone2.name = bone[0]

        # Add bones to parent reweigth list
        for name in Bones.bone_reweigth_to_parent:
            if '\Left' in name or '\L' in name:
                bones = [name.replace('\Left', 'Left').replace('\left', 'left').replace('\L', 'L').replace('\l', 'l'),
                         name.replace('\Left', 'Right').replace('\left', 'right').replace('\L', 'R').replace('\l', 'r')]
            else:
                bones = [name]

            for bone_name in bones:
                bone = armature.data.edit_bones.get(bone_name)
                if bone and bone.parent:
                    temp_list_reweight_bones[bone_name] = bone.parent.name

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

        # Remove un-needed bones, disconnect them and set roll to 0
        for bone in armature.data.edit_bones:
            if bone.name in Bones.bone_list or bone.name.startswith(tuple(Bones.bone_list_with)):
                if bone.parent and mesh.vertex_groups.get(bone.name) and mesh.vertex_groups.get(bone.parent.name):
                    temp_list_reweight_bones[bone.name] = bone.parent.name
                else:
                    armature.data.edit_bones.remove(bone)
            else:
                bone.use_connect = False
                bone.roll = 0

        # Make Hips top parent and reparent other top bones to hips
        if 'Hips' in armature.data.edit_bones:
            hips = armature.data.edit_bones.get('Hips')
            hips.parent = None
            for bone in armature.data.edit_bones:
                if bone.parent is None:
                    bone.parent = hips

        # == FIXING OF SPECIAL BONE CASES ==

        # Fix all spines!
        spine_count = len(spines)

        # Fix spines from armatures with no upper body (like skirts)
        if len(spine_parts) == 1 and not armature.data.edit_bones.get('Neck'):
            if spine_count == 0:
                armature.data.edit_bones.get(spine_parts[0]).name = 'Spine'
            else:
                spines.append(spine_parts[0])

        if spine_count == 0:
            pass

        elif spine_count == 1:  # Create missing Chest
            print('BONE CREATION')
            spine = armature.data.edit_bones.get(spines[0])
            chest = armature.data.edit_bones.new('Chest')
            neck = armature.data.edit_bones.get('Neck')

            # Check for neck
            if neck:
                chest_top = neck.head
            else:
                chest_top = spine.tail

            # Correct the names
            spine.name = 'Spine'
            chest.name = 'Chest'

            # Set new Chest bone to new position
            chest.tail = chest_top
            chest.head = spine.head
            chest.head[z_cord] = spine.head[z_cord] + (chest_top[z_cord] - spine.head[z_cord]) / 2
            chest.head[y_cord] = spine.head[y_cord] + (chest_top[y_cord] - spine.head[y_cord]) / 2

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

        # Fix missing neck
        if 'Neck' not in armature.data.edit_bones:
            if 'Chest' in armature.data.edit_bones:
                if 'Head' in armature.data.edit_bones:
                    neck = armature.data.edit_bones.new('Neck')
                    chest = armature.data.edit_bones.get('Chest')
                    head = armature.data.edit_bones.get('Head')
                    neck.head = chest.tail
                    neck.tail = head.head

                    if neck.head[z_cord] == neck.tail[z_cord]:
                        neck.tail[z_cord] += 0.1

        # Correct arm bone positions for better looks
        tools.common.correct_bone_positions()

        # Hips bone should be fixed as per specification from the SDK code
        full_body_tracking = context.scene.full_body
        if not mixamo:
            if 'Hips' in armature.data.edit_bones:
                if 'Spine' in armature.data.edit_bones:
                    if 'Left leg' in armature.data.edit_bones:
                        if 'Right leg' in armature.data.edit_bones:
                            hips = armature.data.edit_bones.get('Hips')
                            spine = armature.data.edit_bones.get('Spine')
                            left_leg = armature.data.edit_bones.get('Left leg')
                            right_leg = armature.data.edit_bones.get('Right leg')
                            left_knee = armature.data.edit_bones.get('Left knee')
                            right_knee = armature.data.edit_bones.get('Right knee')

                            # Fixing the hips
                            if not full_body_tracking:

                                # Hips should have x value of 0 in both head and tail
                                middle_x = (right_leg.head[x_cord] + left_leg.head[x_cord]) / 2
                                hips.head[x_cord] = middle_x
                                hips.tail[x_cord] = middle_x

                                # Make sure the hips bone (tail and head tip) is aligned with the legs Y
                                hips.head[y_cord] = right_leg.head[y_cord]
                                hips.tail[y_cord] = right_leg.head[y_cord]

                                hips.head[z_cord] = right_leg.head[z_cord]
                                hips.tail[z_cord] = spine.head[z_cord]

                                if hips.tail[z_cord] < hips.head[z_cord]:
                                    hips.tail[z_cord] = hips.tail[z_cord] + 0.1



                                # if hips.tail[z_cord] < hips.head[z_cord]:
                                #     hips_height = hips.head[z_cord]
                                #     hips.head = hips.tail
                                #     hips.tail[z_cord] = hips_height
                                #
                                #
                                #
                                # hips_height = hips.head[z_cord]
                                # hips.head = hips.tail
                                # hips.tail[z_cord] = hips_height

                                # # Hips should have x value of 0 in both head and tail
                                # hips.head[x_cord] = 0
                                # hips.tail[x_cord] = 0

                                # # Make sure the hips bone (tail and head tip) is aligned with the legs Y
                                # hips.head[y_cord] = right_leg.head[y_cord]
                                # hips.tail[y_cord] = right_leg.head[y_cord]

                                # Flip the hips bone and make sure the hips bone is not below the legs bone
                                # hip_bone_length = abs(hips.tail[z_cord] - hips.head[z_cord])
                                # hips.head[z_cord] = right_leg.head[z_cord]
                                # hips.tail[z_cord] = hips.head[z_cord] + hip_bone_length

                                # hips.head[z_cord] = right_leg.head[z_cord]
                                # hips.tail[z_cord] = spine.head[z_cord]

                                # if hips.tail[z_cord] < hips.head[z_cord]:
                                #     hips.tail[z_cord] = hips.tail[z_cord] + 0.1

                            # elif spine and chest and neck and head:
                            #     bones = [hips, spine, chest, neck, head]
                            #     for bone in bones:
                            #         bone_length = abs(bone.tail[z_cord] - bone.head[z_cord])
                            #         bone.tail[x_cord] = bone.head[x_cord]
                            #         bone.tail[y_cord] = bone.head[y_cord]
                            #         bone.tail[z_cord] = bone.head[z_cord] + bone_length

                            else:
                                hips.head[x_cord] = 0
                                hips.tail[x_cord] = 0

                                hips.tail[y_cord] = hips.head[y_cord]

                                hips.head[z_cord] = spine.head[z_cord]
                                hips.tail[z_cord] = right_leg.head[z_cord]

                                left_leg_top = armature.data.edit_bones.new('Left leg top')
                                right_leg_top = armature.data.edit_bones.new('Right leg top')

                                left_leg_top.head = left_leg.head
                                left_leg_top.tail = left_leg.head
                                left_leg_top.tail[z_cord] = left_leg.head[z_cord] + 0.1

                                right_leg_top.head = right_leg.head
                                right_leg_top.tail = right_leg.head
                                right_leg_top.tail[z_cord] = right_leg.head[z_cord] + 0.1

                                spine.head = hips.head
                                # hips.head[z_cord] -= 0.0025
                                # spine.head[z_cord] += 0.0025

                                left_leg.name = "Left leg 2"
                                right_leg.name = "Right leg 2"

                                left_leg_top.name = "Left leg"
                                right_leg_top.name = "Right leg"

                                left_leg_top.parent = hips
                                right_leg_top.parent = hips

                                left_leg.parent = left_leg_top
                                right_leg.parent = right_leg_top

                                left_knee.parent = left_leg_top
                                right_knee.parent = right_leg_top

                            # # Fixing legs
                            # right_knee = armature.data.edit_bones.get('Right knee')
                            # left_knee = armature.data.edit_bones.get('Left knee')
                            # if right_knee and left_knee:
                            #     # Make sure the upper legs tail are the same x/y values as the lower leg tail x/y
                            #     right_leg.tail[x_cord] = right_leg.head[x_cord]
                            #     left_leg.tail[x_cord] = left_knee.head[x_cord]
                            #     right_leg.head[y_cord] = right_knee.head[y_cord]
                            #     left_leg.head[y_cord] = left_knee.head[y_cord]
                            #
                            #     # Make sure the leg bones are setup straight. (head should be same X as tail)
                            #     left_leg.head[x_cord] = left_leg.tail[x_cord]
                            #     right_leg.head[x_cord] = right_leg.tail[x_cord]
                            #
                            #     # Make sure the left legs (head tip) have the same Y values as right leg (head tip)
                            #     left_leg.head[y_cord] = right_leg.head[y_cord]

        # Reweight all eye children into the eyes TODO make recursive
        for eye_name in ['Eye_L', 'Eye_R']:
            if eye_name in armature.data.edit_bones:
                eye = armature.data.edit_bones.get(eye_name)
                for eye1 in eye.children:
                    temp_list_reweight_bones[eye1.name] = eye_name
                    for eye2 in eye1.children:
                        temp_list_reweight_bones[eye2.name] = eye_name
                        for eye3 in eye2.children:
                            temp_list_reweight_bones[eye3.name] = eye_name
                            for eye4 in eye3.children:
                                temp_list_reweight_bones[eye4.name] = eye_name
                                for eye5 in eye4.children:
                                    temp_list_reweight_bones[eye5.name] = eye_name

        # Rotate if on head and not fbx (Unreal engine model)
        if 'Hips' in armature.data.edit_bones:

            hips = armature.pose.bones.get('Hips')

            obj = hips.id_data
            matrix_final = obj.matrix_world * hips.matrix
            print(matrix_final)
            print(matrix_final[2][3])
            print(fbx)

            if not fbx and matrix_final[2][3] < 0:
                print(hips.head[0], hips.head[1], hips.head[2])
                # Rotation of -180 around the X-axis
                rot_x_neg180 = Matrix.Rotation(-math.pi, 4, 'X')
                armature.matrix_world = rot_x_neg180 * armature.matrix_world

                mesh.rotation_euler = (math.radians(180), 0, 0)

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

                    name = ''
                    if bone[1] in mesh.vertex_groups:
                        name = bone[1]
                    elif bone[1].lower() in mesh.vertex_groups:
                        name = bone[1].lower()

                    if name == '':
                        continue

                    if bone[0] == bone[1]:
                        print('BUG: ' + bone[0] + ' tried to mix weights with itself!')
                        continue

                    vg = mesh.vertex_groups.get(name)
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

                    bone_tmp = armature.data.bones.get(name)
                    if bone_tmp:
                        for child in bone_tmp.children:
                            if not temp_list_reparent_bones.get(child.name):
                                temp_list_reparent_bones[child.name] = bone[0]

                    # print(bone[1] + " to2 " + bone[0])
                    mod = mesh.modifiers.new("VertexWeightMix", 'VERTEX_WEIGHT_MIX')
                    mod.vertex_group_a = bone[0]
                    mod.vertex_group_b = name
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
                    if not temp_list_reparent_bones.get(child.name):
                        temp_list_reparent_bones[child.name] = bone[0]

            if key == value:
                print('BUG: ' + key + ' tried to mix weights with itself!')
                continue

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
        tools.common.delete_bone_constraints()

        # Removes unused vertex groups
        tools.common.remove_unused_vertex_groups()

        # Zero weight bones should be deleted
        if context.scene.remove_zero_weight:
            tools.common.delete_zero_weight()

        # # This is code for testing
        # print('LOOKING FOR BONES!')
        #  if 'Eye_L' in tools.common.get_armature().pose.bones:
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

        # Armature should be named correctly (has to be at the end because of multiple armatures)
        tools.common.fix_armature_names()

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
        message = 'The following bones were not found: \n - ' + missing[:-2]
        if not check_parenting:
            message += "\nLooks like you found a model which Cats could not fix!" \
                       "\nIf this is a non modified model we would love to make it compatible." \
                       "\nReport it to us in the forum or in our discord, links can be found in the Credits panel."

        return {'result': False, 'message': message}

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
