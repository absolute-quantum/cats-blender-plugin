# -*- coding: utf-8 -*-

from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from mmd_tools_local.core.material import FnMaterial
from mmd_tools_local.core.exceptions import MaterialNotFoundError
from mmd_tools_local import cycles_converter

class ConvertMaterialsForCycles(Operator):
    bl_idname = 'mmd_tools.convert_materials_for_cycles'
    bl_options = {'PRESET'}
    bl_label = 'Convert Shaders For Cycles'
    bl_description = 'Convert materials of selected objects for Cycles.'

    def execute(self, context):
        for obj in [x for x in context.selected_objects if x.type == 'MESH']:
            cycles_converter.convertToCyclesShader(obj)
        return {'FINISHED'}

class _OpenTextureBase(object):
    """ Create a texture for mmd model material.
    """
    bl_options = {'PRESET'}

    filepath = StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='FILE_PATH',
        )

    use_filter_image = BoolProperty(
        default=True,
        options={'HIDDEN'},
        )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class OpenTexture(Operator, _OpenTextureBase):
    bl_idname = 'mmd_tools.material_open_texture'
    bl_label = 'Open Texture'
    bl_description = 'Create main texture of active material'

    def execute(self, context):
        mat = context.active_object.active_material
        fnMat = FnMaterial(mat)
        fnMat.create_texture(self.filepath)
        return {'FINISHED'}


class RemoveTexture(Operator):
    """ Create a texture for mmd model material.
    """
    bl_idname = 'mmd_tools.material_remove_texture'
    bl_label = 'Remove Texture'
    bl_description = 'Remove main texture of active material'
    bl_options = {'PRESET'}

    def execute(self, context):
        mat = context.active_object.active_material
        fnMat = FnMaterial(mat)
        fnMat.remove_texture()
        return {'FINISHED'}

class OpenSphereTextureSlot(Operator, _OpenTextureBase):
    """ Create a texture for mmd model material.
    """
    bl_idname = 'mmd_tools.material_open_sphere_texture'
    bl_label = 'Open Sphere Texture'
    bl_description = 'Create sphere texture of active material'

    def execute(self, context):
        mat = context.active_object.active_material
        fnMat = FnMaterial(mat)
        fnMat.create_sphere_texture(self.filepath)
        return {'FINISHED'}


class RemoveSphereTexture(Operator):
    """ Create a texture for mmd model material.
    """
    bl_idname = 'mmd_tools.material_remove_sphere_texture'
    bl_label = 'Remove Sphere Texture'
    bl_description = 'Remove sphere texture of active material'
    bl_options = {'PRESET'}

    def execute(self, context):
        mat = context.active_object.active_material
        fnMat = FnMaterial(mat)
        fnMat.remove_sphere_texture()
        return {'FINISHED'}

class MoveMaterialUp(Operator):
    bl_idname = 'mmd_tools.move_material_up'
    bl_label = 'Move Material Up'
    bl_description = 'Moves selected material one slot up'
    bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        valid_mesh = obj and obj.type == 'MESH' and obj.mmd_type == 'NONE'
        return valid_mesh and obj.active_material_index > 0

    def execute(self, context):
        obj = context.active_object
        current_idx = obj.active_material_index
        prev_index = current_idx - 1
        try:
            FnMaterial.swap_materials(obj, current_idx, prev_index,
                                      reverse=True, swap_slots=True)
        except MaterialNotFoundError:
            self.report({'ERROR'}, 'Materials not found')
            return { 'CANCELLED' }
        obj.active_material_index = prev_index

        return { 'FINISHED' }

class MoveMaterialDown(Operator):
    bl_idname = 'mmd_tools.move_material_down'
    bl_label = 'Move Material Down'
    bl_description = 'Moves the selected material one slot down'
    bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        valid_mesh = obj and obj.type == 'MESH' and obj.mmd_type == 'NONE'
        return valid_mesh and obj.active_material_index < len(obj.material_slots) - 1

    def execute(self, context):
        obj = context.active_object
        current_idx = obj.active_material_index
        next_index = current_idx + 1
        try:
            FnMaterial.swap_materials(obj, current_idx, next_index,
                                      reverse=True, swap_slots=True)
        except MaterialNotFoundError:
            self.report({'ERROR'}, 'Materials not found')
            return { 'CANCELLED' }
        obj.active_material_index = next_index
        return { 'FINISHED' }
