# -*- coding: utf-8 -*-
import bpy
import mathutils
from mmd_tools_local.core.shader import _NodeGroupUtils

def __switchToCyclesRenderEngine():
    if bpy.context.scene.render.engine != 'CYCLES':
        bpy.context.scene.render.engine = 'CYCLES'

def __exposeNodeTreeInput(in_socket, name, default_value, node_input, shader):
    _NodeGroupUtils(shader).new_input_socket(name, in_socket, default_value)

def __exposeNodeTreeOutput(out_socket, name, node_output, shader):
    _NodeGroupUtils(shader).new_output_socket(name, out_socket)

def __getMaterialOutput(nodes, bl_idname):
    o = next((n for n in nodes if n.bl_idname == bl_idname and n.is_active_output), None) or nodes.new(bl_idname)
    o.is_active_output = True
    return o

def create_MMDAlphaShader():
    __switchToCyclesRenderEngine()

    if 'MMDAlphaShader' in bpy.data.node_groups:
        return bpy.data.node_groups['MMDAlphaShader']

    shader = bpy.data.node_groups.new(name='MMDAlphaShader', type='ShaderNodeTree')

    node_input = shader.nodes.new('NodeGroupInput')
    node_output = shader.nodes.new('NodeGroupOutput')
    node_output.location.x += 250
    node_input.location.x -= 500

    trans = shader.nodes.new('ShaderNodeBsdfTransparent')
    trans.location.x -= 250
    trans.location.y += 150
    mix = shader.nodes.new('ShaderNodeMixShader')

    shader.links.new(mix.inputs[1], trans.outputs['BSDF'])

    __exposeNodeTreeInput(mix.inputs[2], 'Shader', None, node_input, shader)
    __exposeNodeTreeInput(mix.inputs['Fac'], 'Alpha', 1.0, node_input, shader)
    __exposeNodeTreeOutput(mix.outputs['Shader'], 'Shader', node_output, shader)

    return shader

def create_MMDBasicShader():
    __switchToCyclesRenderEngine()

    if 'MMDBasicShader' in bpy.data.node_groups:
        return bpy.data.node_groups['MMDBasicShader']

    shader = bpy.data.node_groups.new(name='MMDBasicShader', type='ShaderNodeTree')

    node_input = shader.nodes.new('NodeGroupInput')
    node_output = shader.nodes.new('NodeGroupOutput')
    node_output.location.x += 250
    node_input.location.x -= 500

    dif = shader.nodes.new('ShaderNodeBsdfDiffuse')
    dif.location.x -= 250
    dif.location.y += 150
    glo = shader.nodes.new('ShaderNodeBsdfGlossy')
    glo.location.x -= 250
    glo.location.y -= 150
    mix = shader.nodes.new('ShaderNodeMixShader')
    shader.links.new(mix.inputs[1], dif.outputs['BSDF'])
    shader.links.new(mix.inputs[2], glo.outputs['BSDF'])

    __exposeNodeTreeInput(dif.inputs['Color'], 'diffuse', [1.0, 1.0, 1.0, 1.0], node_input, shader)
    __exposeNodeTreeInput(glo.inputs['Color'], 'glossy', [1.0, 1.0, 1.0, 1.0], node_input, shader)
    __exposeNodeTreeInput(glo.inputs['Roughness'], 'glossy_rough', 0.0, node_input, shader)
    __exposeNodeTreeInput(mix.inputs['Fac'], 'reflection', 0.02, node_input, shader)
    __exposeNodeTreeOutput(mix.outputs['Shader'], 'shader', node_output, shader)

    return shader

def __enum_linked_nodes(node):
    yield node
    if node.parent:
        yield node.parent
    for n in set(l.from_node for i in node.inputs for l in i.links):
        yield from __enum_linked_nodes(n)

def __cleanNodeTree(material):
    nodes = getattr(material.node_tree, 'nodes', ())
    node_names = set(n.name for n in nodes)
    for o in (n for n in nodes if n.bl_idname in {'ShaderNodeOutput', 'ShaderNodeOutputMaterial'}):
        if any(i.is_linked for i in o.inputs):
            node_names -= set(linked.name for linked in __enum_linked_nodes(o))
    for name in node_names:
        nodes.remove(nodes[name])

