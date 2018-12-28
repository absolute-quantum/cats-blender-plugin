# -*- coding: utf-8 -*-

import re
import bpy
from bpy.types import Operator
from mathutils import Matrix

from mmd_tools_local import register_wrap
from mmd_tools_local.bpyutils import matmul

@register_wrap
class SetGLSLShading(Operator):
    bl_idname = 'mmd_tools.set_glsl_shading'
    bl_label = 'GLSL View'
    bl_description = 'Use GLSL shading with additional lighting'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mmd_tools.reset_shading()
        if bpy.app.version >= (2, 80, 0):
            shading = context.area.spaces[0].shading
            shading.light = 'STUDIO'
            shading.color_type = 'TEXTURE'
            return {'FINISHED'}

        for i in filter(lambda x: x.type == 'MESH', context.scene.objects):
            for s in i.material_slots:
                if s.material is None:
                    continue
                s.material.use_shadeless = False
        if len(list(filter(lambda x: x.is_mmd_glsl_light, context.scene.objects))) == 0:
            light = bpy.data.objects.new('Hemi', bpy.data.lamps.new('Hemi', 'HEMI'))
            light.is_mmd_glsl_light = True
            light.hide = True
            context.scene.objects.link(light)

        context.area.spaces[0].viewport_shade='TEXTURED'
        context.scene.game_settings.material_mode = 'GLSL'
        return {'FINISHED'}

@register_wrap
class SetShadelessGLSLShading(Operator):
    bl_idname = 'mmd_tools.set_shadeless_glsl_shading'
    bl_label = 'Shadeless GLSL View'
    bl_description = 'Use only toon shading'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.mmd_tools.reset_shading()
        if bpy.app.version >= (2, 80, 0):
            shading = context.area.spaces[0].shading
            shading.light = 'FLAT'
            shading.color_type = 'TEXTURE'
            return {'FINISHED'}

        for i in filter(lambda x: x.type == 'MESH', context.scene.objects):
            for s in i.material_slots:
                if s.material is None:
                    continue
                s.material.use_shadeless = True
        try:
            context.scene.display_settings.display_device = 'None'
        except TypeError:
            pass # Blender was built without OpenColorIO:

        context.area.spaces[0].viewport_shade='TEXTURED'
        context.scene.game_settings.material_mode = 'GLSL'
        return {'FINISHED'}

@register_wrap
class ResetShading(Operator):
    bl_idname = 'mmd_tools.reset_shading'
    bl_label = 'Reset View'
    bl_description = 'Reset to default Blender shading'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.app.version >= (2, 80, 0):
            context.scene.render.engine = 'BLENDER_EEVEE'
            shading = context.area.spaces[0].shading
            shading.type = 'SOLID'
            shading.light = 'STUDIO'
            shading.color_type = 'MATERIAL'
            shading.show_object_outline = False
            shading.show_backface_culling = False
            return {'FINISHED'}

        context.scene.render.engine = 'BLENDER_RENDER'
        for i in filter(lambda x: x.type == 'MESH', context.scene.objects):
            for s in i.material_slots:
                if s.material is None:
                    continue
                s.material.use_shadeless = False
                s.material.use_nodes = False

        for i in filter(lambda x: x.is_mmd_glsl_light, context.scene.objects):
            context.scene.objects.unlink(i)

        try:
            context.scene.display_settings.display_device = 'sRGB'
        except TypeError:
            pass
        context.area.spaces[0].viewport_shade='SOLID'
        context.area.spaces[0].show_backface_culling = False
        context.scene.game_settings.material_mode = 'MULTITEXTURE'
        return {'FINISHED'}

@register_wrap
class FlipPose(Operator):
    bl_idname = 'mmd_tools.flip_pose'
    bl_label = 'Flip Pose'
    bl_description = 'Apply the current pose of selected bones to matching bone on opposite side of X-Axis.'
    bl_options = {'REGISTER', 'UNDO'}

    # https://docs.blender.org/manual/en/dev/rigging/armatures/bones/editing/naming.html
    __LR_REGEX = [
        {"re": re.compile(r'^(.+)(RIGHT|LEFT)(\.\d+)?$', re.IGNORECASE), "lr": 1},
        {"re": re.compile(r'^(.+)([\.\- _])(L|R)(\.\d+)?$', re.IGNORECASE), "lr": 2},
        {"re": re.compile(r'^(LEFT|RIGHT)(.+)$', re.IGNORECASE), "lr": 0},
        {"re": re.compile(r'^(L|R)([\.\- _])(.+)$', re.IGNORECASE), "lr": 0}
    ]
    __LR_MAP = {
        "RIGHT": "LEFT",
        "Right": "Left",
        "right": "left",
        "LEFT": "RIGHT",
        "Left": "Right",
        "left": "right",
        "L": "R",
        "l": "r",
        "R": "L",
        "r": "l"
    }
    @classmethod
    def __flip_name(cls, name):
        for regex in cls.__LR_REGEX:
            match = regex["re"].match(name)
            if match:
                groups = match.groups()
                lr = groups[regex["lr"]]
                if lr in cls.__LR_MAP:
                    flip_lr = cls.__LR_MAP[lr]
                    name = ''
                    for i, s in enumerate(groups):
                        if i == regex["lr"]:
                            name += flip_lr
                        elif s:
                            name += s
                    return name
        return None

    @staticmethod
    def __cmul(vec1, vec2):
        return type(vec1)([x * y for x, y in zip(vec1, vec2)])

    @staticmethod
    def __matrix_compose(loc, rot, scale):
        return matmul(matmul(Matrix.Translation(loc), rot.to_matrix().to_4x4()),
                    Matrix([(scale[0],0,0,0), (0,scale[1],0,0), (0,0,scale[2],0), (0,0,0,1)]))

    @classmethod
    def __flip_direction(cls, bone1, bone2):
        axis1 = bone1.matrix_local.to_3x3().transposed()
        axis2 = bone2.matrix_local.to_3x3().transposed()
        axis1 = [cls.__cmul(vec, (-1, 1, 1)) for vec in axis1]
        return [1] + [(1, -1)[vec1.dot(vec2) > 0] for vec1, vec2 in zip(axis1, axis2)]

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                    context.active_object.type == 'ARMATURE' and
                    context.active_object.mode == 'POSE')

    def execute(self, context):
        copy_buffer = []
        arm = context.active_object

        for pose_bone in context.selected_pose_bones:
            copy_buffer.append({
                'name': pose_bone.bone.name,
                'flipped_name': self.__flip_name(pose_bone.bone.name),
                'bone': pose_bone.bone,
                'matrix_basis': pose_bone.matrix_basis.copy()})

        for b in copy_buffer:
            if b["flipped_name"] and b["flipped_name"] in arm.pose.bones:
                pose_bone = arm.pose.bones[b["flipped_name"]]
                sign = self.__flip_direction(b['bone'], pose_bone.bone)
                loc, rot, scale = b['matrix_basis'].decompose()
                loc = self.__cmul(loc, (-1, 1, 1))
                rot = self.__cmul(rot, sign)
                pose_bone.matrix_basis = self.__matrix_compose(loc, rot, scale)
            else:
                pose_bone = arm.pose.bones[b['name']]
                loc, rot, scale = b['matrix_basis'].decompose()
                loc = self.__cmul(loc, (-1, 1, 1))
                rot = self.__cmul(rot, (1, 1, -1, -1))
                pose_bone.matrix_basis = self.__matrix_compose(loc, rot, scale)

        return {'FINISHED'}
