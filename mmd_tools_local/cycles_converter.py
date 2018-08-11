# -*- coding: utf-8 -*-
import bpy
import mathutils

def __exposeNodeTreeInput(in_socket, name, default_value, node_input, shader):
    t = len(node_input.outputs)-1
    i = node_input.outputs[t]
    shader.links.new(in_socket, i)
    if default_value is not None:
        shader.inputs[t].default_value = default_value
    shader.inputs[t].name = name

def __exposeNodeTreeOutput(out_socket, name, node_output, shader):
    t = len(node_output.inputs)-1
    i = node_output.inputs[t]
    shader.links.new(i, out_socket)
    shader.outputs[t].name = name

def __getMaterialOutput(nodes):
    for node in nodes:
        if isinstance(node, bpy.types.ShaderNodeOutputMaterial):
            return node

    o = nodes.new('ShaderNodeOutputMaterial')
    o.name = 'Material Output'
    return o

def create_MMDAlphaShader():
    bpy.context.scene.render.engine = 'CYCLES'

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
    bpy.context.scene.render.engine = 'CYCLES'

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

def convertToCyclesShader(obj):
    mmd_basic_shader_grp = create_MMDBasicShader()
    mmd_alpha_shader_grp = create_MMDAlphaShader()

    bpy.context.scene.render.engine = 'CYCLES'

    for i in obj.material_slots:
        if i.material is None or i.material.use_nodes:
            continue

        i.material.use_nodes = True

        for j in i.material.node_tree.nodes:
            print(j)
        if any(filter(lambda x: isinstance(x, bpy.types.ShaderNodeGroup) and  x.node_tree.name in ['MMDBasicShader', 'MMDAlphaShader'], i.material.node_tree.nodes)):
            continue

        i.material.node_tree.links.clear()

        # Delete the redundant node
        for node in i.material.node_tree.nodes:
            if isinstance(node, bpy.types.ShaderNodeBsdfDiffuse):
                i.material.node_tree.nodes.remove(node)
                break

        # Add nodes for Cycles Render
        shader = i.material.node_tree.nodes.new('ShaderNodeGroup')
        shader.node_tree = mmd_basic_shader_grp
        shader.inputs[0].default_value = list(i.material.diffuse_color) + [1.0]
        shader.inputs[1].default_value = list(i.material.specular_color) + [1.0]
        shader.inputs['glossy_rough'].default_value = 1.0/i.material.specular_hardness
        outplug = shader.outputs[0]

        node_tex, node_alpha = None, None
        location = shader.location.copy()
        location.x -= 1000
        reuse_nodes = {}
        for j in i.material.texture_slots:
            if j and j.use and isinstance(j.texture, bpy.types.ImageTexture) and getattr(j.texture.image, 'depth', 0):
                if not (j.use_map_color_diffuse or j.use_map_alpha):
                    continue
                if j.texture_coords not in {'UV', 'NORMAL'}:
                    continue

                uv_tag = j.uv_layer if j.texture_coords == 'UV' else ''
                key_node_tex = j.texture.name + j.texture_coords + uv_tag
                tex_img = reuse_nodes.get(key_node_tex)
                if tex_img is None:
                    tex_img = i.material.node_tree.nodes.new('ShaderNodeTexImage')
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
                                node_vector = i.material.node_tree.nodes.new('ShaderNodeUVMap')
                                node_vector.uv_map = j.uv_layer
                                node_vector.location.x = shader.location.x - 1500
                                node_vector.location.y = tex_img.location.y - 50
                                plug_vector = node_vector.outputs[0]
                            elif j.uv_layer:
                                node_vector = i.material.node_tree.nodes.new('ShaderNodeAttribute')
                                node_vector.attribute_name = j.uv_layer
                                node_vector.location.x = shader.location.x - 1500
                                node_vector.location.y = tex_img.location.y - 50
                                plug_vector = node_vector.outputs[1]

                        elif j.texture_coords == 'NORMAL':
                            tex_coord = i.material.node_tree.nodes.new('ShaderNodeTexCoord')
                            tex_coord.location.x = shader.location.x - 1900
                            tex_coord.location.y = shader.location.y - 600

                            vec_trans = i.material.node_tree.nodes.new('ShaderNodeVectorTransform')
                            vec_trans.vector_type = 'NORMAL'
                            vec_trans.convert_from = 'OBJECT'
                            vec_trans.convert_to = 'CAMERA'
                            vec_trans.location.x = tex_coord.location.x + 200
                            vec_trans.location.y = tex_coord.location.y
                            i.material.node_tree.links.new(vec_trans.inputs[0], tex_coord.outputs['Normal'])

                            node_vector = i.material.node_tree.nodes.new('ShaderNodeMapping')
                            node_vector.vector_type = 'POINT'
                            node_vector.translation = (0.5, 0.5, 0.0)
                            node_vector.scale = (0.5, 0.5, 1.0)
                            node_vector.location.x = vec_trans.location.x + 200
                            node_vector.location.y = vec_trans.location.y
                            i.material.node_tree.links.new(node_vector.inputs[0], vec_trans.outputs[0])
                            plug_vector = node_vector.outputs[0]

                        reuse_nodes[key_node_vec] = plug_vector

                    if plug_vector:
                        i.material.node_tree.links.new(tex_img.inputs[0], plug_vector)

                if j.use_map_color_diffuse:
                    if node_tex is None and tuple(i.material.diffuse_color) == (1.0, 1.0, 1.0):
                        node_tex = tex_img
                    else:
                        node_tex_last = node_tex
                        node_tex = i.material.node_tree.nodes.new('ShaderNodeMixRGB')
                        try:
                            node_tex.blend_type = j.blend_type
                        except TypeError as e:
                            print(node_tex, e)
                        node_tex.inputs[0].default_value = 1.0
                        node_tex.inputs[1].default_value = shader.inputs[0].default_value
                        node_tex.location.x = tex_img.location.x + 250
                        node_tex.location.y = tex_img.location.y + 150
                        i.material.node_tree.links.new(node_tex.inputs[2], tex_img.outputs['Color'])
                        if node_tex_last:
                            i.material.node_tree.links.new(node_tex.inputs[1], node_tex_last.outputs[0])

                if j.use_map_alpha:
                    if node_alpha is None and i.material.alpha == 1.0:
                        node_alpha = tex_img
                    else:
                        node_alpha_last = node_alpha
                        node_alpha = i.material.node_tree.nodes.new('ShaderNodeMath')
                        try:
                            node_alpha.operation = j.blend_type
                        except TypeError as e:
                            print(node_alpha, e)
                        node_alpha.inputs[0].default_value = i.material.alpha
                        node_alpha.location.x = tex_img.location.x + 250
                        node_alpha.location.y = tex_img.location.y - 500
                        i.material.node_tree.links.new(node_alpha.inputs[1], tex_img.outputs['Alpha'])
                        if node_alpha_last:
                            i.material.node_tree.links.new(node_alpha.inputs[0], node_alpha_last.outputs[-1])

        if node_tex:
            i.material.node_tree.links.new(shader.inputs[0], node_tex.outputs[0])

        if node_alpha or i.material.alpha < 1.0:
            alpha_shader = i.material.node_tree.nodes.new('ShaderNodeGroup')
            alpha_shader.location.x = shader.location.x + 250
            alpha_shader.location.y = shader.location.y - 150
            alpha_shader.node_tree = mmd_alpha_shader_grp
            alpha_shader.inputs[1].default_value = i.material.alpha
            i.material.node_tree.links.new(alpha_shader.inputs[0], outplug)
            outplug = alpha_shader.outputs[0]
            if node_alpha:
                i.material.node_tree.links.new(alpha_shader.inputs[1], node_alpha.outputs[-1])

        material_output = __getMaterialOutput(i.material.node_tree.nodes)
        i.material.node_tree.links.new(material_output.inputs['Surface'], outplug)
        material_output.location.x = shader.location.x + 500
        material_output.location.y = shader.location.y - 150

        # Add necessary nodes to retain Blender Render functionality
        mat_node = i.material.node_tree.nodes.new('ShaderNodeMaterial')
        out_node = i.material.node_tree.nodes.new('ShaderNodeOutput')
        mat_node.material = i.material
        mat_node.location.x = shader.location.x - 250
        mat_node.location.y = shader.location.y + 500
        out_node.location.x = mat_node.location.x + 750
        out_node.location.y = mat_node.location.y
        i.material.node_tree.links.new(out_node.inputs['Color'], mat_node.outputs['Color'])
        i.material.node_tree.links.new(out_node.inputs['Alpha'], mat_node.outputs['Alpha'])
