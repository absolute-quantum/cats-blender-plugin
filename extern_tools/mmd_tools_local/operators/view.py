# -*- coding: utf-8 -*-

import re
import bpy
from bpy.types import Operator
from mathutils import Matrix

from mmd_tools_local import register_wrap
from mmd_tools_local.bpyutils import matmul


class _SetShadingBase:
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def _get_view3d_spaces(context):
        if getattr(context.area, 'type', None) == 'VIEW_3D':
            return (context.area.spaces[0],)
        return (area.spaces[0] for area in getattr(context.screen, 'areas', ()) if area.type == 'VIEW_3D')

    @staticmethod
    def _reset_color_management(context, use_display_device=True):
        try:
            context.scene.display_settings.display_device = ('None', 'sRGB')[use_display_device]
        except TypeError:
            pass

    @staticmethod
    def _reset_material_shading(context, use_shadeless=False):
        for i in (x for x in context.scene.objects if x.type == 'MESH' and x.mmd_type == 'NONE'):
            for s in i.material_slots:
                if s.material is None:
                    continue
                s.material.use_nodes = False
                s.material.use_shadeless = use_shadeless

    @staticmethod
    def _reset_mmd_glsl_light(context, use_light=False):
        for i in (x for x in context.scene.objects if x.is_mmd_glsl_light):
            if use_light:
                return
            context.scene.objects.unlink(i)

        if use_light:
            light = bpy.data.objects.new('Hemi', bpy.data.lamps.new('Hemi', 'HEMI'))
            light.is_mmd_glsl_light = True
            context.scene.objects.link(light)


    if bpy.app.version < (2, 80, 0):
        def execute(self, context):
            context.scene.render.engine = 'BLENDER_RENDER'

            shading_mode = getattr(self, '_shading_mode', None)
            self._reset_mmd_glsl_light(context, use_light=(shading_mode == 'GLSL'))
            self._reset_material_shading(context, use_shadeless=(shading_mode == 'SHADELESS'))
            self._reset_color_management(context, use_display_device=(shading_mode != 'SHADELESS'))

            shade, context.scene.game_settings.material_mode = ('TEXTURED', 'GLSL') if shading_mode else ('SOLID', 'MULTITEXTURE')
            for space in self._get_view3d_spaces(context):
                space.viewport_shade = shade
                space.show_backface_culling = True
            return {'FINISHED'}
    else:
        def execute(self, context): #TODO
            context.scene.render.engine = 'BLENDER_EEVEE'

            shading_mode = getattr(self, '_shading_mode', None)
            for space in self._get_view3d_spaces(context):
                shading = space.shading
                shading.type = 'SOLID'
                shading.light = 'FLAT' if shading_mode == 'SHADELESS' else 'STUDIO'
                shading.color_type = 'TEXTURE' if shading_mode else 'MATERIAL'
                shading.show_object_outline = False
                shading.show_backface_culling = True
            return {'FINISHED'}


@register_wrap
class SetGLSLShading(Operator, _SetShadingBase):
    bl_idname = 'mmd_tools.set_glsl_shading'
    bl_label = 'GLSL View'
    bl_description = 'Use GLSL shading with additional lighting'

    _shading_mode = 'GLSL'

@register_wrap
class SetShadelessGLSLShading(Operator, _SetShadingBase):
    bl_idname = 'mmd_tools.set_shadeless_glsl_shading'
    bl_label = 'Shadeless GLSL View'
    bl_description = 'Use only toon shading'

    _shading_mode = 'SHADELESS'

@register_wrap
class ResetShading(Operator, _SetShadingBase):
    bl_idname = 'mmd_tools.reset_shading'
    bl_label = 'Reset View'
    bl_description = 'Reset to default Blender shading'


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
        {"re": re.compile(r'^(L|R)([\.\- _])(.+)$', re.IGNORECASE), "lr": 0},
        {"re": re.compile(r'^(.+)(左|右)(\.\d+)?$'), "lr": 1},
        {"re": re.compile(r'^(左|右)(.+)$'), "lr": 0},
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
        "r": "l",
        "左": "右",
        "右": "左",
        }
    @classmethod
    def flip_name(cls, name):
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
        return ''

    @staticmethod
    def __cmul(vec1, vec2):
        return type(vec1)([x * y for x, y in zip(vec1, vec2)])

    @staticmethod
    def __matrix_compose(loc, rot, scale):
        return matmul(matmul(Matrix.Translation(loc), rot.to_matrix().to_4x4()),
                    Matrix([(scale[0],0,0,0), (0,scale[1],0,0), (0,0,scale[2],0), (0,0,0,1)]))

    @classmethod
    def __flip_pose(cls, matrix_basis, bone_src, bone_dest):
        from mathutils import Quaternion
        m = bone_dest.bone.matrix_local.to_3x3().transposed()
        mi = bone_src.bone.matrix_local.to_3x3().transposed().inverted() if bone_src != bone_dest else m.inverted()
        loc, rot, scale = matrix_basis.decompose()
        loc = cls.__cmul(matmul(mi, loc), (-1, 1, 1))
        rot = cls.__cmul(Quaternion(matmul(mi, rot.axis), rot.angle).normalized(), (1, 1, -1, -1))
        bone_dest.matrix_basis = cls.__matrix_compose(matmul(m, loc), Quaternion(matmul(m, rot.axis), rot.angle).normalized(), scale)

    @classmethod
    def poll(cls, context):
        return (context.active_object and
                    context.active_object.type == 'ARMATURE' and
                    context.active_object.mode == 'POSE')

    def execute(self, context):
        pose_bones = context.active_object.pose.bones
        for b, mat in [(x, x.matrix_basis.copy()) for x in context.selected_pose_bones]:
            self.__flip_pose(mat, b, pose_bones.get(self.flip_name(b.name), b))
        return {'FINISHED'}

