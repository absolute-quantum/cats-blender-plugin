# -*- coding: utf-8 -*-

import bpy
import math

class MMDCamera:
    def __init__(self, obj):
        if obj.type == 'CAMERA':
            obj = obj.parent
        if obj and obj.type == 'EMPTY' and obj.mmd_type == 'CAMERA':
            self.__emptyObj = obj
        else:
            raise ValueError('%s is not MMDCamera'%str(obj))


    @staticmethod
    def isMMDCamera(obj):
        if obj.type == 'CAMERA':
            obj = obj.parent
        return obj and obj.type == 'EMPTY' and obj.mmd_type == 'CAMERA'

    @staticmethod
    def addDrivers(cameraObj):
        def __add_ortho_driver(id_data, data_path, expression, index=-1):
            d = id_data.driver_add(data_path, index)
            d.driver.type = 'SCRIPTED'
            if '$dis' in expression:
                var = d.driver.variables.new()
                var.name = 'camera_dis'
                var.type = 'TRANSFORMS'
                target = var.targets[0]
                target.id = cameraObj
                target.transform_type = 'LOC_Y'
                target.transform_space = 'LOCAL_SPACE'
                expression = expression.replace('$dis', var.name)
            if '$type' in expression:
                var = d.driver.variables.new()
                var.name = 'camera_type'
                var.type = 'SINGLE_PROP'
                target = var.targets[0]
                target.id_type = 'OBJECT'
                target.id = cameraObj
                target.data_path = 'data.type'
                expression = expression.replace('$type', var.name)
            d.driver.expression = expression
        #bpy.context.user_preferences.system.use_scripts_auto_execute = True
        __add_ortho_driver(cameraObj.data, 'ortho_scale', '25*(abs($dis)/45)')
        __add_ortho_driver(cameraObj, 'rotation_euler', 'pi if $type == 1 and $dis > 1e-5 else 0', index=1)

    @staticmethod
    def convertToMMDCamera(cameraObj, scale=1.0):
        if MMDCamera.isMMDCamera(cameraObj):
            return MMDCamera(cameraObj)

        empty = bpy.data.objects.new(name='MMD_Camera', object_data=None)
        bpy.context.scene.objects.link(empty)

        cameraObj.parent = empty
        cameraObj.data.dof_object = empty
        cameraObj.data.sensor_fit = 'VERTICAL'
        cameraObj.data.lens_unit = 'MILLIMETERS' # MILLIMETERS, FOV
        cameraObj.data.ortho_scale = 25*scale
        cameraObj.data.clip_end = 500*scale
        cameraObj.data.draw_size = 5*scale
        cameraObj.location = (0, -45*scale, 0)
        cameraObj.rotation_mode = 'XYZ'
        cameraObj.rotation_euler = (math.radians(90), 0, 0)
        cameraObj.lock_location = (True, False, True)
        cameraObj.lock_rotation = (True, True, True)
        cameraObj.lock_scale = (True, True, True)
        MMDCamera.addDrivers(cameraObj)

        empty.location = (0, 0, 10*scale)
        empty.rotation_mode = 'YXZ'
        empty.empty_draw_size = 5*scale
        empty.lock_scale = (True, True, True)
        empty.mmd_type = 'CAMERA'
        empty.mmd_camera.angle = math.radians(30)
        empty.mmd_camera.persp = True
        return MMDCamera(empty)

    @staticmethod
    def newMMDCameraAnimation(cameraObj, cameraTarget=None, scale=1.0):
        if cameraTarget is None:
            cameraTarget = cameraObj

        scene = bpy.context.scene
        mmd_cam = bpy.data.objects.new(name='Camera', object_data=bpy.data.cameras.new('Camera'))
        scene.objects.link(mmd_cam)
        MMDCamera.convertToMMDCamera(mmd_cam, scale=scale)
        mmd_cam_root = mmd_cam.parent

        action_name = mmd_cam_root.name
        parent_action = bpy.data.actions.new(name=action_name)
        distance_action = bpy.data.actions.new(name=action_name+'_dis')

        from math import atan
        from mathutils import Matrix, Vector

        render = scene.render
        factor = (render.resolution_y*render.pixel_aspect_y)/(render.resolution_x*render.pixel_aspect_x)
        matrix_rotation = Matrix(([1,0,0,0], [0,0,1,0], [0,-1,0,0], [0,0,0,1]))
        neg_z_vector = Vector((0,0,-1))
        frame_start, frame_end, frame_current = scene.frame_start, scene.frame_end+1, scene.frame_current
        frame_count = frame_end - frame_start
        frames = range(frame_start, frame_end)

        fcurves = []
        for i in range(3):
            fcurves.append(parent_action.fcurves.new(data_path='location', index=i)) # x, y, z
        for i in range(3):
            fcurves.append(parent_action.fcurves.new(data_path='rotation_euler', index=i)) # rx, ry, rz
        fcurves.append(parent_action.fcurves.new(data_path='mmd_camera.angle')) # fov
        fcurves.append(parent_action.fcurves.new(data_path='mmd_camera.is_perspective')) # persp
        fcurves.append(distance_action.fcurves.new(data_path='location', index=1)) # dis
        for c in fcurves:
            c.keyframe_points.add(frame_count)

        for f, x, y, z, rx, ry, rz, fov, persp, dis in zip(frames, *(c.keyframe_points for c in fcurves)):
            scene.frame_set(f)
            cam_matrix_world = cameraObj.matrix_world
            cam_target_loc = cameraTarget.matrix_world.translation
            cam_rotation = (cam_matrix_world * matrix_rotation).to_euler(mmd_cam_root.rotation_mode)
            cam_vec = cam_matrix_world.to_3x3() * neg_z_vector
            if cameraObj.data.type == 'ORTHO':
                cam_dis = -(9/5) * cameraObj.data.ortho_scale
                if cameraObj.data.sensor_fit != 'VERTICAL':
                    if cameraObj.data.sensor_fit == 'HORIZONTAL':
                        cam_dis *= factor
                    else:
                        cam_dis *= min(1, factor)
            else:
                target_vec = cam_target_loc - cam_matrix_world.translation
                cam_dis = -target_vec.length * abs(cam_vec.dot(target_vec.normalized()))
            cam_target_loc = cam_matrix_world.translation - cam_vec*cam_dis

            tan_val = cameraObj.data.sensor_height/cameraObj.data.lens/2
            if cameraObj.data.sensor_fit != 'VERTICAL':
                ratio = cameraObj.data.sensor_width/cameraObj.data.sensor_height
                if cameraObj.data.sensor_fit == 'HORIZONTAL':
                    tan_val *= factor*ratio
                else: # cameraObj.data.sensor_fit == 'AUTO'
                    tan_val *= min(ratio, factor*ratio)

            x.co, y.co, z.co = ((f, i) for i in cam_target_loc)
            rx.co, ry.co, rz.co = ((f, i) for i in cam_rotation)
            dis.co = (f, cam_dis)
            fov.co = (f, 2*atan(tan_val))
            persp.co = (f, cameraObj.data.type != 'ORTHO')
            persp.interpolation = 'CONSTANT'

        for c in fcurves:
            c.update()

        mmd_cam_root.animation_data_create().action = parent_action
        mmd_cam.animation_data_create().action = distance_action
        scene.frame_set(frame_current)
        return MMDCamera(mmd_cam_root)

    def object(self):
        return self.__emptyObj

    def camera(self):
        for i in self.__emptyObj.children:
            if i.type == 'CAMERA':
                return i
        raise Exception
