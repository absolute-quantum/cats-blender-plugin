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
# Edits by: GiveMeAllYourCats

import bpy
import globs
import tools.common
import bpy

# wm = bpy.context.window_manager
# wm.progress_begin(0, len(bone_merge))
# wm.progress_update(index)
# wm.progress_end()


class BoneMergeButton(bpy.types.Operator):
    bl_idname = 'bone.merge'
    bl_label = 'Merge Bones'
    bl_description = 'Merges the bones'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    # used internally for get_all_childs only because get_all_childs is a recursive function
    child_bones = []

    def get_all_childs(self, parent_bones):
        armature = tools.common.set_default_stage()
        loop_child_bones = []

        for parent_bone in parent_bones:
            bone = armature.data.bones[parent_bone]
            if bone.name not in self.child_bones:
                self.child_bones.append(bone.name)
                for child_bone in bone.children:
                    loop_child_bones.append(child_bone.name)

        if len(loop_child_bones) >= 1:
            return self.get_all_childs(loop_child_bones)

        for_now = self.child_bones
        self.child_bones = []
        return for_now

    def execute(self, context):
        wm = bpy.context.window_manager

        parent_bones = globs.root_bones[context.scene.merge_bone]
        mesh = bpy.data.objects[bpy.context.scene.merge_mesh]

        # Find all childs of the parent bones
        bone_merge = {}
        for parent_bone in parent_bones:
            bone_merge[parent_bone] = self.get_all_childs([parent_bone])

        # For each tree bone, find out how much to merge
        wm.progress_begin(0, len(bone_merge))

        for index, parent_bone in enumerate(bone_merge):
            tree_bones = bone_merge[parent_bone]
            wm.progress_update(index)

            # The amount of bones to reduce to per bone tree
            # NOTE: we do this for every parent bone because the child bones might not be symmetrical across the whole group set
            reduce_to_per_tree = round(len(tree_bones) / 100 * abs(int(bpy.context.scene.merge_ratio * 100.0) - 100))
            if reduce_to_per_tree == 0:
                reduce_to_per_tree = 1

            reduce_to_per_tree = round(len(tree_bones) / reduce_to_per_tree)

            did_loops = 0

            # We want to start from the bottom!
            tree_bones.reverse()

            for index, current_item in enumerate(tree_bones):
                next_item = False
                if index <= len(tree_bones) - 2:
                    next_item = tree_bones[index + 1]

                did_loops += 1

                print(' > ', current_item, next_item)

                # Start merge process
                if next_item:
                    print('merging', current_item, 'into', next_item)

                    # Mix the weights
                    tools.common.unselect_all()
                    tools.common.switch('OBJECT')
                    tools.common.select(mesh)

                    vg = mesh.vertex_groups.get(current_item)
                    if vg is not None:
                        # NOTE: Mixes B into A
                        bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
                        bpy.context.object.modifiers['VertexWeightMix'].vertex_group_a = next_item
                        bpy.context.object.modifiers['VertexWeightMix'].vertex_group_b = current_item
                        bpy.context.object.modifiers['VertexWeightMix'].mix_mode = 'ADD'
                        bpy.context.object.modifiers['VertexWeightMix'].mix_set = 'B'
                        bpy.ops.object.modifier_apply(modifier='VertexWeightMix')
                        mesh.vertex_groups.remove(vg)

                    armature = tools.common.set_default_stage()
                    tools.common.switch('EDIT')

                    # Merge next_item bone with current_item
                    next_item_bone = armature.data.edit_bones[next_item]
                    current_item_bone = armature.data.edit_bones[current_item]

                    next_item_bone.tail = current_item_bone.tail

                    # We are done, remove the bone
                    tools.common.remove_bone(current_item)

                # satisfied with reduction of bones, terminate loop
                if did_loops >= reduce_to_per_tree:
                    break

            print(reduce_to_per_tree, tree_bones)

        tools.common.switch('OBJECT')
        wm.progress_end()
        self.report({'INFO'}, 'Merged bones. hurhur')
        return {'FINISHED'}
