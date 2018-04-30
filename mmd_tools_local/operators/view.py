# -*- coding: utf-8 -*-

import bpy
from bpy.types import Operator


class SetGLSLShading(Operator):
    bl_idname = 'mmd_tools.set_glsl_shading'
    bl_label = 'GLSL View'
    bl_description = 'Use GLSL shading with additional lighting'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ResetShading.execute(self, context)
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
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
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        return {'FINISHED'}

class SetShadelessGLSLShading(Operator):
    bl_idname = 'mmd_tools.set_shadeless_glsl_shading'
    bl_label = 'Shadeless GLSL View'
    bl_description = 'Use only toon shading'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ResetShading.execute(self, context)
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        for i in filter(lambda x: x.type == 'MESH', context.scene.objects):
            for s in i.material_slots:
                if s.material is None:
                    continue
                s.material.use_shadeless = True
        for i in filter(lambda x: x.is_mmd_glsl_light, context.scene.objects):
            context.scene.objects.unlink(i)

        try:
            bpy.context.scene.display_settings.display_device = 'None'
        except TypeError:
            pass # Blender was built without OpenColorIO:

        context.area.spaces[0].viewport_shade='TEXTURED'
        bpy.context.scene.game_settings.material_mode = 'GLSL'
        return {'FINISHED'}

class ResetShading(Operator):
    bl_idname = 'mmd_tools.reset_shading'
    bl_label = 'Reset View'
    bl_description = 'Reset to default Blender shading'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        for i in filter(lambda x: x.type == 'MESH', context.scene.objects):
            for s in i.material_slots:
                if s.material is None:
                    continue
                s.material.use_shadeless = False
                s.material.use_nodes = False

        for i in filter(lambda x: x.is_mmd_glsl_light, context.scene.objects):
            context.scene.objects.unlink(i)

        bpy.context.scene.display_settings.display_device = 'sRGB'
        context.area.spaces[0].viewport_shade='SOLID'
        context.area.spaces[0].show_backface_culling = False
        bpy.context.scene.game_settings.material_mode = 'MULTITEXTURE'
        return {'FINISHED'}
