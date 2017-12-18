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

        # Start the bone check for every parent
        for bone_name in parent_bones:
            bone = armature.data.bones.get(bone_name)
            if bone is None:
                continue

            for child in bone.children:
                self.check_bone(mesh, child, ratio, ratio)

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

    def execute2(self, context):
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
