# -*- coding: utf-8 -*-

import bpy
from bpy.types import Operator

from collections import OrderedDict

from mmd_tools_local import register_wrap
from mmd_tools_local import utils
from mmd_tools_local.utils import ItemOp, ItemMoveOp
import mmd_tools_local.core.model as mmd_model


@register_wrap
class AddDisplayItemFrame(Operator):
    bl_idname = 'mmd_tools.display_item_frame_add'
    bl_label = 'Add Display Item Frame'
    bl_description = 'Add a display item frame to the list'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root

        frames = mmd_root.display_item_frames
        item, index = ItemOp.add_after(frames, max(1, mmd_root.active_display_item_frame))
        item.name = 'Display Frame'
        mmd_root.active_display_item_frame = index
        return {'FINISHED'}

@register_wrap
class RemoveDisplayItemFrame(Operator):
    bl_idname = 'mmd_tools.display_item_frame_remove'
    bl_label = 'Remove Display Item Frame'
    bl_description = 'Remove active display item frame from the list'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root

        index = mmd_root.active_display_item_frame
        frames = mmd_root.display_item_frames
        frame = ItemOp.get_by_index(frames, index)
        if frame and frame.is_special:
            frame.data.clear()
            frame.active_item = 0
        else:
            frames.remove(index)
            mmd_root.active_display_item_frame = min(len(frames)-1, max(2, index-1))
        return {'FINISHED'}

@register_wrap
class MoveDisplayItemFrame(Operator, ItemMoveOp):
    bl_idname = 'mmd_tools.display_item_frame_move'
    bl_label = 'Move Display Item Frame'
    bl_description = 'Move active display item frame up/down in the list'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root

        index = mmd_root.active_display_item_frame
        frames = mmd_root.display_item_frames
        frame = ItemOp.get_by_index(frames, index)
        if frame and frame.is_special:
            pass
        else:
            mmd_root.active_display_item_frame = self.move(frames, index, self.type, index_min=2)
        return {'FINISHED'}

@register_wrap
class AddDisplayItem(Operator):
    bl_idname = 'mmd_tools.display_item_add'
    bl_label = 'Add Display Item'
    bl_description = 'Add a display item to the list'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root
        frame = ItemOp.get_by_index(mmd_root.display_item_frames, mmd_root.active_display_item_frame)
        if frame is None:
            return {'CANCELLED'}

        if frame.name == u'表情':
            morph = ItemOp.get_by_index(getattr(mmd_root, mmd_root.active_morph_type), mmd_root.active_morph)
            morph_name = morph.name if morph else 'Morph Item'
            self._add_item(frame, 'MORPH', morph_name, mmd_root.active_morph_type)
        else:
            bone_name = context.active_bone.name if context.active_bone else 'Bone Item'
            self._add_item(frame, 'BONE', bone_name)
        return {'FINISHED'}

    def _add_item(self, frame, item_type, item_name, morph_type=None):
        items = frame.data
        item, index = ItemOp.add_after(items, frame.active_item)
        item.type = item_type
        item.name = item_name
        if morph_type:
            item.morph_type = morph_type
        frame.active_item = index

@register_wrap
class RemoveDisplayItem(Operator):
    bl_idname = 'mmd_tools.display_item_remove'
    bl_label = 'Remove Display Item'
    bl_description = 'Remove display item(s) from the list'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    all = bpy.props.BoolProperty(
        name='All',
        description='Delete all display items',
        default=False,
        options={'SKIP_SAVE'},
        )

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root
        frame = ItemOp.get_by_index(mmd_root.display_item_frames, mmd_root.active_display_item_frame)
        if frame is None:
            return {'CANCELLED'}
        if self.all:
            frame.data.clear()
            frame.active_item = 0
        else:
            frame.data.remove(frame.active_item)
            frame.active_item = max(0, frame.active_item-1)
        return {'FINISHED'}

