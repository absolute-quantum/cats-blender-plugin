# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: GiveMeAllYourCats
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: 

import bpy
import sys
import os
import importlib
from . import addon_updater_ops

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import tools.viseme
import tools.atlas
import tools.eyetracking
import tools.rootbone
import tools.translate
import tools.armature
import tools.common
import globs

importlib.reload(tools.viseme)
importlib.reload(tools.atlas)
importlib.reload(tools.eyetracking)
importlib.reload(tools.rootbone)
importlib.reload(tools.translate)
importlib.reload(tools.armature)
importlib.reload(tools.common)

bl_info = {
    'name': 'Cats Blender Plugin',
    'category': '3D View',
    'author': 'GiveMeAllYourCats',
    'location': 'View 3D > Tool Shelf > CATS',
    'description': 'A tool designed to shorten steps needed to import and optimise MMD models into VRChat',
    'version': (0, 0, 6),
    'blender': (2, 79, 0),
    'wiki_url': 'https://github.com/michaeldegroot/cats-blender-plugin',
    'tracker_url': 'https://github.com/michaeldegroot/cats-blender-plugin/issues',
    'warning': '',
}

bl_options = {'REGISTER', 'UNDO'}


class ToolPanel():
    bl_label = 'Cats Blender Plugin'
    bl_idname = '3D_VIEW_TS_vrc'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'CATS'

    bpy.types.Scene.island_margin = bpy.props.FloatProperty(
        name='Margin',
        description='Margin to reduce bleed of adjacent islands',
        default=0.01,
        min=0.0,
        max=1.0,
    )

    bpy.types.Scene.area_weight = bpy.props.FloatProperty(
        name='Area weight',
        description='Weight projections vector by faces with larger areas',
        default=0.0,
        min=0.0,
        max=1.0,
    )

    bpy.types.Scene.angle_limit = bpy.props.FloatProperty(
        name='Angle',
        description='Lower for more projection groups, higher for less distortion',
        default=82.0,
        min=1.0,
        max=89.0,
    )

    bpy.types.Scene.texture_size = bpy.props.EnumProperty(
        name='Texture size',
        description='Lower for faster bake time, higher for more detail.',
        items=tools.common.get_texture_sizes
    )

    bpy.types.Scene.one_texture = bpy.props.BoolProperty(
        name='Disable multiple textures',
        description='Texture baking and multiple textures per material can look weird in the end result. Check this box if you are experiencing this.',
        default=True
    )

    bpy.types.Scene.pack_islands = bpy.props.BoolProperty(
        name='Pack islands',
        description='Transform all islands so that they will fill up the UV space as much as possible.',
        default=True
    )

    bpy.types.Scene.mesh_name_eye = bpy.props.EnumProperty(
        name='Mesh',
        description='The mesh with the eyes vertex groups',
        items=tools.common.get_meshes
    )

    bpy.types.Scene.mesh_name_atlas = bpy.props.EnumProperty(
        name='Target mesh',
        description='The mesh that you want to create a atlas from',
        items=tools.common.get_meshes
    )

    bpy.types.Scene.head = bpy.props.EnumProperty(
        name='Head',
        description='The head bone containing the eye bones',
        items=tools.common.get_bones,
    )

    bpy.types.Scene.eye_left = bpy.props.EnumProperty(
        name='Left eye',
        description='The left eye bone',
        items=tools.common.get_bones,
    )

    bpy.types.Scene.eye_right = bpy.props.EnumProperty(
        name='Right eye',
        description='The right eye bone',
        items=tools.common.get_bones,
    )

    bpy.types.Scene.wink_right = bpy.props.EnumProperty(
        name='Blink right',
        description='The shape key containing a blink with the right eye',
        items=tools.common.get_shapekeys,
    )

    bpy.types.Scene.wink_left = bpy.props.EnumProperty(
        name='Blink left',
        description='The shape key containing a blink with the left eye',
        items=tools.common.get_shapekeys,
    )

    bpy.types.Scene.lowerlid_right = bpy.props.EnumProperty(
        name='Lowerlid right',
        description='The shape key containing a slightly raised right lower lid. Can be set to "Basis" to leave empty',
        items=tools.common.get_shapekeys,
    )

    bpy.types.Scene.lowerlid_left = bpy.props.EnumProperty(
        name='Lowerlid left',
        description='The shape key containing a slightly raised left lower lid. Can be set to "Basis" to leave empty',
        items=tools.common.get_shapekeys,
    )

    bpy.types.Scene.experimental_eye_fix = bpy.props.BoolProperty(
        name='Experimental eye fix',
        description='Script will try to verify the newly created eye bones to be located in the correct position, this works by checking the location of the old eye vertex group. It is very useful for models that have over-extended eye bones that point out of the head',
        default=False
    )

    bpy.types.Scene.mesh_name_viseme = bpy.props.EnumProperty(
        name='Mesh',
        description='The mesh with the mouth shape keys',
        items=tools.common.get_meshes
    )

    bpy.types.Scene.mouth_a = bpy.props.EnumProperty(
        name='Viseme AA',
        description='Shape key containing mouth movement that looks like someone is saying "aa"',
        items=tools.common.get_shapekeys,
    )

    bpy.types.Scene.mouth_o = bpy.props.EnumProperty(
        name='Viseme OH',
        description='Shape key containing mouth movement that looks like someone is saying "oh"',
        items=tools.common.get_shapekeys,
    )

    bpy.types.Scene.mouth_ch = bpy.props.EnumProperty(
        name='Viseme CH',
        description='Shape key containing mouth movement that looks like someone is saying "ch". Opened lips and clenched teeth',
        items=tools.common.get_shapekeys,
    )

    bpy.types.Scene.shape_intensity = bpy.props.FloatProperty(
        name='Shape key mix intensity',
        description='Controls the strength in the creation of the shape keys. Lower for less mouth movement strength.',
        max=1,
        min=0.01,
        default=1,
        step=1,
    )

    bpy.types.Scene.root_bone = bpy.props.EnumProperty(
        name='To parent',
        description='This is a list of bones that look like they could be parented together to a root bone, this is very useful for dynamic bones. Select a group of bones from the list and press "Parent bones"',
        items=tools.common.get_parent_root_bones,
    )

    bpy.types.Scene.remove_zero_weight = bpy.props.BoolProperty(
        name='Remove zero weight bones',
        description='Removes zero weight bones in the proces',
        default=True
    )

    bpy.types.Scene.remove_constraints = bpy.props.BoolProperty(
        name='Remove bone constraints',
        description='Removes bone constraints in the proces',
        default=True
    )


class ArmaturePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_armature'
    bl_label = 'Armature'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, 'remove_constraints')
        row = box.row(align=True)
        row.prop(context.scene, 'remove_zero_weight')
        row = box.row(align=True)
        row.operator('armature.fix', icon='BONE_DATA')


class EyeTrackingPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_eye'
    bl_label = 'Eye tracking'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, 'mesh_name_eye', icon='MESH_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'head', icon='BONE_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'eye_left', icon='BONE_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'eye_right', icon='BONE_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'wink_left', icon='SHAPEKEY_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'wink_right', icon='SHAPEKEY_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'lowerlid_left', icon='SHAPEKEY_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'lowerlid_right', icon='SHAPEKEY_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'experimental_eye_fix')
        row = box.row(align=True)
        row.operator('create.eyes', icon='TRIA_RIGHT')


class VisemePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_viseme'
    bl_label = 'Visemes'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, 'mesh_name_viseme', icon='MESH_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'mouth_a', icon='SHAPEKEY_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'mouth_o', icon='SHAPEKEY_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'mouth_ch', icon='SHAPEKEY_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'shape_intensity')
        row = box.row(align=True)
        row.operator('auto.viseme', icon='TRIA_RIGHT')


class TranslationPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_translation'
    bl_label = 'Translation'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.operator('translate.shapekeys', icon='SHAPEKEY_DATA')
        row.operator('translate.bones', icon='BONE_DATA')
        row.operator('translate.meshes', icon='MESH_DATA')
        row = box.row(align=True)
        row.operator('translate.textures', icon='TEXTURE')
        row.operator('translate.materials', icon='MATERIAL')


class BoneRootPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_boneroot'
    bl_label = 'Bone Parenting'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, 'root_bone', icon='BONE_DATA')
        row = box.row(align=True)
        row.operator('refresh.root', icon='FILE_REFRESH')
        row.operator('root.function', icon='TRIA_RIGHT')


class AtlasPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_atlas'
    bl_label = 'Atlas'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, 'island_margin')
        row = box.row(align=True)
        row.prop(context.scene, 'angle_limit')
        row = box.row(align=True)
        row.prop(context.scene, 'area_weight')
        row = box.row(align=True)
        row.prop(context.scene, 'texture_size', icon='TEXTURE')
        row = box.row(align=True)
        row.prop(context.scene, 'mesh_name_atlas', icon='MESH_DATA')
        row = box.row(align=True)
        row.prop(context.scene, 'one_texture')
        row.prop(context.scene, 'pack_islands')
        row = box.row(align=True)
        row.operator('auto.atlas', icon='TRIA_RIGHT')

class UpdaterPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_updater'
    bl_label = 'Updater'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        addon_updater_ops.check_for_update_background()
        addon_updater_ops.update_settings_ui(self, context)

class CreditsPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_credits'
    bl_label = 'Credits'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        box.label('Cats Blender Plugin')
        row = box.row(align=True)
        box.label('Created by GiveMeAllYourCats for the VRC community <3')
        row = box.row(align=True)
        box.label('Special thanks to: Shotariya, Hotox and Neitri!')


class DemoPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # addon updater preferences

    auto_check_update = bpy.props.BoolProperty(
        name='Auto-check for Update',
        description='If enabled, auto-check for updates using an interval',
        default=False,
        )
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description='Number of months between checking for updates',
        default=0,
        min=0
        )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description='Number of days between checking for updates',
        default=7,
        min=0,
        )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description='Number of hours between checking for updates',
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description='Number of minutes between checking for updates',
        default=0,
        min=0,
        max=59
        )

    def draw(self, context):
        layout = self.layout

        # updater draw function
        addon_updater_ops.update_settings_ui(self, context)

def register():
    bpy.utils.register_class(tools.atlas.AutoAtlasButton)
    bpy.utils.register_class(tools.eyetracking.CreateEyesButton)
    bpy.utils.register_class(tools.viseme.AutoVisemeButton)
    bpy.utils.register_class(tools.translate.TranslateShapekeyButton)
    bpy.utils.register_class(tools.translate.TranslateBonesButton)
    bpy.utils.register_class(tools.translate.TranslateMeshesButton)
    bpy.utils.register_class(tools.translate.TranslateTexturesButton)
    bpy.utils.register_class(tools.translate.TranslateMaterialsButton)
    bpy.utils.register_class(tools.rootbone.RootButton)
    bpy.utils.register_class(tools.rootbone.RefreshRootButton)
    bpy.utils.register_class(tools.armature.FixArmature)
    bpy.utils.register_class(ArmaturePanel)
    bpy.utils.register_class(EyeTrackingPanel)
    bpy.utils.register_class(VisemePanel)
    bpy.utils.register_class(BoneRootPanel)
    bpy.utils.register_class(TranslationPanel)
    bpy.utils.register_class(AtlasPanel)
    bpy.utils.register_class(UpdaterPanel)
    bpy.utils.register_class(CreditsPanel)
    bpy.utils.register_class(DemoPreferences)
    addon_updater_ops.register(bl_info)

def unregister():
    bpy.utils.unregister_class(tools.atlas.AutoAtlasButton)
    bpy.utils.unregister_class(tools.eyetracking.CreateEyesButton)
    bpy.utils.unregister_class(tools.viseme.AutoVisemeButton)
    bpy.utils.unregister_class(tools.translate.TranslateShapekeyButton)
    bpy.utils.unregister_class(tools.translate.TranslateBonesButton)
    bpy.utils.unregister_class(tools.translate.TranslateMeshesButton)
    bpy.utils.unregister_class(tools.translate.TranslateTexturesButton)
    bpy.utils.unregister_class(tools.translate.TranslateMaterialsButton)
    bpy.utils.unregister_class(tools.rootbone.RootButton)
    bpy.utils.unregister_class(tools.rootbone.RefreshRootButton)
    bpy.utils.unregister_class(tools.armature.FixArmature)
    bpy.utils.unregister_class(AtlasPanel)
    bpy.utils.unregister_class(EyeTrackingPanel)
    bpy.utils.unregister_class(VisemePanel)
    bpy.utils.unregister_class(BoneRootPanel)
    bpy.utils.unregister_class(TranslationPanel)
    bpy.utils.unregister_class(ArmaturePanel)
    bpy.utils.unregister_class(UpdaterPanel)
    bpy.utils.unregister_class(CreditsPanel)
    bpy.utils.unregister_class(DemoPreferences)
    addon_updater_ops.unregister()

if __name__ == '__main__':
    register()
