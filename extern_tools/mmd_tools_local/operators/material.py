# -*- coding: utf-8 -*-

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

from mmd_tools_local import register_wrap
from mmd_tools_local import cycles_converter
from mmd_tools_local.core.material import FnMaterial
from mmd_tools_local.core.exceptions import MaterialNotFoundError
from mmd_tools_local.core.shader import _NodeGroupUtils

@register_wrap
class ConvertMaterialsForCycles(Operator):
    bl_idname = 'mmd_tools.convert_materials_for_cycles'
    bl_label = 'Convert Shaders For Cycles'
    bl_description = 'Convert materials of selected objects for Cycles.'
    bl_options = {'REGISTER', 'UNDO'}

    use_principled = bpy.props.BoolProperty(
        name='Convert to Principled BSDF',
        description='Convert MMD shader nodes to Principled BSDF as well if enabled',
        default=False,
        options={'SKIP_SAVE'},
        )

    clean_nodes = bpy.props.BoolProperty(
        name='Clean Nodes',
        description='Remove redundant nodes as well if enabled. Disable it to keep node data.',
        default=False,
        options={'SKIP_SAVE'},
        )

    @classmethod
    def poll(cls, context):
        return next((x for x in context.selected_objects if x.type == 'MESH'), None)

    def draw(self, context):
        layout = self.layout
        if cycles_converter.is_principled_bsdf_supported():
            layout.prop(self, 'use_principled')
        layout.prop(self, 'clean_nodes')

    def execute(self, context):
        try:
            context.scene.render.engine = 'CYCLES'
        except:
            self.report({'ERROR'}, ' * Failed to change to Cycles render engine.')
            return {'CANCELLED'}
        for obj in (x for x in context.selected_objects if x.type == 'MESH'):
            cycles_converter.convertToCyclesShader(obj, use_principled=self.use_principled, clean_nodes=self.clean_nodes)
        return {'FINISHED'}

@register_wrap
class _OpenTextureBase(object):
    """ Create a texture for mmd model material.
    """
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

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

@register_wrap
class OpenTexture(Operator, _OpenTextureBase):
    bl_idname = 'mmd_tools.material_open_texture'
    bl_label = 'Open Texture'
    bl_description = 'Create main texture of active material'

    def execute(self, context):
        mat = context.active_object.active_material
        fnMat = FnMaterial(mat)
        fnMat.create_texture(self.filepath)
        return {'FINISHED'}

@register_wrap
class RemoveTexture(Operator):
    """ Create a texture for mmd model material.
    """
    bl_idname = 'mmd_tools.material_remove_texture'
    bl_label = 'Remove Texture'
    bl_description = 'Remove main texture of active material'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        mat = context.active_object.active_material
        fnMat = FnMaterial(mat)
        fnMat.remove_texture()
        return {'FINISHED'}

@register_wrap
class OpenSphereTextureSlot(Operator, _OpenTextureBase):
    """ Create a texture for mmd model material.
    """
    bl_idname = 'mmd_tools.material_open_sphere_texture'
    bl_label = 'Open Sphere Texture'
    bl_description = 'Create sphere texture of active material'

    def execute(self, context):
        mat = context.active_object.active_material
        fnMat = FnMaterial(mat)
        fnMat.create_sphere_texture(self.filepath, context.active_object)
        return {'FINISHED'}

@register_wrap
class RemoveSphereTexture(Operator):
    """ Create a texture for mmd model material.
    """
    bl_idname = 'mmd_tools.material_remove_sphere_texture'
    bl_label = 'Remove Sphere Texture'
    bl_description = 'Remove sphere texture of active material'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        mat = context.active_object.active_material
        fnMat = FnMaterial(mat)
        fnMat.remove_sphere_texture()
        return {'FINISHED'}

@register_wrap
class MoveMaterialUp(Operator):
    bl_idname = 'mmd_tools.move_material_up'
    bl_label = 'Move Material Up'
    bl_description = 'Moves selected material one slot up'
    bl_options = {'REGISTER', 'UNDO'}

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

@register_wrap
class MoveMaterialDown(Operator):
    bl_idname = 'mmd_tools.move_material_down'
    bl_label = 'Move Material Down'
    bl_description = 'Moves the selected material one slot down'
    bl_options = {'REGISTER', 'UNDO'}

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

