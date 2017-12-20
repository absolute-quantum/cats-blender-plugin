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
# Edits by: GiveMeAllYourCats, Hotox

import bpy
import sys
import os
import importlib
import bpy.utils.previews
from . import addon_updater_ops
from collections import OrderedDict

mmd_tools_installed = False
try:
    import mmd_tools

    mmd_tools_installed = True
    print("mmd_tools found!")
except:
    print("mmd_tools not found!")
    pass

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import tools.viseme
import tools.atlas
import tools.eyetracking
import tools.bonemerge
import tools.rootbone
import tools.translate
import tools.armature
import tools.armature_manual
import tools.material
import tools.common
import tools.supporter
import tools.credits

importlib.reload(tools.viseme)
importlib.reload(tools.atlas)
importlib.reload(tools.eyetracking)
importlib.reload(tools.bonemerge)
importlib.reload(tools.rootbone)
importlib.reload(tools.translate)
importlib.reload(tools.armature)
importlib.reload(tools.armature_manual)
importlib.reload(tools.material)
importlib.reload(tools.common)
importlib.reload(tools.supporter)
importlib.reload(tools.credits)

bl_info = {
    'name': 'Cats Blender Plugin',
    'category': '3D View',
    'author': 'GiveMeAllYourCats',
    'location': 'View 3D > Tool Shelf > CATS',
    'description': 'A tool designed to shorten steps needed to import and optimize MMD models into VRChat',
    'version': [0, 4, 0],
    'blender': (2, 79, 0),
    'wiki_url': 'https://github.com/michaeldegroot/cats-blender-plugin',
    'tracker_url': 'https://github.com/michaeldegroot/cats-blender-plugin/issues',
    'warning': '',
}

slider_z = 0

# global variable to store icons in
preview_collections = {}

# List all the supporters here
supporters = OrderedDict()
#       'Display name' = 'Icon name'
supporters['Xeverian'] = 'xeverian'
supporters['Tupper'] = 'tupper'
supporters['Jazneo'] = 'jazneo'
supporters['Idea'] = 'idea'
supporters['RadaruS'] = 'radarus'
supporters['Kry10'] = 'kry10'
supporters['smead'] = 'smead'
supporters['kohai.istool'] = 'kohai'
supporters['Str4fe'] = 'Str4fe'


