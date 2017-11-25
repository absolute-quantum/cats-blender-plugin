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
import tools.common
import globs

class RootButton(bpy.types.Operator):
    bl_idname = 'root.function'
    bl_label = 'Parent bones'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        tools.common.unhide_all()

        bpy.ops.object.mode_set(mode='OBJECT')

        armature = tools.common.get_armature()

        bpy.context.scene.objects.active = armature
        armature.select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='EDIT')

        # this is the bones that will be parented
        child_bones = globs.root_bones[context.scene.root_bone]

        # Create the new root bone
        new_bone_name = 'RootBone_' + child_bones[0]
        root_bone = bpy.context.object.data.edit_bones.new(new_bone_name)
        root_bone.parent = bpy.context.object.data.edit_bones[child_bones[0]].parent

        # Parent all childs to the new root bone
        for child_bone in child_bones:
            bpy.context.object.data.edit_bones[child_bone].use_connect = False
            bpy.context.object.data.edit_bones[child_bone].parent = root_bone

        # Set position of new bone to parent
        root_bone.head = root_bone.parent.head
        root_bone.tail = root_bone.parent.tail

        # reset the root bone cache
        globs.root_bones_choices = {}

        self.report({'INFO'}, 'Bones parented!')

        return{'FINISHED'}


class RefreshRootButton(bpy.types.Operator):
    bl_idname = 'refresh.root'
    bl_label = 'Refresh list'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        globs.root_bones_choices = {}

        self.report({'INFO'}, 'Root bones refreshed, check the root bones list again.')

        return{'FINISHED'}
