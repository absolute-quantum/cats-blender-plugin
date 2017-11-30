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
        texture = None
        outplug = shader.outputs[0]

        for j in i.material.texture_slots:
            if j is not None and isinstance(j.texture, bpy.types.ImageTexture) and j.use:
                if j.texture_coords == 'UV':  # don't use sphere maps for now
                    texture = i.material.node_tree.nodes.new('ShaderNodeTexImage')
                    texture.location.x  = shader.location.x - 250
                    texture.location.y  = shader.location.y - 150
                    texture.image = j.texture.image

        if texture is not None or i.material.alpha < 1.0:
            alpha_shader = i.material.node_tree.nodes.new('ShaderNodeGroup')
            alpha_shader.location.x = shader.location.x + 250
            alpha_shader.location.y = shader.location.y - 150
            alpha_shader.node_tree = mmd_alpha_shader_grp
            i.material.node_tree.links.new(alpha_shader.inputs[0], outplug)
            outplug = alpha_shader.outputs[0]

        if texture is not None:
            if i.material.diffuse_color == mathutils.Color((1.0, 1.0, 1.0)):
                i.material.node_tree.links.new(shader.inputs[0], texture.outputs['Color'])
            else:
                mix_rgb = i.material.node_tree.nodes.new('ShaderNodeMixRGB')
                mix_rgb.blend_type = 'MULTIPLY'
                mix_rgb.inputs[0].default_value = 1.0
                mix_rgb.inputs[1].default_value = list(i.material.diffuse_color) + [1.0]
                mix_rgb.location.x = shader.location.x -250
                texture.location.x  = shader.location.x - 500
                mix_rgb.location.y = shader.location.y
                i.material.node_tree.links.new(mix_rgb.inputs[2], texture.outputs['Color'])
                i.material.node_tree.links.new(shader.inputs[0], mix_rgb.outputs['Color'])
            if i.material.alpha == 1.0:
                i.material.node_tree.links.new(alpha_shader.inputs[1], texture.outputs['Alpha'])
            else:
                mix_alpha = i.material.node_tree.nodes.new('ShaderNodeMath')
                mix_alpha.operation = 'MULTIPLY'
                mix_alpha.inputs[0].default_value = i.material.alpha
                mix_alpha.location.x = shader.location.x
                mix_alpha.location.y = shader.location.y -300
                i.material.node_tree.links.new(mix_alpha.inputs[1], texture.outputs['Alpha'])
                i.material.node_tree.links.new(alpha_shader.inputs[1], mix_alpha.outputs['Value'])
        else:
            shader.inputs[0].default_value = list(i.material.diffuse_color) + [1.0]
            if i.material.alpha < 1.0:
                alpha_shader.inputs[1].default_value = i.material.alpha

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