@register_wrap
class MoveDisplayItem(Operator, ItemMoveOp):
    bl_idname = 'mmd_tools.display_item_move'
    bl_label = 'Move Display Item'
    bl_description = 'Move active display item up/dowm in the list'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root
        frame = ItemOp.get_by_index(mmd_root.display_item_frames, mmd_root.active_display_item_frame)
        if frame is None:
            return {'CANCELLED'}
        frame.active_item = self.move(frame.data, frame.active_item, self.type)
        return {'FINISHED'}

@register_wrap
class FindDisplayItem(Operator):
    bl_idname = 'mmd_tools.display_item_find'
    bl_label = 'Find Display Item'
    bl_description = 'Find the display item of active bone or morph'
    bl_options = {'INTERNAL'}

    type = bpy.props.EnumProperty(
        name='Type',
        description='Find type',
        items = [
            ('BONE', 'Find Bone Item', 'Find active bone in Display Panel', 0),
            ('MORPH', 'Find Morph Item', 'Find active morph of Morph Tools Panel in Display Panel', 1),
            ],
        default = 'BONE',
        )

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root
        if self.type == 'MORPH':
            morph_type = mmd_root.active_morph_type
            morph = ItemOp.get_by_index(getattr(mmd_root, morph_type), mmd_root.active_morph)
            if morph is None:
                return {'CANCELLED'}

            morph_name = morph.name
            def __check(item):
                return item.type == 'MORPH' and item.name == morph_name and item.morph_type == morph_type
            self._find_display_item(mmd_root, __check)
        else:
            if context.active_bone is None:
                return {'CANCELLED'}

            bone_name = context.active_bone.name
            def __check(item):
                return item.type == 'BONE' and item.name == bone_name
            self._find_display_item(mmd_root, __check)
        return {'FINISHED'}

    def _find_display_item(self, mmd_root, check_func=None):
        for i, frame in enumerate(mmd_root.display_item_frames):
            for j, item in enumerate(frame.data):
                if check_func(item):
                    mmd_root.active_display_item_frame = i
                    frame.active_item = j
                    return

@register_wrap
class SelectCurrentDisplayItem(Operator):
    bl_idname = 'mmd_tools.display_item_select_current'
    bl_label = 'Select Current Display Item'
    bl_description = 'Select the bone or morph assigned to the display item'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root
        frame = ItemOp.get_by_index(mmd_root.display_item_frames, mmd_root.active_display_item_frame)
        if frame is None:
            return {'CANCELLED'}
        item = ItemOp.get_by_index(frame.data, frame.active_item)
        if item is None:
            return {'CANCELLED'}

        if item.type == 'MORPH':
            morphs = getattr(mmd_root, item.morph_type)
            index = morphs.find(item.name)
            if index >= 0:
                mmd_root.active_morph_type = item.morph_type
                mmd_root.active_morph = index
        else:
            utils.selectSingleBone(context, mmd_model.Model(root).armature(), item.name)
        return {'FINISHED'}

