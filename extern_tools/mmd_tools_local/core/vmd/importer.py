# -*- coding: utf-8 -*-

import logging
import os

import bpy
import math
from mathutils import Vector, Quaternion

from mmd_tools_local import utils
from mmd_tools_local.bpyutils import matmul
from mmd_tools_local.core import vmd
from mmd_tools_local.core.camera import MMDCamera
from mmd_tools_local.core.lamp import MMDLamp


class _MirrorMapper:
    def __init__(self, data_map=None):
        from mmd_tools_local.operators.view import FlipPose
        self.__data_map = data_map
        self.__flip_name = FlipPose.flip_name

    def get(self, name, default=None):
        return self.__data_map.get(self.__flip_name(name), None) or self.__data_map.get(name, default)

    @staticmethod
    def get_location(location):
        return (-location[0], location[1], location[2])

    @staticmethod
    def get_rotation(rotation_xyzw):
        return (rotation_xyzw[0], -rotation_xyzw[1], -rotation_xyzw[2], rotation_xyzw[3])

    @staticmethod
    def get_rotation3(rotation_xyz):
        return (rotation_xyz[0], -rotation_xyz[1], -rotation_xyz[2])


class RenamedBoneMapper:
    def __init__(self, armObj=None, rename_LR_bones=True, use_underscore=False, translator=None):
        self.__pose_bones = armObj.pose.bones if armObj else None
        self.__rename_LR_bones = rename_LR_bones
        self.__use_underscore = use_underscore
        self.__translator = translator

    def init(self, armObj):
        self.__pose_bones = armObj.pose.bones
        return self

    def get(self, bone_name, default=None):
        bl_bone_name = bone_name
        if self.__rename_LR_bones:
            bl_bone_name = utils.convertNameToLR(bl_bone_name, self.__use_underscore)
        if self.__translator:
            bl_bone_name = self.__translator.translate(bl_bone_name)
        return self.__pose_bones.get(bl_bone_name, default)


class _InterpolationHelper:
    def __init__(self, mat):
        self.__indices = indices = [0, 1, 2]
        l = sorted((-abs(mat[i][j]), i, j) for i in range(3) for j in range(3))
        _, i, j = l[0]
        if i != j:
            indices[i], indices[j] = indices[j], indices[i]
        _, i, j = next(k for k in l if k[1] != i and k[2] != j)
        if indices[i] != j:
            idx = indices.index(j)
            indices[i], indices[idx] = indices[idx], indices[i]

    def convert(self, interpolation_xyz):
        return (interpolation_xyz[i] for i in self.__indices)

class BoneConverter:
    def __init__(self, pose_bone, scale, invert=False):
        mat = pose_bone.bone.matrix_local.to_3x3()
        mat[1], mat[2] = mat[2].copy(), mat[1].copy()
        self.__mat = mat.transposed()
        self.__scale = scale
        if invert:
            self.__mat.invert()
        self.convert_interpolation = _InterpolationHelper(self.__mat).convert

    def convert_location(self, location):
        return matmul(self.__mat, Vector(location)) * self.__scale

    def convert_rotation(self, rotation_xyzw):
        rot = Quaternion()
        rot.x, rot.y, rot.z, rot.w = rotation_xyzw
        return Quaternion(matmul(self.__mat, rot.axis) * -1, rot.angle).normalized()

