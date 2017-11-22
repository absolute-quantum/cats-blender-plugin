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
# Edits by: 

import bpy
import globs

from difflib import SequenceMatcher

def get_armature():
    armature = None
    for object in bpy.data.objects:
        if object.type == 'ARMATURE':

            return object

def unhide_all():
    for object in bpy.data.objects:
        object.hide = False

def remove_empty():
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'EMPTY':
            bpy.context.scene.objects.active = bpy.data.objects[obj.name]
            obj.select = True
            bpy.ops.object.delete(use_global=False)

def get_meshes(self, context):
    choices = []

    for object in bpy.context.scene.objects:
        if object.type == 'MESH':
            choices.append((object.name, object.name, object.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: x[0])
    return bpy.types.Object.Enum

def get_bones(self, context):
    choices = []
    armature = get_armature().data

    for bone in armature.bones:
        choices.append((bone.name, bone.name, bone.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: x[0])

    return bpy.types.Object.Enum

def get_shapekeys(self, context):
    choices = []

    for shapekey in bpy.data.objects[context.scene.mesh_name_eye].data.shape_keys.key_blocks:
        choices.append((shapekey.name, shapekey.name, shapekey.name))

    bpy.types.Object.Enum = sorted(choices, key=lambda x: x[0])

    return bpy.types.Object.Enum

def get_texture_sizes(self, context):
    bpy.types.Object.Enum = [
        ("1024", "1024 (low)", "1024"),
        ("2048", "2048 (medium)", "2048"),
        ("4096", "4096 (high)", "4096")
    ]

    return bpy.types.Object.Enum

def get_parent_root_bones(self, context):
    armature = get_armature().data
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