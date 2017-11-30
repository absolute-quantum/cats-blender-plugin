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

# Code author: GiveMeAllYourCats
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: GiveMeAllYourCats, Hotox

import bpy
import tools.common
import globs

from difflib import SequenceMatcher


class RootButton(bpy.types.Operator):
    bl_idname = 'root.function'
    bl_label = 'Parent Bones'
    bl_description = 'This will duplicate the parent of the bones and reparent them to the duplicate.\n' \
                     'Very useful for Dynamic Bones.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.scene.root_bone == "":
            return False
        return True

    def execute(self, context):
        # PreserveState = tools.common.PreserveState()
        # PreserveState.save()

        tools.common.unhide_all()

        tools.common.switch('OBJECT')

        armature = tools.common.get_armature()

        bpy.context.scene.objects.active = armature
        armature.select = True

        tools.common.switch('EDIT')
        tools.common.switch('EDIT')

        # this is the bones that will be parented
        child_bones = globs.root_bones[context.scene.root_bone]

        # Create the new root bone
        new_bone_name = 'RootBone_' + child_bones[0]
        root_bone = bpy.context.object.data.edit_bones.new(new_bone_name)
        root_bone.parent = bpy.context.object.data.edit_bones[child_bones[0]].parent

        # Parent all children to the new root bone
        for child_bone in child_bones:
            bpy.context.object.data.edit_bones[child_bone].use_connect = False
            bpy.context.object.data.edit_bones[child_bone].parent = root_bone

        # Set position of new bone to parent
        root_bone.head = root_bone.parent.head
        root_bone.tail = root_bone.parent.tail

        # reset the root bone cache
        globs.root_bones_choices = {}

        # PreserveState.load()

        self.report({'INFO'}, 'Bones parented!')

        return{'FINISHED'}


def get_parent_root_bones(self, context):
    armature = tools.common.get_armature().data
    check_these_bones = []
    bone_groups = {}
    choices = []

    # Get cache if exists
    if len(globs.root_bones_choices) >= 1:
        return globs.root_bones_choices

    for bone in armature.bones:
        check_these_bones.append(bone.name)

    ignore_bone_names_with = [
        'finger',
        'chest',
        'leg',
        'arm',
        'spine',
        'shoulder',
        'neck',
        'knee',
        'eye',
        'toe',
        'head',
        'teeth',
        'thumb',
        'wrist',
        'ankle',
        'elbow',
        'hips',
        'twist',
        'shadow',
        'hand',
        'rootbone'
    ]

    # Find and group bones together that look alike
    # Please do not ask how this works
    for rootbone in armature.bones:
        for ignore_bone_name in ignore_bone_names_with:
            if ignore_bone_name in rootbone.name.lower():
                break
        for bone in armature.bones:
            if bone.name in check_these_bones:
                m = SequenceMatcher(None, rootbone.name, bone.name)
                if m.ratio() >= 0.70:
                    accepted = False
                    if bone.parent is not None:
                        for child_bone in bone.parent.children:
                            if child_bone.name == rootbone.name:
                                accepted = True

                    check_these_bones.remove(bone.name)
                    if accepted:
                        if rootbone.name not in bone_groups:
                            bone_groups[rootbone.name] = []
                        bone_groups[rootbone.name].append(bone.name)

    for rootbone in bone_groups:
        # NOTE: user probably doesn't want to parent bones together that have less then 2 bones
        if len(bone_groups[rootbone]) >= 2:
            choices.append((rootbone, rootbone.replace('_R', '').replace('_L', '') + ' (' + str(len(bone_groups[rootbone])) + ' bones)', rootbone))

    bpy.types.Object.Enum = choices

    # set cache
    globs.root_bones = bone_groups
    globs.root_bones_choices = choices

    return bpy.types.Object.Enum


class RefreshRootButton(bpy.types.Operator):
    bl_idname = 'refresh.root'
    bl_label = 'Refresh List'
    bl_description = 'This will clear the group bones list cache and rebuild it, useful if bones have changed or your model.'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        globs.root_bones_choices = {}

        self.report({'INFO'}, 'Root bones refreshed, check the root bones list again.')

        return{'FINISHED'}
