# -*- coding: utf-8 -*-

import bpy
from bpy.types import Panel, UIList

from mmd_tools_local import register_wrap
from mmd_tools_local.bpyutils import SceneOp
from mmd_tools_local.core.model import Model
from mmd_tools_local.panels.tool import TRIA_UP_BAR, TRIA_DOWN_BAR
from mmd_tools_local.panels.tool import _layout_split
from mmd_tools_local.panels.tool import _PanelBase


ICON_APPEND_MOVE, ICON_APPEND_ROT, ICON_APPEND_MOVE_ROT = 'IPO_LINEAR', 'IPO_EXPO', 'IPO_QUAD'
if bpy.app.version < (2, 71, 0):
    ICON_APPEND_MOVE, ICON_APPEND_ROT, ICON_APPEND_MOVE_ROT = 'NDOF_TRANS', 'NDOF_TURN', 'FORCE_MAGNETIC'


@register_wrap
class MMD_TOOLS_UL_Materials(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT'}:
            if item:
                row = layout.row(align=True)
                item_prop = getattr(item, 'mmd_material')
                row.prop(item_prop, 'name_j', text='', emboss=False, icon='MATERIAL')
                row.prop(item_prop, 'name_e', text='', emboss=True)
            else:
                layout.label(text='UNSET', translate=False, icon='ERROR')
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

    def draw_filter(self, context, layout):
        layout.label(text="Use the arrows to sort", icon='INFO')

@register_wrap
class MMDMaterialSorter(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_material_sorter'
    bl_label = 'Material Sorter'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        active_obj = context.active_object
        if (active_obj is None or active_obj.type != 'MESH' or
            active_obj.mmd_type != 'NONE'):
            layout.label(text='Select a mesh object')
            return

        col = layout.column(align=True)
        row = col.row()
        row.template_list("MMD_TOOLS_UL_Materials", "",
                          active_obj.data, "materials",
                          active_obj, "active_material_index")
        tb = row.column()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.move_material_up', text='', icon='TRIA_UP')
        tb1.operator('mmd_tools.move_material_down', text='', icon='TRIA_DOWN')

@register_wrap
class MMD_TOOLS_UL_ModelMeshes(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT'}:
            layout.label(text=item.name, translate=False, icon='OBJECT_DATA')
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

    def draw_filter(self, context, layout):
        layout.label(text="Use the arrows to sort", icon='INFO')

    def filter_items(self, context, data, propname):
        # We will use the filtering to sort the mesh objects to match the rig order
        objects = getattr(data, propname)
        flt_flags = [~self.bitflag_filter_item] * len(objects)
        flt_neworder = list(range(len(objects)))

        armature = Model(Model.findRoot(context.active_object)).armature()
        __is_child_of_armature = lambda x: x.parent and (x.parent == armature or __is_child_of_armature(x.parent))

        name_dict = {}
        for i, obj in enumerate(objects):
            if obj.type == 'MESH' and obj.mmd_type == 'NONE' and __is_child_of_armature(obj):
                flt_flags[i] = self.bitflag_filter_item
                name_dict[obj.name] = i

        for new_index, name in enumerate(sorted(name_dict.keys())):
            i = name_dict[name]
            flt_neworder[i] = new_index

        return flt_flags, flt_neworder

@register_wrap
class MMDMeshSorter(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_meshes_sorter'
    bl_label = 'Meshes Sorter'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        active_obj = context.active_object
        root = Model.findRoot(active_obj)
        if root is None:
            layout.label(text='Select a MMD Model')
            return

        col = layout.column(align=True)
        row = col.row()
        row.template_list("MMD_TOOLS_UL_ModelMeshes", "",
                          SceneOp(context).id_scene, 'objects',
                          root.mmd_root, "active_mesh_index")
        tb = row.column()
        tb1 = tb.column(align=True)
        tb1.enabled = active_obj.type == 'MESH' and active_obj.mmd_type == 'NONE'
        tb1.operator('mmd_tools.object_move', text='', icon=TRIA_UP_BAR).type = 'TOP'
        tb1.operator('mmd_tools.object_move', text='', icon='TRIA_UP').type = 'UP'
        tb1.operator('mmd_tools.object_move', text='', icon='TRIA_DOWN').type = 'DOWN'
        tb1.operator('mmd_tools.object_move', text='', icon=TRIA_DOWN_BAR).type = 'BOTTOM'

class _DummyVertexGroup:
    index = None
    def __init__(self, index):
        self.index = index

@register_wrap
class MMD_TOOLS_UL_ModelBones(UIList):
    _IK_MAP = {}
    _IK_BONES = {}
    _DUMMY_VERTEX_GROUPS = {}

    @classmethod
    def __wrap_pose_bones(cls, pose_bones):
        for i, b in enumerate(pose_bones):
            cls._DUMMY_VERTEX_GROUPS[b.name] = _DummyVertexGroup(i)
            yield b

    @classmethod
    def update_bone_tables(cls, armature, bone_order_object):
        cls._IK_MAP.clear()
        cls._IK_BONES.clear()
        cls._DUMMY_VERTEX_GROUPS.clear()

        ik_target_override = {}
        ik_target_custom = {}
        ik_target_fin = {}
        pose_bones = armature.pose.bones
        bone_count = len(pose_bones)
        pose_bone_list = pose_bones if bone_order_object else cls.__wrap_pose_bones(pose_bones)

        for b in pose_bone_list:
            if b.is_mmd_shadow_bone:
                bone_count -= 1
                continue
            for c in b.constraints:
                if c.type == 'IK' and c.subtarget in pose_bones and c.subtarget not in cls._IK_BONES:
                    if not c.use_tail:
                        cls._IK_MAP.setdefault(hash(b), []).append(c.subtarget)
                        cls._IK_BONES[c.subtarget] = ik_target_fin[c.subtarget] = hash(b)
                        bone_chain = b.parent_recursive
                    else:
                        cls._IK_BONES[c.subtarget] = b.name
                        bone_chain = [b] + b.parent_recursive
                    for l in bone_chain[:c.chain_count]:
                        cls._IK_MAP.setdefault(hash(l), []).append(c.subtarget)
                if 'mmd_ik_target_custom' == c.name:
                    ik_target_custom[getattr(c, 'subtarget', '')] = hash(b)
                elif 'mmd_ik_target_override' == c.name and b.parent:
                    if b.parent.name == getattr(c, 'subtarget', ''):
                        for c in b.parent.constraints:
                            if c.type == 'IK' and c.subtarget in pose_bones and c.subtarget not in ik_target_override and c.subtarget not in ik_target_custom:
                                ik_target_override[c.subtarget] = hash(b)

        for k, v in ik_target_custom.items():
            if k not in ik_target_fin and k in cls._IK_BONES:
                cls._IK_BONES[k] = v
                cls._IK_MAP.setdefault(v, []).append(k)
                if k in ik_target_override:
                    del ik_target_override[k]

        for k, v in ik_target_override.items():
            if k not in ik_target_fin and k in cls._IK_BONES:
                cls._IK_BONES[k] = v
                cls._IK_MAP.setdefault(v, []).append(k)

        for k, v in tuple(cls._IK_BONES.items()):
            if isinstance(v, str):
                b = cls.__get_ik_target_bone(pose_bones[v])
                if b:
                    cls._IK_BONES[k] = hash(b)
                    cls._IK_MAP.setdefault(hash(b), []).append(k)
                else:
                    del cls._IK_BONES[k]
        return bone_count

    @staticmethod
    def __get_ik_target_bone(target_bone):
        r = None
        min_length = None
        for c in (c for c in target_bone.children if not c.is_mmd_shadow_bone):
            if c.bone.use_connect:
                return c
            length = (c.head - target_bone.tail).length
            if min_length is None or length < min_length:
                min_length = length
                r = c
        return r

    @classmethod
    def _draw_bone_item(cls, layout, bone_name, pose_bones, vertex_groups, index):
        bone = pose_bones.get(bone_name, None)
        if not bone or bone.is_mmd_shadow_bone:
            layout.active = False
            layout.label(text=bone_name, translate=False, icon='GROUP_BONE' if bone else 'MESH_DATA')
            r = layout.row()
            r.alignment = 'RIGHT'
            r.label(text=str(index))
        else:
            row = _layout_split(layout, factor=0.45, align=False)
            r0 = row.row()
            r0.label(text=bone_name, translate=False, icon='POSE_HLT' if bone_name in cls._IK_BONES else 'BONE_DATA')
            r = r0.row()
            r.alignment = 'RIGHT'
            r.label(text=str(index))

            row_sub = _layout_split(row, factor=0.67, align=False)

            mmd_bone = bone.mmd_bone
            count = len(pose_bones)
            bone_transform_rank = index + mmd_bone.transform_order*count

            r = row_sub.row()
            bone_parent = bone.parent
            if bone_parent:
                bone_parent = bone_parent.name
                idx = vertex_groups.get(bone_parent, _DummyVertexGroup).index
                if idx is None or bone_transform_rank < (idx + pose_bones[bone_parent].mmd_bone.transform_order*count):
                    r.label(text=str(idx), icon='ERROR')
                else:
                    r.label(text=str(idx), icon='INFO' if index < idx else 'FILE_PARENT')
            else:
                r.label()

            r = r.row()
            if mmd_bone.has_additional_rotation:
                append_bone = mmd_bone.additional_transform_bone
                idx = vertex_groups.get(append_bone, _DummyVertexGroup).index
                if idx is None or bone_transform_rank < (idx + pose_bones[append_bone].mmd_bone.transform_order*count):
                    if append_bone:
                        r.label(text=str(idx), icon='ERROR')
                else:
                    r.label(text=str(idx), icon=ICON_APPEND_MOVE_ROT if mmd_bone.has_additional_location else ICON_APPEND_ROT)
            elif mmd_bone.has_additional_location:
                append_bone = mmd_bone.additional_transform_bone
                idx = vertex_groups.get(append_bone, _DummyVertexGroup).index
                if idx is None or bone_transform_rank < (idx + pose_bones[append_bone].mmd_bone.transform_order*count):
                    if append_bone:
                        r.label(text=str(idx), icon='ERROR')
                else:
                    r.label(text=str(idx), icon=ICON_APPEND_MOVE)

            for idx, b in sorted(((vertex_groups.get(b, _DummyVertexGroup).index, b) for b in cls._IK_MAP.get(hash(bone), ())), key=lambda i: i[0] or 0):
                ik_bone = pose_bones[b]
                is_ik_chain = (hash(bone) != cls._IK_BONES.get(b))
                if idx is None or (is_ik_chain and bone_transform_rank > (idx + ik_bone.mmd_bone.transform_order*count)):
                    r.prop(ik_bone, 'mmd_ik_toggle', text=str(idx), toggle=True, icon='ERROR')
                elif b not in cls._IK_BONES:
                    r.prop(ik_bone, 'mmd_ik_toggle', text=str(idx), toggle=True, icon='QUESTION')
                else:
                    r.prop(ik_bone, 'mmd_ik_toggle', text=str(idx), toggle=True, icon='LINKED' if is_ik_chain else 'HOOK')

            row = row_sub.row(align=True)
            if mmd_bone.transform_after_dynamics:
                row.prop(mmd_bone, 'transform_after_dynamics', text='', toggle=True, icon='PHYSICS')
            else:
                row.prop(mmd_bone, 'transform_after_dynamics', text='', toggle=True)
            row.prop(mmd_bone, 'transform_order', text='', slider=bool(mmd_bone.transform_order))

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT'}:
            if self._DUMMY_VERTEX_GROUPS:
                self._draw_bone_item(layout, item.name, data.bones, self._DUMMY_VERTEX_GROUPS, index)
            else:
                self._draw_bone_item(layout, item.name, data.parent.pose.bones, data.vertex_groups, index)
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

@register_wrap
class MMDBoneOrder(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_bone_order'
    bl_label = 'Bone Order'
    bl_context = ''
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        active_obj = context.active_object
        root = Model.findRoot(active_obj)
        if root is None:
            layout.label(text='Select a MMD Model')
            return

        armature = Model(root).armature()
        if armature is None:
            layout.label(text='The armature object of active MMD model can\'t be found', icon='ERROR')
            return

        bone_order_object = next((i for i in armature.children if 'mmd_bone_order_override' in i.modifiers), None) #TODO consistency issue
        bone_count = MMD_TOOLS_UL_ModelBones.update_bone_tables(armature, bone_order_object)

        col = layout.column(align=True)
        row = col.row()
        if bone_order_object is None:
            row.template_list("MMD_TOOLS_UL_ModelBones", "",
                              armature.pose, 'bones',
                              root.vertex_groups, 'active_index')
            col.label(text='(%d) %s'%(bone_count, armature.name), icon='OUTLINER_OB_ARMATURE')
            col.label(text='No mesh object with "mmd_bone_order_override" modifier', icon='ERROR')
        else:
            row.template_list("MMD_TOOLS_UL_ModelBones", "",
                              bone_order_object, 'vertex_groups',
                              bone_order_object.vertex_groups, 'active_index')
            row = col.row()
            row.label(text='(%d) %s'%(bone_count, armature.name), icon='OUTLINER_OB_ARMATURE')
            row.label(icon='BACK')
            row.label(text=bone_order_object.name, icon='OBJECT_DATA')
            if bone_order_object == active_obj:
                row = row.row(align=True)
                row.operator('object.vertex_group_move', text='', icon='TRIA_UP').direction = 'UP'
                row.operator('object.vertex_group_move', text='', icon='TRIA_DOWN').direction = 'DOWN'

