# -*- coding: utf-8 -*-

import bpy
import mmd_tools_local.core.model as mmd_model


class _PanelBase(object):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'


class MMDModelObjectPanel(_PanelBase, bpy.types.Panel):
    bl_idname = 'OBJECT_PT_mmd_tools_root_object'
    bl_label = 'MMD Model Information'

    @classmethod
    def poll(cls, context):
        return mmd_model.FnModel.find_root(context.active_object)

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        root = mmd_model.FnModel.find_root(obj)

        c = layout.column()
        c.prop(root.mmd_root, 'name')
        c.prop(root.mmd_root, 'name_e')
        c = layout.column()
        c.prop_search(root.mmd_root, 'comment_text', search_data=bpy.data, search_property='texts')
        c.prop_search(root.mmd_root, 'comment_e_text', search_data=bpy.data, search_property='texts')
        c = layout.column()
        c.operator('mmd_tools.change_mmd_ik_loop_factor', text='Change MMD IK Loop Factor')
        c.operator('mmd_tools.recalculate_bone_roll', text='Recalculate bone roll')