class BoneConverterPoseMode:
    def __init__(self, pose_bone, scale, invert=False):
        mat = pose_bone.matrix.to_3x3()
        mat[1], mat[2] = mat[2].copy(), mat[1].copy()
        self.__mat = mat.transposed()
        self.__scale = scale
        self.__mat_rot = pose_bone.matrix_basis.to_3x3()
        self.__mat_loc = matmul(self.__mat_rot, self.__mat)
        self.__offset = pose_bone.location.copy()
        self.convert_location = self._convert_location
        self.convert_rotation = self._convert_rotation
        if invert:
            self.__mat.invert()
            self.__mat_rot.invert()
            self.__mat_loc.invert()
            self.convert_location = self._convert_location_inverted
            self.convert_rotation = self._convert_rotation_inverted
        self.convert_interpolation = _InterpolationHelper(self.__mat_loc).convert

    def _convert_location(self, location):
        return self.__offset + matmul(self.__mat_loc, Vector(location)) * self.__scale

    def _convert_rotation(self, rotation_xyzw):
        rot = Quaternion()
        rot.x, rot.y, rot.z, rot.w = rotation_xyzw
        rot = Quaternion(matmul(self.__mat, rot.axis) * -1, rot.angle)
        return matmul(self.__mat_rot, rot.to_matrix()).to_quaternion()

    def _convert_location_inverted(self, location):
        return matmul(self.__mat_loc, Vector(location) - self.__offset) * self.__scale

    def _convert_rotation_inverted(self, rotation_xyzw):
        rot = Quaternion()
        rot.x, rot.y, rot.z, rot.w = rotation_xyzw
        rot = matmul(self.__mat_rot, rot.to_matrix()).to_quaternion()
        return Quaternion(matmul(self.__mat, rot.axis) * -1, rot.angle).normalized()


class _FnBezier:

    __BLENDER_2_91_OR_NEWER = not (bpy.app.version < (2, 91, 0))

    @classmethod
    def from_fcurve(cls, kp0, kp1):
        p0, p1, p2, p3 = kp0.co, kp0.handle_right, kp1.handle_left, kp1.co
        if cls.__BLENDER_2_91_OR_NEWER: # the F-Curve can become near-vertical
            if p1.x > p3.x:
                t = (p3.x - p0.x) / (p1.x - p0.x)
                p1 = (1-t)*p0 + p1*t
            if p0.x > p2.x:
                t = (p3.x - p0.x) / (p3.x - p2.x)
                p2 = (1-t)*p3 + p2*t
        elif p1.x > p2.x: # legacy F-Curve correction
            t = (p3.x - p0.x) / (p1.x - p0.x + p3.x - p2.x)
            p1 = (1-t)*p0 + p1*t
            p2 = (1-t)*p3 + p2*t
        return cls(p0, p1, p2, p3)

    def __init__(self, p0, p1, p2, p3): # assuming VMD's bezier or F-Curve's bezier
        #assert(p0.x <= p1.x <= p3.x and p0.x <= p2.x <= p3.x)
        self._p0, self._p1, self._p2, self._p3 = p0, p1, p2, p3

    @property
    def points(self):
        return self._p0, self._p1, self._p2, self._p3

    def split(self, t):
        p0, p1, p2, p3 = self._p0, self._p1, self._p2, self._p3
        p01t = (1-t)*p0 + t*p1
        p12t = (1-t)*p1 + t*p2
        p23t = (1-t)*p2 + t*p3
        p012t = (1-t)*p01t + t*p12t
        p123t = (1-t)*p12t + t*p23t
        pt = (1-t)*p012t + t*p123t
        return _FnBezier(p0, p01t, p012t, pt), _FnBezier(pt, p123t, p23t, p3), pt

    def evaluate(self, t):
        p0, p1, p2, p3 = self._p0, self._p1, self._p2, self._p3
        p01t = (1-t)*p0 + t*p1
        p12t = (1-t)*p1 + t*p2
        p23t = (1-t)*p2 + t*p3
        p012t = (1-t)*p01t + t*p12t
        p123t = (1-t)*p12t + t*p23t
        return (1-t)*p012t + t*p123t

    def split_by_x(self, x):
        return self.split(self.axis_to_t(x))

    def evaluate_by_x(self, x):
        return self.evaluate(self.axis_to_t(x))

    def axis_to_t(self, val, axis=0):
        p0, p1, p2, p3 = self._p0[axis], self._p1[axis], self._p2[axis], self._p3[axis]
        a = p3 - p0 + 3 * (p1 - p2)
        b = 3 * (p0 - 2*p1 + p2)
        c = 3 * (p1 - p0)
        d = p0 - val
        return next(self.__find_roots(a, b, c, d))

    def find_critical(self):
        p0, p1, p2, p3 = self._p0.y, self._p1.y, self._p2.y, self._p3.y
        p_min, p_max = (p0, p3) if p0 < p3 else (p3, p0)
        if p1 > p_max or p1 < p_min or p2 > p_max or p2 < p_min:
            a = 3 * (p3 - p0 + 3 * (p1 - p2))
            b = 6 * (p0 - 2*p1 + p2)
            c = 3 * (p1 - p0)
            yield from self.__find_roots(0, a, b, c)

    @staticmethod
    def __find_roots(a, b, c, d): # a*t*t*t + b*t*t + c*t + d = 0
        #TODO fix precision errors (ex: t=0 and t=1) and improve performance
        if a == 0:
            if b == 0:
                t = -d/c
                if 0 <= t <= 1:
                    yield t
            else:
                D = c*c - 4*b*d
                if D < 0:
                    return
                D = D**0.5
                b2 = 2*b
                t = (-c + D)/b2
                if 0 <= t <= 1:
                    yield t
                t = (-c - D)/b2
                if 0 <= t <= 1:
                    yield t
            return

        def _sqrt3(v):
            return -((-v)**(1/3)) if v < 0 else v**(1/3)

        A = b*c/(6*a*a) - b*b*b/(27*a*a*a) - d/(2*a)
        B = c/(3*a) - b*b/(9*a*a)
        b_3a = -b/(3*a)
        D = A*A + B*B*B

        if D > 0:
            D = D**0.5
            t = b_3a + _sqrt3(A+D) + _sqrt3(A-D)
            if 0 <= t <= 1:
                yield t
        elif D == 0:
            t = b_3a + _sqrt3(A)*2
            if 0 <= t <= 1:
                yield t
            t = b_3a - _sqrt3(A)
            if 0 <= t <= 1:
                yield t
        else:
            R = A / (-B*B*B)**0.5
            t = b_3a + 2*(-B)**0.5 * math.cos(math.acos(R) / 3)
            if 0 <= t <= 1:
                yield t
            t = b_3a + 2*(-B)**0.5 * math.cos((math.acos(R) + 2*math.pi) / 3)
            if 0 <= t <= 1:
                yield t
            t = b_3a + 2*(-B)**0.5 * math.cos((math.acos(R) - 2*math.pi) / 3)
            if 0 <= t <= 1:
                yield t


