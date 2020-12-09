# -*- coding: utf-8 -*-

import bpy


class _NodeTreeUtils:

    def __init__(self, shader):
        self.shader, self.nodes, self.links = shader, shader.nodes, shader.links

    def _find_node(self, node_type):
        return next((n for n in self.nodes if n.bl_idname == node_type), None)

    def new_node(self, idname, pos):
        node = self.nodes.new(idname)
        node.location = (pos[0]*210, pos[1]*220)
        return node

    def new_math_node(self, operation, pos, value1=None, value2=None):
        node = self.new_node('ShaderNodeMath', pos)
        node.operation = operation
        if value1 is not None:
            node.inputs[0].default_value = value1
        if value2 is not None:
            node.inputs[1].default_value = value2
        return node

    def new_vector_math_node(self, operation, pos, vector1=None, vector2=None):
        node = self.new_node('ShaderNodeVectorMath', pos)
        node.operation = operation
        if vector1 is not None:
            node.inputs[0].default_value = vector1
        if vector2 is not None:
            node.inputs[1].default_value = vector2
        return node

    def new_mix_node(self, blend_type, pos, fac=None, color1=None, color2=None):
        node = self.new_node('ShaderNodeMixRGB', pos)
        node.blend_type = blend_type
        if fac is not None:
            node.inputs['Fac'].default_value = fac
        if color1 is not None:
            node.inputs[0].default_value = color1
        if color2 is not None:
            node.inputs[1].default_value = color2
        return node


class _NodeGroupUtils(_NodeTreeUtils):

    def __init__(self, shader):
        super().__init__(shader)
        self.__node_input = self.__node_output = None

    @property
    def node_input(self):
        if not self.__node_input:
            self.__node_input = self._find_node('NodeGroupInput') or self.new_node('NodeGroupInput', (-2, 0))
        return self.__node_input

    @property
    def node_output(self):
        if not self.__node_output:
            self.__node_output = self._find_node('NodeGroupOutput') or self.new_node('NodeGroupOutput', (2, 0))
        return self.__node_output

    def hide_nodes(self, hide_sockets=True):
        skip_nodes = {self.__node_input, self.__node_output}
        for n in (x for x in self.nodes if x not in skip_nodes):
            n.hide = True
            if hide_sockets:
                for s in n.inputs:
                    s.hide = not s.is_linked
                for s in n.outputs:
                    s.hide = not s.is_linked

    def new_input_socket(self, io_name, socket, default_val=None, min_max=None):
        self.__new_io(self.shader.inputs, self.node_input.outputs, io_name, socket, default_val, min_max)

    def new_output_socket(self, io_name, socket, default_val=None, min_max=None):
        self.__new_io(self.shader.outputs, self.node_output.inputs, io_name, socket, default_val, min_max)

    def __new_io(self, shader_io, io_sockets, io_name, socket, default_val=None, min_max=None):
        if io_name not in io_sockets:
            shader_io.new(type=socket.bl_idname, name=io_name)
            if not min_max:
                idname = socket.bl_idname
                if idname.endswith('Factor') or io_name.endswith('Alpha'):
                    shader_io[io_name].min_value, shader_io[io_name].max_value = 0, 1
                elif idname.endswith('Float') or idname.endswith('Vector'):
                    shader_io[io_name].min_value, shader_io[io_name].max_value = -10, 10

        self.links.new(io_sockets[io_name], socket)
        if default_val is not None:
            shader_io[io_name].default_value = default_val
        if min_max is not None:
            shader_io[io_name].min_value, shader_io[io_name].max_value = min_max


