# -*- coding: utf-8 -*-


import os
import re
import copy
import logging

import mathutils

import mmd_tools_local.core.pmx.importer as import_pmx
import mmd_tools_local.core.pmd as pmd
import mmd_tools_local.core.pmx as pmx

from math import radians

class PMDImporter:
    def execute(self, **args):
        args['pmx'] = import_pmd_to_pmx(args['filepath'])
        importer = import_pmx.PMXImporter()
        importer.execute(**args)

def import_pmd_to_pmx(filepath):
    """ Import pmd file
    """
    target_path = filepath
    pmd_model = pmd.load(target_path)


    logging.info('')
    logging.info('****************************************')
    logging.info(' mmd_tools.import_pmd module')
    logging.info('----------------------------------------')
    logging.info(' Start to convert pmd data into pmx data')
    logging.info('              by the mmd_tools.pmd modlue.')
    logging.info('')

    pmx_model = pmx.Model()
    pmx_model.filepath = filepath

    pmx_model.name = pmd_model.name
    pmx_model.name_e = pmd_model.name_e
    pmx_model.comment = pmd_model.comment
    pmx_model.comment_e = pmd_model.comment_e

    pmx_model.vertices = []

    # convert vertices
    logging.info('')
    logging.info('------------------------------')
    logging.info(' Convert Vertices')
    logging.info('------------------------------')
    for v in pmd_model.vertices:
        pmx_v = pmx.Vertex()
        pmx_v.co = v.position
        pmx_v.normal = v.normal
        pmx_v.uv = v.uv
        pmx_v.additional_uvs= []
        pmx_v.edge_scale = 1 if v.enable_edge == 0 else 0

        weight = pmx.BoneWeight()
        if v.bones[0] != v.bones[1]:
            weight.type = pmx.BoneWeight.BDEF2
            weight.bones = v.bones
            weight.weights = [float(v.weight)/100.0]
        else:
            weight.type = pmx.BoneWeight.BDEF1
            weight.bones = [v.bones[0]]
            weight.weights = [float(v.weight)/100.0]

        pmx_v.weight = weight

        pmx_model.vertices.append(pmx_v)
    logging.info('----- Converted %d vertices', len(pmx_model.vertices))

    logging.info('')
    logging.info('------------------------------')
    logging.info(' Convert Faces')
    logging.info('------------------------------')
    for f in pmd_model.faces:
        pmx_model.faces.append(f)
    logging.info('----- Converted %d faces', len(pmx_model.faces))

    knee_bones = []

    logging.info('')
    logging.info('------------------------------')
    logging.info(' Convert Bones')
    logging.info('------------------------------')
    # ボーンの種類
    # 0:回転 1:回転/移動 2:IK 3:不明 4:IK影響下 5:回転影響下 6:IK接続先 7:非表示/ボーン接続先 8:捩り 9:回転運動
    for i, bone in enumerate(pmd_model.bones):
        pmx_bone = pmx.Bone()
        pmx_bone.name = bone.name
        pmx_bone.name_e = bone.name_e
        pmx_bone.location = bone.position
        pmx_bone.parent = bone.parent
        if bone.type != 9 and bone.type != 8:
            pmx_bone.displayConnection = bone.tail_bone
        else:
            pmx_bone.displayConnection = -1
        if pmx_bone.displayConnection <= 0:
            pmx_bone.displayConnection = (0.0, 0.0, 0.0)
        pmx_bone.isIK = False
        if bone.type == 0:
            pmx_bone.isMovable = False
        elif bone.type == 1:
            pass
        elif bone.type == 2:
            pmx_bone.transform_order = 1
        elif bone.type == 3:
            pmx_bone.isMovable = False
        elif bone.type == 4:
            pmx_bone.isMovable = False
        elif bone.type == 5:
            pmx_bone.transform_order = 2
            pmx_bone.isMovable = False
            pmx_bone.hasAdditionalRotate = True
            pmx_bone.additionalTransform = (bone.ik_bone, 1.0)
        elif bone.type == 6:
            pmx_bone.visible = False
            pmx_bone.isMovable = False
        elif bone.type == 7:
            pmx_bone.visible = False
            pmx_bone.isMovable = False
        elif bone.type == 8:
            pmx_bone.isMovable = False
            tail_loc = mathutils.Vector(pmd_model.bones[bone.tail_bone].position)
            loc = mathutils.Vector(bone.position)
            vec = tail_loc - loc
            vec.normalize()
            pmx_bone.axis=list(vec)
        elif bone.type == 9:
            pmx_bone.visible = False
            pmx_bone.isMovable = False
            pmx_bone.hasAdditionalRotate = True
            pmx_bone.additionalTransform = (bone.tail_bone, float(bone.ik_bone)/100.0)

        pmx_model.bones.append(pmx_bone)

        if re.search(u'ひざ$', pmx_bone.name):
            knee_bones.append(i)

    for i in pmx_model.bones:
        if 0 <= i.parent < len(pmx_model.bones) and i.transform_order < pmx_model.bones[i.parent].transform_order:
            i.transform_order = pmx_model.bones[i.parent].transform_order
    logging.info('----- Converted %d boness', len(pmx_model.bones))

    logging.info('')
    logging.info('------------------------------')
    logging.info(' Convert IKs')
    logging.info('------------------------------')
    applied_ik_bones = []
    for ik in pmd_model.iks:
        if ik.bone in applied_ik_bones:
            logging.info('The bone %s is targeted by two or more IK bones.', pmx_model.bones[ik.bone].name)
            b = pmx_model.bones[ik.bone]
            t = copy.deepcopy(b)
            t.name += '+'
            t.parent = ik.bone
            t.ik_links = []
            pmx_model.bones.append(t)
            ik.bone = len(pmx_model.bones) - 1
            logging.info('Duplicate the bone: %s -> %s', b.name, t.name)
        pmx_bone = pmx_model.bones[ik.bone]
        logging.debug('Add IK settings to the bone %s', pmx_bone.name)
        pmx_bone.isIK = True
        pmx_bone.target = ik.target_bone
        pmx_bone.loopCount = ik.iterations
        pmx_bone.rotationConstraint = ik.control_weight*4
        for i in ik.ik_child_bones:
            ik_link = pmx.IKLink()
            ik_link.target = i
            if i in knee_bones:
                ik_link.maximumAngle = [radians(-0.5), 0.0, 0.0]
                ik_link.minimumAngle = [radians(-180.0), 0.0, 0.0]
                logging.info('  Add knee constraints to %s', i)
            logging.debug('  IKLink: %s(index: %d)', pmx_model.bones[i].name, i)
            pmx_bone.ik_links.append(ik_link)
        applied_ik_bones.append(ik.bone)
    logging.info('----- Converted %d bones', len(pmd_model.iks))

    texture_map = {}
    toon_texture_map = {}
    logging.info('')
    logging.info('------------------------------')
    logging.info(' Convert Materials')
    logging.info('------------------------------')
    for i, mat in enumerate(pmd_model.materials):
        pmx_mat = pmx.Material()
        pmx_mat.name = '材質%d'%(i+1)
        pmx_mat.name_e = 'Material%d'%(i+1)
        pmx_mat.diffuse = mat.diffuse
        pmx_mat.specular = mat.specular
        pmx_mat.shininess = mat.shininess
        pmx_mat.ambient = mat.ambient
        pmx_mat.is_double_sided = (mat.diffuse[3] < 1.0)
        pmx_mat.enabled_self_shadow_map = abs(mat.diffuse[3] - 0.98) > 1e-7 # consider precision error
        pmx_mat.enabled_toon_edge = (mat.edge_flag != 0)
        pmx_mat.enabled_self_shadow = pmx_mat.enabled_self_shadow_map # True (in MMD)
        pmx_mat.enabled_drop_shadow = pmx_mat.enabled_toon_edge # True (in MMD)
        pmx_mat.edge_color = (0, 0, 0, 1)
        pmx_mat.vertex_count = mat.vertex_count
        if len(mat.texture_path) > 0:
            tex_path = mat.texture_path
            if tex_path not in texture_map:
                logging.info('  Create pmx.Texture -------- %s', tex_path)
                tex = pmx.Texture()
                tex.path = os.path.normpath(os.path.join(os.path.dirname(target_path), tex_path))
                pmx_model.textures.append(tex)
                texture_map[tex_path] = len(pmx_model.textures) - 1
            pmx_mat.texture = texture_map[tex_path]
        if len(mat.sphere_path) > 0:
            tex_path = mat.sphere_path
            if tex_path not in texture_map:
                logging.info('  Create pmx.Texture -Sphere- %s', tex_path)
                tex = pmx.Texture()
                tex.path = os.path.normpath(os.path.join(os.path.dirname(target_path), tex_path))
                pmx_model.textures.append(tex)
                texture_map[tex_path] = len(pmx_model.textures) - 1
            pmx_mat.sphere_texture = texture_map[tex_path]
            pmx_mat.sphere_texture_mode = mat.sphere_mode
        pmx_mat.is_shared_toon_texture = False
        pmx_mat.toon_texture = -1
        if mat.toon_index in range(len(pmd_model.toon_textures)):
            tex_path = pmd_model.toon_textures[mat.toon_index]
            if tex_path not in toon_texture_map:
                logging.info('  Create pmx.Texture --Toon-- %s', tex_path)
                if re.match(r'toon(0[1-9]|10)\.bmp$', tex_path):
                    toon_texture_map[tex_path] = (True, int(tex_path[-6:-4])-1)
                elif tex_path in texture_map:
                    toon_texture_map[tex_path] = (False, texture_map[tex_path])
                else:
                    tex = pmx.Texture()
                    tex.path = os.path.normpath(os.path.join(os.path.dirname(target_path), tex_path))
                    pmx_model.textures.append(tex)
                    texture_map[tex_path] = len(pmx_model.textures) - 1
                    toon_texture_map[tex_path] = (False, len(pmx_model.textures)-1)
            pmx_mat.is_shared_toon_texture, pmx_mat.toon_texture = toon_texture_map[tex_path]
        pmx_model.materials.append(pmx_mat)
    logging.info('----- Converted %d materials', len(pmx_model.materials))

    logging.info('')
    logging.info('------------------------------')
    logging.info(' Convert Morphs')
    logging.info('------------------------------')
    morph_index_map = []
    t = list(filter(lambda x: x.type == 0, pmd_model.morphs))
    if len(t) == 0:
        logging.error('Not found the base morph')
        logging.error('Skip converting vertex morphs.')
    else:
        if len(t) > 1:
            logging.warning('Found two or more base morphs.')
        vertex_map = []
        for i in t[0].data:
            vertex_map.append(i.index)

        for morph in pmd_model.morphs:
            logging.debug('Vertex Morph: %s', morph.name)
            if morph.type == 0:
                morph_index_map.append(-1)
                continue
            pmx_morph = pmx.VertexMorph(morph.name, morph.name_e, morph.type)
            for i in morph.data:
                mo = pmx.VertexMorphOffset()
                mo.index = vertex_map[i.index]
                mo.offset = i.offset
                pmx_morph.offsets.append(mo)
            morph_index_map.append(len(pmx_model.morphs))
            pmx_model.morphs.append(pmx_morph)
    logging.info('----- Converted %d morphs', len(pmx_model.morphs))

    logging.info('')
    logging.info('------------------------------')
    logging.info(' Convert Display Items')
    logging.info('------------------------------')
    if len(pmd_model.bones) > 0:
        pmx_model.display[0].data.append((0, 0))
    if len(morph_index_map) > 0:
        dsp_face = pmx_model.display[1]
        for i, morph_index in enumerate(pmd_model.facial_disp_morphs):
            morph_index = morph_index_map[morph_index]
            if morph_index >= 0:
                dsp_face.data.append((1, morph_index))
    bone_disps_e = pmd_model.bone_disp_names[1]
    for i, bone_disp_name in enumerate(pmd_model.bone_disp_names[0]):
        bone_disp_list = pmd_model.bone_disp_lists[bone_disp_name]
        d = pmx.Display()
        d.name = bone_disp_name.strip()
        if bone_disps_e:
            d.name_e = bone_disps_e[i].strip()
        for bone_index in bone_disp_list:
            d.data.append((0, bone_index))
        pmx_model.display.append(d)
    logging.info('----- Converted %d display items', len(pmx_model.display))

    logging.info('')
    logging.info('------------------------------')
    logging.info(' Convert Rigid bodies')
    logging.info('------------------------------')
    for rigid in pmd_model.rigid_bodies:
        pmx_rigid = pmx.Rigid()

        pmx_rigid.name = rigid.name

        pmx_rigid.bone = rigid.bone
        pmx_rigid.collision_group_number = rigid.collision_group_number
        pmx_rigid.collision_group_mask = rigid.collision_group_mask
        pmx_rigid.type = rigid.type

        pmx_rigid.size = rigid.size

        # a location parameter of pmd.RigidBody is the offset from the relational bone or the center bone.
        if rigid.bone == -1:
            t = 0
        else:
            t = rigid.bone
        pmx_rigid.location = mathutils.Vector(pmx_model.bones[t].location) + mathutils.Vector(rigid.location)
        pmx_rigid.rotation = rigid.rotation

        pmx_rigid.mass = rigid.mass
        pmx_rigid.velocity_attenuation = rigid.velocity_attenuation
        pmx_rigid.rotation_attenuation = rigid.rotation_attenuation
        pmx_rigid.bounce = rigid.bounce
        pmx_rigid.friction = rigid.friction
        pmx_rigid.mode = rigid.mode

        pmx_model.rigids.append(pmx_rigid)
    logging.info('----- Converted %d rigid bodies', len(pmx_model.rigids))

    logging.info('')
    logging.info('------------------------------')
    logging.info(' Convert Joints')
    logging.info('------------------------------')
    for joint in pmd_model.joints:
        pmx_joint = pmx.Joint()

        pmx_joint.name = joint.name
        pmx_joint.src_rigid = joint.src_rigid
        pmx_joint.dest_rigid = joint.dest_rigid

        pmx_joint.location = joint.location
        pmx_joint.rotation = joint.rotation

        pmx_joint.maximum_location = joint.maximum_location
        pmx_joint.minimum_location = joint.minimum_location
        pmx_joint.maximum_rotation = joint.maximum_rotation
        pmx_joint.minimum_rotation = joint.minimum_rotation

        pmx_joint.spring_constant = joint.spring_constant
        pmx_joint.spring_rotation_constant = joint.spring_rotation_constant

        pmx_model.joints.append(pmx_joint)
    logging.info('----- Converted %d joints', len(pmx_model.joints))

    logging.info(' Finish converting pmd into pmx.')
    logging.info('----------------------------------------')
    logging.info(' mmd_tools.import_pmd module')
    logging.info('****************************************')

    return pmx_model
