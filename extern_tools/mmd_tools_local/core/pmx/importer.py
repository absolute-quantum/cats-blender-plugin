# -*- coding: utf-8 -*-
import os
import collections
import logging
import time

import bpy
from mathutils import Vector, Matrix

import mmd_tools_local.core.model as mmd_model
from mmd_tools_local import utils
from mmd_tools_local import bpyutils
from mmd_tools_local.core import pmx
from mmd_tools_local.core.bone import FnBone
from mmd_tools_local.core.material import FnMaterial
from mmd_tools_local.core.morph import FnMorph
from mmd_tools_local.core.vmd.importer import BoneConverter
from mmd_tools_local.operators.display_item import DisplayItemQuickSetup
from mmd_tools_local.operators.misc import MoveObject


class PMXImporter:
    CATEGORIES = {
        0: 'SYSTEM',
        1: 'EYEBROW',
        2: 'EYE',
        3: 'MOUTH',
        }
    MORPH_TYPES = {
        0: 'group_morphs',
        1: 'vertex_morphs',
        2: 'bone_morphs',
        3: 'uv_morphs',
        4: 'uv_morphs',
        5: 'uv_morphs',
        6: 'uv_morphs',
        7: 'uv_morphs',
        8: 'material_morphs',
        }

    def __init__(self):
        self.__model = None
        self.__targetScene = bpyutils.SceneOp(bpy.context)

        self.__scale = None

        self.__root = None
        self.__armObj = None
        self.__meshObj = None

        self.__vertexGroupTable = None
        self.__textureTable = None
        self.__rigidTable = None

        self.__boneTable = []
        self.__materialTable = []
        self.__imageTable = {}

        self.__sdefVertices = {} # pmx vertices
        self.__blender_ik_links = set()
        self.__vertex_map = None

        self.__materialFaceCountTable = None

    @staticmethod
    def __safe_name(name, max_length=59):
        return str(bytes(name, 'utf8')[:max_length], 'utf8', errors='replace')

    @staticmethod
    def flipUV_V(uv):
        u, v = uv
        return u, 1.0-v

    def __createObjects(self):
        """ Create main objects and link them to scene.
        """
        pmxModel = self.__model
        obj_name = self.__safe_name(bpy.path.display_name(pmxModel.filepath), max_length=54)
        self.__rig = mmd_model.Model.create(pmxModel.name, pmxModel.name_e, self.__scale, obj_name)
        root = self.__rig.rootObject()
        mmd_root = root.mmd_root
        self.__root = root

        root['import_folder'] = os.path.dirname(pmxModel.filepath)

        txt = bpy.data.texts.new(obj_name)
        txt.from_string(pmxModel.comment.replace('\r', ''))
        mmd_root.comment_text = txt.name
        txt = bpy.data.texts.new(obj_name+'_e')
        txt.from_string(pmxModel.comment_e.replace('\r', ''))
        mmd_root.comment_e_text = txt.name

        self.__armObj = self.__rig.armature()
        self.__armObj.hide = True
        self.__armObj.select = False

    def __createMeshObject(self):
        model_name = self.__root.name
        self.__meshObj = bpy.data.objects.new(name=model_name+'_mesh', object_data=bpy.data.meshes.new(name=model_name))
        self.__meshObj.parent = self.__armObj
        self.__targetScene.link_object(self.__meshObj)

    def __createBasisShapeKey(self):
        if self.__meshObj.data.shape_keys:
            assert(len(self.__meshObj.data.vertices) > 0)
            assert(len(self.__meshObj.data.shape_keys.key_blocks) > 1)
            return
        self.__targetScene.active_object = self.__meshObj
        bpy.ops.object.shape_key_add()

    def __importVertexGroup(self):
        vgroups = self.__meshObj.vertex_groups
        self.__vertexGroupTable = [vgroups.new(name=i.name) for i in self.__model.bones] or [vgroups.new(name='NO BONES')]

    def __importVertices(self):
        self.__importVertexGroup()

        pmxModel = self.__model
        pmx_vertices = pmxModel.vertices
        vertex_count = len(pmx_vertices)
        vertex_map = self.__vertex_map
        if vertex_map:
            indices = collections.OrderedDict(vertex_map).keys()
            pmx_vertices = tuple(pmxModel.vertices[x] for x in indices)
            vertex_count = len(indices)
        if vertex_count < 1:
            return

        mesh = self.__meshObj.data
        mesh.vertices.add(count=vertex_count)
        mesh.vertices.foreach_set('co', tuple(i for pv in pmx_vertices for i in (Vector(pv.co).xzy * self.__scale)))

        vertex_group_table = self.__vertexGroupTable
        vg_edge_scale = self.__meshObj.vertex_groups.new(name='mmd_edge_scale')
        vg_vertex_order = self.__meshObj.vertex_groups.new(name='mmd_vertex_order')
        for i, pv in enumerate(pmx_vertices):
            pv_bones, pv_weights, idx = pv.weight.bones, pv.weight.weights, (i,)

            vg_edge_scale.add(index=idx, weight=pv.edge_scale, type='REPLACE')
            vg_vertex_order.add(index=idx, weight=i/vertex_count, type='REPLACE')

            if isinstance(pv_weights, pmx.BoneWeightSDEF):
                if pv_bones[0] > pv_bones[1]:
                    pv_bones.reverse()
                    pv_weights.weight = 1.0 - pv_weights.weight
                    pv_weights.r0, pv_weights.r1 = pv_weights.r1, pv_weights.r0
                vertex_group_table[pv_bones[0]].add(index=idx, weight=pv_weights.weight, type='ADD')
                vertex_group_table[pv_bones[1]].add(index=idx, weight=1.0-pv_weights.weight, type='ADD')
                self.__sdefVertices[i] = pv
            elif len(pv_bones) == 1:
                bone_index = pv_bones[0]
                if bone_index >= 0:
                    vertex_group_table[bone_index].add(index=idx, weight=1.0, type='ADD')
            elif len(pv_bones) == 2:
                vertex_group_table[pv_bones[0]].add(index=idx, weight=pv_weights[0], type='ADD')
                vertex_group_table[pv_bones[1]].add(index=idx, weight=1.0-pv_weights[0], type='ADD')
            elif len(pv_bones) == 4:
                for bone, weight in zip(pv_bones, pv_weights):
                    vertex_group_table[bone].add(index=idx, weight=weight, type='ADD')
            else:
                raise Exception('unkown bone weight type.')

        vg_edge_scale.lock_weight = True
        vg_vertex_order.lock_weight = True

    def __storeVerticesSDEF(self):
        if len(self.__sdefVertices) < 1:
            return

        self.__createBasisShapeKey()
        sdefC = self.__meshObj.shape_key_add(name='mmd_sdef_c')
        sdefR0 = self.__meshObj.shape_key_add(name='mmd_sdef_r0')
        sdefR1 = self.__meshObj.shape_key_add(name='mmd_sdef_r1')
        for i, pv in self.__sdefVertices.items():
            w = pv.weight.weights
            sdefC.data[i].co = Vector(w.c).xzy * self.__scale
            sdefR0.data[i].co = Vector(w.r0).xzy * self.__scale
            sdefR1.data[i].co = Vector(w.r1).xzy * self.__scale
        logging.info('Stored %d SDEF vertices', len(self.__sdefVertices))

    def __importTextures(self):
        pmxModel = self.__model

        self.__textureTable = []
        for i in pmxModel.textures:
            self.__textureTable.append(bpy.path.resolve_ncase(path=i.path))

    def __createEditBones(self, obj, pmx_bones):
        """ create EditBones from pmx file data.
        @return the list of bone names which can be accessed by the bone index of pmx data.
        """
        editBoneTable = []
        nameTable = []
        specialTipBones = []
        dependency_cycle_ik_bones = []
        #for i, p_bone in enumerate(pmx_bones):
        #    if p_bone.isIK:
        #        if p_bone.target != -1:
        #            t = pmx_bones[p_bone.target]
        #            if p_bone.parent == t.parent:
        #                dependency_cycle_ik_bones.append(i)

        from math import isfinite
        def _VectorXZY(v):
            return Vector(v).xzy if all(isfinite(n) for n in v) else Vector((0,0,0))

        with bpyutils.edit_object(obj) as data:
            for i in pmx_bones:
                bone = data.edit_bones.new(name=i.name)
                loc = _VectorXZY(i.location) * self.__scale
                bone.head = loc
                editBoneTable.append(bone)
                nameTable.append(bone.name)

            for i, (b_bone, m_bone) in enumerate(zip(editBoneTable, pmx_bones)):
                if m_bone.parent != -1:
                    if i not in dependency_cycle_ik_bones:
                        b_bone.parent = editBoneTable[m_bone.parent]
                    else:
                        b_bone.parent = editBoneTable[m_bone.parent].parent

            for b_bone, m_bone in zip(editBoneTable, pmx_bones):
                if isinstance(m_bone.displayConnection, int):
                    if m_bone.displayConnection != -1:
                        b_bone.tail = editBoneTable[m_bone.displayConnection].head
                    else:
                        b_bone.tail = b_bone.head
                else:
                    loc = _VectorXZY(m_bone.displayConnection) * self.__scale
                    b_bone.tail = b_bone.head + loc

            for b_bone, m_bone in zip(editBoneTable, pmx_bones):
                if m_bone.isIK and m_bone.target != -1:
                    logging.debug(' - checking IK links of %s', b_bone.name)
                    b_target = editBoneTable[m_bone.target]
                    for i in range(len(m_bone.ik_links)):
                        b_bone_link = editBoneTable[m_bone.ik_links[i].target]
                        if self.__fix_IK_links or b_bone_link.length < 0.001:
                            b_bone_tail = b_target if i == 0 else editBoneTable[m_bone.ik_links[i-1].target]
                            loc = b_bone_tail.head - b_bone_link.head
                            if loc.length < 0.001:
                                logging.warning('   ** unsolved IK link %s **', b_bone_link.name)
                            elif b_bone_tail.parent != b_bone_link:
                                logging.warning('   ** skipped IK link %s **', b_bone_link.name)
                            elif (b_bone_link.tail - b_bone_tail.head).length > 1e-4:
                                logging.debug('   * fix IK link %s', b_bone_link.name)
                                b_bone_link.tail = b_bone_link.head + loc

            for b_bone, m_bone in zip(editBoneTable, pmx_bones):
                # Set the length of too short bones to 1 because Blender delete them.
                if b_bone.length < 0.001:
                    if not self.__apply_bone_fixed_axis and m_bone.axis is not None:
                        fixed_axis = Vector(m_bone.axis)
                        if fixed_axis.length:
                            b_bone.tail = b_bone.head + fixed_axis.xzy.normalized() * self.__scale
                        else:
                            b_bone.tail = b_bone.head + Vector((0, 0, 1)) * self.__scale
                    else:
                        b_bone.tail = b_bone.head + Vector((0, 0, 1)) * self.__scale
                    if m_bone.displayConnection != -1 and m_bone.displayConnection != [0.0, 0.0, 0.0]:
                        logging.debug(' * special tip bone %s, display %s', b_bone.name, str(m_bone.displayConnection))
                        specialTipBones.append(b_bone.name)

            for b_bone, m_bone in zip(editBoneTable, pmx_bones):
                if m_bone.localCoordinate is not None:
                    FnBone.update_bone_roll(b_bone, m_bone.localCoordinate.x_axis, m_bone.localCoordinate.z_axis)
                elif FnBone.has_auto_local_axis(m_bone.name):
                    FnBone.update_auto_bone_roll(b_bone)

            for b_bone, m_bone in zip(editBoneTable, pmx_bones):
                if isinstance(m_bone.displayConnection, int) and m_bone.displayConnection >= 0:
                    t = editBoneTable[m_bone.displayConnection]
                    if t.parent is None or t.parent != b_bone:
                        logging.warning(' * disconnected: %s (%d)<> %s', b_bone.name, len(b_bone.children), t.name)
                        continue
                    if pmx_bones[m_bone.displayConnection].isMovable:
                        logging.warning(' * disconnected: %s (%d)-> %s', b_bone.name, len(b_bone.children), t.name)
                        continue
                    if (b_bone.tail - t.head).length > 1e-4:
                        logging.warning(' * disconnected: %s (%d)=> %s', b_bone.name, len(b_bone.children), t.name)
                        continue
                    t.use_connect = True

        return nameTable, specialTipBones

    def __sortPoseBonesByBoneIndex(self, pose_bones, bone_names):
        r = []
        for i in bone_names:
            r.append(pose_bones[i])
        return r

    @staticmethod
    def convertIKLimitAngles(min_angle, max_angle, bone_matrix, invert=False):
        mat = bone_matrix.to_3x3() * -1
        mat[1], mat[2] = mat[2].copy(), mat[1].copy()
        mat.transpose()
        if invert:
            mat.invert()

        # align matrix to global axes
        m = Matrix([[0,0,0], [0,0,0], [0,0,0]])
        i_set, j_set = [0, 1, 2], [0, 1, 2]
        for _ in range(3):
            ii, jj = i_set[0], j_set[0]
            for i in i_set:
                for j in j_set:
                    if abs(mat[i][j]) > abs(mat[ii][jj]):
                        ii, jj = i, j
            i_set.remove(ii)
            j_set.remove(jj)
            m[ii][jj] = -1 if mat[ii][jj] < 0 else 1

        new_min_angle = bpyutils.matmul(m, Vector(min_angle))
        new_max_angle = bpyutils.matmul(m, Vector(max_angle))
        for i in range(3):
            if new_min_angle[i] > new_max_angle[i]:
                new_min_angle[i], new_max_angle[i] = new_max_angle[i], new_min_angle[i]
        return new_min_angle, new_max_angle

    def __applyIk(self, index, pmx_bone, pose_bones):
        """ create a IK bone constraint
         If the IK bone and the target bone is separated, a dummy IK target bone is created as a child of the IK bone.
         @param index the bone index
         @param pmx_bone pmx.Bone
         @param pose_bones the list of PoseBones sorted by the bone index
        """

        # for tracking mmd ik target, simple explaination:
        # + Root
        # | + link1
        # |   + link0 (ik_constraint_bone) <- ik constraint, chain_count=2
        # |     + IK target (ik_target) <- constraint 'mmd_ik_target_override', subtarget=link0
        # + IK bone (ik_bone)
        #
        # it is possible that the link0 is the IK target,
        # so ik constraint will be on link1, chain_count=1
        # the IK target isn't affected by IK bone

        ik_bone = pose_bones[index]
        ik_target = pose_bones[pmx_bone.target]
        ik_constraint_bone = ik_target.parent
        is_valid_ik = False
        if len(pmx_bone.ik_links) > 0:
            ik_constraint_bone_real = pose_bones[pmx_bone.ik_links[0].target]
            if ik_constraint_bone_real == ik_target:
                if len(pmx_bone.ik_links) > 1:
                    ik_constraint_bone_real = pose_bones[pmx_bone.ik_links[1].target]
                del pmx_bone.ik_links[0]
                logging.warning(' * fix IK settings of IK bone (%s)', ik_bone.name)
            is_valid_ik = (ik_constraint_bone == ik_constraint_bone_real)
            if not is_valid_ik:
                ik_constraint_bone = ik_constraint_bone_real
                logging.warning(' * IK bone (%s) warning: IK target (%s) is not a child of IK link 0 (%s)',
                                ik_bone.name, ik_target.name, ik_constraint_bone.name)
            elif any(pose_bones[i.target].parent != pose_bones[j.target] for i, j in zip(pmx_bone.ik_links, pmx_bone.ik_links[1:])):
                logging.warning(' * Invalid IK bone (%s): IK chain does not follow parent-child relationship', ik_bone.name)
                return
        if ik_constraint_bone is None or len(pmx_bone.ik_links) < 1:
            logging.warning(' * Invalid IK bone (%s)', ik_bone.name)
            return

        c = ik_target.constraints.new(type='DAMPED_TRACK')
        c.name = 'mmd_ik_target_override'
        c.mute = True
        c.influence = 0
        c.target = self.__armObj
        c.subtarget = ik_constraint_bone.name
        if not is_valid_ik or next((c for c in ik_constraint_bone.constraints if c.type == 'IK' and c.is_valid), None):
            c.name = 'mmd_ik_target_custom'
            c.subtarget = ik_bone.name # point to IK control bone
            ik_bone.mmd_bone.ik_rotation_constraint = pmx_bone.rotationConstraint
            use_custom_ik = True
        else:
            ik_constraint_bone.mmd_bone.ik_rotation_constraint = pmx_bone.rotationConstraint
            use_custom_ik = False

        ikConst = self.__rig.create_ik_constraint(ik_constraint_bone, ik_bone)
        ikConst.iterations = pmx_bone.loopCount
        ikConst.chain_count = len(pmx_bone.ik_links)
        if not is_valid_ik:
            ikConst.pole_target = self.__armObj # make it an incomplete/invalid setting
        for idx, i in enumerate(pmx_bone.ik_links):
            if use_custom_ik or i.target in self.__blender_ik_links:
                c = ik_bone.constraints.new(type='LIMIT_ROTATION')
                c.mute = True
                c.influence = 0
                c.name = 'mmd_ik_limit_custom%d'%idx
                use_limits = c.use_limit_x = c.use_limit_y = c.use_limit_z = (i.maximumAngle is not None)
                if use_limits:
                    minimum, maximum = self.convertIKLimitAngles(i.minimumAngle, i.maximumAngle, pose_bones[i.target].bone.matrix_local)
                    c.max_x, c.max_y, c.max_z = maximum
                    c.min_x, c.min_y, c.min_z = minimum
                continue
            self.__blender_ik_links.add(i.target)
            if i.maximumAngle is not None:
                bone = pose_bones[i.target]
                minimum, maximum = self.convertIKLimitAngles(i.minimumAngle, i.maximumAngle, bone.bone.matrix_local)

                bone.use_ik_limit_x = True
                bone.use_ik_limit_y = True
                bone.use_ik_limit_z = True
                bone.ik_max_x, bone.ik_max_y, bone.ik_max_z = maximum
                bone.ik_min_x, bone.ik_min_y, bone.ik_min_z = minimum

                c = bone.constraints.new(type='LIMIT_ROTATION')
                c.mute = not is_valid_ik
                c.name = 'mmd_ik_limit_override'
                c.owner_space = 'POSE' # WORLD/POSE/LOCAL
                c.max_x, c.max_y, c.max_z = maximum
                c.min_x, c.min_y, c.min_z = minimum
                c.use_limit_x = bone.ik_max_x != c.max_x or bone.ik_min_x != c.min_x
                c.use_limit_y = bone.ik_max_y != c.max_y or bone.ik_min_y != c.min_y
                c.use_limit_z = bone.ik_max_z != c.max_z or bone.ik_min_z != c.min_z

    def __importBones(self):
        pmxModel = self.__model

        boneNameTable, specialTipBones = self.__createEditBones(self.__armObj, pmxModel.bones)
        pose_bones = self.__sortPoseBonesByBoneIndex(self.__armObj.pose.bones, boneNameTable)
        self.__boneTable = pose_bones
        for i, pmx_bone in sorted(enumerate(pmxModel.bones), key=lambda x: x[1].transform_order):
            b_bone = pose_bones[i]
            mmd_bone = b_bone.mmd_bone
            mmd_bone.name_j = b_bone.name #pmx_bone.name
            mmd_bone.name_e = pmx_bone.name_e
            mmd_bone.is_controllable = pmx_bone.isControllable
            mmd_bone.transform_order = pmx_bone.transform_order
            mmd_bone.transform_after_dynamics = pmx_bone.transAfterPhis

            if pmx_bone.displayConnection == -1 or pmx_bone.displayConnection == (0.0, 0.0, 0.0):
                mmd_bone.is_tip = True
            elif b_bone.name in specialTipBones:
                mmd_bone.is_tip = True

            b_bone.bone.hide = not pmx_bone.visible #or mmd_bone.is_tip

            if not pmx_bone.isRotatable:
                b_bone.lock_rotation = [True, True, True]

            if not pmx_bone.isMovable:
                b_bone.lock_location = [True, True, True]

            if pmx_bone.isIK:
                if 0 <= pmx_bone.target < len(pose_bones):
                    self.__applyIk(i, pmx_bone, pose_bones)

            if pmx_bone.hasAdditionalRotate or pmx_bone.hasAdditionalLocation:
                bone_index, influ = pmx_bone.additionalTransform
                mmd_bone.has_additional_rotation = pmx_bone.hasAdditionalRotate
                mmd_bone.has_additional_location = pmx_bone.hasAdditionalLocation
                mmd_bone.additional_transform_influence = influ
                if 0 <= bone_index < len(pose_bones):
                    mmd_bone.additional_transform_bone = pose_bones[bone_index].name

            if pmx_bone.localCoordinate is not None:
                mmd_bone.enabled_local_axes = True
                mmd_bone.local_axis_x = pmx_bone.localCoordinate.x_axis
                mmd_bone.local_axis_z = pmx_bone.localCoordinate.z_axis

            if pmx_bone.axis is not None:
                mmd_bone.enabled_fixed_axis = True
                mmd_bone.fixed_axis = pmx_bone.axis

                if not self.__apply_bone_fixed_axis and mmd_bone.is_tip:
                    b_bone.lock_rotation = [True, False, True]
                    b_bone.lock_location = [True, True, True]
                    b_bone.lock_scale = [True, True, True]

    def __importRigids(self):
        start_time = time.time()
        self.__rigidTable = {}
        rigid_pool = self.__rig.createRigidBodyPool(len(self.__model.rigids))
        for i, (rigid, rigid_obj) in enumerate(zip(self.__model.rigids, rigid_pool)):
            loc = Vector(rigid.location).xzy * self.__scale
            rot = Vector(rigid.rotation).xzy * -1
            size = Vector(rigid.size).xzy if rigid.type == pmx.Rigid.TYPE_BOX else Vector(rigid.size)

            obj = self.__rig.createRigidBody(
                obj = rigid_obj,
                name = rigid.name,
                name_e = rigid.name_e,
                shape_type = rigid.type,
                dynamics_type = rigid.mode,
                location = loc,
                rotation = rot,
                size = size * self.__scale,
                collision_group_number = rigid.collision_group_number,
                collision_group_mask = [rigid.collision_group_mask & (1<<i) == 0 for i in range(16)],
                arm_obj = self.__armObj,
                mass=rigid.mass,
                friction = rigid.friction,
                angular_damping = rigid.rotation_attenuation,
                linear_damping = rigid.velocity_attenuation,
                bounce = rigid.bounce,
                bone = None if rigid.bone == -1 or rigid.bone is None else self.__boneTable[rigid.bone].name,
                )
            obj.hide = True
            MoveObject.set_index(obj, i)
            self.__rigidTable[i] = obj

        logging.debug('Finished importing rigid bodies in %f seconds.', time.time() - start_time)

    def __importJoints(self):
        start_time = time.time()
        joint_pool = self.__rig.createJointPool(len(self.__model.joints))
        for i, (joint, joint_obj) in enumerate(zip(self.__model.joints, joint_pool)):
            loc = Vector(joint.location).xzy * self.__scale
            rot = Vector(joint.rotation).xzy * -1

            obj = self.__rig.createJoint(
                obj = joint_obj,
                name = joint.name,
                name_e = joint.name_e,
                location = loc,
                rotation = rot,
                rigid_a = self.__rigidTable.get(joint.src_rigid, None),
                rigid_b = self.__rigidTable.get(joint.dest_rigid, None),
                maximum_location = Vector(joint.maximum_location).xzy * self.__scale,
                minimum_location = Vector(joint.minimum_location).xzy * self.__scale,
                maximum_rotation = Vector(joint.minimum_rotation).xzy * -1,
                minimum_rotation = Vector(joint.maximum_rotation).xzy * -1,
                spring_linear = Vector(joint.spring_constant).xzy,
                spring_angular = Vector(joint.spring_rotation_constant).xzy,
                )
            obj.hide = True
            MoveObject.set_index(obj, i)

        logging.debug('Finished importing joints in %f seconds.', time.time() - start_time)

    def __importMaterials(self):
        self.__importTextures()

        pmxModel = self.__model

        self.__materialFaceCountTable = []
        for i in pmxModel.materials:
            mat = bpy.data.materials.new(name=self.__safe_name(i.name, max_length=50))
            self.__materialTable.append(mat)
            mmd_mat = mat.mmd_material
            mmd_mat.name_j = i.name
            mmd_mat.name_e = i.name_e
            mmd_mat.ambient_color = i.ambient
            mmd_mat.diffuse_color = i.diffuse[0:3]
            mmd_mat.alpha = i.diffuse[3]
            mmd_mat.specular_color = i.specular
            mmd_mat.shininess = i.shininess
            mmd_mat.is_double_sided = i.is_double_sided
            mmd_mat.enabled_drop_shadow = i.enabled_drop_shadow
            mmd_mat.enabled_self_shadow_map = i.enabled_self_shadow_map
            mmd_mat.enabled_self_shadow = i.enabled_self_shadow
            mmd_mat.enabled_toon_edge = i.enabled_toon_edge
            mmd_mat.edge_color = i.edge_color
            mmd_mat.edge_weight = i.edge_size
            mmd_mat.comment = i.comment

            self.__materialFaceCountTable.append(int(i.vertex_count/3))
            self.__meshObj.data.materials.append(mat)
            fnMat = FnMaterial(mat)
            if i.texture != -1:
                texture_slot = fnMat.create_texture(self.__textureTable[i.texture])
                texture_slot.texture.use_mipmap = self.__use_mipmap
                self.__imageTable[len(self.__materialTable)-1] = texture_slot.texture.image

            if i.is_shared_toon_texture:
                mmd_mat.is_shared_toon_texture = True
                mmd_mat.shared_toon_texture = i.toon_texture
            else:
                mmd_mat.is_shared_toon_texture = False
                if i.toon_texture >= 0:
                    mmd_mat.toon_texture = self.__textureTable[i.toon_texture]

            if i.sphere_texture_mode == 2:
                amount = self.__spa_blend_factor
            else:
                amount = self.__sph_blend_factor
            if i.sphere_texture != -1 and amount != 0.0:
                texture_slot = fnMat.create_sphere_texture(self.__textureTable[i.sphere_texture])
                texture_slot.diffuse_color_factor = amount
                if i.sphere_texture_mode == 3 and getattr(pmxModel.header, 'additional_uvs', 0):
                    texture_slot.uv_layer = 'UV1' # for SubTexture
            mmd_mat.sphere_texture_type = str(i.sphere_texture_mode)

    def __importFaces(self):
        pmxModel = self.__model
        mesh = self.__meshObj.data
        vertex_map = self.__vertex_map

        loop_indices_orig = tuple(i for f in pmxModel.faces for i in f)
        loop_indices = tuple(vertex_map[i][1] for i in loop_indices_orig) if vertex_map else loop_indices_orig
        material_indices = tuple(i for i, c in enumerate(self.__materialFaceCountTable) for x in range(c))

        mesh.loops.add(len(pmxModel.faces)*3)
        mesh.loops.foreach_set('vertex_index', loop_indices)

        mesh.polygons.add(len(pmxModel.faces))
        mesh.polygons.foreach_set('loop_start', tuple(range(0, len(mesh.loops), 3)))
        mesh.polygons.foreach_set('loop_total', (3,)*len(pmxModel.faces))
        mesh.polygons.foreach_set('use_smooth', (True,)*len(pmxModel.faces))
        mesh.polygons.foreach_set('material_index', material_indices)

        uv_textures, uv_layers = getattr(mesh, 'uv_textures', mesh.uv_layers), mesh.uv_layers
        uv_tex = uv_textures.new()
        uv_layer = uv_layers[uv_tex.name]
        uv_table = {vi:self.flipUV_V(v.uv) for vi, v in enumerate(pmxModel.vertices)}
        uv_layer.data.foreach_set('uv', tuple(v for i in loop_indices_orig for v in uv_table[i]))

        if hasattr(mesh, 'uv_textures'):
            for bf, mi in zip(uv_tex.data, material_indices):
                bf.image = self.__imageTable.get(mi, None)

        if pmxModel.header and pmxModel.header.additional_uvs:
            logging.info('Importing %d additional uvs', pmxModel.header.additional_uvs)
            zw_data_map = collections.OrderedDict()
            split_uvzw = lambda uvi: (self.flipUV_V(uvi[:2]), uvi[2:])
            for i in range(pmxModel.header.additional_uvs):
                add_uv = uv_layers[uv_textures.new(name='UV'+str(i+1)).name]
                logging.info(' - %s...(uv channels)', add_uv.name)
                uv_table = {vi:split_uvzw(v.additional_uvs[i]) for vi, v in enumerate(pmxModel.vertices)}
                add_uv.data.foreach_set('uv', tuple(v for i in loop_indices_orig for v in uv_table[i][0]))
                if not any(any(s[1]) for s in uv_table.values()):
                    logging.info('\t- zw are all zeros: %s', add_uv.name)
                else:
                    zw_data_map['_'+add_uv.name] = {k:self.flipUV_V(v[1]) for k, v in uv_table.items()}
            for name, zw_table in zw_data_map.items():
                logging.info(' - %s...(zw channels of %s)', name, name[1:])
                add_zw = uv_textures.new(name=name)
                if add_zw is None:
                    logging.warning('\t* Lost zw channels')
                    continue
                add_zw = uv_layers[add_zw.name]
                add_zw.data.foreach_set('uv', tuple(v for i in loop_indices_orig for v in zw_table[i]))

        if bpy.app.version >= (2, 80, 0):
            self.__fixOverlappingFaceMaterials(mesh.materials, mesh.vertices, loop_indices, material_indices)

    def __fixOverlappingFaceMaterials(self, materials, vertices, loop_indices, material_indices):
        # This is not the best way to setup blend_method, might just work for some common cases. And FnMaterial.update_alpha() is still using 'HASHED'.
        # For EEVEE, basically users should know which blend_method is best for each material of their models.
        # For Cycles, users have to offset or delete those z-fighting faces to fix it manually.
        check = {}
        mi_skip = -1
        def _rounded_co(co): return tuple(round(v, 6) for v in co)
        assert(len(loop_indices) == len(material_indices)*3)
        for i, mi in enumerate(material_indices):
            if mi > mi_skip:
                si = 3*i
                verts = tuple(sorted(_rounded_co(vertices[vi].co) for vi in loop_indices[si:si+3]))
                if verts not in check:
                    check[verts] = mi
                elif check[verts] < mi:
                    logging.debug(' >> fix blend method of material: %s', materials[mi].name)
                    materials[mi].blend_method = 'BLEND'
                    materials[mi].show_transparent_back = False
                    mi_skip = mi

    def __importVertexMorphs(self):
        mmd_root = self.__root.mmd_root
        categories = self.CATEGORIES
        self.__createBasisShapeKey()
        for morph in (x for x in self.__model.morphs if isinstance(x, pmx.VertexMorph)):
            shapeKey = self.__meshObj.shape_key_add(name=morph.name)
            vtx_morph = mmd_root.vertex_morphs.add()
            vtx_morph.name = morph.name
            vtx_morph.name_e = morph.name_e
            vtx_morph.category = categories.get(morph.category, 'OTHER')
            for md in morph.offsets:
                shapeKeyPoint = shapeKey.data[md.index]
                shapeKeyPoint.co += Vector(md.offset).xzy * self.__scale

    def __importMaterialMorphs(self):
        mmd_root = self.__root.mmd_root
        categories = self.CATEGORIES
        for morph in (x for x in self.__model.morphs if isinstance(x, pmx.MaterialMorph)):
            mat_morph = mmd_root.material_morphs.add()
            mat_morph.name = morph.name
            mat_morph.name_e = morph.name_e
            mat_morph.category = categories.get(morph.category, 'OTHER')
            for morph_data in morph.offsets:
                data = mat_morph.data.add()
                data.related_mesh = self.__meshObj.data.name
                if 0 <= morph_data.index < len(self.__materialTable):
                    data.material = self.__materialTable[morph_data.index].name
                data.offset_type = ['MULT', 'ADD'][morph_data.offset_type]
                data.diffuse_color = morph_data.diffuse_offset
                data.specular_color = morph_data.specular_offset
                data.shininess = morph_data.shininess_offset
                data.ambient_color = morph_data.ambient_offset
                data.edge_color = morph_data.edge_color_offset
                data.edge_weight = morph_data.edge_size_offset
                data.texture_factor = morph_data.texture_factor
                data.sphere_texture_factor = morph_data.sphere_texture_factor
                data.toon_texture_factor = morph_data.toon_texture_factor

    def __importBoneMorphs(self):
        mmd_root = self.__root.mmd_root
        categories = self.CATEGORIES
        for morph in (x for x in self.__model.morphs if isinstance(x, pmx.BoneMorph)):
            bone_morph = mmd_root.bone_morphs.add()
            bone_morph.name = morph.name
            bone_morph.name_e = morph.name_e
            bone_morph.category = categories.get(morph.category, 'OTHER')
            for morph_data in morph.offsets:
                if not (0 <= morph_data.index < len(self.__boneTable)):
                    continue
                data = bone_morph.data.add()
                bl_bone = self.__boneTable[morph_data.index]
                data.bone = bl_bone.name
                converter = BoneConverter(bl_bone, self.__scale)
                data.location = converter.convert_location(morph_data.location_offset)
                data.rotation = converter.convert_rotation(morph_data.rotation_offset)

    def __importUVMorphs(self):
        mmd_root = self.__root.mmd_root
        categories = self.CATEGORIES
        __OffsetData = collections.namedtuple('OffsetData', 'index, offset')
        __convert_offset = lambda x: (x[0], -x[1], x[2], -x[3])
        for morph in (x for x in self.__model.morphs if isinstance(x, pmx.UVMorph)):
            uv_morph = mmd_root.uv_morphs.add()
            uv_morph.name = morph.name
            uv_morph.name_e = morph.name_e
            uv_morph.category = categories.get(morph.category, 'OTHER')
            uv_morph.uv_index = morph.uv_index

            offsets = (__OffsetData(d.index, __convert_offset(d.offset)) for d in morph.offsets)
            FnMorph.store_uv_morph_data(self.__meshObj, uv_morph, offsets, '')
            uv_morph.data_type = 'VERTEX_GROUP'

    def __importGroupMorphs(self):
        mmd_root = self.__root.mmd_root
        categories = self.CATEGORIES
        morph_types = self.MORPH_TYPES
        pmx_morphs = self.__model.morphs
        for morph in (x for x in pmx_morphs if isinstance(x, pmx.GroupMorph)):
            group_morph = mmd_root.group_morphs.add()
            group_morph.name = morph.name
            group_morph.name_e = morph.name_e
            group_morph.category = categories.get(morph.category, 'OTHER')
            for morph_data in morph.offsets:
                if not (0 <= morph_data.morph < len(pmx_morphs)):
                    continue
                data = group_morph.data.add()
                m = pmx_morphs[morph_data.morph]
                data.name = m.name
                data.morph_type = morph_types[m.type_index()]
                data.factor = morph_data.factor

    def __importDisplayFrames(self):
        pmxModel = self.__model
        root = self.__root
        morph_types = self.MORPH_TYPES

        for i in pmxModel.display:
            frame = root.mmd_root.display_item_frames.add()
            frame.name = i.name
            frame.name_e = i.name_e
            frame.is_special = i.isSpecial
            for disp_type, index in i.data:
                item = frame.data.add()
                if disp_type == 0:
                    item.type = 'BONE'
                    item.name = self.__boneTable[index].name
                elif disp_type == 1:
                    item.type = 'MORPH'
                    morph = pmxModel.morphs[index]
                    item.name = morph.name
                    item.morph_type = morph_types[morph.type_index()]
                else:
                    raise Exception('Unknown display item type.')

        DisplayItemQuickSetup.apply_bone_groups(root.mmd_root, self.__armObj)

    def __addArmatureModifier(self, meshObj, armObj):
        armModifier = meshObj.modifiers.new(name='Armature', type='ARMATURE')
        armModifier.object = armObj
        armModifier.use_vertex_groups = True
        armModifier.name = 'mmd_bone_order_override'
        armModifier.show_render = armModifier.show_viewport = (len(meshObj.data.vertices) > 0)

    def __assignCustomNormals(self):
        mesh = self.__meshObj.data
        if not hasattr(mesh, 'has_custom_normals'):
            logging.info(' * No support for custom normals!!')
            return
        logging.info('Setting custom normals...')
        if self.__vertex_map:
            verts, faces = self.__model.vertices, self.__model.faces
            custom_normals = [(Vector(verts[i].normal).xzy).normalized() for f in faces for i in f]
            mesh.normals_split_custom_set(custom_normals)
        else:
            custom_normals = [(Vector(v.normal).xzy).normalized() for v in self.__model.vertices]
            mesh.normals_split_custom_set_from_vertices(custom_normals)
        mesh.use_auto_smooth = True
        logging.info('   - Done!!')

    def __renameLRBones(self, use_underscore):
        pose_bones = self.__armObj.pose.bones
        for i in pose_bones:
            self.__rig.renameBone(i.name, utils.convertNameToLR(i.name, use_underscore))
            # self.__meshObj.vertex_groups[i.mmd_bone.name_j].name = i.name

    def __translateBoneNames(self):
        pose_bones = self.__armObj.pose.bones
        for i in pose_bones:
            self.__rig.renameBone(i.name, self.__translator.translate(i.name))

    def __fixRepeatedMorphName(self):
        used_names = set()
        for m in self.__model.morphs:
            m.name = utils.uniqueName(m.name or 'Morph', used_names)
            used_names.add(m.name)

    def execute(self, **args):
        if 'pmx' in args:
            self.__model = args['pmx']
        else:
            self.__model = pmx.load(args['filepath'])
        self.__fixRepeatedMorphName()

        types = args.get('types', set())
        clean_model = args.get('clean_model', False)
        remove_doubles = args.get('remove_doubles', False)
        self.__scale = args.get('scale', 1.0)
        self.__use_mipmap = args.get('use_mipmap', True)
        self.__sph_blend_factor = args.get('sph_blend_factor', 1.0)
        self.__spa_blend_factor = args.get('spa_blend_factor', 1.0)
        self.__fix_IK_links = args.get('fix_IK_links', False)
        self.__apply_bone_fixed_axis = args.get('apply_bone_fixed_axis', False)
        self.__translator = args.get('translator', None)

        logging.info('****************************************')
        logging.info(' mmd_tools.import_pmx module')
        logging.info('----------------------------------------')
        logging.info(' Start to load model data form a pmx file')
        logging.info('            by the mmd_tools.pmx modlue.')
        logging.info('')

        start_time = time.time()

        self.__createObjects()

        if 'MESH' in types:
            if clean_model:
                _PMXCleaner.clean(self.__model, 'MORPHS' not in types)
            if remove_doubles:
                self.__vertex_map = _PMXCleaner.remove_doubles(self.__model, 'MORPHS' not in types)
            self.__createMeshObject()
            self.__importVertices()
            self.__importMaterials()
            self.__importFaces()
            self.__meshObj.data.update()
            self.__assignCustomNormals()
            self.__storeVerticesSDEF()

        if 'ARMATURE' in types:
            # for tracking bone order
            if 'MESH' not in types:
                self.__createMeshObject()
                self.__importVertexGroup()
            self.__importBones()
            if args.get('rename_LR_bones', False):
                use_underscore = args.get('use_underscore', False)
                self.__renameLRBones(use_underscore)
            if self.__translator:
                self.__translateBoneNames()
            if self.__apply_bone_fixed_axis:
                FnBone.apply_bone_fixed_axis(self.__armObj)
            FnBone.apply_additional_transformation(self.__armObj)

        if 'PHYSICS' in types:
            self.__importRigids()
            self.__importJoints()

        if 'DISPLAY' in types:
            self.__importDisplayFrames()
        else:
            self.__rig.initialDisplayFrames()

        if 'MORPHS' in types:
            self.__importGroupMorphs()
            self.__importVertexMorphs()
            self.__importBoneMorphs()
            self.__importMaterialMorphs()
            self.__importUVMorphs()

        if self.__meshObj:
            self.__addArmatureModifier(self.__meshObj, self.__armObj)

        #bpy.context.scene.gravity[2] = -9.81 * 10 * self.__scale
        root = self.__root
        if 'ARMATURE' in types:
            root.mmd_root.show_armature = True
        if 'MESH' in types:
            root.mmd_root.show_meshes = True
        self.__targetScene.active_object = root
        root.select = True

        logging.info(' Finished importing the model in %f seconds.', time.time() - start_time)
        logging.info('----------------------------------------')
        logging.info(' mmd_tools.import_pmx module')
        logging.info('****************************************')