@register_wrap
class EdgePreviewSetup(Operator):
    bl_idname = 'mmd_tools.edge_preview_setup'
    bl_label = 'Edge Preview Setup'
    bl_description = 'Preview toon edge settings of active model using "Solidify" modifier'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    action = bpy.props.EnumProperty(
        name='Action',
        description='Select action',
        items=[
            ('CREATE', 'Create', 'Create toon edge', 0),
            ('CLEAN', 'Clean', 'Clear toon edge', 1),
            ],
        default='CREATE',
        )

    def execute(self, context):
        from mmd_tools_local.core.model import Model
        root = Model.findRoot(context.active_object)
        if root is None:
            self.report({'ERROR'}, 'Select a MMD model')
            return {'CANCELLED'}

        rig = Model(root)
        if self.action == 'CLEAN':
            for obj in rig.meshes():
                self.__clean_toon_edge(obj)
        else:
            scale = rig.rootObject().empty_draw_size * 0.2
            counts = sum(self.__create_toon_edge(obj, scale) for obj in rig.meshes())
            self.report({'INFO'}, 'Created %d toon edge(s)'%counts)
        return {'FINISHED'}

    def __clean_toon_edge(self, obj):
        if 'mmd_edge_preview' in obj.modifiers:
            obj.modifiers.remove(obj.modifiers['mmd_edge_preview'])

        if 'mmd_edge_preview' in obj.vertex_groups:
            obj.vertex_groups.remove(obj.vertex_groups['mmd_edge_preview'])

        FnMaterial.clean_materials(obj, can_remove=lambda m: m and m.name.startswith('mmd_edge.'))

    def __create_toon_edge(self, obj, scale=1.0):
        self.__clean_toon_edge(obj)
        materials = obj.data.materials
        material_offset = len(materials)
        for m in tuple(materials):
            if m and m.mmd_material.enabled_toon_edge:
                mat_edge = self.__get_edge_material('mmd_edge.'+m.name, m.mmd_material.edge_color, materials)
                materials.append(mat_edge)
            elif material_offset > 1:
                mat_edge = self.__get_edge_material('mmd_edge.disabled', (0, 0, 0, 0), materials)
                materials.append(mat_edge)
        if len(materials) > material_offset:
            mod = obj.modifiers.get('mmd_edge_preview', None)
            if mod is None:
                mod = obj.modifiers.new('mmd_edge_preview', 'SOLIDIFY')
            mod.material_offset = material_offset
            mod.thickness_vertex_group = 1e-3 # avoid overlapped faces
            mod.use_flip_normals = True
            mod.use_rim = False
            mod.offset = 1
            self.__create_edge_preview_group(obj)
            mod.thickness = scale
            mod.vertex_group = 'mmd_edge_preview'
        return len(materials) - material_offset

    def __create_edge_preview_group(self, obj):
        vertices, materials = obj.data.vertices, obj.data.materials
        weight_map = {i:m.mmd_material.edge_weight for i, m in enumerate(materials) if m}
        scale_map = {}
        vg_scale_index = obj.vertex_groups.find('mmd_edge_scale')
        if vg_scale_index >= 0:
            scale_map = {v.index:g.weight for v in vertices for g in v.groups if g.group == vg_scale_index}
        vg_edge_preview = obj.vertex_groups.new(name='mmd_edge_preview')
        for i, mi in {v:f.material_index for f in reversed(obj.data.polygons) for v in f.vertices}.items():
            weight = scale_map.get(i, 1.0) * weight_map.get(mi, 1.0) * 0.02
            vg_edge_preview.add(index=[i], weight=weight, type='REPLACE')

    def __get_edge_material(self, mat_name, edge_color, materials):
        if mat_name in materials:
            return materials[mat_name]
        mat = bpy.data.materials.get(mat_name, None)
        if mat is None:
            mat = bpy.data.materials.new(mat_name)
        mmd_mat = mat.mmd_material
        # note: edge affects ground shadow
        mmd_mat.is_double_sided = mmd_mat.enabled_drop_shadow = False
        mmd_mat.enabled_self_shadow_map = mmd_mat.enabled_self_shadow = False
        #mmd_mat.enabled_self_shadow_map = True # for blender 2.78+ BI viewport only
        mmd_mat.diffuse_color = mmd_mat.specular_color = (0, 0, 0)
        mmd_mat.ambient_color = edge_color[:3]
        mmd_mat.alpha = edge_color[3]
        mmd_mat.edge_color = edge_color
        self.__make_shader(mat)
        return mat

    def __make_shader(self, m):
        m.use_nodes = True
        nodes, links = m.node_tree.nodes, m.node_tree.links

        node_shader = nodes.get('mmd_edge_preview', None)
        if node_shader is None or not any(s.is_linked for s in node_shader.outputs):
            XPOS, YPOS = 210, 110
            nodes.clear()
            node_shader = nodes.new('ShaderNodeGroup')
            node_shader.name = 'mmd_edge_preview'
            node_shader.location = (0, 0)
            node_shader.width = 200
            node_shader.node_tree = self.__get_edge_preview_shader()

            if bpy.app.version < (2, 80, 0):
                node_out = nodes.new('ShaderNodeOutput')
                node_out.location = (XPOS*2, YPOS*2)
                links.new(node_shader.outputs['Color'], node_out.inputs['Color'])
                links.new(node_shader.outputs['Alpha'], node_out.inputs['Alpha'])

            node_out = nodes.new('ShaderNodeOutputMaterial')
            node_out.location = (XPOS*2, YPOS*0)
            links.new(node_shader.outputs['Shader'], node_out.inputs['Surface'])

        node_shader.inputs['Color'].default_value = m.mmd_material.edge_color
        node_shader.inputs['Alpha'].default_value = m.mmd_material.edge_color[3]

    def __get_edge_preview_shader(self):
        group_name = 'MMDEdgePreview'
        shader = bpy.data.node_groups.get(group_name, None) or bpy.data.node_groups.new(name=group_name, type='ShaderNodeTree')
        if len(shader.nodes):
            return shader

        ng = _NodeGroupUtils(shader)

        node_input = ng.new_node('NodeGroupInput', (-5, 0))
        node_output = ng.new_node('NodeGroupOutput', (3, 0))

        ############################################################################
        node_color = ng.new_node('ShaderNodeMixRGB', (-1, -1.5))
        node_color.mute = True

        ng.new_input_socket('Color', node_color.inputs['Color1'])

        if bpy.app.version < (2, 80, 0):
            node_geo = ng.new_node('ShaderNodeGeometry', (-2, -2.5))
            node_cull = ng.new_math_node('MULTIPLY', (-1, -2.5))

            ng.links.new(node_geo.outputs['Front/Back'], node_cull.inputs[1])

            ng.new_input_socket('Alpha', node_cull.inputs[0])
            ng.new_output_socket('Color', node_color.outputs['Color'])
            ng.new_output_socket('Alpha', node_cull.outputs['Value'])

        ############################################################################
        node_ray = ng.new_node('ShaderNodeLightPath', (-3, 1.5))
        node_geo = ng.new_node('ShaderNodeNewGeometry', (-3, 0))
        node_max = ng.new_math_node('MAXIMUM', (-2, 1.5))
        node_max.mute = True
        node_gt = ng.new_math_node('GREATER_THAN', (-1, 1))
        node_alpha = ng.new_math_node('MULTIPLY', (0, 1))
        node_trans = ng.new_node('ShaderNodeBsdfTransparent', (0, 0))
        EDGE_NODE_NAME = 'ShaderNodeEmission' if bpy.app.version < (2, 80, 0) else 'ShaderNodeBackground'
        node_rgb = ng.new_node(EDGE_NODE_NAME, (0, -0.5)) # BsdfDiffuse/Background/Emission
        node_mix = ng.new_node('ShaderNodeMixShader', (1, 0.5))

        links = ng.links
        links.new(node_ray.outputs['Is Camera Ray'], node_max.inputs[0])
        links.new(node_ray.outputs['Is Glossy Ray'], node_max.inputs[1])
        links.new(node_max.outputs['Value'], node_gt.inputs[0])
        links.new(node_geo.outputs['Backfacing'], node_gt.inputs[1])
        links.new(node_gt.outputs['Value'], node_alpha.inputs[0])
        links.new(node_alpha.outputs['Value'], node_mix.inputs['Fac'])
        links.new(node_trans.outputs['BSDF'], node_mix.inputs[1])
        links.new(node_rgb.outputs[0], node_mix.inputs[2])
        links.new(node_color.outputs['Color'], node_rgb.inputs['Color'])

        ng.new_input_socket('Alpha', node_alpha.inputs[1])
        ng.new_output_socket('Shader', node_mix.outputs['Shader'])

        return shader

