# -*- coding: utf-8 -*-
import os
import copy
import logging
import shutil
import time

import mathutils
import bpy
import bmesh

from collections import OrderedDict
from mmd_tools_local.core import pmx
from mmd_tools_local.core.bone import FnBone
from mmd_tools_local.core.material import FnMaterial
from mmd_tools_local.core.morph import FnMorph
from mmd_tools_local.core.sdef import FnSDEF
from mmd_tools_local.core.vmd.importer import BoneConverter, BoneConverterPoseMode
from mmd_tools_local import bpyutils
from mmd_tools_local.utils import saferelpath
from mmd_tools_local.bpyutils import matmul
from mmd_tools_local.operators.misc import MoveObject


class _Vertex:
    def __init__(self, co, groups, offsets, edge_scale, vertex_order, uv_offsets):
        self.co = co
        self.groups = groups # [(group_number, weight), ...]
        self.offsets = offsets
        self.edge_scale = edge_scale
        self.vertex_order = vertex_order # used for controlling vertex order
        self.uv_offsets = uv_offsets
        self.index = None
        self.uv = None
        self.normal = None
        self.sdef_data = [] # (C, R0, R1)
        self.add_uvs = [None]*4 # UV1~UV4

class _Face:
    def __init__(self, vertices):
        ''' Temporary Face Class
        '''
        self.vertices = vertices

class _Mesh:
    def __init__(self, material_faces, shape_key_names, material_names):
        self.material_faces = material_faces # dict of {material_index => [face1, face2, ....]}
        self.shape_key_names = shape_key_names
        self.material_names = material_names


class _DefaultMaterial:
    def __init__(self):
        mat = bpy.data.materials.new('')
        #mat.mmd_material.diffuse_color = (0, 0, 0)
        #mat.mmd_material.specular_color = (0, 0, 0)
        #mat.mmd_material.ambient_color = (0, 0, 0)
        self.material = mat
        logging.debug('create default material: %s', str(self.material))

    def __del__(self):
        if self.material:
            logging.debug('remove default material: %s', str(self.material))
            bpy.data.materials.remove(self.material)


