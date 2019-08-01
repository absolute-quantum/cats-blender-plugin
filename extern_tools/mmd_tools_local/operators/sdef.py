# -*- coding: utf-8 -*-

import bpy
from bpy.types import Operator

from mmd_tools_local import register_wrap
from mmd_tools_local.core.model import Model
from mmd_tools_local.core.sdef import FnSDEF

def _get_selected_objects(context):
    selected_objects = set(i for i in context.selected_objects if i.type == 'MESH')
    for i in context.selected_objects:
        root = Model.findRoot(i)
        if root and root in {i, i.parent}:
            selected_objects |= set(Model(root).meshes())
    return selected_objects

@register_wrap
class ResetSDEFCache(Operator):
    bl_idname = 'mmd_tools.sdef_cache_reset'
    bl_label = 'Reset MMD SDEF cache'
    bl_description = 'Reset MMD SDEF cache of selected objects and clean unused cache'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        for i in _get_selected_objects(context):
            FnSDEF.clear_cache(i)
        FnSDEF.clear_cache(unused_only=True)
        return {'FINISHED'}

@register_wrap
class BindSDEF(Operator):
    bl_idname = 'mmd_tools.sdef_bind'
    bl_label = 'Bind SDEF Driver'
    bl_description = 'Bind MMD SDEF data of selected objects'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    mode = bpy.props.EnumProperty(
        name='Mode',
        description='Select mode',
        items = [
            ('2', 'Bulk', 'Speed up with numpy (may be slower in some cases)', 2),
            ('1', 'Normal', 'Normal mode', 1),
            ('0', '- Auto -', 'Select best mode by benchmark result', 0),
            ],
        default='0',
        )
    use_skip = bpy.props.BoolProperty(
        name='Skip',
        description='Skip when the bones are not moving',
        default=True,
        )
    use_scale = bpy.props.BoolProperty(
        name='Scale',
        description='Support bone scaling (slow)',
        default=False,
        )

    def invoke(self, context, event):
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

    def execute(self, context):
        selected_objects = _get_selected_objects(context)
        param = ((None, False, True)[int(self.mode)], self.use_skip, self.use_scale)
        count = sum(FnSDEF.bind(i, *param) for i in selected_objects)
        self.report({'INFO'}, 'Binded %d of %d selected mesh(es)'%(count, len(selected_objects)))
        return {'FINISHED'}

@register_wrap
class UnbindSDEF(Operator):
    bl_idname = 'mmd_tools.sdef_unbind'
    bl_label = 'Unbind SDEF Driver'
    bl_description = 'Unbind MMD SDEF data of selected objects'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        for i in _get_selected_objects(context):
            FnSDEF.unbind(i)
        return {'FINISHED'}
