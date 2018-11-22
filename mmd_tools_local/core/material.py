# -*- coding: utf-8 -*-

import logging
import os

import bpy
from mmd_tools_local.bpyutils import addon_preferences, select_object
from mmd_tools_local.core.exceptions import MaterialNotFoundError

SPHERE_MODE_OFF    = 0
SPHERE_MODE_MULT   = 1
SPHERE_MODE_ADD    = 2
SPHERE_MODE_SUBTEX = 3

class FnMaterial(object):
    __BASE_TEX_SLOT = 0
    __TOON_TEX_SLOT = 1
    __SPHERE_TEX_SLOT = 2
    __SPHERE_ALPHA_SLOT = 5

    def __init__(self, material=None):
        self.__material = material

    @classmethod
    def from_material_id(cls, material_id):
        for material in bpy.data.materials:
            if material.mmd_material.material_id == material_id:
                return cls(material)
        return None

    @classmethod
    def swap_materials(cls, meshObj, mat1_ref, mat2_ref, reverse=False,
                       swap_slots=False):
        """
        This method will assign the polygons of mat1 to mat2.
        If reverse is True it will also swap the polygons assigned to mat2 to mat1.
        The reference to materials can be indexes or names
        Finally it will also swap the material slots if the option is given.
        """
        try:
            # Try to find the materials
            mat1 = meshObj.data.materials[mat1_ref]
            mat2 = meshObj.data.materials[mat2_ref]
            if None in (mat1, mat2):
                raise MaterialNotFoundError()
        except (KeyError, IndexError):
            # Wrap exceptions within our custom ones
            raise MaterialNotFoundError()
        mat1_idx = meshObj.data.materials.find(mat1.name)
        mat2_idx = meshObj.data.materials.find(mat2.name)
        if 1: #with select_object(meshObj):
            # Swap polygons
            for poly in meshObj.data.polygons:
                if poly.material_index == mat1_idx:
                    poly.material_index = mat2_idx
                elif reverse and poly.material_index == mat2_idx:
                    poly.material_index = mat1_idx
            # Swap slots if specified
            if swap_slots:
                meshObj.material_slots[mat1_idx].material = mat2
                meshObj.material_slots[mat2_idx].material = mat1
        return mat1, mat2

    @classmethod
    def fixMaterialOrder(cls, meshObj, material_names):
        """
        This method will fix the material order. Which is lost after joining meshes.
        """
        for new_idx, mat in enumerate(material_names):
            # Get the material that is currently on this index
            other_mat = meshObj.data.materials[new_idx]
            if other_mat.name == mat:
                continue  # This is already in place
            cls.swap_materials(meshObj, mat, new_idx, reverse=True, swap_slots=True)

    @property
    def material_id(self):
        mmd_mat = self.__material.mmd_material
        if mmd_mat.material_id < 0:
            max_id = -1
            for mat in bpy.data.materials:
                max_id = max(max_id, mat.mmd_material.material_id)
            mmd_mat.material_id = max_id + 1
        return mmd_mat.material_id

    @property
    def material(self):
        return self.__material


    def __same_image_file(self, image, filepath):
        if image and image.source == 'FILE' and image.use_alpha:
            img_filepath = bpy.path.abspath(image.filepath) # image.filepath_from_user()
            if img_filepath == filepath:
                return True
            try:
                return os.path.samefile(img_filepath, filepath)
            except:
                pass
        return False

    def __load_image(self, filepath):
        for i in bpy.data.images:
            if self.__same_image_file(i, filepath):
                return i

        try:
            return bpy.data.images.load(filepath)
        except:
            logging.warning('Cannot create a texture for %s. No such file.', filepath)

        img = bpy.data.images.new(os.path.basename(filepath), 1, 1)
        img.source = 'FILE'
        img.filepath = filepath
        return img

    def __load_texture(self, filepath):
        for t in bpy.data.textures:
            if t.type == 'IMAGE' and self.__same_image_file(t.image, filepath) and t.use_alpha:
                return t
        tex = bpy.data.textures.new(name=bpy.path.display_name_from_filepath(filepath), type='IMAGE')
        tex.image = self.__load_image(filepath)
        return tex

    def __has_alpha_channel(self, texture):
        return texture.type == 'IMAGE' and getattr(texture.image, 'depth', -1) == 32


    def get_texture(self):
        return self.__get_texture(self.__BASE_TEX_SLOT)

    def __get_texture(self, index):
        texture_slot = self.__material.texture_slots[index]
        return texture_slot.texture if texture_slot else None

    def __use_texture(self, index, use_tex):
        texture_slot = self.__material.texture_slots[index]
        if texture_slot:
            texture_slot.use = use_tex

    def create_texture(self, filepath):
        """ create a texture slot for textures of MMD models.

        Args:
            material: the material object to add a texture_slot
            filepath: the file path to texture.

        Returns:
            bpy.types.MaterialTextureSlot object
        """
        texture_slot = self.__material.texture_slots.create(self.__BASE_TEX_SLOT)
        texture_slot.texture_coords = 'UV'
        texture_slot.blend_type = 'MULTIPLY'
        texture_slot.texture = self.__load_texture(filepath)
        texture_slot.use_map_alpha = self.__has_alpha_channel(texture_slot.texture)
        return texture_slot

    def remove_texture(self):
        self.__remove_texture(self.__BASE_TEX_SLOT)

    def __remove_texture(self, index):
        texture_slot = self.__material.texture_slots[index]
        if texture_slot:
            tex = texture_slot.texture
            self.__material.texture_slots.clear(index)
            #print('clear texture: %s  users: %d'%(tex.name, tex.users))
            if tex and tex.users < 1 and tex.type == 'IMAGE':
                #print(' - remove texture: '+tex.name)
                img = tex.image
                tex.image = None
                bpy.data.textures.remove(tex)
                if img and img.users < 1:
                    #print('    - remove image: '+img.name)
                    bpy.data.images.remove(img)


    def get_sphere_texture(self):
        return self.__get_texture(self.__SPHERE_TEX_SLOT)

    def use_sphere_texture(self, use_sphere, obj=None):
        if use_sphere:
            self.update_sphere_texture_type(obj)
        else:
            self.__use_texture(self.__SPHERE_TEX_SLOT, use_sphere)
            self.__use_texture(self.__SPHERE_ALPHA_SLOT, use_sphere)

    def create_sphere_texture(self, filepath, obj=None):
        """ create a texture slot for environment mapping textures of MMD models.

        Args:
            material: the material object to add a texture_slot
            filepath: the file path to environment mapping texture.

        Returns:
            bpy.types.MaterialTextureSlot object
        """
        texture_slot = self.__material.texture_slots.create(self.__SPHERE_TEX_SLOT)
        texture_slot.texture_coords = 'NORMAL'
        texture_slot.texture = self.__load_texture(filepath)
        self.update_sphere_texture_type(obj)
        return texture_slot

    def update_sphere_texture_type(self, obj=None):
        texture_slot = self.__material.texture_slots[self.__SPHERE_TEX_SLOT]
        if not texture_slot:
            self.__remove_texture(self.__SPHERE_ALPHA_SLOT)
            return

        sphere_texture_type = int(self.__material.mmd_material.sphere_texture_type)
        if sphere_texture_type not in (1, 2, 3):
            texture_slot.use = False
        else:
            texture_slot.use = True
            texture_slot.blend_type = ('MULTIPLY', 'ADD', 'MULTIPLY')[sphere_texture_type-1]
            if sphere_texture_type == 3:
                texture_slot.texture_coords = 'UV'
                if obj and obj.type == 'MESH' and self.__material in tuple(obj.data.materials):
                    uv_layers = (l for l in obj.data.uv_layers if not l.name.startswith('_'))
                    next(uv_layers, None) # skip base UV
                    texture_slot.uv_layer = getattr(next(uv_layers, None), 'name', '')
            else:
                texture_slot.texture_coords = 'NORMAL'

        if not texture_slot.use or not self.__has_alpha_channel(texture_slot.texture):
            self.__remove_texture(self.__SPHERE_ALPHA_SLOT)
            return

        alpha_slot = self.__material.texture_slots[self.__SPHERE_ALPHA_SLOT]
        if not alpha_slot:
            alpha_slot = self.__material.texture_slots.create(self.__SPHERE_ALPHA_SLOT)
            alpha_slot.use_map_color_diffuse = False
            alpha_slot.use_map_alpha = True
            alpha_slot.blend_type = 'MULTIPLY'
            alpha_slot.texture = texture_slot.texture
            alpha_slot.alpha_factor = texture_slot.diffuse_color_factor
        alpha_slot.use = texture_slot.use
        alpha_slot.texture_coords = texture_slot.texture_coords
        alpha_slot.uv_layer = texture_slot.uv_layer

    def remove_sphere_texture(self):
        self.__remove_texture(self.__SPHERE_TEX_SLOT)
        self.__remove_texture(self.__SPHERE_ALPHA_SLOT)


    def get_toon_texture(self):
        return self.__get_texture(self.__TOON_TEX_SLOT)

    def use_toon_texture(self, use_toon):
        self.__use_texture(self.__TOON_TEX_SLOT, use_toon)

    def create_toon_texture(self, filepath):
        """ create a texture slot for toon textures of MMD models.

        Args:
            material: the material object to add a texture_slot
            filepath: the file path to toon texture.

        Returns:
            bpy.types.MaterialTextureSlot object
        """
        texture_slot = self.__material.texture_slots.create(self.__TOON_TEX_SLOT)
        texture_slot.texture_coords = 'NORMAL'
        texture_slot.blend_type = 'MULTIPLY'
        texture_slot.texture = self.__load_texture(filepath)
        texture_slot.use_map_alpha = self.__has_alpha_channel(texture_slot.texture)
        return texture_slot

    def update_toon_texture(self):
        mmd_mat = self.__material.mmd_material
        if mmd_mat.is_shared_toon_texture:
            shared_toon_folder = addon_preferences('shared_toon_folder', '')
            toon_path = os.path.join(shared_toon_folder, 'toon%02d.bmp'%(mmd_mat.shared_toon_texture+1))
            self.create_toon_texture(bpy.path.resolve_ncase(path=toon_path))
        elif mmd_mat.toon_texture != '':
            self.create_toon_texture(mmd_mat.toon_texture)
        else:
            self.remove_toon_texture()

    def remove_toon_texture(self):
        self.__remove_texture(self.__TOON_TEX_SLOT)


    def _mixDiffuseAndAmbient(self, mmd_mat):
        r, g, b = mmd_mat.diffuse_color
        ar, ag, ab = mmd_mat.ambient_color
        return [min(1.0,0.5*r+ar), min(1.0,0.5*g+ag), min(1.0,0.5*b+ab)]

    def update_ambient_color(self):
        self.update_diffuse_color()

    def update_diffuse_color(self):
        mat = self.__material
        mmd_mat = mat.mmd_material
        mat.diffuse_color = self._mixDiffuseAndAmbient(mmd_mat)
        mat.diffuse_intensity = 0.8

    def update_alpha(self):
        mat = self.__material
        mmd_mat = mat.mmd_material
        mat.alpha = mmd_mat.alpha
        mat.specular_alpha = mmd_mat.alpha
        mat.use_transparency = True
        mat.transparency_method = 'Z_TRANSPARENCY'
        mat.game_settings.alpha_blend = 'ALPHA'
        self.update_self_shadow_map()

    def update_specular_color(self):
        mat = self.__material
        mmd_mat = mat.mmd_material
        mat.specular_color = mmd_mat.specular_color
        mat.specular_shader = 'PHONG'
        mat.specular_intensity = 0.8

    def update_shininess(self):
        mat = self.__material
        mmd_mat = mat.mmd_material
        shininess = mmd_mat.shininess
        mat.specular_hardness = shininess

    def update_is_double_sided(self):
        mat = self.__material
        mmd_mat = mat.mmd_material
        mat.game_settings.use_backface_culling = not mmd_mat.is_double_sided

    def update_drop_shadow(self):
        pass

    def update_self_shadow_map(self):
        mat = self.__material
        mmd_mat = mat.mmd_material
        cast_shadows = mmd_mat.enabled_self_shadow_map if mat.alpha > 1e-3 else False
        mat.use_cast_buffer_shadows = cast_shadows # only buffer shadows
        if hasattr(mat, 'use_cast_shadows'):
            # "use_cast_shadows" is not supported in older Blender (< 2.71),
            # so we still use "use_cast_buffer_shadows".
            mat.use_cast_shadows = cast_shadows

    def update_self_shadow(self):
        mat = self.__material
        mmd_mat = mat.mmd_material
        mat.use_shadows = mmd_mat.enabled_self_shadow
        mat.use_transparent_shadows = mmd_mat.enabled_self_shadow

    def update_enabled_toon_edge(self):
        mat = self.__material
        if not hasattr(mat, 'line_color'): # freestyle line color
            return
        mmd_mat = mat.mmd_material
        mat.line_color[3] = min(int(mmd_mat.enabled_toon_edge), mmd_mat.edge_color[3])

    def update_edge_color(self):
        mat = self.__material
        if not hasattr(mat, 'line_color'): # freestyle line color
            return
        mmd_mat = mat.mmd_material
        r, g, b, a = mmd_mat.edge_color
        mat.line_color = [r, g, b, min(int(mmd_mat.enabled_toon_edge), a)]

    def update_edge_weight(self):
        pass