class __PmxExporter:
    CATEGORIES = {
        'SYSTEM': pmx.Morph.CATEGORY_SYSTEM,
        'EYEBROW': pmx.Morph.CATEGORY_EYEBROW,
        'EYE': pmx.Morph.CATEGORY_EYE,
        'MOUTH': pmx.Morph.CATEGORY_MOUTH,
        }

    def __init__(self):
        self.__model = None
        self.__bone_name_table = []
        self.__material_name_table = []
        self.__exported_vertices = []
        self.__default_material = None
        self.__vertex_order_map = None # used for controlling vertex order
        self.__disable_specular = False
        self.__add_uv_count = 0

    @staticmethod
    def flipUV_V(uv):
        u, v = uv
        return u, 1.0-v

    def __getDefaultMaterial(self):
        if self.__default_material is None:
            self.__default_material = _DefaultMaterial()
        return self.__default_material.material

    def __sortVertices(self):
        logging.info(' - Sorting vertices ...')
        weight_items = self.__vertex_order_map.items()
        sorted_indices = [i[0] for i in sorted(weight_items, key=lambda x: x[1].vertex_order)]
        vertices = self.__model.vertices
        self.__model.vertices = [vertices[i] for i in sorted_indices]

        # update indices
        index_map = {x:i for i, x in enumerate(sorted_indices)}
        for v in self.__vertex_order_map.values():
            v.index = index_map[v.index]
        for f in self.__model.faces:
            f[:] = [index_map[i] for i in f]
        logging.debug('   - Done (count:%d)', len(self.__vertex_order_map))

    def __exportMeshes(self, meshes, bone_map):
        mat_map = OrderedDict()
        for mesh in meshes:
            for index, mat_faces in sorted(mesh.material_faces.items(), key=lambda x: x[0]):
                name = mesh.material_names[index]
                if name not in mat_map:
                    mat_map[name] = []
                mat_map[name].append(mat_faces)

        sort_vertices = self.__vertex_order_map is not None
        if sort_vertices:
            self.__vertex_order_map.clear()

        # export vertices
        for mat_name, mat_meshes in mat_map.items():
            face_count = 0
            for mat_faces in mat_meshes:
                mesh_vertices = []
                for face in mat_faces:
                    mesh_vertices.extend(face.vertices)

                for v in mesh_vertices:
                    if v.index is not None:
                        continue

                    v.index = len(self.__model.vertices)
                    if sort_vertices:
                        self.__vertex_order_map[v.index] = v

                    pv = pmx.Vertex()
                    pv.co = v.co
                    pv.normal = v.normal
                    pv.uv = self.flipUV_V(v.uv)
                    pv.edge_scale = v.edge_scale
                    for _uvzw in v.add_uvs:
                        if _uvzw:
                            pv.additional_uvs.append(self.flipUV_V(_uvzw[0])+self.flipUV_V(_uvzw[1]))

                    t = len(v.groups)
                    if t == 0:
                        weight = pmx.BoneWeight()
                        weight.type = pmx.BoneWeight.BDEF1
                        weight.bones = [0]
                        pv.weight = weight
                    elif t == 1:
                        weight = pmx.BoneWeight()
                        weight.type = pmx.BoneWeight.BDEF1
                        weight.bones = [v.groups[0][0]]
                        pv.weight = weight
                    elif t == 2:
                        vg1, vg2 = v.groups
                        weight = pmx.BoneWeight()
                        weight.type = pmx.BoneWeight.BDEF2
                        weight.bones = [vg1[0], vg2[0]]
                        w1, w2 = vg1[1], vg2[1]
                        weight.weights = [w1/(w1+w2)]
                        if v.sdef_data:
                            weight.type = pmx.BoneWeight.SDEF
                            sdef_weights = pmx.BoneWeightSDEF()
                            sdef_weights.weight = weight.weights[0]
                            sdef_weights.c, sdef_weights.r0, sdef_weights.r1 = v.sdef_data
                            if weight.bones[0] > weight.bones[1]:
                                weight.bones.reverse()
                                sdef_weights.weight = 1.0 - sdef_weights.weight
                            weight.weights = sdef_weights
                        pv.weight = weight
                    else:
                        weight = pmx.BoneWeight()
                        weight.type = pmx.BoneWeight.BDEF4
                        weight.bones = [0, 0, 0, 0]
                        weight.weights = [0.0, 0.0, 0.0, 0.0]
                        w_all = 0.0
                        if t > 4:
                            v.groups.sort(key=lambda x: -x[1])
                        for i in range(min(t, 4)):
                            gn, w = v.groups[i]
                            weight.bones[i] = gn
                            weight.weights[i] = w
                            w_all += w
                        for i in range(4):
                            weight.weights[i] /= w_all
                        pv.weight = weight
                    self.__model.vertices.append(pv)
                    self.__exported_vertices.append(v)

                for face in mat_faces:
                    self.__model.faces.append([x.index for x in face.vertices])
                face_count += len(mat_faces)
            self.__exportMaterial(bpy.data.materials[mat_name], face_count)

        if sort_vertices:
            self.__sortVertices()

    def __exportTexture(self, filepath):
        if filepath.strip() == '':
            return -1
        # Use bpy.path to resolve '//' in .blend relative filepaths
        filepath = bpy.path.abspath(filepath)
        filepath = os.path.abspath(filepath)
        for i, tex in enumerate(self.__model.textures):
            if os.path.normcase(tex.path) == os.path.normcase(filepath):
                return i
        t = pmx.Texture()
        t.path = filepath
        self.__model.textures.append(t)
        if not os.path.isfile(t.path):
            logging.warning('  The texture file does not exist: %s', t.path)
        return len(self.__model.textures) - 1

    def __copy_textures(self, output_dir, base_folder=''):
        tex_dir_fallback = os.path.join(output_dir, 'textures')
        tex_dir_preference = bpyutils.addon_preferences('base_texture_folder', '')

        path_set = set() # to prevent overwriting
        tex_copy_list = []
        for texture in self.__model.textures:
            path = texture.path
            tex_dir = output_dir  # restart to the default directory at each loop
            if not os.path.isfile(path):
                logging.warning('*** skipping texture file which does not exist: %s', path)
                path_set.add(os.path.normcase(path))
                continue
            dst_name = os.path.basename(path)
            if base_folder:
                dst_name = saferelpath(path, base_folder, strategy='outside')
                if dst_name.startswith('..'):
                    # Check if the texture comes from the preferred folder
                    if tex_dir_preference:
                        dst_name = saferelpath(path, tex_dir_preference, strategy='outside')
                    if dst_name.startswith('..'):
                        # If the code reaches here the texture is somewhere else
                        logging.warning('The texture %s is not inside the base texture folder', path)
                        # Fall back to basename and textures folder
                        dst_name = os.path.basename(path)
                        tex_dir = tex_dir_fallback
            else:
                tex_dir = tex_dir_fallback
            dest_path = os.path.join(tex_dir, dst_name)
            if os.path.normcase(path) != os.path.normcase(dest_path): # Only copy if the paths are different
                tex_copy_list.append((texture, path, dest_path))
            else:
                path_set.add(os.path.normcase(path))

        for texture, path, dest_path in tex_copy_list:
            counter = 1
            base, ext = os.path.splitext(dest_path)
            while os.path.normcase(dest_path) in path_set:
                dest_path = '%s_%d%s'%(base, counter, ext)
                counter += 1
            path_set.add(os.path.normcase(dest_path))
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copyfile(path, dest_path)
            logging.info('Copy file %s --> %s', path, dest_path)
            texture.path = dest_path

    def __exportMaterial(self, material, num_faces):
        p_mat = pmx.Material()
        mmd_mat = material.mmd_material

        p_mat.name = mmd_mat.name_j or material.name
        p_mat.name_e = mmd_mat.name_e
        p_mat.diffuse = list(mmd_mat.diffuse_color) + [mmd_mat.alpha]
        p_mat.ambient = mmd_mat.ambient_color
        p_mat.specular = mmd_mat.specular_color
        p_mat.shininess = mmd_mat.shininess
        p_mat.is_double_sided = mmd_mat.is_double_sided
        p_mat.enabled_drop_shadow = mmd_mat.enabled_drop_shadow
        p_mat.enabled_self_shadow_map = mmd_mat.enabled_self_shadow_map
        p_mat.enabled_self_shadow = mmd_mat.enabled_self_shadow
        p_mat.enabled_toon_edge = mmd_mat.enabled_toon_edge
        p_mat.edge_color = mmd_mat.edge_color
        p_mat.edge_size = mmd_mat.edge_weight
        p_mat.sphere_texture_mode = int(mmd_mat.sphere_texture_type)
        if self.__disable_specular:
            p_mat.sphere_texture_mode = pmx.Material.SPHERE_MODE_OFF
        p_mat.comment = mmd_mat.comment

        p_mat.vertex_count = num_faces * 3
        fnMat = FnMaterial(material)
        tex = fnMat.get_texture()
        if tex and tex.type == 'IMAGE' and tex.image:  # Ensure the texture is an image
            index = self.__exportTexture(tex.image.filepath)
            p_mat.texture = index
        tex = fnMat.get_sphere_texture()
        if tex and tex.type == 'IMAGE' and tex.image:  # Ensure the texture is an image
            index = self.__exportTexture(tex.image.filepath)
            p_mat.sphere_texture = index

        if mmd_mat.is_shared_toon_texture:
            p_mat.toon_texture = mmd_mat.shared_toon_texture
            p_mat.is_shared_toon_texture = True
        else:
            p_mat.toon_texture =  self.__exportTexture(mmd_mat.toon_texture)
            p_mat.is_shared_toon_texture = False

        self.__material_name_table.append(material.name)
        self.__model.materials.append(p_mat)

    @classmethod
    def __countBoneDepth(cls, bone):
        if bone.parent is None:
            return 0
        else:
            return cls.__countBoneDepth(bone.parent) + 1

    def __exportBones(self, meshes):
        """ Export bones.
        Returns:
            A dictionary to map Blender bone names to bone indices of the pmx.model instance.
        """
        arm = self.__armature
        if hasattr(arm, 'evaluated_get'):
            bpy.context.view_layer.update()
            arm = arm.evaluated_get(bpy.context.evaluated_depsgraph_get())
        boneMap = {}
        pmx_bones = []
        pose_bones = arm.pose.bones
        world_mat = arm.matrix_world
        r = {}

        # determine the bone order
        vtx_grps = {}
        for mesh in meshes:
            if mesh.modifiers.get('mmd_bone_order_override', None):
                vtx_grps = mesh.vertex_groups
                break

        class _Dummy:
            index = float('inf')
        sorted_bones = sorted(pose_bones, key=lambda x: vtx_grps.get(x.name, _Dummy).index)
        #sorted_bones = sorted(pose_bones, key=self.__countBoneDepth)

        Vector = mathutils.Vector
        pmx_matrix = world_mat * self.__scale
        pmx_matrix[1], pmx_matrix[2] = pmx_matrix[2].copy(), pmx_matrix[1].copy()
        def __to_pmx_location(loc):
            return matmul(pmx_matrix, Vector(loc))

        pmx_matrix_rot = pmx_matrix.to_3x3()
        def __to_pmx_axis(axis, pose_bone):
            m = matmul(pose_bone.matrix, pose_bone.bone.matrix_local.inverted()).to_3x3()
            return matmul(matmul(pmx_matrix_rot, m), Vector(axis).xzy).normalized()

        if True: # no need to enter edit mode
            for p_bone in sorted_bones:
                if p_bone.is_mmd_shadow_bone:
                    continue
                bone = p_bone.bone
                mmd_bone = p_bone.mmd_bone
                pmx_bone = pmx.Bone()
                pmx_bone.name = mmd_bone.name_j or bone.name
                pmx_bone.name_e = mmd_bone.name_e

                pmx_bone.hasAdditionalRotate = mmd_bone.has_additional_rotation
                pmx_bone.hasAdditionalLocation = mmd_bone.has_additional_location
                pmx_bone.additionalTransform = [mmd_bone.additional_transform_bone, mmd_bone.additional_transform_influence]

                pmx_bone.location = __to_pmx_location(p_bone.head)
                pmx_bone.parent = bone.parent
                pmx_bone.visible = not bone.hide and any((all(x) for x in zip(bone.layers, arm.data.layers)))
                pmx_bone.isControllable = mmd_bone.is_controllable
                pmx_bone.isMovable = not all(p_bone.lock_location)
                pmx_bone.isRotatable = not all(p_bone.lock_rotation)
                pmx_bone.transform_order = mmd_bone.transform_order
                pmx_bone.transAfterPhis = mmd_bone.transform_after_dynamics
                pmx_bones.append(pmx_bone)
                self.__bone_name_table.append(p_bone.name)
                boneMap[bone] = pmx_bone
                r[bone.name] = len(pmx_bones) - 1

                if bone.use_connect and p_bone.parent.mmd_bone.is_tip:
                    logging.debug(' * fix location of bone %s, parent %s is tip', bone.name, bone.parent.name)
                    pmx_bone.location = boneMap[bone.parent].location

                # a connected child bone is preferred
                pmx_bone.displayConnection = None
                for child in bone.children:
                    if child.use_connect:
                        pmx_bone.displayConnection = child
                        break
                if not pmx_bone.displayConnection:
                    if mmd_bone.is_tip:
                        pmx_bone.displayConnection = -1
                    else:
                        tail_loc = __to_pmx_location(p_bone.tail)
                        pmx_bone.displayConnection = tail_loc - pmx_bone.location

                if mmd_bone.enabled_fixed_axis:
                    pmx_bone.axis = __to_pmx_axis(mmd_bone.fixed_axis, p_bone)

                if mmd_bone.enabled_local_axes:
                    pmx_bone.localCoordinate = pmx.Coordinate(
                        __to_pmx_axis(mmd_bone.local_axis_x, p_bone),
                        __to_pmx_axis(mmd_bone.local_axis_z, p_bone))

            for idx, i in enumerate(pmx_bones):
                if i.parent is not None:
                    i.parent = pmx_bones.index(boneMap[i.parent])
                    logging.debug('the parent of %s:%s: %s', idx, i.name, i.parent)
                if isinstance(i.displayConnection, pmx.Bone):
                    i.displayConnection = pmx_bones.index(i.displayConnection)
                elif isinstance(i.displayConnection, bpy.types.Bone):
                    i.displayConnection = pmx_bones.index(boneMap[i.displayConnection])
                i.additionalTransform[0] = r.get(i.additionalTransform[0], -1)

            if len(pmx_bones) == 0:
                # avoid crashing MMD
                pmx_bone = pmx.Bone()
                pmx_bone.name = u'全ての親'
                pmx_bone.name_e = 'Root'
                pmx_bone.location = __to_pmx_location([0,0,0])
                tail_loc = __to_pmx_location([0,0,1])
                pmx_bone.displayConnection = tail_loc - pmx_bone.location
                pmx_bones.append(pmx_bone)

            self.__model.bones = pmx_bones
        self.__exportIK(r)
        return r

    def __exportIKLinks(self, pose_bone, count, bone_map, ik_links, custom_bone):
        if count <= 0 or pose_bone is None or pose_bone.name not in bone_map:
            return ik_links

        logging.debug('    Create IK Link for %s', pose_bone.name)
        ik_link = pmx.IKLink()
        ik_link.target = bone_map[pose_bone.name]

        from math import pi
        minimum, maximum = [-pi]*3, [pi]*3
        unused_counts = 0
        ik_limit_custom = next((c for c in custom_bone.constraints if c.type == 'LIMIT_ROTATION' and c.name == 'mmd_ik_limit_custom%d'%len(ik_links)), None)
        ik_limit_override = next((c for c in pose_bone.constraints if c.type == 'LIMIT_ROTATION' and not c.mute), None)
        for i, axis in enumerate('xyz'):
            if ik_limit_custom: # custom ik limits for MMD only
                if getattr(ik_limit_custom, 'use_limit_'+axis):
                    minimum[i] = getattr(ik_limit_custom, 'min_'+axis)
                    maximum[i] = getattr(ik_limit_custom, 'max_'+axis)
                else:
                    unused_counts += 1
                continue

            if getattr(pose_bone, 'lock_ik_'+axis):
                minimum[i] = maximum[i] = 0
            elif ik_limit_override is not None and getattr(ik_limit_override, 'use_limit_'+axis):
                minimum[i] = getattr(ik_limit_override, 'min_'+axis)
                maximum[i] = getattr(ik_limit_override, 'max_'+axis)
            elif getattr(pose_bone, 'use_ik_limit_'+axis):
                minimum[i] = getattr(pose_bone, 'ik_min_'+axis)
                maximum[i] = getattr(pose_bone, 'ik_max_'+axis)
            else:
                unused_counts += 1

        if unused_counts < 3:
            convertIKLimitAngles = pmx.importer.PMXImporter.convertIKLimitAngles
            bone_matrix = matmul(pose_bone.id_data.matrix_world, pose_bone.matrix)
            minimum, maximum = convertIKLimitAngles(minimum, maximum, bone_matrix, invert=True)
            ik_link.minimumAngle = list(minimum)
            ik_link.maximumAngle = list(maximum)

        return self.__exportIKLinks(pose_bone.parent, count - 1, bone_map, ik_links + [ik_link], custom_bone)


    def __exportIK(self, bone_map):
        """ Export IK constraints
         @param bone_map the dictionary to map Blender bone names to bone indices of the pmx.model instance.
        """
        pmx_bones = self.__model.bones
        arm = self.__armature
        ik_loop_factor = max(arm.get('mmd_ik_loop_factor', 1), 1)
        pose_bones = arm.pose.bones

        ik_target_custom_map = {getattr(b.constraints.get('mmd_ik_target_custom', None), 'subtarget', None):b for b in pose_bones if not b.is_mmd_shadow_bone}
        def __ik_target_bone_get(ik_constraint_bone, ik_bone):
            if ik_bone.name in ik_target_custom_map:
                logging.debug('  (use "mmd_ik_target_custom")')
                return ik_target_custom_map[ik_bone.name] # for supporting the ik target which is not a child of ik_constraint_bone
            return self.__get_ik_target_bone(ik_constraint_bone) # this only search the children of ik_constraint_bone

        for bone in pose_bones:
            if bone.is_mmd_shadow_bone:
                continue
            for c in bone.constraints:
                if c.type == 'IK' and not c.mute:
                    logging.debug('  Found IK constraint on %s', bone.name)
                    ik_pose_bone = self.__get_ik_control_bone(c)
                    if ik_pose_bone is None:
                        logging.warning('  * Invalid IK constraint "%s" on bone %s', c.name, bone.name)
                        continue

                    ik_bone_index = bone_map.get(ik_pose_bone.name, -1)
                    if ik_bone_index < 0:
                        logging.warning('  * IK bone "%s" not found !!!', ik_pose_bone.name)
                        continue

                    pmx_ik_bone = pmx_bones[ik_bone_index]
                    if pmx_ik_bone.isIK:
                        logging.warning('  * IK bone "%s" is used by another IK setting !!!', ik_pose_bone.name)
                        continue

                    ik_chain0 = bone if c.use_tail else bone.parent
                    ik_target_bone = __ik_target_bone_get(bone, ik_pose_bone) if c.use_tail else bone
                    if ik_target_bone is None:
                        logging.warning('  * IK bone: %s, IK Target not found !!!', ik_pose_bone.name)
                        continue
                    logging.debug('  - IK bone: %s, IK Target: %s', ik_pose_bone.name, ik_target_bone.name)
                    pmx_ik_bone.isIK = True
                    pmx_ik_bone.loopCount = max(int(c.iterations/ik_loop_factor), 1)
                    if ik_pose_bone.name in ik_target_custom_map:
                        pmx_ik_bone.rotationConstraint = ik_pose_bone.mmd_bone.ik_rotation_constraint
                    else:
                        pmx_ik_bone.rotationConstraint = bone.mmd_bone.ik_rotation_constraint
                    pmx_ik_bone.target = bone_map[ik_target_bone.name]
                    pmx_ik_bone.ik_links = self.__exportIKLinks(ik_chain0, c.chain_count, bone_map, [], ik_pose_bone)

    def __get_ik_control_bone(self, ik_constraint):
        arm = ik_constraint.target
        if arm != ik_constraint.id_data:
            return None
        bone = arm.pose.bones.get(ik_constraint.subtarget, None)
        if bone is None:
            return None
        if bone.mmd_shadow_bone_type == 'IK_TARGET':
            logging.debug('  Found IK proxy bone: %s -> %s', bone.name, getattr(bone.parent, 'name', None))
            return bone.parent
        return bone

    def __get_ik_target_bone(self, target_bone):
        """ Get mmd ik target bone.

         Args:
             target_bone: A blender PoseBone

         Returns:
             A bpy.types.PoseBone object which is the closest bone from the tail position of target_bone.
             Return None if target_bone has no child bones.
        """
        valid_children = [c for c in target_bone.children if not c.is_mmd_shadow_bone]

        # search 'mmd_ik_target_override' first
        for c in valid_children:
            ik_target_override = c.constraints.get('mmd_ik_target_override', None)
            if ik_target_override and ik_target_override.subtarget == target_bone.name:
                logging.debug('  (use "mmd_ik_target_override")')
                return c

        r = None
        min_length = None
        for c in valid_children:
            if c.bone.use_connect:
                return c
            length = (c.head - target_bone.tail).length
            if min_length is None or length < min_length:
                min_length = length
                r = c
        return r

    def __exportVertexMorphs(self, meshes, root):
        shape_key_names = []
        for mesh in meshes:
            for i in mesh.shape_key_names:
                if i not in shape_key_names:
                    shape_key_names.append(i)

        morph_categories = {}
        morph_english_names = {}
        if root:
            categories = self.CATEGORIES
            for vtx_morph in root.mmd_root.vertex_morphs:
                morph_english_names[vtx_morph.name] = vtx_morph.name_e
                morph_categories[vtx_morph.name] = categories.get(vtx_morph.category, pmx.Morph.CATEGORY_OHTER)
            shape_key_names.sort(key=lambda x: root.mmd_root.vertex_morphs.find(x))

        for i in shape_key_names:
            morph = pmx.VertexMorph(
                name=i,
                name_e=morph_english_names.get(i, ''),
                category=morph_categories.get(i, pmx.Morph.CATEGORY_OHTER)
            )
            self.__model.morphs.append(morph)

        append_table = dict(zip(shape_key_names, [m.offsets.append for m in self.__model.morphs]))
        for v in self.__exported_vertices:
            for i, offset in v.offsets.items():
                mo = pmx.VertexMorphOffset()
                mo.index = v.index
                mo.offset = offset
                append_table[i](mo)

    def __export_material_morphs(self, root):
        mmd_root = root.mmd_root
        categories = self.CATEGORIES
        for morph in mmd_root.material_morphs:
            mat_morph = pmx.MaterialMorph(
                name=morph.name,
                name_e=morph.name_e,
                category=categories.get(morph.category, pmx.Morph.CATEGORY_OHTER)
            )
            for data in morph.data:
                morph_data = pmx.MaterialMorphOffset()
                try:
                    if data.material != '':
                        morph_data.index = self.__material_name_table.index(data.material)
                    else:
                        morph_data.index = -1
                except ValueError:
                    logging.warning('Material Morph (%s): Material "%s" was not found.', morph.name, data.material)
                    continue
                morph_data.offset_type = ['MULT', 'ADD'].index(data.offset_type)
                morph_data.diffuse_offset = data.diffuse_color
                morph_data.specular_offset = data.specular_color
                morph_data.shininess_offset = data.shininess
                morph_data.ambient_offset = data.ambient_color
                morph_data.edge_color_offset = data.edge_color
                morph_data.edge_size_offset = data.edge_weight
                morph_data.texture_factor = data.texture_factor
                morph_data.sphere_texture_factor = data.sphere_texture_factor
                morph_data.toon_texture_factor = data.toon_texture_factor
                mat_morph.offsets.append(morph_data)
            self.__model.morphs.append(mat_morph)

    def __sortMaterials(self):
        """ sort materials for alpha blending

         モデル内全頂点の平均座標をモデルの中心と考えて、
         モデル中心座標とマテリアルがアサインされている全ての面の構成頂点との平均距離を算出。
         この値が小さい順にソートしてみる。
         モデル中心座標から離れている位置で使用されているマテリアルほどリストの後ろ側にくるように。
         かなりいいかげんな実装
        """
        center = mathutils.Vector([0, 0, 0])
        vertices = self.__model.vertices
        vert_num = len(vertices)
        for v in self.__model.vertices:
            center += mathutils.Vector(v.co) / vert_num

        faces = self.__model.faces
        offset = 0
        distances = []
        for mat, bl_mat_name in zip(self.__model.materials, self.__material_name_table):
            d = 0
            face_num = int(mat.vertex_count / 3)
            for i in range(offset, offset + face_num):
                face = faces[i]
                d += (mathutils.Vector(vertices[face[0]].co) - center).length
                d += (mathutils.Vector(vertices[face[1]].co) - center).length
                d += (mathutils.Vector(vertices[face[2]].co) - center).length
            distances.append((d/mat.vertex_count, mat, offset, face_num, bl_mat_name))
            offset += face_num
        sorted_faces = []
        sorted_mat = []
        self.__material_name_table.clear()
        for d, mat, offset, vert_count, bl_mat_name in sorted(distances, key=lambda x: x[0]):
            sorted_faces.extend(faces[offset:offset+vert_count])
            sorted_mat.append(mat)
            self.__material_name_table.append(bl_mat_name)
        self.__model.materials = sorted_mat
        self.__model.faces = sorted_faces

    def __export_bone_morphs(self, root):
        mmd_root = root.mmd_root
        if len(mmd_root.bone_morphs) == 0:
            return
        categories = self.CATEGORIES
        pose_bones = self.__armature.pose.bones
        use_pose_mode = mmd_root.is_built and self.__armature.data.pose_position != 'REST'
        bone_util_cls = BoneConverterPoseMode if use_pose_mode else BoneConverter
        for morph in mmd_root.bone_morphs:
            bone_morph = pmx.BoneMorph(
                name=morph.name,
                name_e=morph.name_e,
                category=categories.get(morph.category, pmx.Morph.CATEGORY_OHTER)
            )
            for data in morph.data:
                morph_data = pmx.BoneMorphOffset()
                try:
                    morph_data.index = self.__bone_name_table.index(data.bone)
                except ValueError:
                    continue
                blender_bone = pose_bones.get(data.bone, None)
                if blender_bone is None:
                    logging.warning('Bone Morph (%s): Bone "%s" was not found.', morph.name, data.bone)
                    continue
                converter = bone_util_cls(blender_bone, self.__scale, invert=True)
                morph_data.location_offset = converter.convert_location(data.location)
                rw, rx, ry, rz = data.rotation
                rw, rx, ry, rz = converter.convert_rotation([rx, ry, rz, rw])
                morph_data.rotation_offset = (rx, ry, rz, rw)
                bone_morph.offsets.append(morph_data)
            self.__model.morphs.append(bone_morph)

    def __export_uv_morphs(self, root):
        mmd_root = root.mmd_root
        if len(mmd_root.uv_morphs) == 0:
            return
        categories = self.CATEGORIES
        append_table_vg = {}
        for morph in mmd_root.uv_morphs:
            uv_morph = pmx.UVMorph(
                name=morph.name,
                name_e=morph.name_e,
                category=categories.get(morph.category, pmx.Morph.CATEGORY_OHTER)
            )
            uv_morph.uv_index = morph.uv_index
            self.__model.morphs.append(uv_morph)
            if morph.data_type == 'VERTEX_GROUP':
                append_table_vg[morph.name] = uv_morph.offsets.append
                continue
            logging.warning(' * Deprecated UV morph "%s", please convert it to vertex groups', morph.name)

        if append_table_vg:
            incompleted = set()
            uv_morphs = mmd_root.uv_morphs
            for v in self.__exported_vertices:
                for name, offset in v.uv_offsets.items():
                    if name not in append_table_vg:
                        incompleted.add(name)
                        continue
                    scale = uv_morphs[name].vertex_group_scale
                    morph_data = pmx.UVMorphOffset()
                    morph_data.index = v.index
                    morph_data.offset = (offset[0]*scale, -offset[1]*scale, offset[2]*scale, -offset[3]*scale)
                    append_table_vg[name](morph_data)

            if incompleted:
                logging.warning(' * Incompleted UV morphs %s with vertex groups', incompleted)

    def __export_group_morphs(self, root):
        mmd_root = root.mmd_root
        if len(mmd_root.group_morphs) == 0:
            return
        categories = self.CATEGORIES
        start_index = len(self.__model.morphs)
        for morph in mmd_root.group_morphs:
            group_morph = pmx.GroupMorph(
                name=morph.name,
                name_e=morph.name_e,
                category=categories.get(morph.category, pmx.Morph.CATEGORY_OHTER)
            )
            self.__model.morphs.append(group_morph)

        morph_map = self.__get_pmx_morph_map()
        for morph, group_morph in zip(mmd_root.group_morphs, self.__model.morphs[start_index:]):
            for data in morph.data:
                morph_index = morph_map.get((data.morph_type, data.name), -1)
                if morph_index < 0:
                    logging.warning('Group Morph (%s): Morph "%s" was not found.', morph.name, data.name)
                    continue
                morph_data = pmx.GroupMorphOffset()
                morph_data.morph = morph_index
                morph_data.factor = data.factor
                group_morph.offsets.append(morph_data)

    def __exportDisplayItems(self, root, bone_map):
        res = []
        morph_map = self.__get_pmx_morph_map()
        for i in root.mmd_root.display_item_frames:
            d = pmx.Display()
            d.name = i.name
            d.name_e = i.name_e
            d.isSpecial = i.is_special
            items = []
            for j in i.data:
                if j.type == 'BONE' and j.name in bone_map:
                    items.append((0, bone_map[j.name]))
                elif j.type == 'MORPH' and (j.morph_type, j.name) in morph_map:
                    items.append((1, morph_map[(j.morph_type, j.name)]))
                else:
                    logging.warning('Display item (%s, %s) was not found.', j.type, j.name)
            d.data = items
            res.append(d)
        self.__model.display = res

    def __get_pmx_morph_map(self):
        morph_types = {
            pmx.GroupMorph : 'group_morphs',
            pmx.VertexMorph : 'vertex_morphs',
            pmx.BoneMorph : 'bone_morphs',
            pmx.UVMorph : 'uv_morphs',
            pmx.MaterialMorph : 'material_morphs',
            }
        morph_map = {}
        for i, m in enumerate(self.__model.morphs):
            morph_map[(morph_types[type(m)], m.name)] = i
        return morph_map


    def __exportRigidBodies(self, rigid_bodies, bone_map):
        rigid_map = {}
        rigid_cnt = 0
        Vector = mathutils.Vector
        for obj in rigid_bodies:
            t, r, s = obj.matrix_world.decompose()
            r = r.to_euler('YXZ')
            rb = obj.rigid_body
            if rb is None:
                logging.warning(' * Settings of rigid body "%s" not found, skipped!', obj.name)
                continue
            p_rigid = pmx.Rigid()
            mmd_rigid = obj.mmd_rigid
            p_rigid.name = mmd_rigid.name_j or MoveObject.get_name(obj)
            p_rigid.name_e = mmd_rigid.name_e
            p_rigid.location = Vector(t).xzy * self.__scale
            p_rigid.rotation = Vector(r).xzy * -1
            p_rigid.mode = int(mmd_rigid.type)

            rigid_shape = mmd_rigid.shape
            shape_size = Vector(mmd_rigid.size) * (sum(s) / 3)
            if rigid_shape == 'SPHERE':
                p_rigid.type = 0
                p_rigid.size = shape_size * self.__scale
            elif rigid_shape == 'BOX':
                p_rigid.type = 1
                p_rigid.size = shape_size.xzy * self.__scale
            elif rigid_shape == 'CAPSULE':
                p_rigid.type = 2
                p_rigid.size = shape_size * self.__scale
            else:
                raise Exception('Invalid rigid body type: %s %s', obj.name, rigid_shape)

            p_rigid.bone = bone_map.get(mmd_rigid.bone, -1)
            p_rigid.collision_group_number = mmd_rigid.collision_group_number
            mask = 0
            for i, v in enumerate(mmd_rigid.collision_group_mask):
                if not v:
                    mask += (1<<i)
            p_rigid.collision_group_mask = mask

            p_rigid.mass = rb.mass
            p_rigid.friction = rb.friction
            p_rigid.bounce = rb.restitution
            p_rigid.velocity_attenuation = rb.linear_damping
            p_rigid.rotation_attenuation = rb.angular_damping

            self.__model.rigids.append(p_rigid)
            rigid_map[obj] = rigid_cnt
            rigid_cnt += 1
        return rigid_map

    def __exportJoints(self, joints, rigid_map):
        Vector = mathutils.Vector
        for joint in joints:
            t, r, s = joint.matrix_world.decompose()
            r = r.to_euler('YXZ')
            rbc = joint.rigid_body_constraint
            if rbc is None:
                logging.warning(' * Settings of joint "%s" not found, skipped!', joint.name)
                continue
            p_joint = pmx.Joint()
            mmd_joint = joint.mmd_joint
            p_joint.name = mmd_joint.name_j or MoveObject.get_name(joint, 'J.')
            p_joint.name_e = mmd_joint.name_e
            p_joint.location = Vector(t).xzy * self.__scale
            p_joint.rotation = Vector(r).xzy * -1
            p_joint.src_rigid = rigid_map.get(rbc.object1, -1)
            p_joint.dest_rigid = rigid_map.get(rbc.object2, -1)
            scale = self.__scale * sum(s) / 3
            p_joint.maximum_location = Vector((rbc.limit_lin_x_upper, rbc.limit_lin_z_upper, rbc.limit_lin_y_upper)) * scale
            p_joint.minimum_location = Vector((rbc.limit_lin_x_lower, rbc.limit_lin_z_lower, rbc.limit_lin_y_lower)) * scale
            p_joint.maximum_rotation = Vector((rbc.limit_ang_x_lower, rbc.limit_ang_z_lower, rbc.limit_ang_y_lower)) * -1
            p_joint.minimum_rotation = Vector((rbc.limit_ang_x_upper, rbc.limit_ang_z_upper, rbc.limit_ang_y_upper)) * -1
            p_joint.spring_constant = Vector(mmd_joint.spring_linear).xzy
            p_joint.spring_rotation_constant = Vector(mmd_joint.spring_angular).xzy
            self.__model.joints.append(p_joint)


    @staticmethod
    def __convertFaceUVToVertexUV(vert_index, uv, normal, vertices_map):
        vertices = vertices_map[vert_index]
        for i in vertices:
            if i.uv is None:
                i.uv = uv
                i.normal = normal
                return i
            elif (i.uv - uv).length < 0.001 and (normal - i.normal).length < 0.01:
                return i
        n = copy.copy(i) # shallow copy should be fine
        n.uv = uv
        n.normal = normal
        vertices.append(n)
        return n

    @staticmethod
    def __convertAddUV(vert, adduv, addzw, uv_index, vertices, rip_vertices):
        if vert.add_uvs[uv_index] is None:
            vert.add_uvs[uv_index] = (adduv, addzw)
            return vert
        for i in rip_vertices:
            uvzw = i.add_uvs[uv_index]
            if (uvzw[0] - adduv).length < 0.001 and (uvzw[1] - addzw).length < 0.001:
                return i
        n = copy.copy(vert)
        add_uvs = n.add_uvs.copy()
        add_uvs[uv_index] = (adduv, addzw)
        n.add_uvs = add_uvs
        vertices.append(n)
        rip_vertices.append(n)
        return n

    @staticmethod
    def __triangulate(mesh, custom_normals):
        bm = bmesh.new()
        bm.from_mesh(mesh)

        is_triangulated = True
        face_verts_to_loop_id_map = {}

        loop_id = 0
        for f in bm.faces:
            vert_to_loop_id = face_verts_to_loop_id_map.setdefault(f, {})
            if is_triangulated and len(f.verts) != 3:
                is_triangulated = False
            for v in f.verts:
                vert_to_loop_id[v] = loop_id
                loop_id += 1

        loop_normals = None
        if is_triangulated:
            loop_normals = custom_normals
        else:
            quad_method, ngon_method = (1, 1) if bpy.app.version < (2, 80, 0) else ('FIXED', 'EAR_CLIP')
            face_map = bmesh.ops.triangulate(bm, faces=bm.faces, quad_method=quad_method, ngon_method=ngon_method)['face_map']
            logging.debug(' - Remapping custom normals...')
            loop_normals = []
            for f in bm.faces:
                vert_to_loop_id = face_verts_to_loop_id_map[face_map.get(f, f)]
                for v in f.verts:
                    loop_normals.append(custom_normals[vert_to_loop_id[v]])
            logging.debug('   - Done (faces:%d)', len(bm.faces))
            bm.to_mesh(mesh)
            face_map.clear()
        face_verts_to_loop_id_map.clear()
        bm.free()

        assert(len(loop_normals) == len(mesh.loops))
        return loop_normals

    @staticmethod
    def __get_normals(mesh, matrix):
        custom_normals = None
        if hasattr(mesh, 'has_custom_normals'):
            logging.debug(' - Calculating normals split...')
            mesh.calc_normals_split()
            custom_normals = [matmul(matrix, l.normal).normalized() for l in mesh.loops]
            mesh.free_normals_split()
        elif mesh.use_auto_smooth:
            logging.debug(' - Calculating normals split (angle:%f)...', mesh.auto_smooth_angle)
            mesh.calc_normals_split(mesh.auto_smooth_angle)
            custom_normals = [matmul(matrix, l.normal).normalized() for l in mesh.loops]
            mesh.free_normals_split()
        else:
            logging.debug(' - Calculating normals...')
            mesh.calc_normals()
            #custom_normals = [matmul(matrix, mesh.vertices[l.vertex_index].normal).normalized() for l in mesh.loops]
            custom_normals = []
            for f in mesh.polygons:
                if f.use_smooth:
                    for v in f.vertices:
                        custom_normals.append(matmul(matrix, mesh.vertices[v].normal).normalized())
                else:
                    for v in f.vertices:
                        custom_normals.append(matmul(matrix, f.normal).normalized())
        logging.debug('   - Done (polygons:%d)', len(mesh.polygons))
        return custom_normals

    def __doLoadMeshData(self, meshObj, bone_map):
        vg_to_bone = {i:bone_map[x.name] for i, x in enumerate(meshObj.vertex_groups) if x.name in bone_map}
        vg_edge_scale = meshObj.vertex_groups.get('mmd_edge_scale', None)
        vg_vertex_order = meshObj.vertex_groups.get('mmd_vertex_order', None)

        pmx_matrix = meshObj.matrix_world * self.__scale
        pmx_matrix[1], pmx_matrix[2] = pmx_matrix[2].copy(), pmx_matrix[1].copy()
        sx, sy, sz = meshObj.matrix_world.to_scale()
        normal_matrix = pmx_matrix.to_3x3()
        if not (sx == sy == sz):
            invert_scale_matrix = mathutils.Matrix([[1.0/sx,0,0], [0,1.0/sy,0], [0,0,1.0/sz]])
            normal_matrix = matmul(normal_matrix, invert_scale_matrix) # reset the scale of meshObj.matrix_world
            normal_matrix = matmul(normal_matrix, invert_scale_matrix) # the scale transform of normals

        if bpy.app.version < (2, 80, 0):
            _to_mesh = lambda obj: obj.to_mesh(bpy.context.scene, apply_modifiers=True, settings='PREVIEW', calc_tessface=False, calc_undeformed=False)
            _to_mesh_clear = lambda obj, mesh: bpy.data.meshes.remove(mesh)
        else:
            def _to_mesh(obj):
                bpy.context.view_layer.update()
                depsgraph = bpy.context.evaluated_depsgraph_get()
                return obj.evaluated_get(depsgraph).to_mesh(depsgraph=depsgraph, preserve_all_data_layers=True)
            _to_mesh_clear = lambda obj, mesh: obj.to_mesh_clear()

        base_mesh = _to_mesh(meshObj)
        loop_normals = self.__triangulate(base_mesh, self.__get_normals(base_mesh, normal_matrix))
        base_mesh.transform(pmx_matrix)

        def _get_weight(vertex_group_index, vertex, default_weight):
            for i in vertex.groups:
                if i.group == vertex_group_index:
                    return i.weight
            return default_weight

        get_edge_scale = None
        if vg_edge_scale:
            get_edge_scale = lambda x: _get_weight(vg_edge_scale.index, x, 1)
        else:
            get_edge_scale = lambda x: 1

        get_vertex_order = None
        if self.__vertex_order_map: # sort vertices
            mesh_id = self.__vertex_order_map.setdefault('mesh_id', 0)
            self.__vertex_order_map['mesh_id'] += 1
            if vg_vertex_order and self.__vertex_order_map['method'] == 'CUSTOM':
                get_vertex_order = lambda x: (mesh_id, _get_weight(vg_vertex_order.index, x, 2), x.index)
            else:
                get_vertex_order = lambda x: (mesh_id, x.index)
        else:
            get_vertex_order = lambda x: None

        uv_morph_names = {g.index:(n, x) for g, n, x in FnMorph.get_uv_morph_vertex_groups(meshObj)}
        def get_uv_offsets(v):
            uv_offsets = {}
            for x in v.groups:
                if x.group in uv_morph_names and x.weight > 0:
                    name, axis = uv_morph_names[x.group]
                    d = uv_offsets.setdefault(name, [0, 0, 0, 0])
                    d['XYZW'.index(axis[1])] += -x.weight if axis[0] == '-' else x.weight
            return uv_offsets

        base_vertices = {}
        for v in base_mesh.vertices:
            base_vertices[v.index] = [_Vertex(
                v.co.copy(),
                [(vg_to_bone[x.group], x.weight) for x in v.groups if x.weight > 0 and x.group in vg_to_bone],
                {},
                get_edge_scale(v),
                get_vertex_order(v),
                get_uv_offsets(v),
                )]

        # load face data
        class _DummyUV:
            uv1 = uv2 = uv3 = mathutils.Vector((0, 1))
            def __init__(self, uvs):
                self.uv1,  self.uv2, self.uv3 = (v.uv.copy() for v in uvs)

        _UVWrapper = lambda x: (_DummyUV(x[i:i+3]) for i in range(0, len(x), 3))

        material_faces = {}
        uv_data = base_mesh.uv_layers.active
        if uv_data:
            uv_data = _UVWrapper(uv_data.data)
        else:
            uv_data = iter(lambda: _DummyUV, None)
        face_seq = []
        for face, uv in zip(base_mesh.polygons, uv_data):
            if len(face.vertices) != 3:
                raise Exception
            idx = face.index * 3
            n1, n2, n3 = loop_normals[idx:idx+3]
            v1 = self.__convertFaceUVToVertexUV(face.vertices[0], uv.uv1, n1, base_vertices)
            v2 = self.__convertFaceUVToVertexUV(face.vertices[1], uv.uv2, n2, base_vertices)
            v3 = self.__convertFaceUVToVertexUV(face.vertices[2], uv.uv3, n3, base_vertices)

            t = _Face([v1, v2, v3])
            face_seq.append(t)
            if face.material_index not in material_faces:
                material_faces[face.material_index] = []
            material_faces[face.material_index].append(t)

        _mat_name = lambda x: x.name if x else self.__getDefaultMaterial().name
        material_names = {i:_mat_name(m) for i, m in enumerate(base_mesh.materials)}
        material_names = {i:material_names.get(i, None) or _mat_name(None) for i in material_faces.keys()}

        # export add UV
        bl_add_uvs = [i for i in base_mesh.uv_layers[1:] if not i.name.startswith('_')]
        self.__add_uv_count = max(self.__add_uv_count, len(bl_add_uvs))
        for uv_n, uv_tex in enumerate(bl_add_uvs):
            if uv_n > 3:
                logging.warning(' * extra addUV%d+ are not supported', uv_n+1)
                break
            uv_data = _UVWrapper(uv_tex.data)
            zw_data = base_mesh.uv_layers.get('_'+uv_tex.name, None)
            logging.info(' # exporting addUV%d: %s [zw: %s]', uv_n+1, uv_tex.name, zw_data)
            if zw_data:
                zw_data = _UVWrapper(zw_data.data)
            else:
                zw_data = iter(lambda: _DummyUV, None)
            rip_vertices_map = {}
            for f, face, uv, zw in zip(face_seq, base_mesh.polygons, uv_data, zw_data):
                vertices = [base_vertices[x] for x in face.vertices]
                rip_vertices = [rip_vertices_map.setdefault(x, [x]) for x in f.vertices]
                f.vertices[0] = self.__convertAddUV(f.vertices[0], uv.uv1, zw.uv1, uv_n, vertices[0], rip_vertices[0])
                f.vertices[1] = self.__convertAddUV(f.vertices[1], uv.uv2, zw.uv2, uv_n, vertices[1], rip_vertices[1])
                f.vertices[2] = self.__convertAddUV(f.vertices[2], uv.uv3, zw.uv3, uv_n, vertices[2], rip_vertices[2])

        _to_mesh_clear(meshObj, base_mesh)

        # calculate offsets
        shape_key_list = []
        if meshObj.data.shape_keys:
            for i, kb in enumerate(meshObj.data.shape_keys.key_blocks):
                if i == 0: # Basis
                    continue
                if kb.name.startswith('mmd_bind') or kb.name == FnSDEF.SHAPEKEY_NAME:
                    continue
                if kb.name == 'mmd_sdef_c': # make sure 'mmd_sdef_c' is at first
                    shape_key_list = [(i, kb)] + shape_key_list
                else:
                    shape_key_list.append((i, kb))

        shape_key_names = []
        sdef_counts = 0
        for i, kb in shape_key_list:
            shape_key_name = kb.name
            logging.info(' - processing shape key: %s', shape_key_name)
            kb_mute, kb.mute = kb.mute, False
            meshObj.active_shape_key_index = i
            mesh = _to_mesh(meshObj)
            mesh.transform(pmx_matrix)
            kb.mute = kb_mute
            if len(mesh.vertices) != len(base_vertices):
                logging.warning('   * Error! vertex count mismatch!')
                continue
            if shape_key_name in {'mmd_sdef_c', 'mmd_sdef_r0', 'mmd_sdef_r1'}:
                if shape_key_name == 'mmd_sdef_c':
                    for v in mesh.vertices:
                        base = base_vertices[v.index][0]
                        if len(base.groups) != 2:
                            continue
                        base_co = base.co
                        c_co = v.co
                        if (c_co - base_co).length < 0.001:
                            continue
                        base.sdef_data[:] = tuple(c_co), base_co, base_co
                        sdef_counts += 1
                    logging.info('   - Restored %d SDEF vertices', sdef_counts)
                elif sdef_counts > 0:
                    ri = 1 if shape_key_name == 'mmd_sdef_r0' else 2
                    for v in mesh.vertices:
                        sdef_data = base_vertices[v.index][0].sdef_data
                        if sdef_data:
                            sdef_data[ri] = tuple(v.co)
                    logging.info('   - Updated SDEF data')
            else:
                shape_key_names.append(shape_key_name)
                for v in mesh.vertices:
                    base = base_vertices[v.index][0]
                    offset = v.co - base.co
                    if offset.length < 0.001:
                        continue
                    base.offsets[shape_key_name] = offset
            _to_mesh_clear(meshObj, mesh)

        if not pmx_matrix.is_negative: # pmx.load/pmx.save reverse face vertices by default
            for f in face_seq:
                f.vertices.reverse()

        return _Mesh(
            material_faces,
            shape_key_names,
            material_names)

    def __loadMeshData(self, meshObj, bone_map):
        show_only_shape_key = meshObj.show_only_shape_key
        meshObj.show_only_shape_key = True
        active_shape_key_index = meshObj.active_shape_key_index
        meshObj.active_shape_key_index = 0
        uv_textures = getattr(meshObj.data, 'uv_textures', meshObj.data.uv_layers)
        active_uv_texture_index = uv_textures.active_index
        uv_textures.active_index = 0

        muted_modifiers = []
        for m in meshObj.modifiers:
            if m.type != 'ARMATURE' or m.object is None:
                continue
            if m.object.data.pose_position == 'REST':
                muted_modifiers.append((m, m.show_viewport))
                m.show_viewport = False

        try:
            logging.info('Loading mesh: %s', meshObj.name)
            return self.__doLoadMeshData(meshObj, bone_map)
        finally:
            meshObj.show_only_shape_key = show_only_shape_key
            meshObj.active_shape_key_index = active_shape_key_index
            uv_textures.active_index = active_uv_texture_index
            for m, show in muted_modifiers:
                m.show_viewport = show


    def execute(self, filepath, **args):
        root = args.get('root', None)
        self.__model = pmx.Model()
        self.__model.name = 'test'
        self.__model.name_e = 'test eng'
        self.__model.comment = 'exported by mmd_tools'
        self.__model.comment_e = 'exported by mmd_tools'

        if root is not None:
            self.__model.name = root.mmd_root.name or root.name
            self.__model.name_e = root.mmd_root.name_e
            txt = bpy.data.texts.get(root.mmd_root.comment_text, None)
            if txt:
                self.__model.comment = txt.as_string().replace('\n', '\r\n')
            txt = bpy.data.texts.get(root.mmd_root.comment_e_text, None)
            if txt:
                self.__model.comment_e = txt.as_string().replace('\n', '\r\n')

        self.__armature = args.get('armature', None)
        meshes = sorted(args.get('meshes', []), key=lambda x: x.name)
        rigids = sorted(args.get('rigid_bodies', []), key=lambda x: x.name)
        joints = sorted(args.get('joints', []), key=lambda x: x.name)

        self.__scale = args.get('scale', 1.0)
        self.__disable_specular = args.get('disable_specular', False)
        sort_vertices = args.get('sort_vertices', 'NONE')
        if sort_vertices != 'NONE':
            self.__vertex_order_map = {'method':sort_vertices}

        nameMap = self.__exportBones(meshes)

        mesh_data = [self.__loadMeshData(i, nameMap) for i in meshes]
        self.__exportMeshes(mesh_data, nameMap)
        if args.get('sort_materials', False):
            self.__sortMaterials()

        self.__exportVertexMorphs(mesh_data, root)
        if root is not None:
            self.__export_bone_morphs(root)
            self.__export_material_morphs(root)
            self.__export_uv_morphs(root)
            self.__export_group_morphs(root)
            self.__exportDisplayItems(root, nameMap)

        rigid_map = self.__exportRigidBodies(rigids, nameMap)
        self.__exportJoints(joints, rigid_map)

        if args.get('copy_textures', False):
            output_dir = os.path.dirname(filepath)
            import_folder = root.get('import_folder', '') if root else ''
            base_folder = bpyutils.addon_preferences('base_texture_folder', '')
            self.__copy_textures(output_dir, import_folder or base_folder)

        pmx.save(filepath, self.__model, add_uv_count=self.__add_uv_count)

def export(filepath, **kwargs):
    logging.info('****************************************')
    logging.info(' %s module'%__name__)
    logging.info('----------------------------------------')
    start_time = time.time()
    exporter = __PmxExporter()
    exporter.execute(filepath, **kwargs)
    logging.info(' Finished exporting the model in %f seconds.', time.time() - start_time)
    logging.info('----------------------------------------')
    logging.info(' %s module'%__name__)
    logging.info('****************************************')