class VMDImporter:
    def __init__(self, filepath, scale=1.0, bone_mapper=None, use_pose_mode=False,
            convert_mmd_camera=True, convert_mmd_lamp=True, frame_margin=5, use_mirror=False):
        self.__vmdFile = vmd.File()
        self.__vmdFile.load(filepath=filepath)
        logging.debug(str(self.__vmdFile.header))
        self.__scale = scale
        self.__convert_mmd_camera = convert_mmd_camera
        self.__convert_mmd_lamp = convert_mmd_lamp
        self.__bone_mapper = bone_mapper
        self.__bone_util_cls = BoneConverterPoseMode if use_pose_mode else BoneConverter
        self.__frame_margin = frame_margin + 1
        self.__mirror = use_mirror


    @staticmethod
    def __minRotationDiff(prev_q, curr_q):
        t1 = (prev_q.w - curr_q.w)**2 + (prev_q.x - curr_q.x)**2 + (prev_q.y - curr_q.y)**2 + (prev_q.z - curr_q.z)**2
        t2 = (prev_q.w + curr_q.w)**2 + (prev_q.x + curr_q.x)**2 + (prev_q.y + curr_q.y)**2 + (prev_q.z + curr_q.z)**2
        #t1 = prev_q.rotation_difference(curr_q).angle
        #t2 = prev_q.rotation_difference(-curr_q).angle
        return -curr_q if t2 < t1 else curr_q

    @staticmethod
    def __setInterpolation(bezier, kp0, kp1):
        if bezier[0] == bezier[1] and bezier[2] == bezier[3]:
            kp0.interpolation = 'LINEAR'
        else:
            kp0.interpolation = 'BEZIER'
        kp0.handle_right_type = 'FREE'
        kp1.handle_left_type = 'FREE'
        d = (kp1.co - kp0.co) / 127.0
        kp0.handle_right = kp0.co + Vector((d.x * bezier[0], d.y * bezier[1]))
        kp1.handle_left = kp0.co + Vector((d.x * bezier[2], d.y * bezier[3]))

    @staticmethod
    def __fixFcurveHandles(fcurve):
        kp0 = fcurve.keyframe_points[0]
        kp0.handle_left_type = 'FREE'
        kp0.handle_left = kp0.co + Vector((-1, 0))
        kp = fcurve.keyframe_points[-1]
        kp.handle_right_type = 'FREE'
        kp.handle_right = kp.co + Vector((1, 0))

    def __getBoneConverter(self, bone):
        converter = self.__bone_util_cls(bone, self.__scale)
        mode = bone.rotation_mode
        compatible_quaternion = self.__minRotationDiff
        class _ConverterWrap:
            convert_location = converter.convert_location
            convert_interpolation = converter.convert_interpolation
            if mode == 'QUATERNION':
                convert_rotation = converter.convert_rotation
                compatible_rotation = compatible_quaternion
            elif mode == 'AXIS_ANGLE':
                @staticmethod
                def convert_rotation(rot):
                    (x, y, z), angle = converter.convert_rotation(rot).to_axis_angle()
                    return (angle, x, y, z)
                @staticmethod
                def compatible_rotation(prev, curr):
                    angle, x, y, z = curr
                    if prev[1]*x + prev[2]*y + prev[3]*z < 0:
                        angle, x, y, z = -angle, -x, -y, -z
                    angle_diff = prev[0] - angle
                    if abs(angle_diff) > math.pi:
                        pi_2 = math.pi * 2
                        bias = -0.5 if angle_diff < 0 else 0.5
                        angle += int(bias + angle_diff/pi_2) * pi_2
                    return (angle, x, y, z)
            else:
                convert_rotation = lambda rot: converter.convert_rotation(rot).to_euler(mode)
                compatible_rotation = lambda prev, curr: curr.make_compatible(prev) or curr
        return _ConverterWrap

    def __assignToArmature(self, armObj, action_name=None):
        boneAnim = self.__vmdFile.boneAnimation
        logging.info('---- bone animations:%5d  target: %s', len(boneAnim), armObj.name)
        if len(boneAnim) < 1:
            return

        action_name = action_name or armObj.name
        action = bpy.data.actions.new(name=action_name)
        armObj.animation_data_create().action = action

        extra_frame = 1 if self.__frame_margin > 1 else 0

        pose_bones = armObj.pose.bones
        if self.__bone_mapper:
            pose_bones = self.__bone_mapper(armObj)

        _loc = _rot = lambda i: i
        if self.__mirror:
            pose_bones = _MirrorMapper(pose_bones)
            _loc, _rot = _MirrorMapper.get_location, _MirrorMapper.get_rotation

        class _Dummy: pass
        dummy_keyframe_points = iter(lambda: _Dummy, None)
        prop_rot_map = {'QUATERNION':'rotation_quaternion', 'AXIS_ANGLE':'rotation_axis_angle'}

        bone_name_table = {}
        for name, keyFrames in boneAnim.items():
            num_frame = len(keyFrames)
            if num_frame < 1:
                continue
            bone = pose_bones.get(name, None)
            if bone is None:
                logging.warning('WARNING: not found bone %s (%d frames)', name, len(keyFrames))
                continue
            logging.info('(bone) frames:%5d  name: %s', len(keyFrames), name)
            assert(bone_name_table.get(bone.name, name) == name)
            bone_name_table[bone.name] = name

            fcurves = [dummy_keyframe_points]*7 # x, y, z, r0, r1, r2, (r3)
            data_path_rot = prop_rot_map.get(bone.rotation_mode, 'rotation_euler')
            bone_rotation = getattr(bone, data_path_rot)
            default_values = list(bone.location) + list(bone_rotation)
            data_path = 'pose.bones["%s"].location'%bone.name
            for axis_i in range(3):
                fcurves[axis_i] = action.fcurves.new(data_path=data_path, index=axis_i, action_group=bone.name)
            data_path = 'pose.bones["%s"].%s'%(bone.name, data_path_rot)
            for axis_i in range(len(bone_rotation)):
                fcurves[3+axis_i] = action.fcurves.new(data_path=data_path, index=axis_i, action_group=bone.name)

            for i in range(len(default_values)):
                c = fcurves[i]
                c.keyframe_points.add(extra_frame+num_frame)
                kp_iter = iter(c.keyframe_points)
                if extra_frame:
                    kp = next(kp_iter)
                    kp.co = (1, default_values[i])
                    kp.interpolation = 'LINEAR'
                fcurves[i] = kp_iter

            converter = self.__getBoneConverter(bone)
            prev_rot = bone_rotation if extra_frame else None
            prev_kps, indices = None, tuple(converter.convert_interpolation((0, 16, 32)))+(48,)*len(bone_rotation)
            keyFrames.sort(key=lambda x:x.frame_number)
            for k, x, y, z, r0, r1, r2, r3 in zip(keyFrames, *fcurves):
                frame = k.frame_number + self.__frame_margin
                loc = converter.convert_location(_loc(k.location))
                curr_rot = converter.convert_rotation(_rot(k.rotation))
                if prev_rot is not None:
                    curr_rot = converter.compatible_rotation(prev_rot, curr_rot)
                    #FIXME the rotation interpolation has slightly different result
                    #   Blender: rot(x) = prev_rot*(1 - bezier(t)) + curr_rot*bezier(t)
                    #       MMD: rot(x) = prev_rot.slerp(curr_rot, factor=bezier(t))
                prev_rot = curr_rot

                x.co = (frame, loc[0])
                y.co = (frame, loc[1])
                z.co = (frame, loc[2])
                r0.co = (frame, curr_rot[0])
                r1.co = (frame, curr_rot[1])
                r2.co = (frame, curr_rot[2])
                r3.co = (frame, curr_rot[-1])

                curr_kps = (x, y, z, r0, r1, r2, r3)
                if prev_kps is not None:
                    interp = k.interp
                    for idx, prev_kp, kp in zip(indices, prev_kps, curr_kps):
                        self.__setInterpolation(interp[idx:idx+16:4], prev_kp, kp)
                prev_kps = curr_kps

        for c in action.fcurves:
            self.__fixFcurveHandles(c)

        # ensure IK's default state
        for b in armObj.pose.bones:
            if not b.mmd_ik_toggle:
                b.mmd_ik_toggle = True

        # property animation
        propertyAnim = self.__vmdFile.propertyAnimation
        if len(propertyAnim) < 1:
            return
        logging.info('---- IK animations:%5d  target: %s', len(propertyAnim), armObj.name)
        for keyFrame in propertyAnim:
            logging.debug('(IK) frame:%5d  list: %s', keyFrame.frame_number, keyFrame.ik_states)
            frame = keyFrame.frame_number + self.__frame_margin
            for ikName, enable in keyFrame.ik_states:
                bone = pose_bones.get(ikName, None)
                if bone:
                    bone.mmd_ik_toggle = enable
                    bone.keyframe_insert(data_path='mmd_ik_toggle', frame=frame)


    def __assignToMesh(self, meshObj, action_name=None):
        shapeKeyAnim = self.__vmdFile.shapeKeyAnimation
        logging.info('---- morph animations:%5d  target: %s', len(shapeKeyAnim), meshObj.name)
        if len(shapeKeyAnim) < 1:
            return

        action_name = action_name or meshObj.name
        action = bpy.data.actions.new(name=action_name)
        meshObj.data.shape_keys.animation_data_create().action = action

        mirror_map = _MirrorMapper(meshObj.data.shape_keys.key_blocks) if self.__mirror else {}
        shapeKeyDict = {k:mirror_map.get(k, v) for k, v in meshObj.data.shape_keys.key_blocks.items()}

        from math import floor, ceil
        for name, keyFrames in shapeKeyAnim.items():
            if name not in shapeKeyDict:
                logging.warning('WARNING: not found shape key %s (%d frames)', name, len(keyFrames))
                continue
            logging.info('(mesh) frames:%5d  name: %s', len(keyFrames), name)
            shapeKey = shapeKeyDict[name]
            fcurve = action.fcurves.new(data_path='key_blocks["%s"].value'%shapeKey.name)
            fcurve.keyframe_points.add(len(keyFrames))
            keyFrames.sort(key=lambda x:x.frame_number)
            for k, v in zip(keyFrames, fcurve.keyframe_points):
                v.co = (k.frame_number+self.__frame_margin, k.weight)
                v.interpolation = 'LINEAR'
            weights = tuple(i.weight for i in keyFrames)
            shapeKey.slider_min = min(shapeKey.slider_min, floor(min(weights)))
            shapeKey.slider_max = max(shapeKey.slider_max, ceil(max(weights)))


    def __assignToRoot(self, rootObj, action_name=None):
        propertyAnim = self.__vmdFile.propertyAnimation
        logging.info('---- display animations:%5d  target: %s', len(propertyAnim), rootObj.name)
        if len(propertyAnim) < 1:
            return

        action_name = action_name or rootObj.name
        action = bpy.data.actions.new(name=action_name)
        rootObj.animation_data_create().action = action

        logging.debug('(Display) list(frame, show): %s', [(keyFrame.frame_number, bool(keyFrame.visible)) for keyFrame in propertyAnim])
        for keyFrame in propertyAnim:
            rootObj.mmd_root.show_meshes = keyFrame.visible
            rootObj.keyframe_insert(data_path='mmd_root.show_meshes',
                                    frame=keyFrame.frame_number+self.__frame_margin)


    @staticmethod
    def detectCameraChange(fcurve, threshold=10.0):
        frames = list(fcurve.keyframe_points)
        frameCount = len(frames)
        frames.sort(key=lambda x:x.co[0])
        for i, f in enumerate(frames):
            if i+1 < frameCount:
                n = frames[i+1]
                if n.co[0] - f.co[0] <= 1.0 and abs(f.co[1] - n.co[1]) > threshold:
                    f.interpolation = 'CONSTANT'

    def __assignToCamera(self, cameraObj, action_name=None):
        mmdCameraInstance = MMDCamera.convertToMMDCamera(cameraObj, self.__scale)
        mmdCamera = mmdCameraInstance.object()
        cameraObj = mmdCameraInstance.camera()

        cameraAnim = self.__vmdFile.cameraAnimation
        logging.info('(camera) frames:%5d  name: %s', len(cameraAnim), mmdCamera.name)
        if len(cameraAnim) < 1:
            return

        action_name = action_name or mmdCamera.name
        parent_action = bpy.data.actions.new(name=action_name)
        distance_action = bpy.data.actions.new(name=action_name+'_dis')
        mmdCamera.animation_data_create().action = parent_action
        cameraObj.animation_data_create().action = distance_action

        _loc = _rot = lambda i: i
        if self.__mirror:
            _loc, _rot = _MirrorMapper.get_location, _MirrorMapper.get_rotation3

        fcurves = []
        for i in range(3):
            fcurves.append(parent_action.fcurves.new(data_path='location', index=i)) # x, y, z
        for i in range(3):
            fcurves.append(parent_action.fcurves.new(data_path='rotation_euler', index=i)) # rx, ry, rz
        fcurves.append(parent_action.fcurves.new(data_path='mmd_camera.angle')) # fov
        fcurves.append(parent_action.fcurves.new(data_path='mmd_camera.is_perspective')) # persp
        fcurves.append(distance_action.fcurves.new(data_path='location', index=1)) # dis
        for c in fcurves:
            c.keyframe_points.add(len(cameraAnim))

        prev_kps, indices = None, (0, 8, 4, 12, 12, 12, 16, 20) # x, z, y, rx, ry, rz, dis, fov
        cameraAnim.sort(key=lambda x:x.frame_number)
        for k, x, y, z, rx, ry, rz, fov, persp, dis in zip(cameraAnim, *(c.keyframe_points for c in fcurves)):
            frame = k.frame_number + self.__frame_margin
            x.co, z.co, y.co = ((frame, val*self.__scale) for val in _loc(k.location))
            rx.co, rz.co, ry.co = ((frame, val) for val in _rot(k.rotation))
            fov.co = (frame, math.radians(k.angle))
            dis.co = (frame, k.distance*self.__scale)
            persp.co = (frame, k.persp)

            persp.interpolation = 'CONSTANT'
            curr_kps = (x, y, z, rx, ry, rz, dis, fov)
            if prev_kps is not None:
                interp = k.interp
                for idx, prev_kp, kp in zip(indices, prev_kps, curr_kps):
                    self.__setInterpolation(interp[idx:idx+4:2]+interp[idx+1:idx+4:2], prev_kp, kp)
            prev_kps = curr_kps

        for fcurve in fcurves:
            self.__fixFcurveHandles(fcurve)
            if fcurve.data_path == 'rotation_euler':
                self.detectCameraChange(fcurve)


    @staticmethod
    def detectLampChange(fcurve, threshold=0.1):
        frames = list(fcurve.keyframe_points)
        frameCount = len(frames)
        frames.sort(key=lambda x:x.co[0])
        for i, f in enumerate(frames):
            f.interpolation = 'LINEAR'
            if i+1 < frameCount:
                n = frames[i+1]
                if n.co[0] - f.co[0] <= 1.0 and abs(f.co[1] - n.co[1]) > threshold:
                    f.interpolation = 'CONSTANT'

    def __assignToLamp(self, lampObj, action_name=None):
        mmdLampInstance = MMDLamp.convertToMMDLamp(lampObj, self.__scale)
        mmdLamp = mmdLampInstance.object()
        lampObj = mmdLampInstance.lamp()

        lampAnim = self.__vmdFile.lampAnimation
        logging.info('(lamp) frames:%5d  name: %s', len(lampAnim), mmdLamp.name)
        if len(lampAnim) < 1:
            return

        action_name = action_name or mmdLamp.name
        color_action = bpy.data.actions.new(name=action_name+'_color')
        location_action = bpy.data.actions.new(name=action_name+'_loc')
        lampObj.data.animation_data_create().action = color_action
        lampObj.animation_data_create().action = location_action

        _loc = _MirrorMapper.get_location if self.__mirror else lambda i: i
        for keyFrame in lampAnim:
            frame = keyFrame.frame_number + self.__frame_margin
            lampObj.data.color = Vector(keyFrame.color)
            lampObj.location = Vector(_loc(keyFrame.direction)).xzy * -1
            lampObj.data.keyframe_insert(data_path='color', frame=frame)
            lampObj.keyframe_insert(data_path='location', frame=frame)

        for fcurve in lampObj.animation_data.action.fcurves:
            self.detectLampChange(fcurve)


    def assign(self, obj, action_name=None):
        if obj is None:
            return
        if action_name is None:
            action_name = os.path.splitext(os.path.basename(self.__vmdFile.filepath))[0]

        if MMDCamera.isMMDCamera(obj):
            self.__assignToCamera(obj, action_name+'_camera')
        elif MMDLamp.isMMDLamp(obj):
            self.__assignToLamp(obj, action_name+'_lamp')
        elif getattr(obj.data, 'shape_keys', None):
            self.__assignToMesh(obj, action_name+'_facial')
        elif obj.type == 'ARMATURE':
            self.__assignToArmature(obj, action_name+'_bone')
        elif obj.type == 'CAMERA' and self.__convert_mmd_camera:
            self.__assignToCamera(obj, action_name+'_camera')
        elif obj.type == 'LAMP' and self.__convert_mmd_lamp:
            self.__assignToLamp(obj, action_name+'_lamp')
        elif obj.mmd_type == 'ROOT':
            self.__assignToRoot(obj, action_name+'_display')
        else:
            pass

