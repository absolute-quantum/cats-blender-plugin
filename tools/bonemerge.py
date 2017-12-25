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
# Edits by: GiveMeAllYourCats

import bpy
import globs
import tools.common

# wm = bpy.context.window_manager
# wm.progress_begin(0, len(bone_merge))
# wm.progress_update(index)
# wm.progress_end()


class BoneMergeButton(bpy.types.Operator):
    bl_idname = 'bone.merge'
    bl_label = 'Merge Bones'
    bl_description = 'Merges the given percentage of bones together.\n' \
                     'This is useful to reduce the amount of bones used by Dynamic Bones.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if context.scene.merge_mesh == "" or context.scene.merge_bone == "":
            return False
        return True

    def execute(self, context):
        armature = tools.common.set_default_stage()

        parent_bones = globs.root_bones[context.scene.merge_bone]
        mesh = bpy.data.objects[context.scene.merge_mesh]
        ratio = context.scene.merge_ratio
        print(ratio)

        did = 0
        todo = 0
        for bone_name in parent_bones:
            bone = armature.data.bones.get(bone_name)
            if bone is None:
                continue

            for child in bone.children:
                todo += 1

        wm = bpy.context.window_manager
        wm.progress_begin(did, todo)

        # Start the bone check for every parent
        for bone_name in parent_bones:
            bone = armature.data.bones.get(bone_name)
            if bone is None:
                continue

            for child in bone.children:
                self.check_bone(mesh, child, ratio, ratio)
                did += 1
                wm.progress_update(did)

        wm.progress_end()
        self.report({'INFO'}, 'Merged bones.')
        return {'FINISHED'}

    # Go through this until the last child is reached
    def check_bone(self, mesh, bone, ratio, i):
        if bone is None:
            print('END FOUND')
            return

        # Increase number by the ratio
        i += ratio
        bone_name = bone.name

        # Get all children names
        children = []
        for child in bone.children:
            children.append(child.name)

        # Check if bone will be merged
        if i >= 100:
            i -= 100

            if bone.parent is not None:
                parent_name = bone.parent.name

                print('Merging ' + bone_name + ' into ' + parent_name+ ' with ratio ' + str(i) )

                # # Set new parent bone position
                # armature = tools.common.set_default_stage()
                # tools.common.switch('EDIT')
                #
                # child = armature.data.edit_bones.get(bone_name)
                # parent = armature.data.edit_bones.get(parent_name)
                # parent.tail = child.tail

                # Mix the weights
                tools.common.set_default_stage()
                tools.common.select(mesh)

                vg = mesh.vertex_groups.get(bone_name)
                vg2 = mesh.vertex_groups.get(parent_name)
                if vg is not None and vg2 is not None:
                    # NOTE: Mixes B into A
                    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
                    bpy.context.object.modifiers['VertexWeightMix'].vertex_group_a = parent_name
                    bpy.context.object.modifiers['VertexWeightMix'].vertex_group_b = bone_name
                    bpy.context.object.modifiers['VertexWeightMix'].mix_mode = 'ADD'
                    bpy.context.object.modifiers['VertexWeightMix'].mix_set = 'B'
                    bpy.ops.object.modifier_apply(modifier='VertexWeightMix')
                    mesh.vertex_groups.remove(vg)

                tools.common.set_default_stage()

                # We are done, remove the bone
                tools.common.remove_bone(bone_name)

        armature = tools.common.set_default_stage()
        for child in children:
            bone = armature.data.bones.get(child)
            if bone is not None:
                self.check_bone(mesh, bone, ratio, i)