if bpy.app.version >= (2, 80, 0):
    from bpy_extras import image_utils
    from bpy_extras.node_shader_utils import PrincipledBSDFWrapper

    class _DummyTexture:
        def __init__(self, image):
            self.type = 'IMAGE'
            self.image = image
            self.use_mipmap = True

    class _DummyTextureSlot:
        def __init__(self, image):
            self.diffuse_color_factor = 1
            self.uv_layer = ''
            self.texture = _DummyTexture(image)

    __FnMaterialBase = FnMaterial
    class FnMaterial(__FnMaterialBase):
        @property
        def __shader_wrap(self):
            if not hasattr(self, '_shader_wrapper'):
                self._shader_wrapper = PrincipledBSDFWrapper(self.material, is_readonly=True)
            return self._shader_wrapper

        @property
        def __shader_read(self):
            shader = self.__shader_wrap
            shader.is_readonly = True
            return shader

        @property
        def __shader(self):
            shader = self.__shader_wrap
            shader.is_readonly = False
            shader.use_nodes = True
            return shader

        def get_texture(self):
            texture = self.__shader_read.base_color_texture
            if texture and texture.image:
                return _DummyTexture(texture.image)
            return None

        def create_texture(self, filepath):
            image = image_utils.load_image(filepath, place_holder=True,)
            shader = self.__shader
            shader.base_color_texture.image = image
            return _DummyTextureSlot(image)

        def remove_texture(self):
            shader = self.__shader
            shader.base_color_texture.image = None


        def get_sphere_texture(self):
            texture = self.__shader_read.metallic_texture
            if texture and texture.image:
                return _DummyTexture(texture.image)
            return None

        def use_sphere_texture(self, use_sphere, obj=None):
            pass

        def create_sphere_texture(self, filepath, obj=None):
            image = image_utils.load_image(filepath, place_holder=True,)
            shader = self.__shader
            shader.metallic_texture.image = image
            shader.metallic_texture.texcoords = 'Normal'
            shader.metallic_texture.node_mapping.vector_type = 'POINT'
            shader.metallic_texture.node_mapping.translation = (0.5, 0.5, 0.0)
            shader.metallic_texture.node_mapping.scale = (0.5, 0.5, 1.0)
            return _DummyTextureSlot(image)

        def update_sphere_texture_type(self, obj=None):
            pass

        def remove_sphere_texture(self):
            shader = self.__shader
            shader.metallic_texture.image = None


        def get_toon_texture(self):
            return None

        def use_toon_texture(self, use_toon):
            pass

        def create_toon_texture(self, filepath):
            image = image_utils.load_image(filepath, place_holder=True,)
            return _DummyTextureSlot(image)

        def remove_toon_texture(self):
            pass


        def update_diffuse_color(self):
            mat = self.__material
            mmd_mat = mat.mmd_material
            shader = self.__shader
            shader.base_color = self._mixDiffuseAndAmbient(mmd_mat)

        def update_alpha(self):
            mat = self.__material
            mmd_mat = mat.mmd_material
            shader = self.__shader
            shader.transmission = 1 - mmd_mat.alpha
            shader.ior = 1
            mat.blend_method = 'BLEND'

        def update_specular_color(self):
            mat = self.__material
            mmd_mat = mat.mmd_material
            mat.specular_color = mmd_mat.specular_color
            shader = self.__shader
            shader.specular = mmd_mat.specular_color.v

        def update_shininess(self):
            mat = self.__material
            mmd_mat = mat.mmd_material
            shader = self.__shader
            shader.roughness = 1/max(mmd_mat.shininess, 1)

        def update_is_double_sided(self):
            mat = self.__material
            mmd_mat = mat.mmd_material

        def update_self_shadow_map(self):
            pass

        def update_self_shadow(self):
            mat = self.__material
            mmd_mat = mat.mmd_material