class _MaterialMorph:

    @classmethod
    def update_morph_inputs(cls, material, morph):
        if material and material.node_tree and morph.name in material.node_tree.nodes:
            cls.__update_node_inputs(material.node_tree.nodes[morph.name], morph)
            cls.update_morph_inputs(bpy.data.materials.get('mmd_edge.'+material.name, None), morph)

    @classmethod
    def setup_morph_nodes(cls, material, morphs):
        node, nodes = None, []
        for m in morphs:
            node = cls.__morph_node_add(material, m, node)
            nodes.append(node)
        if node:
            node = cls.__morph_node_add(material, None, node) or node
            for n in reversed(nodes):
                n.location += node.location
                if n.node_tree.name != node.node_tree.name:
                    n.location.x -= 100
                if node.name.startswith('mmd_'):
                    n.location.y += 1500
                node = n
        return nodes

    @classmethod
    def reset_morph_links(cls, node):
        cls.__update_morph_links(node, reset=True)

    @classmethod
    def __update_morph_links(cls, node, reset=False):
        nodes, links = node.id_data.nodes, node.id_data.links
        if reset:
            if any(l.from_node.name.startswith('mmd_bind') for i in node.inputs for l in i.links):
                return
            def __init_link(socket_morph, socket_shader):
                if socket_shader and socket_morph.is_linked:
                    links.new(socket_morph.links[0].from_socket, socket_shader)
        else:
            def __init_link(socket_morph, socket_shader):
                if socket_shader:
                    if socket_shader.is_linked:
                        links.new(socket_shader.links[0].from_socket, socket_morph)
                    if socket_morph.type == 'VALUE':
                        socket_morph.default_value = socket_shader.default_value
                    else:
                        socket_morph.default_value[:3] = socket_shader.default_value[:3]
        shader = nodes.get('mmd_shader', None)
        if shader:
            __init_link(node.inputs['Ambient1'], shader.inputs.get('Ambient Color'))
            __init_link(node.inputs['Diffuse1'], shader.inputs.get('Diffuse Color'))
            __init_link(node.inputs['Specular1'], shader.inputs.get('Specular Color'))
            __init_link(node.inputs['Reflect1'], shader.inputs.get('Reflect'))
            __init_link(node.inputs['Alpha1'], shader.inputs.get('Alpha'))
            __init_link(node.inputs['Base1 RGB'], shader.inputs.get('Base Tex'))
            __init_link(node.inputs['Toon1 RGB'], shader.inputs.get('Toon Tex')) #FIXME toon only affect shadow color
            __init_link(node.inputs['Sphere1 RGB'], shader.inputs.get('Sphere Tex'))
        elif 'mmd_edge_preview' in nodes:
            shader = nodes['mmd_edge_preview']
            __init_link(node.inputs['Edge1 RGB'], shader.inputs['Color'])
            __init_link(node.inputs['Edge1 A'], shader.inputs['Alpha'])

    @classmethod
    def __update_node_inputs(cls, node, morph):
        node.inputs['Ambient2'].default_value[:3] = morph.ambient_color[:3]
        node.inputs['Diffuse2'].default_value[:3] = morph.diffuse_color[:3]
        node.inputs['Specular2'].default_value[:3] = morph.specular_color[:3]
        node.inputs['Reflect2'].default_value = morph.shininess
        node.inputs['Alpha2'].default_value = morph.diffuse_color[3]

        node.inputs['Edge2 RGB'].default_value[:3] = morph.edge_color[:3]
        node.inputs['Edge2 A'].default_value = morph.edge_color[3]

        node.inputs['Base2 RGB'].default_value[:3] = morph.texture_factor[:3]
        node.inputs['Base2 A'].default_value = morph.texture_factor[3]
        node.inputs['Toon2 RGB'].default_value[:3] = morph.toon_texture_factor[:3]
        node.inputs['Toon2 A'].default_value = morph.toon_texture_factor[3]
        node.inputs['Sphere2 RGB'].default_value[:3] = morph.sphere_texture_factor[:3]
        node.inputs['Sphere2 A'].default_value = morph.sphere_texture_factor[3]

    @classmethod
    def __morph_node_add(cls, material, morph, prev_node):
        nodes, links = material.node_tree.nodes, material.node_tree.links

        shader = nodes.get('mmd_shader', None)
        if morph:
            node = nodes.new('ShaderNodeGroup')
            node.parent = getattr(shader, 'parent', None)
            node.location = (-250, 0)
            node.node_tree = cls.__get_shader('Add' if morph.offset_type == 'ADD' else 'Mul')
            cls.__update_node_inputs(node, morph)
            if prev_node:
                for id_name in ('Ambient', 'Diffuse', 'Specular' , 'Reflect','Alpha'):
                    links.new(prev_node.outputs[id_name], node.inputs[id_name+'1'])
                for id_name in ('Edge', 'Base', 'Toon' , 'Sphere'):
                    links.new(prev_node.outputs[id_name+' RGB'], node.inputs[id_name+'1 RGB'])
                    links.new(prev_node.outputs[id_name+' A'], node.inputs[id_name+'1 A'])
            else: # initial first node
                if node.node_tree.name.endswith('Add'):
                    node.inputs['Base1 A'].default_value = 1
                    node.inputs['Toon1 A'].default_value = 1
                    node.inputs['Sphere1 A'].default_value = 1
                cls.__update_morph_links(node)
            return node
        # connect last node to shader
        if shader:
            def __soft_link(socket_out, socket_in):
                if socket_out and socket_in:
                    links.new(socket_out, socket_in)
            __soft_link(prev_node.outputs['Ambient'], shader.inputs.get('Ambient Color'))
            __soft_link(prev_node.outputs['Diffuse'], shader.inputs.get('Diffuse Color'))
            __soft_link(prev_node.outputs['Specular'], shader.inputs.get('Specular Color'))
            __soft_link(prev_node.outputs['Reflect'], shader.inputs.get('Reflect'))
            __soft_link(prev_node.outputs['Alpha'], shader.inputs.get('Alpha'))
            __soft_link(prev_node.outputs['Base Tex'], shader.inputs.get('Base Tex'))
            __soft_link(prev_node.outputs['Toon Tex'], shader.inputs.get('Toon Tex'))
            if int(material.mmd_material.sphere_texture_type) != 2: # shader.inputs['Sphere Mul/Add'].default_value < 0.5
                __soft_link(prev_node.outputs['Sphere Tex'], shader.inputs.get('Sphere Tex'))
            else:
                __soft_link(prev_node.outputs['Sphere Tex Add'], shader.inputs.get('Sphere Tex'))
        elif 'mmd_edge_preview' in nodes:
            shader = nodes['mmd_edge_preview']
            links.new(prev_node.outputs['Edge RGB'], shader.inputs['Color'])
            links.new(prev_node.outputs['Edge A'], shader.inputs['Alpha'])
        return shader

    _LEGACY_MODE = '-' if bpy.app.version < (2, 75, 0) else ''

    @classmethod
    def __get_shader(cls, morph_type):
        group_name = 'MMDMorph' + cls._LEGACY_MODE + morph_type
        shader = bpy.data.node_groups.get(group_name, None) or bpy.data.node_groups.new(name=group_name, type='ShaderNodeTree')
        if len(shader.nodes):
            return shader

        ng = _NodeGroupUtils(shader)
        nodes, links = ng.nodes, ng.links

        use_mul = (morph_type == 'Mul')

        def __value_to_color_wrap(out_value, pos):
            if cls._LEGACY_MODE: # for viewport
                node_wrap = ng.new_node('ShaderNodeCombineRGB', pos)
                links.new(out_value, node_wrap.inputs[0])
                links.new(out_value, node_wrap.inputs[1])
                links.new(out_value, node_wrap.inputs[2])
                return node_wrap.outputs[0]
            return out_value

        ############################################################################
        node_input = ng.new_node('NodeGroupInput', (-4, 0))
        node_output = ng.new_node('NodeGroupOutput', (5, 0))

        node_invert = ng.new_math_node('SUBTRACT', (-3, 1), value1=1.0)
        node_dummy_vec = ng.new_node('ShaderNodeVectorMath', (-3, -6))
        default_vector = (use_mul,)*len(node_dummy_vec.inputs[0].default_value)

        ng.new_input_socket('Fac', node_invert.inputs[1], 0)

        out_color = __value_to_color_wrap(node_input.outputs['Fac'], (-3, 2))
        if use_mul:
            out_color_inv = __value_to_color_wrap(node_invert.outputs[0], (-2, 2))
        else:
            nodes.remove(node_invert)
            del node_invert

        def __new_io_vector_wrap(io_name, pos):
            if cls._LEGACY_MODE: # for cycles
                node_wrap = ng.new_vector_math_node('ADD', pos, vector2=(0, 0, 0))
                ng.new_input_socket(io_name, node_wrap.inputs[0], default_vector)
                return node_wrap.outputs[0]
            ng.new_input_socket(io_name, node_dummy_vec.inputs[0], default_vector)
            return node_input.outputs[io_name]

        def __blend_color_add(id_name, pos, tag=''):
            # ColorMul = Color1 * (Fac * Color2 + (1 - Fac))
            # ColorAdd = Color1 + Fac * Color2
            if use_mul:
                node_mul = ng.new_mix_node('MULTIPLY', (pos[0]+1, pos[1]), fac=1.0)
                node_blend = ng.new_mix_node('ADD', (pos[0]+2, pos[1]), fac=1.0)
                links.new(out_color_inv, node_blend.inputs['Color1'])
                links.new(node_mul.outputs['Color'], node_blend.inputs['Color2'])
            else:
                node_mul = node_blend = ng.new_mix_node('MULTIPLY', (pos[0]+1, pos[1]), fac=1.0)

            node_final = ng.new_mix_node('MULTIPLY' if use_mul else 'ADD', (pos[0]+2+use_mul, pos[1]), fac=1.0)

            out_vector1 = __new_io_vector_wrap('%s1'%id_name+tag, (pos[0]+1.5+use_mul, pos[1]+0.1))
            out_vector2 = __new_io_vector_wrap('%s2'%id_name+tag, (pos[0]+0.5, pos[1]-0.1))
            links.new(out_vector1, node_final.inputs['Color1'])
            links.new(out_vector2, node_mul.inputs['Color2'])
            links.new(out_color, node_mul.inputs['Color1'])
            links.new(node_blend.outputs['Color'], node_final.inputs['Color2'])

            ng.new_output_socket(id_name+tag, node_final.outputs['Color'])
            return node_final

        def __blend_value_add(id_name, pos, tag=''):
            # ValueMul = Value1 * (Fac * Value2 + (1 - Fac))
            # ValueAdd = Value1 + Fac * Value2
            if use_mul:
                node_mul = ng.new_math_node('MULTIPLY', (pos[0]+1, pos[1]))
                node_blend = ng.new_math_node('ADD', (pos[0]+2, pos[1]))
                links.new(node_invert.outputs['Value'], node_blend.inputs[0])
                links.new(node_mul.outputs['Value'], node_blend.inputs[1])
            else:
                node_mul = node_blend = ng.new_math_node('MULTIPLY', (pos[0]+1, pos[1]))

            node_final = ng.new_math_node('MULTIPLY' if use_mul else 'ADD', (pos[0]+2+use_mul, pos[1]))

            ng.new_input_socket('%s1'%id_name+tag, node_final.inputs[0], use_mul)
            ng.new_input_socket('%s2'%id_name+tag, node_mul.inputs[1], use_mul)
            ng.new_output_socket(id_name+tag, node_final.outputs['Value'])

            links.new(node_input.outputs['Fac'], node_mul.inputs[0])
            links.new(node_blend.outputs['Value'], node_final.inputs[1])
            return node_final

        def __blend_tex_color(id_name, pos, node_tex_rgb, node_tex_a):
            # Tex Color = tex_rgb * tex_a + (1 - tex_a)
            # : tex_rgb = TexRGB * ColorMul + ColorAdd
            # : tex_a = TexA * ValueMul + ValueAdd
            node_inv = ng.new_math_node('SUBTRACT', (pos[0], pos[1]-0.5), value1=1.0)
            node_mul = ng.new_mix_node('MULTIPLY', (pos[0], pos[1]), fac=1.0)
            node_blend = ng.new_mix_node('ADD', (pos[0]+1, pos[1]), fac=1.0)

            out_tex_a = __value_to_color_wrap(node_tex_a.outputs[0], (pos[0]-0.5, pos[1]-0.1))
            out_tex_a_inv = __value_to_color_wrap(node_inv.outputs[0], (pos[0]+0.5, pos[1]-0.1))

            links.new(node_tex_a.outputs['Value'], node_inv.inputs[1])
            links.new(node_tex_rgb.outputs['Color'], node_mul.inputs['Color1'])
            links.new(out_tex_a, node_mul.inputs['Color2'])
            links.new(node_mul.outputs['Color'], node_blend.inputs['Color1'])
            links.new(out_tex_a_inv, node_blend.inputs['Color2'])

            ng.new_output_socket(id_name+' Tex', node_blend.outputs['Color'])
            if id_name == 'Sphere':
                ng.new_output_socket(id_name+' Tex Add', node_mul.outputs['Color'])

        pos_x = -2
        __blend_color_add('Ambient', (pos_x, 1.5))
        __blend_color_add('Diffuse', (pos_x, 1))
        __blend_color_add('Specular', (pos_x, 0.5))
        __blend_value_add('Reflect', (pos_x, 0))
        __blend_value_add('Alpha', (pos_x, -0.5))
        __blend_color_add('Edge', (pos_x, -1), ' RGB')
        __blend_value_add('Edge', (pos_x, -1.5), ' A')
        for id_name, dy in zip(('Base', 'Toon', 'Sphere'), (0, 1, 2)):
            node_tex_rgb = __blend_color_add(id_name, (pos_x, -2-dy), ' RGB')
            node_tex_a = __blend_value_add(id_name, (pos_x, -2.5-dy), ' A')
            __blend_tex_color(id_name, (pos_x+4+use_mul, -2-dy), node_tex_rgb, node_tex_a)

        nodes.remove(node_dummy_vec)
        del node_dummy_vec

        ng.hide_nodes()
        return ng.shader

