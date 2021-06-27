# -*- coding: utf-8 -*-

import logging

import bpy
from mathutils import Matrix

from mmd_tools_local import bpyutils
from mmd_tools_local.core import vmd
from mmd_tools_local.core import vpd


class VPDImporter:
    def __init__(self, filepath, scale=1.0, bone_mapper=None, use_pose_mode=False):
        self.__pose_name = bpy.path.display_name_from_filepath(filepath)
        self.__vpd_file = vpd.File()
        self.__vpd_file.load(filepath=filepath)
        self.__scale = scale
        self.__bone_mapper = bone_mapper
        if use_pose_mode:
            self.__bone_util_cls = vmd.importer.BoneConverterPoseMode
            self.__assignToArmature = self.__assignToArmaturePoseMode
        else:
            self.__bone_util_cls = vmd.importer.BoneConverter
            self.__assignToArmature = self.__assignToArmatureSimple
        logging.info('Loaded %s', self.__vpd_file)


    def __assignToArmaturePoseMode(self, armObj):
        pose_orig = {b:b.matrix_basis.copy() for b in armObj.pose.bones}
        try:
            self.__assignToArmatureSimple(armObj, reset_transform=False)
        finally:
            for bone, matrix_basis in pose_orig.items():
                bone.matrix_basis = matrix_basis


    def __assignToArmatureSimple(self, armObj, reset_transform=True):
        logging.info('  - assigning to armature "%s"', armObj.name)

        pose_bones = armObj.pose.bones
        if self.__bone_mapper:
            pose_bones = self.__bone_mapper(armObj)

        matmul = bpyutils.matmul
        pose_data = {}
        for b in self.__vpd_file.bones:
            bone = pose_bones.get(b.bone_name, None)
            if bone is None:
                logging.warning(' * Bone not found: %s', b.bone_name)
                continue
            converter = self.__bone_util_cls(bone, self.__scale)
            loc = converter.convert_location(b.location)
            rot = converter.convert_rotation(b.rotation)
            assert(bone not in pose_data)
            pose_data[bone] = matmul(Matrix.Translation(loc), rot.to_matrix().to_4x4())

        for bone in armObj.pose.bones:
            vpd_pose = pose_data.get(bone, None)
            bone.bone.select = bool(vpd_pose)
            if vpd_pose:
                bone.matrix_basis = vpd_pose
            elif reset_transform:
                bone.matrix_basis.identity()

        if armObj.pose_library is None:
            armObj.pose_library = bpy.data.actions.new(name='PoseLib')

        frames = [m.frame for m in armObj.pose_library.pose_markers]
        frame_max = max(frames) if len(frames) else 0
        bpy.ops.poselib.pose_add(frame=frame_max+1, name=self.__pose_name)


    def __assignToMesh(self, meshObj):
        if meshObj.data.shape_keys is None:
            return

        logging.info('  - assigning to mesh "%s"', meshObj.name)

        key_blocks = meshObj.data.shape_keys.key_blocks
        for i in key_blocks.values():
            i.value = 0

        for m in self.__vpd_file.morphs:
            shape_key = key_blocks.get(m.morph_name, None)
            if shape_key is None:
                logging.warning(' * Shape key not found: %s', m.morph_name)
                continue
            shape_key.value = m.weight


    def assign(self, obj):
        if obj is None:
            return
        if obj.type == 'ARMATURE':
            with bpyutils.select_object(obj):
                bpy.ops.object.mode_set(mode='POSE')
                self.__assignToArmature(obj)
        elif obj.type == 'MESH':
            self.__assignToMesh(obj)
        else:
            pass