def is_principled_bsdf_supported():
    return hasattr(bpy.types, 'ShaderNodeBsdfPrincipled')

def convertToCyclesShader(obj, use_principled=False, clean_nodes=False):
    use_principled = (use_principled and is_principled_bsdf_supported())
    __switchToCyclesRenderEngine()
    for i in obj.material_slots:
        if i.material:
            if not i.material.use_nodes:
                i.material.use_nodes = True
                __convertToMMDBasicShader(i.material)
            if use_principled:
                __convertToPrincipledBsdf(i.material)
            if clean_nodes:
                __cleanNodeTree(i.material)

def __convertToMMDBasicShader(material):
    mmd_basic_shader_grp = create_MMDBasicShader()
    mmd_alpha_shader_grp = create_MMDAlphaShader()

    if not any(filter(lambda x: isinstance(x, bpy.types.ShaderNodeGroup) and  x.node_tree.name in {'MMDBasicShader', 'MMDAlphaShader'}, material.node_tree.nodes)):
        # Add nodes for Cycles Render
        shader = material.node_tree.nodes.new('ShaderNodeGroup')
        shader.node_tree = mmd_basic_shader_grp
        shader.inputs[0].default_value[:3] = material.diffuse_color[:3]
        shader.inputs[1].default_value[:3] = material.specular_color[:3]
        shader.inputs['glossy_rough'].default_value = 1.0/getattr(material, 'specular_hardness', 50)
        outplug = shader.outputs[0]

        node_tex, node_alpha = None, None
        location = shader.location.copy()
        location.x -= 1000
        reuse_nodes = {}
        for j in getattr(material, 'texture_slots', ()):
            if j and j.use and isinstance(j.texture, bpy.types.ImageTexture) and getattr(j.texture.image, 'depth', 0):
                if not (j.use_map_color_diffuse or j.use_map_alpha):
                    continue
                if j.texture_coords not in {'UV', 'NORMAL'}:
                    continue

                uv_tag = j.uv_layer if j.texture_coords == 'UV' else ''
                key_node_tex = j.texture.name + j.texture_coords + uv_tag
                tex_img = reuse_nodes.get(key_node_tex)
                if tex_img is None:
                    tex_img = material.node_tree.nodes.new('ShaderNodeTexImage')
                    tex_img.location = location
                    tex_img.image = j.texture.image
                    if j.texture_coords == 'NORMAL' and j.blend_type == 'ADD':
                        tex_img.color_space = 'NONE'
                    reuse_nodes[key_node_tex] = tex_img
                    location.x += 250
                    location.y -= 150

                    key_node_vec = j.texture_coords + uv_tag
                    plug_vector = reuse_nodes.get(key_node_vec)
                    if plug_vector is None:
                        plug_vector = 0
                        if j.texture_coords == 'UV':
                            if j.uv_layer and hasattr(bpy.types, 'ShaderNodeUVMap'):
                                node_vector = material.node_tree.nodes.new('ShaderNodeUVMap')
                                node_vector.uv_map = j.uv_layer
                                node_vector.location.x = shader.location.x - 1500
                                node_vector.location.y = tex_img.location.y - 50
                                plug_vector = node_vector.outputs[0]
                            elif j.uv_layer:
                                node_vector = material.node_tree.nodes.new('ShaderNodeAttribute')
                                node_vector.attribute_name = j.uv_layer
                                node_vector.location.x = shader.location.x - 1500
                                node_vector.location.y = tex_img.location.y - 50
                                plug_vector = node_vector.outputs[1]

                        elif j.texture_coords == 'NORMAL':
                            tex_coord = material.node_tree.nodes.new('ShaderNodeTexCoord')
                            tex_coord.location.x = shader.location.x - 1900
                            tex_coord.location.y = shader.location.y - 600

                            vec_trans = material.node_tree.nodes.new('ShaderNodeVectorTransform')
                            vec_trans.vector_type = 'NORMAL'
                            vec_trans.convert_from = 'OBJECT'
                            vec_trans.convert_to = 'CAMERA'
                            vec_trans.location.x = tex_coord.location.x + 200
                            vec_trans.location.y = tex_coord.location.y
                            material.node_tree.links.new(vec_trans.inputs[0], tex_coord.outputs['Normal'])

                            node_vector = material.node_tree.nodes.new('ShaderNodeMapping')
                            node_vector.vector_type = 'POINT'
                            node_vector.translation = (0.5, 0.5, 0.0)
                            node_vector.scale = (0.5, 0.5, 1.0)
                            node_vector.location.x = vec_trans.location.x + 200
                            node_vector.location.y = vec_trans.location.y
                            material.node_tree.links.new(node_vector.inputs[0], vec_trans.outputs[0])
                            plug_vector = node_vector.outputs[0]

                        reuse_nodes[key_node_vec] = plug_vector

                    if plug_vector:
                        material.node_tree.links.new(tex_img.inputs[0], plug_vector)

                if j.use_map_color_diffuse:
                    if node_tex is None and tuple(material.diffuse_color) == (1.0, 1.0, 1.0):
                        node_tex = tex_img
                    else:
                        node_tex_last = node_tex
                        node_tex = material.node_tree.nodes.new('ShaderNodeMixRGB')
                        try:
                            node_tex.blend_type = j.blend_type
                        except TypeError as e:
                            print(node_tex, e)
                        node_tex.inputs[0].default_value = 1.0
                        node_tex.inputs[1].default_value = shader.inputs[0].default_value
                        node_tex.location.x = tex_img.location.x + 250
                        node_tex.location.y = tex_img.location.y + 150
                        material.node_tree.links.new(node_tex.inputs[2], tex_img.outputs['Color'])
                        if node_tex_last:
                            material.node_tree.links.new(node_tex.inputs[1], node_tex_last.outputs[0])

                if j.use_map_alpha:
                    if node_alpha is None and material.alpha == 1.0:
                        node_alpha = tex_img
                    else:
                        node_alpha_last = node_alpha
                        node_alpha = material.node_tree.nodes.new('ShaderNodeMath')
                        try:
                            node_alpha.operation = j.blend_type
                        except TypeError as e:
                            print(node_alpha, e)
                        node_alpha.inputs[0].default_value = material.alpha
                        node_alpha.location.x = tex_img.location.x + 250
                        node_alpha.location.y = tex_img.location.y - 500
                        material.node_tree.links.new(node_alpha.inputs[1], tex_img.outputs['Alpha'])
                        if node_alpha_last:
                            material.node_tree.links.new(node_alpha.inputs[0], node_alpha_last.outputs[len(node_alpha_last.outputs)-1])

        if node_tex:
            material.node_tree.links.new(shader.inputs[0], node_tex.outputs[0])

        alpha_value = 1.0
        if hasattr(material, 'alpha'):
            alpha_value = material.alpha
        elif len(material.diffuse_color) > 3:
            alpha_value = material.diffuse_color[3]

        if node_alpha or alpha_value < 1.0:
            alpha_shader = material.node_tree.nodes.new('ShaderNodeGroup')
            alpha_shader.location.x = shader.location.x + 250
            alpha_shader.location.y = shader.location.y - 150
            alpha_shader.node_tree = mmd_alpha_shader_grp
            alpha_shader.inputs[1].default_value = alpha_value
            material.node_tree.links.new(alpha_shader.inputs[0], outplug)
            outplug = alpha_shader.outputs[0]
            if node_alpha:
                material.node_tree.links.new(alpha_shader.inputs[1], node_alpha.outputs[len(node_alpha.outputs)-1])

        material_output = __getMaterialOutput(material.node_tree.nodes, 'ShaderNodeOutputMaterial')
        material.node_tree.links.new(material_output.inputs['Surface'], outplug)
        material_output.location.x = shader.location.x + 500
        material_output.location.y = shader.location.y - 150

        if not hasattr(bpy.types, 'ShaderNodeMaterial'):
            return
        # Add necessary nodes to retain Blender Render functionality
        out_node = __getMaterialOutput(material.node_tree.nodes, 'ShaderNodeOutput')
        mat_node = material.node_tree.nodes.new('ShaderNodeMaterial')
        mat_node.material = material
        mat_node.location.x = shader.location.x - 250
        mat_node.location.y = shader.location.y + 500
        out_node.location.x = mat_node.location.x + 750
        out_node.location.y = mat_node.location.y
        material.node_tree.links.new(out_node.inputs['Color'], mat_node.outputs['Color'])
        material.node_tree.links.new(out_node.inputs['Alpha'], mat_node.outputs['Alpha'])

