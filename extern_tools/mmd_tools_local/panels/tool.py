# -*- coding: utf-8 -*-

import bpy
from bpy.types import Panel, Menu, UIList

from mmd_tools_local import register_wrap
from mmd_tools_local import operators
from mmd_tools_local.utils import ItemOp
from mmd_tools_local.bpyutils import SceneOp
import mmd_tools_local.core.model as mmd_model


TRIA_UP_BAR = 'TRIA_UP_BAR'
TRIA_DOWN_BAR = 'TRIA_DOWN_BAR'
if bpy.app.version < (2, 73, 0):
    TRIA_UP_BAR = 'TRIA_UP'
    TRIA_DOWN_BAR = 'TRIA_DOWN'

ICON_ADD, ICON_REMOVE = 'ADD', 'REMOVE'
if bpy.app.version < (2, 80, 0):
    ICON_ADD, ICON_REMOVE = 'ZOOMIN', 'ZOOMOUT'


if bpy.app.version < (2, 80, 0):
    def _layout_split(layout, factor, align):
        return layout.split(percentage=factor, align=align)
else:
    def _layout_split(layout, factor, align):
        return layout.split(factor=factor, align=align)


class _PanelBase(object):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if bpy.app.version < (2, 80, 0) else 'UI'
    bl_category = 'MMD'


@register_wrap
class MMDToolsObjectPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_object'
    bl_label = 'Operator'
    bl_context = ''

    def draw(self, context):
        active_obj = context.active_object

        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('mmd_tools.create_mmd_model_root_object', text='Create Model', icon='OUTLINER_OB_ARMATURE')
        row.operator('mmd_tools.convert_to_mmd_model', text='Convert Model', icon='OUTLINER_OB_ARMATURE')
        row.operator('mmd_tools.rigid_body_world_update', text='', icon='PHYSICS')

        col = layout.column(align=True)
        col.operator('mmd_tools.convert_materials_for_cycles', text='Convert Materials For Cycles')
        col.operator('mmd_tools.separate_by_materials', text='Separate By Materials')

        root = mmd_model.Model.findRoot(active_obj)
        if root:
            col.operator('mmd_tools.join_meshes')
            col.operator('mmd_tools.attach_meshes')
            col.operator('mmd_tools.translate_mmd_model', text='Translation')

            row = _layout_split(layout, factor=1/3, align=False)

            col = row.column(align=True)
            col.label(text='Bone Constraints:', icon='CONSTRAINT_BONE')
            col.operator('mmd_tools.apply_additional_transform', text='Apply')
            col.operator('mmd_tools.clean_additional_transform', text='Clean')

            col = row.column(align=True)
            col.active = getattr(context.scene.rigidbody_world, 'enabled', False)
            sub_row = col.row(align=True)
            sub_row.label(text='Physics:', icon='PHYSICS')
            if not root.mmd_root.is_built:
                sub_row.label(icon='ERROR')
            col.operator('mmd_tools.build_rig', text='Build')
            col.operator('mmd_tools.clean_rig', text='Clean')

            col = row.column(align=True)
            col.label(text='Edge Preview:', icon='MATERIAL')
            col.operator_enum('mmd_tools.edge_preview_setup', 'action')

        row = layout.row()

        col = row.column(align=True)
        col.label(text='Model:', icon='OUTLINER_OB_ARMATURE')
        col.operator('mmd_tools.import_model', text='Import')
        col.operator('mmd_tools.export_pmx', text='Export')

        col = row.column(align=True)
        col.label(text='Motion:', icon='ANIM')
        col.operator('mmd_tools.import_vmd', text='Import')
        col.operator('mmd_tools.export_vmd', text='Export')

        col = row.column(align=True)
        col.label(text='Pose:', icon='POSE_HLT')
        col.operator('mmd_tools.import_vpd', text='Import')
        col.operator('mmd_tools.export_vpd', text='Export')


