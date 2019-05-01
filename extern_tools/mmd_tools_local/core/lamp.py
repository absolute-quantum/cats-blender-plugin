# -*- coding: utf-8 -*-

import bpy

from mmd_tools_local.bpyutils import SceneOp

class MMDLamp:
    def __init__(self, obj):
        if MMDLamp.isLamp(obj):
            obj = obj.parent
        if obj and obj.type == 'EMPTY' and obj.mmd_type == 'LIGHT':
            self.__emptyObj = obj
        else:
            raise ValueError('%s is not MMDLamp'%str(obj))


    @staticmethod
    def isLamp(obj):
        return obj and obj.type in {'LIGHT', 'LAMP'}

    @staticmethod
    def isMMDLamp(obj):
        if MMDLamp.isLamp(obj):
            obj = obj.parent
        return obj and obj.type == 'EMPTY' and obj.mmd_type == 'LIGHT'

    @staticmethod
    def convertToMMDLamp(lampObj, scale=1.0):
        if MMDLamp.isMMDLamp(lampObj):
            return MMDLamp(lampObj)

        empty = bpy.data.objects.new(name='MMD_Light', object_data=None)
        SceneOp(bpy.context).link_object(empty)

        empty.rotation_mode = 'XYZ'
        empty.lock_rotation = (True, True, True)
        empty.empty_draw_size = 0.4
        empty.scale = [10*scale] * 3
        empty.mmd_type = 'LIGHT'
        empty.location = (0, 0, 11*scale)

        lampObj.parent = empty
        lampObj.data.color = (0.602, 0.602, 0.602)
        lampObj.location = (0.5, -0.5, 1.0)
        lampObj.rotation_mode = 'XYZ'
        lampObj.rotation_euler = (0, 0, 0)
        lampObj.lock_rotation = (True, True, True)

        constraint = lampObj.constraints.new(type='TRACK_TO')
        constraint.name = 'mmd_lamp_track'
        constraint.target = empty
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'

        return MMDLamp(empty)

    def object(self):
        return self.__emptyObj

    def lamp(self):
        for i in self.__emptyObj.children:
            if MMDLamp.isLamp(i):
                return i
        raise Exception

