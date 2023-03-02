# GPL License

import bpy

from . import common as Common
from .register import register_wrap
from .. import globs
from .translations import t

# wm = bpy.context.window_manager
# wm.progress_begin(0, len(bone_merge))
# wm.progress_update(index)
# wm.progress_end()


@register_wrap
class BoneMergeButton(bpy.types.Operator):
    bl_idname = 'cats_bonemerge.merge_bones'
    bl_label = t('BoneMergeButton.label')
    bl_description = t('BoneMergeButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return Common.is_enum_non_empty(context.scene.merge_mesh) and Common.is_enum_non_empty(context.scene.merge_bone)

    def execute(self, context):
        saved_data = Common.SavedData()
        armature = Common.set_default_stage()

        parent_bones = globs.root_bones[context.scene.merge_bone]
        mesh = Common.get_objects()[context.scene.merge_mesh]
        ratio = context.scene.merge_ratio
        # debug
        print(ratio)

        did = 0
        todo = 0
        for bone_name in parent_bones:
            bone = armature.data.bones.get(bone_name)
            if not bone:
                continue

            for child in bone.children:
                todo += 1

        wm = bpy.context.window_manager
        wm.progress_begin(did, todo)

        # Start the bone check for every parent
        for bone_name in parent_bones:
            print('\nPARENT: ' + bone_name)
            bone = armature.data.bones.get(bone_name)
            if not bone:
                continue

            children = []
            for child in bone.children:
                children.append(child.name)

            for child_name in children:
                child = armature.data.bones.get(child_name)
                print('CHILD: ' + child.name)
                self.check_bone(mesh, child, ratio, ratio)
                did += 1
                wm.progress_update(did)

        saved_data.load()

        wm.progress_end()
        self.report({'INFO'}, t('BoneMergeButton.success'))
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
                # armature = Common.set_default_stage()
                # Common.switch('EDIT')
                #
                # child = armature.data.edit_bones.get(bone_name)
                # parent = armature.data.edit_bones.get(parent_name)
                # parent.tail = child.tail

                # Mix the weights
                Common.set_default_stage()
                Common.set_active(mesh)

                vg = mesh.vertex_groups.get(bone_name)
                vg2 = mesh.vertex_groups.get(parent_name)
                if vg is not None and vg2 is not None:
                    Common.mix_weights(mesh, bone_name, parent_name)

                Common.set_default_stage()

                # We are done, remove the bone
                Common.remove_bone(bone_name)

        armature = Common.set_default_stage()
        for child in children:
            bone = armature.data.bones.get(child)
            if bone is not None:
                self.check_bone(mesh, bone, ratio, i)