@register_wrap
class DisplayItemQuickSetup(Operator):
    bl_idname = 'mmd_tools.display_item_quick_setup'
    bl_label = 'Display Item Quick Setup'
    bl_description = 'Quick setup display items'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    type = bpy.props.EnumProperty(
        name='Type',
        description='Select type',
        items = [
            ('RESET', 'Reset', 'Clear all items and frames, reset to default', 'X', 0),
            ('FACIAL', 'Load Facial Items', 'Load all morphs to faical frame', 'SHAPEKEY_DATA', 1),
            ('GROUP_LOAD', 'Load Bone Groups', "Load armature's bone groups to display item frames", 'GROUP_BONE', 2),
            ('GROUP_APPLY', 'Apply Bone Groups', "Apply display item frames to armature's bone groups", 'GROUP_BONE', 3),
            ],
        default='FACIAL',
        )

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        if self.type == 'RESET':
            rig.initialDisplayFrames()
        elif self.type == 'FACIAL':
            rig.initialDisplayFrames(reset=False) # ensure default frames
            self.load_facial_items(root.mmd_root)
        elif self.type == 'GROUP_LOAD':
            self.load_bone_groups(root.mmd_root, rig.armature())
            rig.initialDisplayFrames(reset=False) # ensure default frames
        elif self.type == 'GROUP_APPLY':
            self.apply_bone_groups(root.mmd_root, rig.armature())
        return {'FINISHED'}

    @staticmethod
    def load_facial_items(mmd_root):
        item_list = []
        item_list.extend(('vertex_morphs', i.name) for i in mmd_root.vertex_morphs)
        item_list.extend(('bone_morphs', i.name) for i in mmd_root.bone_morphs)
        item_list.extend(('material_morphs', i.name) for i in mmd_root.material_morphs)
        item_list.extend(('uv_morphs', i.name) for i in mmd_root.uv_morphs)
        item_list.extend(('group_morphs', i.name) for i in mmd_root.group_morphs)

        frames = mmd_root.display_item_frames
        frame = frames[u'表情']
        facial_items = frame.data
        mmd_root.active_display_item_frame = frames.find(frame.name)

        # keep original item order
        old = tuple((i.morph_type, i.name) for i in facial_items)
        item_list.sort(key=lambda x: old.index(x) if x in old else len(old))

        ItemOp.resize(facial_items, len(item_list))
        for item, data in zip(facial_items, item_list):
            item.type = 'MORPH'
            item.morph_type, item.name = data
        frame.active_item = 0

    @staticmethod
    def load_bone_groups(mmd_root, armature):
        bone_groups = OrderedDict((i.name, []) for i in armature.pose.bone_groups)
        for b in armature.pose.bones:
            if b.bone_group:
                bone_groups[b.bone_group.name].append(b.name)

        frames = mmd_root.display_item_frames
        used_index = set()
        for group_name, bone_names in bone_groups.items():
            if len(bone_names) < 1: # skip empty group
                continue

            frame = frames.get(group_name)
            if frame is None:
                frame = frames.add()
                frame.name = group_name
                frame.name_e = group_name
            used_index.add(frames.find(group_name))

            items = frame.data
            ItemOp.resize(items, len(bone_names))
            for item, name in zip(items, bone_names):
                item.type = 'BONE'
                item.name = name
            frame.active_item = 0

        # remove unused frames
        for i in reversed(range(len(frames))):
            if i not in used_index:
                frame = frames[i]
                if frame.is_special:
                    if frame.name != u'表情':
                        frame.data.clear()
                else:
                    frames.remove(i)
        mmd_root.active_display_item_frame = 0

    @staticmethod
    def apply_bone_groups(mmd_root, armature):
        arm_bone_groups = armature.pose.bone_groups
        if not hasattr(arm_bone_groups, 'remove'): #bpy.app.version < (2, 72, 0):
            from mmd_tools_local import bpyutils
            bpyutils.select_object(armature)
            bpy.ops.object.mode_set(mode='POSE')
            class arm_bone_groups:
                values = armature.pose.bone_groups.values
                get = armature.pose.bone_groups.get
                @staticmethod
                def new(name):
                    bpy.ops.pose.group_add()
                    group = armature.pose.bone_groups.active
                    group.name = name
                    return group
                @staticmethod
                def remove(group):
                    armature.pose.bone_groups.active = group
                    bpy.ops.pose.group_remove()

        pose_bones = armature.pose.bones
        used_groups = set()
        unassigned_bones = {b.name for b in pose_bones}
        for frame in mmd_root.display_item_frames:
            for item in frame.data:
                if item.type == 'BONE' and item.name in unassigned_bones:
                    unassigned_bones.remove(item.name)
                    group_name = frame.name
                    used_groups.add(group_name)
                    group = arm_bone_groups.get(group_name)
                    if group is None:
                        group = arm_bone_groups.new(name=group_name)
                    pose_bones[item.name].bone_group = group

        for name in unassigned_bones:
            pose_bones[name].bone_group = None

        # remove unused bone groups
        for group in arm_bone_groups.values():
            if group.name not in used_groups:
                arm_bone_groups.remove(group)