class _PMXCleaner:
    @classmethod
    def clean(cls, pmx_model, mesh_only):
        logging.info('Cleaning PMX data...')
        pmx_faces = pmx_model.faces
        pmx_vertices = pmx_model.vertices

        # clean face/vertex
        cls.__clean_pmx_faces(pmx_faces, pmx_model.materials, lambda f: frozenset(f))

        index_map = {v:v for f in pmx_faces for v in f}
        is_index_clean = len(index_map) == len(pmx_vertices)
        if is_index_clean:
            logging.info('   (vertices is clean)')
        else:
            new_vertex_count = 0
            for v in sorted(index_map):
                if v != new_vertex_count:
                    pmx_vertices[new_vertex_count] = pmx_vertices[v]
                    index_map[v] = new_vertex_count
                new_vertex_count += 1
            logging.warning('   - removed %d vertices', len(pmx_vertices)-new_vertex_count)
            del pmx_vertices[new_vertex_count:]

            # update vertex indices of faces
            for f in pmx_faces:
                f[:] = [index_map[v] for v in f]

        if mesh_only:
            logging.info('   - Done (mesh only)!!')
            return

        if not is_index_clean:
            # clean vertex/uv morphs
            def __update_index(x):
                x.index = index_map.get(x.index, None)
                return x.index is not None
            cls.__clean_pmx_morphs(pmx_model.morphs, __update_index)
        logging.info('   - Done!!')

    @classmethod
    def remove_doubles(cls, pmx_model, mesh_only):
        logging.info('Removing doubles...')
        pmx_vertices = pmx_model.vertices

        vertex_map = [None] * len(pmx_vertices)
        # gather vertex data
        for i, v in enumerate(pmx_vertices):
            vertex_map[i] = [tuple(v.co)]
        if not mesh_only:
            for m in pmx_model.morphs:
                if not isinstance(m, pmx.VertexMorph) and not isinstance(m, pmx.UVMorph):
                    continue
                for x in m.offsets:
                    vertex_map[x.index].append(tuple(x.offset))
        # generate vertex merging table
        keys = {}
        for i, v in enumerate(vertex_map):
            k = tuple(v)
            if k in keys:
                vertex_map[i] = keys[k] # merge pmx_vertices[i] to pmx_vertices[keys[k][0]]
            else:
                vertex_map[i] = keys[k] = (i, len(keys)) # (pmx index, blender index)
        counts = len(vertex_map) - len(keys)
        keys.clear()
        if counts:
            logging.warning('   - %d vertices will be removed', counts)
        else:
            logging.info('   - Done (no changes)!!')
            return None

        # clean face
        #face_key_func = lambda f: frozenset(vertex_map[x][0] for x in f)
        face_key_func = lambda f: frozenset({vertex_map[x][0]:tuple(pmx_vertices[x].uv) for x in f}.items())
        cls.__clean_pmx_faces(pmx_model.faces, pmx_model.materials, face_key_func)

        if mesh_only:
            logging.info('   - Done (mesh only)!!')
        else:
            # clean vertex/uv morphs
            def __update_index(x):
                indices = vertex_map[x.index]
                x.index = indices[1] if x.index == indices[0] else None
                return x.index is not None
            cls.__clean_pmx_morphs(pmx_model.morphs, __update_index)
            logging.info('   - Done!!')
        return vertex_map


    @staticmethod
    def __clean_pmx_faces(pmx_faces, pmx_materials, face_key_func):
        new_face_count = 0
        face_iter = iter(pmx_faces)
        for mat in pmx_materials:
            used_faces = set()
            new_vertex_count = 0
            for i in range(int(mat.vertex_count/3)):
                f = next(face_iter)

                f_key = face_key_func(f)
                if len(f_key) != 3 or f_key in used_faces:
                    continue
                used_faces.add(f_key)

                pmx_faces[new_face_count] = list(f)
                new_face_count += 1
                new_vertex_count += 3
            mat.vertex_count = new_vertex_count
        face_iter = None
        if new_face_count == len(pmx_faces):
            logging.info('   (faces is clean)')
        else:
            logging.warning('   - removed %d faces', len(pmx_faces)-new_face_count)
            del pmx_faces[new_face_count:]

    @staticmethod
    def __clean_pmx_morphs(pmx_morphs, index_update_func):
        for m in pmx_morphs:
            if not isinstance(m, pmx.VertexMorph) and not isinstance(m, pmx.UVMorph):
                continue
            old_len = len(m.offsets)
            m.offsets = [x for x in m.offsets if index_update_func(x)]
            counts = old_len - len(m.offsets)
            if counts:
                logging.warning('   - removed %d (of %d) offsets of "%s"', counts, old_len, m.name)

