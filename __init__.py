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
from . import addon_updater_ops

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import tools.viseme
import tools.atlas
import tools.eyetracking
import tools.rootbone
import tools.translate
import tools.armature
import tools.armature_manual
import tools.common
import tools.credits

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
    'version': [0, 2, 0],
    'blender': (2, 79, 0),
    'wiki_url': 'https://github.com/michaeldegroot/cats-blender-plugin',
    'tracker_url': 'https://github.com/michaeldegroot/cats-blender-plugin/issues',
    'warning': '',
}

slider_z = 0


class ListItem(bpy.types.PropertyGroup):
    """ Group of properties representing an item in the list """

    name = bpy.props.StringProperty(
        name="Name",
        description="A name for this item",
        default="Untitled"
    )

    random_prop = bpy.props.StringProperty(
        name="Any other property you want",
        description="",
        default=""
    )


class ToolPanel:
    bl_label = 'Cats Blender Plugin'
    bl_idname = '3D_VIEW_TS_vrc'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'CATS'

    # Armature
    bpy.types.Scene.remove_zero_weight = bpy.props.BoolProperty(
        name='Remove Zero Weight Bones',
        description="Cleans up the bones hierarchy, because MMD models usually come with a lot of extra bones that don't directly affect any vertices.",
        default=True
    )

    # Eye Tracking
    bpy.types.Scene.eye_mode = bpy.props.EnumProperty(
        name="Eye Mode",
        description="Mode",
        items=[
            ("CREATION", "Eye Creation", "Here you can create eye tracking."),
            ("TESTING", "Eye Testing", "Here you can test how eye tracking will look ingame.")
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
        description='The shape key containing a blink with the left eye.\n'
                    'IMPORTANT: Do not set this to "Basis"! Disable Eye Blinking instead!',
        items=tools.common.get_shapekeys_eye_blink_l
    )

    bpy.types.Scene.wink_right = bpy.props.EnumProperty(
        name='Blink Right',
        description='The shape key containing a blink with the right eye.\n'
                    'IMPORTANT: Do not set this to "Basis"! Disable Eye Blinking instead!',
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
        name='Eye Movement Speed',
        description='Higher = more eye movement\n'
                    'Lower = less eye movement\n'
                    'Warning: Too little or too much speed can glitch the eyes.\n'
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
        min=-22,
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

    # Auto Atlas
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
        name='Disable Multiple Textures',
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


class ArmaturePanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_armature_v1'
    bl_label = 'Armature'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.prop(context.scene, 'remove_zero_weight')
        row = box.row(align=True)
        row.scale_y = 1.4
        row.operator('armature.fix', icon='BONE_DATA')

        col = box.column(align=True)

        col.label('Manual Armature Fixing:')
        col.separator()
        # row = col.row(align=True)
        # row.scale_y = 1.1
        # row.operator('armature_manual.separate_by_materials', icon='MESH_DATA')
        # row = col.row(align=True)
        # row.scale_y = 1.1
        # row.operator('armature_manual.join_meshes2', icon='MESH_DATA')
        row = col.row(align=True)
        row.scale_y = 1.1
        row.operator('armature_manual.join_meshes', icon='MESH_DATA')
        row = col.row(align=True)
        row.scale_y = 1.1
        row.operator('armature_manual.mix_weights', icon='BONE_DATA')


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
            row.prop(context.scene, 'disable_eye_movement')

            row = col.row(align=True)
            row.prop(context.scene, 'disable_eye_blinking')

            if not context.scene.disable_eye_movement:
                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_distance')

            col = box.column(align=True)
            row = col.row(align=True)
            row.operator('create.eyes', icon='TRIA_RIGHT')

            # armature = tools.common.get_armature()
            # if "RightEye" in armature.pose.bones:
            #     row = col.row(align=True)
            #     row.label('Eye Bone Tweaking:')
        else:
            mode = bpy.context.active_object.mode
            if mode != 'POSE':
                col.separator()
                row = col.row(align=True)
                row.operator('eyes.test', icon='TRIA_RIGHT')
            else:
                col.separator()
                row = col.row(align=True)
                row.operator('eyes.test_stop', icon='TRIA_RIGHT')

                col.separator()
                row = col.row(align=True)
                row.prop(context.scene, 'eye_rotation_x', icon='FILE_PARENT')
                row = col.row(align=True)
                row.prop(context.scene, 'eye_rotation_y', icon='ARROW_LEFTRIGHT')

                # global slider_z
                # if context.scene.eye_rotation_z != slider_z:
                #     slider_z = context.scene.eye_rotation_z
                #     tools.eyetracking.update_bones(slider_z)

                col.separator()
                row = col.row(align=True)
                row.operator('eyes.set_rotation', icon='TRIA_RIGHT')


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


class AtlasPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_atlas_v1'
    bl_label = 'Texture Atlas'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
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


class UpdaterPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_updater_v2'
    bl_label = 'Updater'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        addon_updater_ops.check_for_update_background()
        addon_updater_ops.update_settings_ui(self, context)


class CreditsPanel(ToolPanel, bpy.types.Panel):
    bl_idname = 'VIEW3D_PT_credits_v1'
    bl_label = 'Credits'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        version = bl_info.get('version')
        version_str = 'Cats Blender Plugin ('
        if len(version) > 0:
            version_str += str(version[0])
            for index, i in enumerate(version):
                if index == 0:
                    continue
                version_str += '.' + str(version[index])
        version_str += ')'
        box.label(version_str)
        box.label('Created by GiveMeAllYourCats for the VRC community <3')
        box.label('Special thanks to: Shotariya, Hotox and Neitri!')
        box.label('Want to give feedback or found a bug?')
        row = box.row(align=True)
        row.operator('credits.forum', icon='LOAD_FACTORY')


class UpdaterPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

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
        addon_updater_ops.update_settings_ui(self, context)


def register():
    bpy.utils.register_class(tools.atlas.AutoAtlasButton)
    bpy.utils.register_class(tools.eyetracking.CreateEyesButton)
    bpy.utils.register_class(tools.eyetracking.StartTestingButton)
    bpy.utils.register_class(tools.eyetracking.StopTestingButton)
    bpy.utils.register_class(tools.eyetracking.SetRotationButton)
    bpy.utils.register_class(tools.viseme.AutoVisemeButton)
    bpy.utils.register_class(tools.translate.TranslateShapekeyButton)
    bpy.utils.register_class(tools.translate.TranslateBonesButton)
    bpy.utils.register_class(tools.translate.TranslateMeshesButton)
    bpy.utils.register_class(tools.translate.TranslateTexturesButton)
    bpy.utils.register_class(tools.translate.TranslateMaterialsButton)
    bpy.utils.register_class(tools.rootbone.RootButton)
    bpy.utils.register_class(tools.rootbone.RefreshRootButton)
    bpy.utils.register_class(tools.armature.FixArmature)
    # bpy.utils.register_class(tools.armature_manual.SeparateByMaterials)
    # bpy.utils.register_class(tools.armature_manual.JoinMeshesTest)
    bpy.utils.register_class(tools.armature_manual.JoinMeshes)
    bpy.utils.register_class(tools.armature_manual.MixWeights)
    bpy.utils.register_class(tools.credits.ForumButton)
    bpy.utils.register_class(ArmaturePanel)
    bpy.utils.register_class(TranslationPanel)
    bpy.utils.register_class(EyeTrackingPanel)
    bpy.utils.register_class(VisemePanel)
    bpy.utils.register_class(BoneRootPanel)
    bpy.utils.register_class(AtlasPanel)
    bpy.utils.register_class(UpdaterPanel)
    bpy.utils.register_class(CreditsPanel)
    bpy.utils.register_class(UpdaterPreferences)
    addon_updater_ops.register(bl_info)


def unregister():
    bpy.utils.unregister_class(tools.atlas.AutoAtlasButton)
    bpy.utils.unregister_class(tools.eyetracking.CreateEyesButton)
    bpy.utils.unregister_class(tools.eyetracking.StartTestingButton)
    bpy.utils.unregister_class(tools.eyetracking.StopTestingButton)
    bpy.utils.unregister_class(tools.eyetracking.SetRotationButton)
    bpy.utils.unregister_class(tools.viseme.AutoVisemeButton)
    bpy.utils.unregister_class(tools.translate.TranslateShapekeyButton)
    bpy.utils.unregister_class(tools.translate.TranslateBonesButton)
    bpy.utils.unregister_class(tools.translate.TranslateMeshesButton)
    bpy.utils.unregister_class(tools.translate.TranslateTexturesButton)
    bpy.utils.unregister_class(tools.translate.TranslateMaterialsButton)
    bpy.utils.unregister_class(tools.rootbone.RootButton)
    bpy.utils.unregister_class(tools.rootbone.RefreshRootButton)
    bpy.utils.unregister_class(tools.armature.FixArmature)
    bpy.utils.unregister_class(tools.armature_manual.MixWeights)
    bpy.utils.unregister_class(tools.armature_manual.JoinMeshes)
    # bpy.utils.unregister_class(tools.armature_manual.JoinMeshesTest)
    # bpy.utils.unregister_class(tools.armature_manual.SeparateByMaterials)
    bpy.utils.unregister_class(tools.credits.ForumButton)
    bpy.utils.unregister_class(AtlasPanel)
    bpy.utils.unregister_class(EyeTrackingPanel)
    bpy.utils.unregister_class(VisemePanel)
    bpy.utils.unregister_class(BoneRootPanel)
    bpy.utils.unregister_class(TranslationPanel)
    bpy.utils.unregister_class(ArmaturePanel)
    bpy.utils.unregister_class(UpdaterPanel)
    bpy.utils.unregister_class(CreditsPanel)
    bpy.utils.unregister_class(UpdaterPreferences)
    addon_updater_ops.unregister()


if __name__ == '__main__':
    register()