@register_wrap
class MMD_ROOT_UL_display_item_frames(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        frame = item
        if self.layout_type in {'DEFAULT'}:
            row = _layout_split(layout, factor=0.5, align=True)
            if frame.is_special:
                row.label(text=frame.name, translate=False)
                row = row.row(align=True)
                row.label(text=frame.name_e, translate=False)
                row.label(text='', icon='LOCKED')
            else:
                row.prop(frame, 'name', text='', emboss=False)
                row.prop(frame, 'name_e', text='', emboss=True)
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

@register_wrap
class MMD_ROOT_UL_display_items(UIList):
    morph_filter = bpy.props.EnumProperty(
        name="Morph Filter",
        description='Only show items matching this category',
        options={'ENUM_FLAG'},
        items = [
            ('SYSTEM', 'Hidden', '', 1),
            ('EYEBROW', 'Eye Brow', '', 2),
            ('EYE', 'Eye', '', 4),
            ('MOUTH', 'Mouth', '', 8),
            ('OTHER', 'Other', '', 16),
            ],
        default={'SYSTEM', 'EYEBROW', 'EYE', 'MOUTH', 'OTHER',},
        )
    mmd_name = bpy.props.EnumProperty(
        name='MMD Name',
        description='Show JP or EN name of MMD bone',
        items = [
            ('name_j', 'JP', '', 1),
            ('name_e', 'EN', '', 2),
            ],
        default='name_e',
        )

    @staticmethod
    def draw_bone_special(layout, armature, bone_name, mmd_name=None):
        if armature is None:
            return
        row = layout.row(align=True)
        p_bone = armature.pose.bones.get(bone_name, None)
        if p_bone:
            bone = p_bone.bone
            if mmd_name:
                row.prop(p_bone.mmd_bone, mmd_name, text='', emboss=True)
            ic = 'RESTRICT_VIEW_ON' if bone.hide else 'RESTRICT_VIEW_OFF'
            row.prop(bone, 'hide', text='', emboss=p_bone.mmd_bone.is_tip, icon=ic)
            row.active = armature.mode != 'EDIT'
        else:
            row.label() # for alignment only
            row.label(icon='ERROR')

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT'}:
            if item.type == 'BONE':
                row = _layout_split(layout, factor=0.5, align=True)
                row.prop(item, 'name', text='', emboss=False, icon='BONE_DATA')
                self.draw_bone_special(row, mmd_model.Model(item.id_data).armature(), item.name, self.mmd_name)
            else:
                row = _layout_split(layout, factor=0.6, align=True)
                row.prop(item, 'name', text='', emboss=False, icon='SHAPEKEY_DATA')
                row = row.row(align=True)
                row.prop(item, 'morph_type', text='', emboss=False)
                if item.name not in getattr(item.id_data.mmd_root, item.morph_type):
                    row.label(icon='ERROR')
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

    def filter_items(self, context, data, propname):
        if len(self.morph_filter) == 5 or data.name != u'表情':
            return [], []

        objects = getattr(data, propname)
        flt_flags = [~self.bitflag_filter_item] * len(objects)
        flt_neworder = []

        for i, item in enumerate(objects):
            morph = getattr(item.id_data.mmd_root, item.morph_type).get(item.name, None)
            if morph and morph.category in self.morph_filter:
                flt_flags[i] = self.bitflag_filter_item

        return flt_flags, flt_neworder

    def draw_filter(self, context, layout):
        row = layout.row()
        row.prop(self, 'morph_filter', expand=True)
        row.prop(self, 'mmd_name', expand=True)


@register_wrap
class MMDDisplayItemFrameMenu(Menu):
    bl_idname = 'OBJECT_MT_mmd_tools_display_item_frame_menu'
    bl_label = 'Display Item Frame Menu'

    def draw(self, context):
        layout = self.layout
        layout.operator_enum('mmd_tools.display_item_quick_setup', 'type')
        layout.separator()
        layout.operator('mmd_tools.display_item_frame_move', icon=TRIA_UP_BAR, text='Move To Top').type = 'TOP'
        layout.operator('mmd_tools.display_item_frame_move', icon=TRIA_DOWN_BAR, text='Move To Bottom').type = 'BOTTOM'

@register_wrap
class MMDDisplayItemMenu(Menu):
    bl_idname = 'OBJECT_MT_mmd_tools_display_item_menu'
    bl_label = 'Display Item Menu'

    def draw(self, context):
        layout = self.layout
        layout.operator('mmd_tools.display_item_remove', text='Delete All', icon='X').all = True
        layout.separator()
        layout.operator('mmd_tools.display_item_move', icon=TRIA_UP_BAR, text='Move To Top').type = 'TOP'
        layout.operator('mmd_tools.display_item_move', icon=TRIA_DOWN_BAR, text='Move To Bottom').type = 'BOTTOM'

@register_wrap
class MMDDisplayItemsPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_display_items'
    bl_label = 'Display Panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        active_obj = context.active_object
        root = mmd_model.Model.findRoot(active_obj)
        if root is None:
            self.layout.label(text='Select a MMD Model')
            return

        mmd_root = root.mmd_root
        col = self.layout.column()
        row = col.row()
        row.template_list(
            "MMD_ROOT_UL_display_item_frames",
            "",
            mmd_root, "display_item_frames",
            mmd_root, "active_display_item_frame",
            )
        tb = row.column()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.display_item_frame_add', text='', icon=ICON_ADD)
        tb1.operator('mmd_tools.display_item_frame_remove', text='', icon=ICON_REMOVE)
        tb1.menu('OBJECT_MT_mmd_tools_display_item_frame_menu', text='', icon='DOWNARROW_HLT')
        tb.separator()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.display_item_frame_move', text='', icon='TRIA_UP').type = 'UP'
        tb1.operator('mmd_tools.display_item_frame_move', text='', icon='TRIA_DOWN').type = 'DOWN'

        frame = ItemOp.get_by_index(mmd_root.display_item_frames, mmd_root.active_display_item_frame)
        if frame is None:
            return

        c = col.column(align=True)
        row = c.row()
        row.template_list(
            "MMD_ROOT_UL_display_items",
            "",
            frame, "data",
            frame, "active_item",
            )
        tb = row.column()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.display_item_add', text='', icon=ICON_ADD)
        tb1.operator('mmd_tools.display_item_remove', text='', icon=ICON_REMOVE)
        tb1.menu('OBJECT_MT_mmd_tools_display_item_menu', text='', icon='DOWNARROW_HLT')
        tb.separator()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.display_item_move', text='', icon='TRIA_UP').type = 'UP'
        tb1.operator('mmd_tools.display_item_move', text='', icon='TRIA_DOWN').type = 'DOWN'

        row = col.row()
        r = row.row(align=True)
        r.operator('mmd_tools.display_item_find', text='Bone', icon='VIEWZOOM').type = 'BONE'
        r.operator('mmd_tools.display_item_find', text='Morph', icon='VIEWZOOM').type = 'MORPH'
        row.operator('mmd_tools.display_item_select_current', text='Select')


@register_wrap
class MMD_TOOLS_UL_Morphs(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        mmd_root = data
        if self.layout_type in {'DEFAULT'}:
            row = _layout_split(layout, factor=0.4, align=True)
            row.prop(item, 'name', text='', emboss=False, icon='SHAPEKEY_DATA')
            row = _layout_split(row, factor=0.6, align=True)
            row.prop(item, 'name_e', text='', emboss=True)
            row = row.row(align=True)
            row.prop(item, 'category', text='', emboss=False)
            frame_facial = mmd_root.display_item_frames.get(u'表情')
            morph_item = frame_facial.data.get(item.name) if frame_facial else None
            if morph_item is None:
                row.label(icon='INFO')
            elif morph_item.morph_type != mmd_root.active_morph_type:
                row.label(icon='SHAPEKEY_DATA')
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

@register_wrap
class MMD_TOOLS_UL_MaterialMorphOffsets(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT'}:
            material = item.material
            if not material and item.material_id >= 0:
                layout.label(text='Material ID %d is missing'%item.material_id, translate=False, icon='ERROR')
            else:
                layout.label(text=material or 'All Materials', translate=False, icon='MATERIAL')
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

@register_wrap
class MMD_TOOLS_UL_UVMorphOffsets(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT'}:
            layout.label(text=str(item.index), translate=False, icon='MESH_DATA')
            layout.prop(item, 'offset', text='', emboss=False, slider=True)
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

@register_wrap
class MMD_TOOLS_UL_BoneMorphOffsets(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT'}:
            layout.prop(item, 'bone', text='', emboss=False, icon='BONE_DATA')
            MMD_ROOT_UL_display_items.draw_bone_special(layout, mmd_model.Model(item.id_data).armature(), item.bone)
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

@register_wrap
class MMD_TOOLS_UL_GroupMorphOffsets(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT'}:
            row = _layout_split(layout, factor=0.5, align=True)
            row.prop(item, 'name', text='', emboss=False, icon='SHAPEKEY_DATA')
            row = row.row(align=True)
            row.prop(item, 'morph_type', text='', emboss=False)
            if item.name in getattr(item.id_data.mmd_root, item.morph_type):
                row.prop(item, 'factor', text='', emboss=False, slider=True)
            else:
                row.label(icon='ERROR')
        elif self.layout_type in {'COMPACT'}:
            pass
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

@register_wrap
class MMDMorphMenu(Menu):
    bl_idname = 'OBJECT_MT_mmd_tools_morph_menu'
    bl_label = 'Morph Menu'

    def draw(self, context):
        layout = self.layout
        layout.operator('mmd_tools.morph_remove', text='Delete All', icon='X').all = True
        layout.separator()
        layout.operator_enum('mmd_tools.morph_slider_setup', 'type')
        layout.separator()
        layout.operator('mmd_tools.morph_copy', icon='COPY_ID')
        layout.separator()
        layout.operator('mmd_tools.morph_move', icon=TRIA_UP_BAR, text='Move To Top').type = 'TOP'
        layout.operator('mmd_tools.morph_move', icon=TRIA_DOWN_BAR, text='Move To Bottom').type = 'BOTTOM'

@register_wrap
class MMDMorphToolsPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_morph_tools'
    bl_label = 'Morph Tools'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        active_obj = context.active_object
        root = mmd_model.Model.findRoot(active_obj)
        if root is None:
            self.layout.label(text='Select a MMD Model')
            return

        rig = mmd_model.Model(root)
        mmd_root = root.mmd_root
        col = self.layout.column()
        row = col.row()
        row.prop(mmd_root, 'active_morph_type', expand=True)
        morph_type = mmd_root.active_morph_type

        c = col.column(align=True)
        row = c.row()
        row.template_list(
            "MMD_TOOLS_UL_Morphs", "",
            mmd_root, morph_type,
            mmd_root, "active_morph"
            )
        tb = row.column()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.morph_add', text='', icon=ICON_ADD)
        tb1.operator('mmd_tools.morph_remove', text='', icon=ICON_REMOVE)
        tb1.menu('OBJECT_MT_mmd_tools_morph_menu', text='', icon='DOWNARROW_HLT')
        tb.separator()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.morph_move', text='', icon='TRIA_UP').type = 'UP'
        tb1.operator('mmd_tools.morph_move', text='', icon='TRIA_DOWN').type = 'DOWN'

        morph = ItemOp.get_by_index(getattr(mmd_root, morph_type), mmd_root.active_morph)
        if morph:
            slider = rig.morph_slider.get(morph.name)
            if slider:
                col.row().prop(slider, 'value')
            draw_func = getattr(self, '_draw_%s_data'%morph_type[:-7], None)
            if draw_func:
                draw_func(context, rig, col, morph)

    def _template_morph_offset_list(self, layout, morph, list_type_name):
        row = layout.row()
        row.template_list(
            list_type_name, '',
            morph, 'data',
            morph, 'active_data',
            )
        tb = row.column()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.morph_offset_add', text='', icon=ICON_ADD)
        tb1.operator('mmd_tools.morph_offset_remove', text='', icon=ICON_REMOVE)
        tb.operator('mmd_tools.morph_offset_remove', text='', icon='X').all = True
        return ItemOp.get_by_index(morph.data, morph.active_data)

    def _draw_vertex_data(self, context, rig, col, morph):
        row = col.row()
        col = row.column()
        row.operator('mmd_tools.morph_offset_remove', text='', icon='X').all = True
        for i in rig.meshes():
            shape_keys = i.data.shape_keys
            if shape_keys is None:
                continue
            kb = shape_keys.key_blocks.get(morph.name, None)
            if kb:
                found = row = col.row(align=True)
                row.active = not (i.show_only_shape_key or kb.mute)
                row.label(text=i.name, icon='OBJECT_DATA')
                row.prop(kb, 'value', text=kb.name)
        if 'found' not in locals():
            col.label(text='Not found', icon='INFO')

    def _draw_material_data(self, context, rig, col, morph):
        col.label(text='Material Offsets (%d)'%len(morph.data))
        data = self._template_morph_offset_list(col, morph, 'MMD_TOOLS_UL_MaterialMorphOffsets')
        if data is None:
            return

        c_mat = col.column(align=True)
        c_mat.prop_search(data, 'related_mesh', bpy.data, 'meshes')

        related_mesh = bpy.data.meshes.get(data.related_mesh, None)
        c_mat.prop_search(data, 'material', related_mesh or bpy.data, 'materials')

        base_mat_name = data.material
        if '_temp' in base_mat_name:
            col.label(text='This is not a valid base material', icon='ERROR')
            return

        work_mat = bpy.data.materials.get(base_mat_name + '_temp', None)
        use_work_mat = work_mat and related_mesh and work_mat.name in related_mesh.materials
        if not use_work_mat:
            c = col.column()
            row = c.row(align=True)
            if base_mat_name == '':
                row.label(text='This offset affects all materials', icon='INFO')
            else:
                row.operator(operators.morph.CreateWorkMaterial.bl_idname)
                row.operator(operators.morph.ClearTempMaterials.bl_idname, text='Clear')

            row = c.row()
            row.prop(data, 'offset_type', expand=True)
            r1 = row.row(align=True)
            r1.operator(operators.morph.InitMaterialOffset.bl_idname, text='', icon='TRIA_LEFT').target_value = 0
            r1.operator(operators.morph.InitMaterialOffset.bl_idname, text='', icon='TRIA_RIGHT').target_value = 1
            row = c.row()
            row.column(align=True).prop(data, 'diffuse_color', expand=True, slider=True)
            c1 = row.column(align=True)
            c1.prop(data, 'specular_color', expand=True, slider=True)
            c1.prop(data, 'shininess', slider=True)
            row.column(align=True).prop(data, 'ambient_color', expand=True, slider=True)
            row = c.row()
            row.column(align=True).prop(data, 'edge_color', expand=True, slider=True)
            row = c.row()
            row.prop(data, 'edge_weight', slider=True)
            row = c.row()
            row.column(align=True).prop(data, 'texture_factor', expand=True, slider=True)
            row.column(align=True).prop(data, 'sphere_texture_factor', expand=True, slider=True)
            row.column(align=True).prop(data, 'toon_texture_factor', expand=True, slider=True)
        else:
            c_mat.enabled = False
            c = col.column()
            row = c.row(align=True)
            row.operator(operators.morph.ApplyMaterialOffset.bl_idname, text='Apply')
            row.operator(operators.morph.ClearTempMaterials.bl_idname, text='Clear')

            row = c.row()
            row.prop(data, 'offset_type')
            row = c.row()
            row.prop(work_mat.mmd_material, 'diffuse_color')
            row.prop(work_mat.mmd_material, 'alpha', slider=True)
            row = c.row()
            row.prop(work_mat.mmd_material, 'specular_color')
            row.prop(work_mat.mmd_material, 'shininess', slider=True)
            row = c.row()
            row.prop(work_mat.mmd_material, 'ambient_color')
            row.label() # for alignment only
            row = c.row()
            row.prop(work_mat.mmd_material, 'edge_color')
            row.prop(work_mat.mmd_material, 'edge_weight', slider=True)
            row = c.row()
            row.column(align=True).prop(data, 'texture_factor', expand=True, slider=True)
            row.column(align=True).prop(data, 'sphere_texture_factor', expand=True, slider=True)
            row.column(align=True).prop(data, 'toon_texture_factor', expand=True, slider=True)

    def _draw_bone_data(self, context, rig, col, morph):
        armature = rig.armature()
        if armature is None:
            col.label(text='Armature not found', icon='ERROR')
            return

        row = col.row(align=True)
        row.operator(operators.morph.ViewBoneMorph.bl_idname, text='View')
        row.operator(operators.morph.ApplyBoneMorph.bl_idname, text='Apply')
        row.operator(operators.morph.ClearBoneMorphView.bl_idname, text='Clear')

        col.label(text='Bone Offsets (%d)'%len(morph.data))
        data = self._template_morph_offset_list(col, morph, 'MMD_TOOLS_UL_BoneMorphOffsets')
        if data is None:
            return

        row = col.row(align=True)
        row.prop_search(data, 'bone', armature.pose, 'bones')
        if data.bone:
            row = col.row(align=True)
            row.operator(operators.morph.SelectRelatedBone.bl_idname, text='Select')
            row.operator(operators.morph.EditBoneOffset.bl_idname, text='Edit')
            row.operator(operators.morph.ApplyBoneOffset.bl_idname, text='Update')

        row = col.row()
        row.column(align=True).prop(data, 'location')
        row.column(align=True).prop(data, 'rotation')

    def _draw_uv_data(self, context, rig, col, morph):
        c = col.column(align=True)
        row = c.row(align=True)
        row.operator(operators.morph.ViewUVMorph.bl_idname, text='View')
        row.operator(operators.morph.ClearUVMorphView.bl_idname, text='Clear')
        row = c.row(align=True)
        row.operator(operators.morph.EditUVMorph.bl_idname, text='Edit')
        row.operator(operators.morph.ApplyUVMorph.bl_idname, text='Apply')

        c = col.column()
        if len(morph.data):
            row = c.row()
            row.prop(morph, 'data_type', expand=True)
        row = c.row()
        if morph.data_type == 'VERTEX_GROUP':
            row.prop(morph, 'vertex_group_scale', text='Scale')
        else:
            row.label(text='UV Offsets (%d)'%len(morph.data))
            #self._template_morph_offset_list(c, morph, 'MMD_TOOLS_UL_UVMorphOffsets')
        row.prop(morph, 'uv_index')
        row.operator('mmd_tools.morph_offset_remove', text='', icon='X').all = True

    def _draw_group_data(self, context, rig, col, morph):
        col.label(text='Group Offsets (%d)'%len(morph.data))
        item = self._template_morph_offset_list(col, morph, 'MMD_TOOLS_UL_GroupMorphOffsets')
        if item is None:
            return

        c = col.column(align=True)
        row = _layout_split(c, factor=0.67, align=True)
        row.prop_search(item, 'name', morph.id_data.mmd_root, item.morph_type, icon='SHAPEKEY_DATA', text='')
        row.prop(item, 'morph_type', text='')


@register_wrap
class UL_ObjectsMixIn(object):
    model_filter = bpy.props.EnumProperty(
        name="Model Filter",
        description='Show items of active model or all models',
        items = [
            ('ACTIVE', 'Active Model', '', 0),
            ('ALL', 'All Models', '', 1),
            ],
        default='ACTIVE',
        )
    visible_only = bpy.props.BoolProperty(
        name='Visible Only',
        description='Only show visible items',
        default=False,
        )

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = _layout_split(layout, factor=0.5, align=True)
            item_prop = getattr(item, self.prop_name)
            row.prop(item_prop, 'name_j', text='', emboss=False, icon=self.icon)
            row = row.row(align=True)
            row.prop(item_prop, 'name_e', text='', emboss=True)
            self.draw_item_special(context, row, item)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='', icon=self.icon)

    def draw_filter(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, 'model_filter', expand=True)
        row.prop(self, 'visible_only', text='', toggle=True, icon='RESTRICT_VIEW_OFF')

    def filter_items(self, context, data, propname):
        objects = getattr(data, propname)
        flt_flags = [~self.bitflag_filter_item] * len(objects)
        flt_neworder = list(range(len(objects)))

        if self.model_filter == 'ACTIVE':
            active_root = mmd_model.Model.findRoot(context.active_object)
            for i, obj in enumerate(objects):
                if obj.mmd_type == self.mmd_type and mmd_model.Model.findRoot(obj) == active_root:
                    flt_flags[i] = self.bitflag_filter_item
        else:
            for i, obj in enumerate(objects):
                if obj.mmd_type == self.mmd_type:
                    flt_flags[i] = self.bitflag_filter_item

        if self.visible_only:
            for i, obj in enumerate(objects):
                if obj.hide and flt_flags[i] == self.bitflag_filter_item:
                    flt_flags[i] = ~self.bitflag_filter_item

        indices = (i for i, x in enumerate(flt_flags) if x == self.bitflag_filter_item)
        for i_new, i_orig in enumerate(sorted(indices, key=lambda k: objects[k].name)):
            flt_neworder[i_orig] = i_new
        return flt_flags, flt_neworder

@register_wrap
class MMD_TOOLS_UL_rigidbodies(UIList, UL_ObjectsMixIn):
    mmd_type = 'RIGID_BODY'
    icon = 'MESH_ICOSPHERE'
    prop_name = 'mmd_rigid'

    def draw_item_special(self, context, layout, item):
        rb = item.rigid_body
        if rb is None:
            layout.label(icon='ERROR')
        elif not item.mmd_rigid.bone:
            layout.label(icon='BONE_DATA')

@register_wrap
class MMDRigidbodySelectMenu(Menu):
    bl_idname = 'OBJECT_MT_mmd_tools_rigidbody_select_menu'
    bl_label = 'Rigidbody Select Menu'

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator('mmd_tools.rigid_body_select', text='Select Similar...')
        layout.separator()
        layout.operator_context = 'EXEC_DEFAULT'
        layout.operator_enum('mmd_tools.rigid_body_select', 'properties')

@register_wrap
class MMDRigidbodyMenu(Menu):
    bl_idname = 'OBJECT_MT_mmd_tools_rigidbody_menu'
    bl_label = 'Rigidbody Menu'

    def draw(self, context):
        layout = self.layout
        layout.enabled = context.active_object.mmd_type == 'RIGID_BODY'
        layout.menu('OBJECT_MT_mmd_tools_rigidbody_select_menu', text='Select Similar')
        layout.separator()
        layout.operator('mmd_tools.object_move', icon=TRIA_UP_BAR, text='Move To Top').type = 'TOP'
        layout.operator('mmd_tools.object_move', icon=TRIA_DOWN_BAR, text='Move To Bottom').type = 'BOTTOM'

@register_wrap
class MMDRigidbodySelectorPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_rigidbody_list'
    bl_label = 'Rigid Bodies'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        active_obj = context.active_object
        root = mmd_model.Model.findRoot(active_obj)
        if root is None:
            self.layout.label(text='Select a MMD Model')
            return

        col = self.layout.column()
        c = col.column(align=True)
        row = c.row()
        row.template_list(
            "MMD_TOOLS_UL_rigidbodies",
            "",
            SceneOp(context).id_scene, 'objects',
            root.mmd_root, 'active_rigidbody_index',
            )
        tb = row.column()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.rigid_body_add', text='', icon=ICON_ADD)
        tb1.operator('mmd_tools.rigid_body_remove', text='', icon=ICON_REMOVE)
        tb1.menu('OBJECT_MT_mmd_tools_rigidbody_menu', text='', icon='DOWNARROW_HLT')
        tb.separator()
        tb1 = tb.column(align=True)
        tb1.enabled = active_obj.mmd_type == 'RIGID_BODY'
        tb1.operator('mmd_tools.object_move', text='', icon='TRIA_UP').type = 'UP'
        tb1.operator('mmd_tools.object_move', text='', icon='TRIA_DOWN').type = 'DOWN'


@register_wrap
class MMD_TOOLS_UL_joints(UIList, UL_ObjectsMixIn):
    mmd_type = 'JOINT'
    icon = 'CONSTRAINT'
    prop_name = 'mmd_joint'

    def draw_item_special(self, context, layout, item):
        rbc = item.rigid_body_constraint
        if rbc is None:
            layout.label(icon='ERROR')
        elif rbc.object1 is None or rbc.object2 is None:
            layout.label(icon='OBJECT_DATA')
        elif rbc.object1 == rbc.object2:
            layout.label(icon='MESH_CUBE')

@register_wrap
class MMDJointMenu(Menu):
    bl_idname = 'OBJECT_MT_mmd_tools_joint_menu'
    bl_label = 'Joint Menu'

    def draw(self, context):
        layout = self.layout
        layout.enabled = context.active_object.mmd_type == 'JOINT'
        layout.operator('mmd_tools.object_move', icon=TRIA_UP_BAR, text='Move To Top').type = 'TOP'
        layout.operator('mmd_tools.object_move', icon=TRIA_DOWN_BAR, text='Move To Bottom').type = 'BOTTOM'

@register_wrap
class MMDJointSelectorPanel(_PanelBase, Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_joint_list'
    bl_label = 'Joints'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        active_obj = context.active_object
        root = mmd_model.Model.findRoot(active_obj)
        if root is None:
            self.layout.label(text='Select a MMD Model')
            return

        col = self.layout.column()
        c = col.column(align=True)

        row = c.row()
        row.template_list(
            "MMD_TOOLS_UL_joints",
            "",
            SceneOp(context).id_scene, 'objects',
            root.mmd_root, 'active_joint_index',
            )
        tb = row.column()
        tb1 = tb.column(align=True)
        tb1.operator('mmd_tools.joint_add', text='', icon=ICON_ADD)
        tb1.operator('mmd_tools.joint_remove', text='', icon=ICON_REMOVE)
        tb1.menu('OBJECT_MT_mmd_tools_joint_menu', text='', icon='DOWNARROW_HLT')
        tb.separator()
        tb1 = tb.column(align=True)
        tb1.enabled = active_obj.mmd_type == 'JOINT'
        tb1.operator('mmd_tools.object_move', text='', icon='TRIA_UP').type = 'UP'
        tb1.operator('mmd_tools.object_move', text='', icon='TRIA_DOWN').type = 'DOWN'