class ToolPanel:
    bl_label = 'Cats Blender Plugin'
    bl_idname = '3D_VIEW_TS_vrc'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'CATS'

    # Armature
    bpy.types.Scene.remove_zero_weight = bpy.props.BoolProperty(
        name='Remove Zero Weight Bones',
        description="Cleans up the bones hierarchy, because MMD models usually come with a lot of extra bones that don't directly affect any vertices.\n"
                    'Uncheck this if bones you want to keep got deleted.',
        default=True
    )

    # Eye Tracking
    bpy.types.Scene.eye_mode = bpy.props.EnumProperty(
        name="Eye Mode",
        description="Mode",
        items=[
            ("CREATION", "Creation", "Here you can create eye tracking."),
            ("TESTING", "Testing", "Here you can test how eye tracking will look ingame.")
        ]
    )

    bpy.types.Scene.mesh_name_eye = bpy.props.EnumProperty(
        name='Mesh',
        description='The mesh with the eyes vertex groups',
        items=tools.common.get_meshes
    )

    bpy.types.Scene.head = bpy.props.EnumProperty(
        name='Head',
        description='The head bone containing the eye bones',
        items=tools.common.get_bones_head
    )

    bpy.types.Scene.eye_left = bpy.props.EnumProperty(
        name='Left Eye',
        description='The left eye bone',
        items=tools.common.get_bones_eye_l
    )

    bpy.types.Scene.eye_right = bpy.props.EnumProperty(
        name='Right Eye',
        description='The right eye bone',
        items=tools.common.get_bones_eye_r
    )

    bpy.types.Scene.wink_left = bpy.props.EnumProperty(
        name='Blink Left',
        description='The shape key containing a blink with the left eye.',
        items=tools.common.get_shapekeys_eye_blink_l
    )

    bpy.types.Scene.wink_right = bpy.props.EnumProperty(
        name='Blink Right',
        description='The shape key containing a blink with the right eye.',
        items=tools.common.get_shapekeys_eye_blink_r
    )

    bpy.types.Scene.lowerlid_left = bpy.props.EnumProperty(
        name='Lowerlid Left',
        description='The shape key containing a slightly raised left lower lid.\n'
                    'Can be set to "Basis" to disable lower lid movement',
        items=tools.common.get_shapekeys_eye_low_l
    )

    bpy.types.Scene.lowerlid_right = bpy.props.EnumProperty(
        name='Lowerlid Right',
        description='The shape key containing a slightly raised right lower lid.\n'
                    'Can be set to "Basis" to disable lower lid movement',
        items=tools.common.get_shapekeys_eye_low_r
    )

    bpy.types.Scene.disable_eye_movement = bpy.props.BoolProperty(
        name='Disable Eye Movement',
        description='IMPORTANT: Do your decimation first if you check this!\n'
                    '\n'
                    'Disables eye movement. Useful if you only want blinking.\n'
                    'This creates eye bones with no movement bound to them.\n'
                    'You still have to correctly assign the eye bones in Unity.',
        subtype='DISTANCE'
    )

    bpy.types.Scene.disable_eye_blinking = bpy.props.BoolProperty(
        name='Disable Eye Blinking',
        description='Disables eye blinking. Useful if you only want eye movement.\n'
                    'This will create the necessary shape keys but leaves them empty.',
        subtype='NONE'
    )

    bpy.types.Scene.eye_distance = bpy.props.FloatProperty(
        name='Eye Movement Range',
        description='Higher = more eye movement\n'
                    'Lower = less eye movement\n'
                    'Warning: Too little or too much range can glitch the eyes.\n'
                    'Test your results in the "Eye Testing"-Tab!',
        default=0.8,
        min=0.0,
        max=2.0,
        step=1.0,
        precision=2,
        subtype='FACTOR'
    )

    bpy.types.Scene.eye_rotation_x = bpy.props.IntProperty(
        name='Up - Down',
        description='Rotate the eye bones on the vertical axis.',
        default=0,
        min=-19,
        max=25,
        step=1,
        subtype='FACTOR'
    )

    bpy.types.Scene.eye_rotation_y = bpy.props.IntProperty(
        name='Left - Right',
        description='Rotate the eye bones on the horizontal axis.',
        default=0,
        min=-19,
        max=19,
        step=1,
        subtype='FACTOR'
    )

    bpy.types.Scene.eye_blink_shape = bpy.props.FloatProperty(
        name='Blink Strenght',
        description='Test the blinking of the eye.',
        default=1.0,
        min=0.0,
        max=1.0,
        step=1.0,
        precision=2,
        subtype='FACTOR'
    )

    bpy.types.Scene.eye_lowerlid_shape = bpy.props.FloatProperty(
        name='Lowerlid Strenght',
        description='Test the lowerlid blinking of the eye.',
        default=1.0,
        min=0.0,
        max=1.0,
        step=1.0,
        precision=2,
        subtype='FACTOR'
    )

    # Visemes
    bpy.types.Scene.mesh_name_viseme = bpy.props.EnumProperty(
        name='Mesh',
        description='The mesh with the mouth shape keys',
        items=tools.common.get_meshes
    )

    bpy.types.Scene.mouth_a = bpy.props.EnumProperty(
        name='Viseme AA',
        description='Shape key containing mouth movement that looks like someone is saying "aa".\nDo not put empty shape keys like "Basis" in here',
        items=tools.common.get_shapekeys_mouth_ah
    )

    bpy.types.Scene.mouth_o = bpy.props.EnumProperty(
        name='Viseme OH',
        description='Shape key containing mouth movement that looks like someone is saying "oh".\nDo not put empty shape keys like "Basis" in here',
        items=tools.common.get_shapekeys_mouth_oh
    )

    bpy.types.Scene.mouth_ch = bpy.props.EnumProperty(
        name='Viseme CH',
        description='Shape key containing mouth movement that looks like someone is saying "ch". Opened lips and clenched teeth.\nDo not put empty shape keys like "Basis" in here',
        items=tools.common.get_shapekeys_mouth_ch
    )

    bpy.types.Scene.shape_intensity = bpy.props.FloatProperty(
        name='Shape Key Mix Intensity',
        description='Controls the strength in the creation of the shape keys. Lower for less mouth movement strength.',
        default=1.0,
        min=0.0,
        max=1.0,
        step=0.1,
        precision=2,
        subtype='FACTOR'
    )

    # Bone Parenting
    bpy.types.Scene.root_bone = bpy.props.EnumProperty(
        name='To Parent',
        description='List of bones that look like they could be parented together to a root bone.',
        items=tools.rootbone.get_parent_root_bones,
    )

    # Optimize
    bpy.types.Scene.optimize_mode = bpy.props.EnumProperty(
        name="Optimize Mode",
        description="Mode",
        items=[
            ("ATLAS", "Atlas", "Allows you to make a texture atlas."),
            ("MATERIAL", "Material", "Some various options on material manipulation."),
            ("BONEMERGING", "Bone Merging", "Allows child bones to be merged and mixed in their above parents."),
        ]
    )

    bpy.types.Scene.island_margin = bpy.props.FloatProperty(
        name='Margin',
        description='Margin to reduce bleed of adjacent islands',
        default=0.01,
        min=0.0,
        max=1.0,
        step=0.1,
        precision=2,
        subtype='FACTOR'
    )

    bpy.types.Scene.area_weight = bpy.props.FloatProperty(
        name='Area Weight',
        description='Weight projections vector by faces with larger areas',
        default=0.0,
        min=0.0,
        max=1.0,
        step=0.1,
        precision=2,
        subtype='FACTOR'
    )

    bpy.types.Scene.angle_limit = bpy.props.FloatProperty(
        name='Angle',
        description='Lower for more projection groups, higher for less distortion',
        default=82.0,
        min=1.0,
        max=89.0,
        step=10.0,
        precision=1,
        subtype='FACTOR'
    )

    bpy.types.Scene.texture_size = bpy.props.EnumProperty(
        name='Texture Size',
        description='Lower for faster bake time, higher for more detail.',
        items=tools.common.get_texture_sizes
    )

    bpy.types.Scene.one_texture = bpy.props.BoolProperty(
        name='One Texture Material',
        description='Texture baking and multiple textures per material can look weird in the end result. Check this box if you are experiencing this.',
        default=True
    )

    bpy.types.Scene.pack_islands = bpy.props.BoolProperty(
        name='Pack Islands',
        description='Transform all islands so that they will fill up the UV space as much as possible.',
        default=False
    )

    bpy.types.Scene.mesh_name_atlas = bpy.props.EnumProperty(
        name='Target Mesh',
        description='The mesh that you want to create a atlas from',
        items=tools.common.get_meshes
    )

    # Bone Merging
    bpy.types.Scene.merge_ratio = bpy.props.FloatProperty(
        name='Merge Ratio',
        description='Higher = more bones will be merged\n'
                    'Lower = less bones will be merged\n',
        default=50,
        min=1,
        max=100,
        step=1,
        precision=0,
        subtype='PERCENTAGE'
    )

    bpy.types.Scene.merge_mesh = bpy.props.EnumProperty(
        name='Mesh',
        description='The mesh with the bones vertex groups',
        items=tools.common.get_meshes
    )

    bpy.types.Scene.merge_bone = bpy.props.EnumProperty(
        name='To Merge',
        description='List of bones that look like they could be marged together to reduce overall bones.',
        items=tools.rootbone.get_parent_root_bones,
    )


class ArmaturePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_armature_v1'
    bl_label = 'Model'

    def draw(self, context):
        addon_updater_ops.check_for_update_background()
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        if mmd_tools_installed:
            row = col.row(align=True)
            row.scale_y = 1.4
            row.operator('armature_manual.import_model', icon='ARMATURE_DATA')
            col.separator()

        row = col.row(align=True)
        row.prop(context.scene, 'remove_zero_weight')
        row = col.row(align=True)
        row.scale_y = 1.4
        row.operator('armature.fix', icon='BONE_DATA')

        col.separator()
        col.label('Manual Model Fixing:')
        row = col.row(align=True)
        row.scale_y = 1.05
        row.operator('armature_manual.separate_by_materials', icon='MESH_DATA')
        row = col.row(align=True)
        row.scale_y = 1.05
        row.operator('armature_manual.join_meshes', icon='MESH_DATA')
        row = col.row(align=True)
        row.scale_y = 1.05
        row.operator('armature_manual.mix_weights', icon='BONE_DATA')

        ob = bpy.context.active_object
        if bpy.context.active_object is None or ob.mode != 'POSE':
            row = col.row(align=True)
            row.scale_y = 1.05
            row.operator('armature_manual.start_pose_mode', icon='POSE_HLT')
        else:
            row = col.row(align=True)
            row.scale_y = 1.05
            row.operator('armature_manual.stop_pose_mode', icon='POSE_DATA')

        # row = col.row(align=True)
        # row.scale_y = 1.1
        # row.operator('armature_manual.separate_by_materials', icon='MESH_DATA')
        # row = col.row(align=True)
        # row.scale_y = 1.1
        # row.operator('armature_manual.join_meshes2', icon='MESH_DATA')


class TranslationPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_translation_v1'
    bl_label = 'Translation'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1
        row.operator('translate.shapekeys', icon='SHAPEKEY_DATA')
        row.operator('translate.bones', icon='BONE_DATA')
        row = col.row(align=True)
        row.scale_y = 1
        row.operator('translate.meshes', icon='MESH_DATA')
        # row.operator('translate.textures', icon='TEXTURE')
        row.operator('translate.materials', icon='MATERIAL')


class EyeTrackingPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_eye_v1'
    bl_label = 'Eye Tracking'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'eye_mode', expand=True)

        if context.scene.eye_mode == 'CREATION':
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'mesh_name_eye', icon='MESH_DATA')

            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'head', icon='BONE_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_movement:
                row.active = False
            row.prop(context.scene, 'eye_left', icon='BONE_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_movement:
                row.active = False
            row.prop(context.scene, 'eye_right', icon='BONE_DATA')

            col.separator()
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_blinking:
                row.active = False
            row.prop(context.scene, 'wink_left', icon='SHAPEKEY_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_blinking:
                row.active = False
            row.prop(context.scene, 'wink_right', icon='SHAPEKEY_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_blinking:
                row.active = False
            row.prop(context.scene, 'lowerlid_left', icon='SHAPEKEY_DATA')
            row = col.row(align=True)
            row.scale_y = 1.1
            if context.scene.disable_eye_blinking:
                row.active = False
            row.prop(context.scene, 'lowerlid_right', icon='SHAPEKEY_DATA')

            col.separator()
            row = col.row(align=True)
            row.prop(context.scene, 'disable_eye_blinking')

            row = col.row(align=True)
            row.prop(context.scene, 'disable_eye_movement')

            if not context.scene.disable_eye_movement:
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_distance')

            col = box.column(align=True)
            row = col.row(align=True)
            row.operator('create.eyes', icon='TRIA_RIGHT')

            # armature = common.get_armature()
            # if "RightEye" in armature.pose.bones:
            #     row = col.row(align=True)
            #     row.label('Eye Bone Tweaking:')
        else:
            if tools.common.get_armature() is None:
                box.label('No model found!', icon='ERROR')
                return

            mode = bpy.context.active_object.mode
            if mode != 'POSE':
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.5
                row.operator('eyes.test', icon='TRIA_RIGHT')
            else:
                # col.separator()
                # row = col.row(align=True)
                # row.operator('eyes.test_stop', icon='PAUSE')

                col.separator()
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_rotation_x', icon='FILE_PARENT')
                row = col.row(align=True)
                row.prop(context.scene, 'eye_rotation_y', icon='ARROW_LEFTRIGHT')
                row = col.row(align=True)
                row.operator('eyes.set_rotation', icon='MAN_ROT')

                # global slider_z
                # if context.scene.eye_blink_shape != slider_z:
                #     slider_z = context.scene.eye_blink_shape
                #     eyetracking.update_bones(context, slider_z)

                col.separator()
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_distance')
                row = col.row(align=True)
                row.operator('eyes.adjust_eyes', icon='CURVE_NCIRCLE')

                col.separator()
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_blink_shape')
                row.operator('eyes.test_blink', icon='RESTRICT_VIEW_OFF')
                row = col.row(align=True)
                row.prop(context.scene, 'eye_lowerlid_shape')
                row.operator('eyes.test_lowerlid', icon='RESTRICT_VIEW_OFF')
                row = col.row(align=True)
                row.operator('eyes.reset_blink_test', icon='FILE_REFRESH')

                col.separator()
                col.separator()
                row = col.row(align=True)
                row.scale_y = 1.5
                row.operator('eyes.test_stop', icon='PAUSE')


class VisemePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_viseme_v1'
    bl_label = 'Visemes'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, 'mesh_name_viseme', icon='MESH_DATA')
        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, 'mouth_a', icon='SHAPEKEY_DATA')
        row = col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, 'mouth_o', icon='SHAPEKEY_DATA')
        row = col.row(align=True)
        row.scale_y = 1.1
        row.prop(context.scene, 'mouth_ch', icon='SHAPEKEY_DATA')
        col.separator()
        row = col.row(align=True)
        row.prop(context.scene, 'shape_intensity')
        col.separator()
        row = col.row(align=True)
        row.operator('auto.viseme', icon='TRIA_RIGHT')


class BoneRootPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_boneroot_v1'
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


class OptimizePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_optimize_v1'
    bl_label = 'Optimization'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        col = box.column(align=True)

        row = col.row(align=True)
        row.prop(context.scene, 'optimize_mode', expand=True)

        if context.scene.optimize_mode == 'ATLAS':
            col.separator()
            row = box.row(align=True)
            row.prop(context.scene, 'island_margin')
            row.scale_y = 0.9
            row = box.row(align=True)
            row.prop(context.scene, 'angle_limit')
            row.scale_y = 0.9
            row = box.row(align=True)
            row.prop(context.scene, 'area_weight')
            row.scale_y = 0.9
            row = box.row(align=True)
            row.prop(context.scene, 'texture_size', icon='TEXTURE')
            row = box.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'mesh_name_atlas', icon='MESH_DATA')
            row = box.row(align=True)
            row.scale_y = 1.1
            row.prop(context.scene, 'one_texture')
            row.prop(context.scene, 'pack_islands')
            row = box.row(align=True)
            row.operator('auto.atlas', icon='TRIA_RIGHT')

        if context.scene.optimize_mode == 'MATERIAL':
            col = box.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator('combine.mats', icon='MATERIAL')
            row = col.row(align=True)
            row.scale_y = 1.1
            row.operator('one.tex', icon='TEXTURE')

        if context.scene.optimize_mode == 'BONEMERGING':
            row = box.row(align=True)
            row.prop(context.scene, 'merge_mesh')
            row = box.row(align=True)
            row.prop(context.scene, 'merge_bone')
            row = box.row(align=True)
            row.prop(context.scene, 'merge_ratio')
            row = box.row(align=True)
            col.separator()
            row.operator('refresh.root', icon='FILE_REFRESH')
            row.operator('bone.merge', icon="AUTOMERGE_ON")


class UpdaterPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_updater_v2'
    bl_label = 'Updater'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        # addon_updater_ops.check_for_update_background()
        addon_updater_ops.update_settings_ui(self, context)


class SupporterPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_supporter_v2'
    bl_label = 'Supporters'
    # bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)

        i = 0
        cont = True
        items = list(supporters.items())
        while cont:
            try:
                item = items[i]
                if i == 0:
                    row.label('Thanks to our awesome supporters! <3')
                    col.separator()
                if i % 3 == 0:
                    row = col.row(align=True)
                row.operator('supporter.person', text=item[0], emboss=False, icon_value=preview_collections["custom_icons"][item[1]].icon_id)
                i += 1
            except IndexError:
                if i % 3 == 0:
                    cont = False
                    continue
                row.label('')
                i += 1

        row = col.row(align=True)
        row.separator()
        row = col.row(align=True)
        row.label('Do you like this plugin and want to support us?')
        row = col.row(align=True)
        row.operator('supporter.patreon', icon_value=preview_collections["custom_icons"]["heart1"].icon_id)


class CreditsPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_credits_v1'
    bl_label = 'Credits'

    def draw(self, context):
        global custom_icons
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)

        version = bl_info.get('version')
        version_str = 'Cats Blender Plugin ('
        if len(version) > 0:
            version_str += str(version[0])
            for index, i in enumerate(version):
                if index == 0:
                    continue
                version_str += '.' + str(version[index])
        version_str += ')'

        row.label(version_str, icon_value=preview_collections["custom_icons"]["cats1"].icon_id)
        col.separator()
        row = col.row(align=True)
        row.label('Created by GiveMeAllYourCats for the VRC community <3')
        row.scale_y = 0.5
        row = col.row(align=True)
        row.label('Special thanks to: Shotariya, Hotox and Neitri!')
        row = col.row(align=True)
        row.label('Want to give feedback or found a bug?')
        # box.label('Want to give feedback or found a bug?', icon_value=preview_collections["custom_icons"]["heart1"].icon_id)
        # box.label('Want to give feedback or found a bug?', icon_value=preview_collections["custom_icons"]["heart2"].icon_id)
        # box.label('Want to give feedback or found a bug?', icon_value=preview_collections["custom_icons"]["heart3"].icon_id)
        # box.label('Want to give feedback or found a bug?', icon_value=preview_collections["custom_icons"]["heart4"].icon_id)
        # box.label('Want to give feedback or found a bug?', icon_value=preview_collections["custom_icons"]["discord1"].icon_id)
        # box.label('Want to give feedback or found a bug?', icon_value=preview_collections["custom_icons"]["discord2"].icon_id)

        row = col.row(align=True)
        row.operator('credits.discord', icon_value=preview_collections["custom_icons"]["discord1"].icon_id)
        row = col.row(align=True)
        row.operator('credits.forum', icon_value=preview_collections["custom_icons"]["cats1"].icon_id)


class UpdaterPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    auto_check_update = bpy.props.BoolProperty(
        name='Auto-check for Update',
        description='If enabled, auto-check for updates using an interval',
        default=True,
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
        default=1,
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
        addon_updater_ops.update_settings_ui(self, context)


def load_icons():
    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    pcoll = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    # load a preview thumbnail of a file and store in the previews collection
    pcoll.load('heart1', os.path.join(my_icons_dir, 'heart1.png'), 'IMAGE')
    pcoll.load('heart2', os.path.join(my_icons_dir, 'heart2.png'), 'IMAGE')
    pcoll.load('heart3', os.path.join(my_icons_dir, 'heart3.png'), 'IMAGE')
    pcoll.load('heart4', os.path.join(my_icons_dir, 'heart4.png'), 'IMAGE')
    pcoll.load('discord1', os.path.join(my_icons_dir, 'discord1.png'), 'IMAGE')
    pcoll.load('discord2', os.path.join(my_icons_dir, 'discord2.png'), 'IMAGE')
    pcoll.load('cats1', os.path.join(my_icons_dir, 'cats1.png'), 'IMAGE')
    pcoll.load('patreon1', os.path.join(my_icons_dir, 'patreon1.png'), 'IMAGE')
    pcoll.load('patreon2', os.path.join(my_icons_dir, 'patreon2.png'), 'IMAGE')
    pcoll.load('merge', os.path.join(my_icons_dir, 'merge.png'), 'IMAGE')

    # load the supporters icons
    for key, value in supporters.items():
        try:
            pcoll.load(value, os.path.join(my_icons_dir, 'supporters/' + value + '.png'), 'IMAGE')
        except KeyError:
            pass

    preview_collections['custom_icons'] = pcoll


def unload_icons():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()


classesToRegister = [
    ArmaturePanel,
    BoneRootPanel,
    CreditsPanel,
    EyeTrackingPanel,
    OptimizePanel,
    SupporterPanel,
    TranslationPanel,
    UpdaterPanel,
    UpdaterPreferences,
    VisemePanel,
    tools.armature.FixArmature,
    # tools.armature_manual.Finalize,
    # tools.armature_manual.Import,
    tools.armature_manual.ImportModel,
    tools.armature_manual.JoinMeshes,
    # tools.armature_manual.JoinMeshesTest,
    tools.armature_manual.MixWeights,
    tools.armature_manual.SeparateByMaterials,
    # tools.armature_manual.SeparateByMaterials,
    tools.armature_manual.StartPoseMode,
    tools.armature_manual.StopPoseMode,
    # tools.armature_manual.Test,
    tools.atlas.AutoAtlasButton,
    tools.bonemerge.BoneMergeButton,
    tools.credits.DiscordButton,
    tools.credits.ForumButton,
    tools.eyetracking.AdjustEyesButton,
    tools.eyetracking.CreateEyesButton,
    tools.eyetracking.ResetBlinkTest,
    tools.eyetracking.SetRotationButton,
    tools.eyetracking.StartTestingButton,
    tools.eyetracking.StopTestingButton,
    tools.eyetracking.TestBlinking,
    tools.eyetracking.TestLowerlid,
    tools.material.CombineMaterialsButton,
    tools.material.OneTexPerMatButton,
    tools.rootbone.RefreshRootButton,
    tools.rootbone.RootButton,
    tools.supporter.PatreonButton,
    tools.supporter.PersonButton,
    tools.translate.TranslateBonesButton,
    tools.translate.TranslateMaterialsButton,
    tools.translate.TranslateMeshesButton,
    tools.translate.TranslateShapekeyButton,
    tools.translate.TranslateTexturesButton,
    tools.viseme.AutoVisemeButton,
]

def register():
    load_icons()
    for value in classesToRegister:        
        bpy.utils.register_class(value)
    addon_updater_ops.register(bl_info)


def unregister():
    for value in classesToRegister:        
        bpy.utils.unregister_class(value)
    addon_updater_ops.unregister()
    unload_icons()


if __name__ == '__main__':
    register()