def __convertToPrincipledBsdf(material):
    node_names = set()
    for s in tuple(n for n in material.node_tree.nodes if isinstance(n, bpy.types.ShaderNodeGroup)):
        if s.node_tree.name == 'MMDBasicShader':
            for l in s.outputs[0].links:
                to_node = l.to_node
                # assuming there is no bpy.types.NodeReroute between MMDBasicShader and MMDAlphaShader
                if isinstance(to_node, bpy.types.ShaderNodeGroup) and to_node.node_tree.name == 'MMDAlphaShader':
                    __switchToPrincipledBsdf(material.node_tree, s, to_node)
                    node_names.add(to_node.name)
                else:
                    __switchToPrincipledBsdf(material.node_tree, s)
            node_names.add(s.name)
        elif s.node_tree.name == 'MMDShaderDev':
            __switchToPrincipledBsdf(material.node_tree, s)
            node_names.add(s.name)
    # remove MMD shader nodes
    nodes = material.node_tree.nodes
    for name in node_names:
        nodes.remove(nodes[name])

def __switchToPrincipledBsdf(node_tree, node_basic, node_alpha=None):
    shader = node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    shader.parent = node_basic.parent
    shader.location.x = node_basic.location.x
    shader.location.y = node_basic.location.y

    alpha_socket_name = 'Alpha'
    if node_basic.node_tree.name == 'MMDShaderDev':
        node_alpha, alpha_socket_name = node_basic, 'Base Alpha'
        if 'Base Tex' in node_basic.inputs and node_basic.inputs['Base Tex'].is_linked:
            node_tree.links.new(node_basic.inputs['Base Tex'].links[0].from_socket, shader.inputs['Base Color'])
        elif 'Diffuse Color' in node_basic.inputs:
            shader.inputs['Base Color'].default_value[:3] = node_basic.inputs['Diffuse Color'].default_value[:3]
    elif 'diffuse' in node_basic.inputs:
        shader.inputs['Base Color'].default_value[:3] = node_basic.inputs['diffuse'].default_value[:3]
        if node_basic.inputs['diffuse'].is_linked:
            node_tree.links.new(node_basic.inputs['diffuse'].links[0].from_socket, shader.inputs['Base Color'])

    shader.inputs['IOR'].default_value = 1.0

    output_links = node_basic.outputs[0].links
    if node_alpha:
        output_links = node_alpha.outputs[0].links
        shader.parent = node_alpha.parent or shader.parent
        shader.location.x = node_alpha.location.x

        if alpha_socket_name in node_alpha.inputs:
            if 'Alpha' in shader.inputs:
                shader.inputs['Alpha'].default_value = node_alpha.inputs[alpha_socket_name].default_value
                if node_alpha.inputs[alpha_socket_name].is_linked:
                    node_tree.links.new(node_alpha.inputs[alpha_socket_name].links[0].from_socket, shader.inputs['Alpha'])
            else:
                shader.inputs['Transmission'].default_value = 1 - node_alpha.inputs[alpha_socket_name].default_value
                if node_alpha.inputs[alpha_socket_name].is_linked:
                    node_invert = node_tree.nodes.new('ShaderNodeMath')
                    node_invert.parent = shader.parent
                    node_invert.location.x = node_alpha.location.x - 250
                    node_invert.location.y = node_alpha.location.y - 300
                    node_invert.operation = 'SUBTRACT'
                    node_invert.use_clamp = True
                    node_invert.inputs[0].default_value = 1
                    node_tree.links.new(node_alpha.inputs[alpha_socket_name].links[0].from_socket, node_invert.inputs[1])
                    node_tree.links.new(node_invert.outputs[0], shader.inputs['Transmission'])

    for l in output_links:
        node_tree.links.new(shader.outputs[0], l.to_socket)
