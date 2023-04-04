# GPL License

import os
import bpy
import copy
import zipfile
import webbrowser
import addon_utils
import shutil
import bpy_extras.io_utils
import time
import subprocess
from mathutils import Matrix
from math import sqrt

from .. import globs
from . import armature_manual
from . import common as Common
from . import settings as Settings
from . import fbx_patch as Fbx_patch
from .common import version_2_79_or_older
from .register import register_wrap
from .translations import t

mmd_tools_installed = False
try:
    import mmd_tools_local
    mmd_tools_installed = True
except:
    pass

current_blender_version = str(bpy.app.version[:2])[1:-1].replace(', ', '.')

# In blender 2.79 this string gets cut off after char 63, so don't go over that limit
# Bug Report: https://blender.stackexchange.com/questions/110788/file-browser-filter-not-working-correctly
#             <                                                               > Don't go outside these brackets
formats_279 = '*.pm*;*.xps;*.mesh;*.ascii;*.smd;*.qc;*.fbx;*.dae;*.vrm;*.zip'
formats = '*.pmx;*.pmd;*.xps;*.mesh;*.ascii;*.smd;*.qc;*.qci;*.vta;*.dmx;*.fbx;*.dae;*.vrm;*.zip'
format_list = formats.replace('*.', '').split(';')
zip_files = {}


@register_wrap
class ImportAnyModel(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'cats_importer.import_any_model'
    bl_label = t('ImportAnyModel.label')
    if version_2_79_or_older():
        bl_description = t('ImportAnyModel.desc2.79')
    else:
        bl_description = t('ImportAnyModel.desc2.8')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    files = bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory = bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob = bpy.props.StringProperty(default=formats_279 if version_2_79_or_older() else formats, options={'HIDDEN'})
    text1 = bpy.props.BoolProperty(
        name=t('ImportAnyModel.importantInfo.label'),
        description=t('ImportAnyModel.importantInfo.desc'),
        default=False
    )

    def execute(self, context):
        global zip_files
        zip_files = {}
        has_zip_file = False

        Common.remove_unused_objects()

        # Make sure that the first layer is visible
        if hasattr(context.scene, 'layers'):
            context.scene.layers[0] = True

        # Save all current objects to check which armatures got added by the importer
        pre_import_objects = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']

        # Import the files using their corresponding importer
        if self.directory:
            for f in self.files:
                file_name = f.name
                self.import_file(self.directory, file_name)
                if file_name.lower().endswith('.zip'):
                    has_zip_file = True
        # If this operator is called with no directory but a filepath argument, import that
        elif self.filepath:
            print(self.filepath)
            self.import_file(os.path.dirname(self.filepath), os.path.basename(self.filepath))

        if has_zip_file:
            if not zip_files:
                Common.show_error(4, [t('ImportAnyModel.error.emptyZip')])

            # Import all models from zip files that contain only one importable model
            remove_keys = []
            for zip_path, files in copy.deepcopy(zip_files).items():
                context.scene.zip_content = zip_path + ' ||| ' + files[0]
                if len(files) == 1:
                    ImportAnyModel.extract_file()
                    remove_keys.append(zip_path)

            # Remove the models from zip file list that got already imported
            for key in remove_keys:
                zip_files.pop(key)

            # Only if a zip contains more than one model, open the zip model selection popup
            if zip_files.keys():
                bpy.ops.cats_importer.zip_popup('INVOKE_DEFAULT')

        # Create list of armatures that got added during import, select them in cats and fix their bone orientations if necessary
        fix_armatures_post_import(pre_import_objects)

        return {'FINISHED'}

    @staticmethod
    def import_file(directory, file_name):
        file_path = os.path.join(directory, file_name)
        file_ending = file_name.split('.')[-1].lower()

        # MMD
        if file_ending == 'pmx' or file_ending == 'pmd':
            try:
                bpy.ops.mmd_tools.import_model('EXEC_DEFAULT',
                                               files=[{'name': file_name}],
                                               directory=directory,
                                               scale=0.08,
                                               types={'MESH', 'ARMATURE', 'MORPHS'},
                                               log_level='WARNING')
            except AttributeError:
                bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT')
            except (TypeError, ValueError):
                bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT')

        # XNALara
        elif file_ending == 'xps' or file_ending == 'mesh' or file_ending == 'ascii':
            try:
                if version_2_79_or_older():
                    bpy.ops.xps_tools.import_model('EXEC_DEFAULT',
                                                   filepath=file_path,
                                                   colorizeMesh=False)
                else:
                    bpy.ops.xps_tools.import_model('EXEC_DEFAULT',
                                                   filepath=file_path)
            except AttributeError:
                bpy.ops.cats_importer.install_xps('INVOKE_DEFAULT')

        # Source Engine
        elif file_ending == 'smd' or file_ending == 'qc' or file_ending == 'qci' or file_ending == 'vta' or file_ending == 'dmx':
            try:
                bpy.ops.import_scene.smd('EXEC_DEFAULT',
                                         files=[{'name': file_name}],
                                         directory=directory)
            except AttributeError:
                bpy.ops.cats_importer.install_source('INVOKE_DEFAULT')

        # FBX
        elif file_ending == 'fbx':

            # Enable fbx if it isn't enabled yet
            fbx_is_enabled = addon_utils.check('io_scene_fbx')[1]
            if not fbx_is_enabled:
                addon_utils.enable('io_scene_fbx')

            try:
                bpy.ops.import_scene.fbx('EXEC_DEFAULT',
                                         filepath=file_path,
                                         automatic_bone_orientation=False,  # Is true better? There are issues with True
                                         use_prepost_rot=False,
                                         use_anim=False)
            except (TypeError, ValueError):
                bpy.ops.import_scene.fbx('INVOKE_DEFAULT')
            except RuntimeError as e:
                if 'unsupported, must be 7100 or later' in str(e):
                    Common.show_error(6.2, [t('ImportAnyModel.error.unsupportedFBX')])
                print(str(e))

        # VRM
        elif file_ending == 'vrm':
            pre_import_armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
            pre_import_meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

            try:
                bpy.ops.import_scene.vrm('EXEC_DEFAULT',
                                         filepath=file_path)
            except (TypeError, ValueError):
                bpy.ops.import_scene.vrm('INVOKE_DEFAULT')
                return
            except AttributeError:
                bpy.ops.cats_importer.install_vrm('INVOKE_DEFAULT')
                return

            post_import_armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE' and obj not in pre_import_armatures]
            post_import_meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj not in pre_import_meshes]

            if len(post_import_armatures) != 1:
                return

            # Set imported vrm armature as the parent for the imported meshes
            post_import_armature = post_import_armatures[0]
            for mesh in post_import_meshes:
                mesh.parent = post_import_armature

        # DAE
        elif file_ending == 'dae':
            try:
                bpy.ops.wm.collada_import('EXEC_DEFAULT',
                                          filepath=file_path,
                                          fix_orientation=True,
                                          auto_connect=True)
            except (TypeError, ValueError):
                bpy.ops.wm.collada_import('INVOKE_DEFAULT')

        # ZIP
        elif file_ending == 'zip':
            with zipfile.ZipFile(file_path, 'r') as zipObj:
                global zip_files

                # Check content of zip for importable models
                for content in zipObj.namelist():
                    content_name = os.path.basename(content)
                    content_format = content_name.split('.')[-1]
                    if content_format.lower() in format_list:
                        if not zip_files.get(file_path):
                            zip_files[file_path] = []
                        zip_files[file_path].append(content)

    @staticmethod
    def extract_file():
        zip_id = bpy.context.scene.zip_content.split(' ||| ')
        zip_path = zip_id[0]
        zip_extract_path = '.'.join(zip_path.split('.')[:-1])
        model_path = encode_str(zip_id[1])
        model_path_full = os.path.join(zip_extract_path, model_path)
        model_dir = os.path.dirname(model_path_full)
        model_file_name = os.path.basename(model_path_full)

        # Extract the
        with zipfile.ZipFile(zip_path, 'r') as zipObj:
            for member in zipObj.infolist():
                member.filename = encode_str(member.filename)
                zipObj.extract(member, path=zip_extract_path)

        ImportAnyModel.import_file(model_dir, model_file_name)


def fix_bone_orientations(armature):
    Common.unselect_all()
    Common.set_active(armature)
    Common.switch('EDIT')

    fix_bones = True

    # Check if all the bones are pointing in the same direction
    for bone in armature.data.edit_bones:
        equal_axis_count = 0
        if bone.head[0] == bone.tail[0]:
            equal_axis_count += 1
        if bone.head[1] == bone.tail[1]:
            equal_axis_count += 1
        if bone.head[2] == bone.tail[2]:
            equal_axis_count += 1

        # If the bone points to more than one direction, don't fix the armatures bones
        if equal_axis_count < 2:
            fix_bones = False

    if fix_bones:
        Common.fix_bone_orientations(armature)
    Common.switch('OBJECT')


def fix_armatures_post_import(pre_import_objects):
    arm_added_during_import = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE' and obj not in pre_import_objects]
    for armature in arm_added_during_import:
        print('Added: ', armature.name)
        bpy.context.scene.armature = armature.name
        fix_bone_orientations(armature)

        # Set better bone view
        if hasattr(armature, 'draw_type'):
            armature.draw_type = 'WIRE'
        if version_2_79_or_older():
            armature.show_x_ray = True
        else:
            armature.show_in_front = True


@register_wrap
class ZipPopup(bpy.types.Operator):
    bl_idname = "cats_importer.zip_popup"
    bl_label = t('ZipPopup.label')
    bl_description = t('ZipPopup.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        # Save all current objects to check which armatures got added by the importer
        pre_import_objects = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']

        # Import the file
        ImportAnyModel.extract_file()

        # Create list of armatures that got added during import, select them in cats and fix their bone orientations if necessary
        fix_armatures_post_import(pre_import_objects)

        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 6))

    def check(self, context):
        # Important for changing options
        return False

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 0.9
        row.label(text=t('ZipPopup.selectModel1'))
        row = col.row(align=True)
        row.scale_y = 0.9
        row.label(text=t('ZipPopup.selectModel2'))

        col.separator()
        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop(context.scene, 'zip_content')


def get_zip_content(self, context):
    choices = []

    for zip_path, files in zip_files.items():
        for file_path in files:
            file_id = zip_path + ' ||| ' + file_path
            file_name = os.path.basename(file_path)
            zip_name = os.path.basename(zip_path)

            # 1. Will be returned by context.scene
            # 2. Will be shown in lists
            # 3. will be shown in the hover description (below description)
            choices.append((
                file_id,
                encode_str(file_name),
                t('get_zip_content.choose', model=encode_str(file_name), zipName=encode_str(zip_name))))

    return choices


def encode_str(s):
    try:
        s = s.encode('cp437').decode('cp932')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return s


@register_wrap
class ModelsPopup(bpy.types.Operator):
    bl_idname = "cats_importer.model_popup"
    bl_label = t('ModelsPopup.label')
    bl_description = t('ModelsPopup.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 3))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator(ImportMMD.bl_idname)
        row.operator(ImportXPS.bl_idname)
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator(ImportSource.bl_idname)
        row.operator(ImportFBX.bl_idname)
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator(ImportVRM.bl_idname)
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator(ImportMMDAnimation.bl_idname)


@register_wrap
class ImportMMD(bpy.types.Operator):
    bl_idname = 'cats_importer.import_mmd'
    bl_label = t('ImportMMD.label')
    bl_description = t('ImportMMD.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        Common.remove_unused_objects()

        # Make sure that the first layer is visible
        if hasattr(context.scene, 'layers'):
            context.scene.layers[0] = True

        if not mmd_tools_installed:
            bpy.ops.cats_importer.enable_mmd('INVOKE_DEFAULT')
            return {'FINISHED'}

        try:
            bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT',
                                           scale=0.08,
                                           types={'MESH', 'ARMATURE', 'MORPHS'},
                                           log_level='WARNING')
        except AttributeError:
            bpy.ops.cats_importer.enable_mmd('INVOKE_DEFAULT')
        except (TypeError, ValueError):
            bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT')

        return {'FINISHED'}





@register_wrap
class ImportMMDAnimation(bpy.types.Operator,bpy_extras.io_utils.ImportHelper):
    bl_idname = 'cats_importer.import_mmd_animation'
    bl_label = "MMD Animation"
    bl_description = "Import a MMD Animation (.vmd)"
    bl_options = {'INTERNAL'}

    filter_glob: bpy.props.StringProperty(
        default="*.vmd",
        options={'HIDDEN'}
    )

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        Common.remove_unused_objects()

        # Make sure that the first layer is visible
        if hasattr(context.scene, 'layers'):
            context.scene.layers[0] = True

        if not mmd_tools_installed:
            bpy.ops.cats_importer.enable_mmd('INVOKE_DEFAULT')
            return {'FINISHED'}

        #try:
        filename, extension = os.path.splitext(self.filepath)

        if(extension == ".vmd"):

            #A dictionary to change the current model to MMD importer compatable temporarily
            bonedict = {
                "Chest":"UpperBody",
                "Neck":"Neck",
                "Head":"Head",
                "Hips":"Center",
                "Spine":"LowerBody",

                "Right wrist":"Wrist_R",
                "Right elbow":"Elbow_R",
                "Right arm":"Arm_R",
                "Right shoulder":"Shoulder_R",
                "Right leg":"Leg_R",
                "Right knee":"Knee_R",
                "Right ankle":"Ankle_R",
                "Right toe":"Toe_R",


                "Left wrist":"Wrist_L",
                "Left elbow":"Elbow_L",
                "Left arm":"Arm_L",
                "Left shoulder":"Shoulder_L",
                "Left leg":"Leg_L",
                "Left knee":"Knee_L",
                "Left ankle":"Ankle_L",
                "Left toe":"Toe_L"

            }

            armature = Common.set_default_stage()
            new_armature = armature.copy()
            bpy.context.collection.objects.link(new_armature)
            new_armature.data = armature.data.copy()
            new_armature.name = "Cats MMD Rig Proxy"
            new_armature.animation_data_clear()

            Common.unselect_all()
            Common.set_active(new_armature)
            Common.switch('OBJECT')

            for bone in new_armature.data.bones:
                if bone.name in bonedict:
                    bone.name = bonedict[bone.name]

            bpy.ops.mmd_tools.import_vmd(filepath=self.filepath,bone_mapper='RENAMED_BONES',use_underscore=True, dictionary='INTERNAL')

            #create animation for original if there isn't one.
            if armature.animation_data == None :
                armature.animation_data_create()
            if armature.animation_data.action == None:
                armature.animation_data.action = bpy.data.actions.new("MMD Animation")


            #create animation for new if there isn't one.
            if new_armature.animation_data == None :
                new_armature.animation_data_create()
            if new_armature.animation_data.action == None:
                new_armature.animation_data.action = bpy.data.actions.new("EMPTY_SOURCE")

            active_obj = new_armature
            ad = armature.animation_data

            #iterate through bones and translate them back, therefore blender API will change the animation to be correct.
            reverse_bonedict = {v: k for k, v in bonedict.items()}
            for bone in new_armature.data.bones:
                if bone.name in reverse_bonedict:
                    bone.name = reverse_bonedict[bone.name] #reverse name of bone from value in dictionary back to a key to change the animation.

            #assign animation back to original rig.
            armature.animation_data.action = new_armature.animation_data.action

            #make sure our new armature is selected
            Common.unselect_all()
            Common.switch('OBJECT')
            Common.unselect_all()
            Common.set_active(new_armature)

            #delete active object which is armature.
            bpy.ops.object.delete(use_global=True, confirm=False)


@register_wrap
class ImportXPS(bpy.types.Operator):
    bl_idname = 'cats_importer.import_xps'
    bl_label = t('ImportXPS.label')
    bl_description = t('ImportXPS.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        Common.remove_unused_objects()

        # Make sure that the first layer is visible
        if hasattr(context.scene, 'layers'):
            context.scene.layers[0] = True

        try:
            if version_2_79_or_older():
                bpy.ops.xps_tools.import_model('INVOKE_DEFAULT', colorizeMesh=False)
            else:
                bpy.ops.xps_tools.import_model('INVOKE_DEFAULT')
        except AttributeError:
            bpy.ops.cats_importer.install_xps('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class ImportSource(bpy.types.Operator):
    bl_idname = 'cats_importer.import_source'
    bl_label = t('ImportSource.label')
    bl_description = t('ImportSource.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        Common.remove_unused_objects()

        # Make sure that the first layer is visible
        if hasattr(context.scene, 'layers'):
            context.scene.layers[0] = True

        try:
            bpy.ops.import_scene.smd('INVOKE_DEFAULT')
        except AttributeError:
            bpy.ops.cats_importer.install_source('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class ImportFBX(bpy.types.Operator):
    bl_idname = 'cats_importer.import_fbx'
    bl_label = t('ImportFBX.label')
    bl_description = t('ImportFBX.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        Common.remove_unused_objects()

        # Make sure that the first layer is visible
        if hasattr(context.scene, 'layers'):
            context.scene.layers[0] = True

        # Enable fbx if it isn't enabled yet
        fbx_is_enabled = addon_utils.check('io_scene_fbx')[1]
        if not fbx_is_enabled:
            addon_utils.enable('io_scene_fbx')

        try:
            bpy.ops.import_scene.fbx('INVOKE_DEFAULT',
                                     automatic_bone_orientation=False,
                                     use_prepost_rot=False,
                                     use_anim=False)
        except (TypeError, ValueError):
            bpy.ops.import_scene.fbx('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class ImportVRM(bpy.types.Operator):
    bl_idname = 'cats_importer.import_vrm'
    bl_label = t('ImportVRM.label')
    bl_description = t('ImportVRM.desc')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        Common.remove_unused_objects()

        # Make sure that the first layer is visible
        if hasattr(context.scene, 'layers'):
            context.scene.layers[0] = True

        try:
            bpy.ops.import_scene.vrm('INVOKE_DEFAULT')
        except AttributeError:
            bpy.ops.cats_importer.install_vrm('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class InstallXPS(bpy.types.Operator):
    bl_idname = "cats_importer.install_xps"
    bl_label = t('InstallXPS.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 4.5))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        # row = col.row(align=True)
        # row.label(text="The plugin 'XPS Tools' is required for this function.")
        col.separator()
        row = col.row(align=True)
        row.label(text=t('InstallX.pleaseInstall1'))
        row = col.row(align=True)
        row.label(text=t('InstallX.pleaseInstall2'))
        col.separator()
        col.separator()
        row = col.row(align=True)
        row.label(text=t('InstallX.pleaseInstall3', blenderVersion=current_blender_version), icon="INFO")
        col.separator()
        row = col.row(align=True)
        row.operator(XpsToolsButton.bl_idname, icon=globs.ICON_URL)


@register_wrap
class InstallSource(bpy.types.Operator):
    bl_idname = "cats_importer.install_source"
    bl_label = t('InstallSource.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 4.5))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        # row = col.row(align=True)
        # row.label(text="The plugin 'Source Tools' is required for this function.")
        col.separator()
        row = col.row(align=True)
        row.label(text=t('InstallX.pleaseInstall1'))
        row = col.row(align=True)
        row.label(text=t('InstallX.pleaseInstall2'))
        col.separator()
        col.separator()
        row = col.row(align=True)
        row.label(text=t('InstallX.pleaseInstall3', blenderVersion=current_blender_version), icon="INFO")
        col.separator()
        row = col.row(align=True)
        row.operator(SourceToolsButton.bl_idname, icon=globs.ICON_URL)


@register_wrap
class InstallVRM(bpy.types.Operator):
    bl_idname = "cats_importer.install_vrm"
    bl_label = t('InstallVRM.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 4.5))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        # row = col.row(align=True)
        # row.label(text="The plugin 'VRM Importer' is required for this function.")
        col.separator()
        row = col.row(align=True)
        row.label(text=t('InstallX.pleaseInstall1'))
        row = col.row(align=True)
        row.label(text=t('InstallX.pleaseInstallTesting'))
        col.separator()
        row = col.row(align=True)
        row.label(text=t('InstallX.pleaseInstall2'))
        col.separator()
        row = col.row(align=True)
        row.operator(VrmToolsButton.bl_idname, icon=globs.ICON_URL)


@register_wrap
class EnableMMD(bpy.types.Operator):
    bl_idname = "cats_importer.enable_mmd"
    bl_label = t('EnableMMD.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 4))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(text=t('EnableMMD.required1'))
        row = col.row(align=True)
        row.label(text=t('EnableMMD.required2'))



@register_wrap
class ExportGmodPlayermodel(bpy.types.Operator):
    bl_idname = "cats_importer.export_gmod_addon"
    bl_label = "Export Gmod Addon"
    bl_description = "Export as Gmod Playermodel Addon to your addons and make GMA beside Blender file. May not always work."
    bl_options = {'INTERNAL'}

    steam_library_path = bpy.props.StringProperty(subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})
    gmod_model_name = bpy.props.StringProperty(default = "Missing No")
    platform_name = bpy.props.StringProperty(default = "Garrys Mod")
    armature_name = bpy.props.StringProperty(default = "")

    def execute(self, context):
        print("===============START GMOD EXPORT PROCESS===============")

        model_name = self.gmod_model_name
        platform_name = self.platform_name
        sanitized_model_name = ""
        offical_model_name = ""

        #for file names which must be lower case and no special symbols.
        for i in model_name.lower():
            if i.isalnum() or i == "_":
                sanitized_model_name += i
            else:
                sanitized_model_name += "_"
        #for name that appears in playermodel selection screen.
        for i in model_name:
            if i.isalnum() or i == "_" or i == " ":
                offical_model_name += i
            else:
                offical_model_name += "_"

        print("sanitized model name:"+sanitized_model_name)
        print("Playermodel Selection Menu Name"+offical_model_name)


        steam_librarypath = self.steam_library_path+"steamapps/common/GarrysMod" #add the rest onto it so that we can get garrysmod only.
        addonpath = steam_librarypath+"/garrysmod/addons/"+sanitized_model_name+"_playermodel/"

        Common.switch("OBJECT")
        Common.unselect_all()
        print("testing if SMD tools exist.")
        try:
            bpy.ops.import_scene.smd('EXEC_DEFAULT',files=[{'name': "barney_reference.smd"}], append = "NEW_ARMATURE",directory=os.path.dirname(os.path.abspath(__file__))+"/../extern_tools/valve_resources/")
        except AttributeError:
            bpy.ops.cats_importer.install_source('INVOKE_DEFAULT')
            return
        #clean imported stuff
        print("cleaning imported armature")
        objects = [j.name for j in bpy.context.selected_objects]
        barneycollection = bpy.data.collections.get("barney_collection")
        if not barneycollection:
            barneycollection = bpy.data.collections.new("barney_collection")
        for obj in objects:
            newobj = bpy.data.objects.get(obj)
            if newobj.type == "MESH":
                Common.unselect_all()
                Common.set_active(newobj)
                bpy.ops.object.delete(use_global=False)
                continue
            for collection in bpy.data.collections:
                try:
                    collection.objects.unlink(newobj)
                except:
                    pass
            try:
                bpy.context.collection.objects.unlink(newobj)
            except:
                pass
            barneycollection.objects.link(newobj)
        bpy.context.collection.children.link(barneycollection)
        Common.unselect_all()

        if self.armature_name != "":
            context.scene.armature = self.armature_name
        armature = Common.set_default_stage()
        print("translating bones. if you hit an error here please fix your model using fix model!!!!!! If you have, please ignore the error.")
        bpy.ops.cats_manual.convert_to_valve()

        print("putting armature and objects under reference collection")
        #putting objects and armature under a better collection.
        refcoll = bpy.data.collections.get(sanitized_model_name+"_ref")
        if not refcoll:
            refcoll = bpy.data.collections.new(sanitized_model_name+"_ref")
        for obj in armature.children:
            for collection in bpy.data.collections:
                try:
                    collection.objects.unlink(obj)
                except:
                    pass
            try:
                bpy.context.collection.objects.unlink(obj)
            except:
                pass
            refcoll.objects.link(obj)
        for collection in bpy.data.collections:
            try:
                collection.objects.unlink(armature)
            except:
                pass
        try:
            bpy.context.collection.objects.unlink(armature)
        except:
            pass
        refcoll.objects.link(armature)
        bpy.context.collection.children.link(refcoll)

        for obj in refcoll.objects:
            objname = obj.name
            if bpy.data.objects[objname].type == "MESH":
                print("lowercasing material name for gmod for object "+objname)
                for material in bpy.data.objects[objname].material_slots:
                    mat = material.material
                    sanitized_material_name = ""
                    for i in mat.name.lower():
                        if i.isalnum() or i == "_":
                            sanitized_material_name += i
                        else:
                            sanitized_material_name += "_"
                    mat.name = sanitized_material_name


        print("zeroing transforms and then scaling to gmod scale, then applying transforms.")
        #zero armature position, scale to gmod size, and then apply transforms
        armature.rotation_euler[0] = 0
        armature.rotation_euler[1] = 0
        armature.rotation_euler[2] = 0
        armature.location[0] = 0
        armature.location[1] = 0
        armature.location[2] = 0
        armature.scale[0] = 52.4934383202 #meters to hammer units
        armature.scale[1] = 52.4934383202 #meters to hammer units
        armature.scale[2] = 52.4934383202 #meters to hammer units
        #apply transforms of all objects in ref collection
        Common.unselect_all()
        for obj in refcoll.objects:
            Common.select(obj,True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        print("joining meshes in ref collection")
        #clear selection
        Common.unselect_all()
        parentobj = None
        body_armature = None
        for obj in refcoll.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                body_armature = obj

        if (not body_armature) or (not parentobj):
            print('Report: Error')
            print(refcoll.name+" collection joining failed because it doesn't have atleast one armature and one mesh!")

        for obj in refcoll.objects:
            if obj.type == "MESH" and obj != parentobj:
                #clear selection
                Common.unselect_all()
                Common.select(obj,True)
                Common.set_active(parentobj)
                bpy.ops.object.join()

        print("clearing bone rolls")
        Common.unselect_all()
        Common.set_active(body_armature)
        Common.switch("EDIT")
        bpy.ops.armature.select_all(action='SELECT')
        bpy.ops.armature.roll_clear()
        Common.switch("OBJECT")

        print("a-posing armature")
        Common.unselect_all()
        Common.set_active(body_armature)
        Common.switch("POSE")
        bpy.ops.pose.select_all(action='SELECT')
        body_armature.pose.bones["ValveBiped.Bip01_L_UpperArm"].rotation_mode = "XYZ"
        body_armature.pose.bones["ValveBiped.Bip01_L_UpperArm"].rotation_euler[0] = -45
        body_armature.pose.bones["ValveBiped.Bip01_R_UpperArm"].rotation_mode = "XYZ"
        body_armature.pose.bones["ValveBiped.Bip01_R_UpperArm"].rotation_euler[0] = -45
        bpy.ops.cats_manual.pose_to_rest()
        Common.switch("OBJECT")



        print("grabbing barney armature")
        barney_armature = None
        barney_mesh = None
        barneycollection = bpy.data.collections.get("barney_collection")
        assert(barneycollection is not None)
        assert(len(barneycollection.objects) > 0)
        for obj in barneycollection.objects:
            if obj.type == "ARMATURE":
                barney_armature = obj
                break
        print("duplicating barney armature")
        Common.switch('OBJECT')
        Common.unselect_all()
        Common.set_active(barney_armature)
        bpy.ops.object.duplicate(
        {"object" : barney_armature,
         "selected_objects" : [barney_armature]},
        linked=False)
        barney_armature = context.object

        def children_bone_recursive(parent_bone):
            child_bones = []
            child_bones.append(parent_bone)
            for child in parent_bone.children:
                child_bones.extend(children_bone_recursive(child))
            return child_bones

        print("positioning bones for barney armature at your armature's bones PLEASE HAVE A PELVIS BONE")
        barney_pose_bone_names = [j.name for j in children_bone_recursive(barney_armature.pose.bones["ValveBiped.Bip01_Pelvis"])] #bones are default in order of parent child.

        armature_matrixes = dict()
        barney_armature_name = barney_armature.name
        body_armature_name = body_armature.name
        for barney_bone_name in barney_pose_bone_names:


            Common.switch('OBJECT')
            Common.unselect_all()
            Common.set_active(bpy.data.objects[body_armature_name])
            Common.switch('EDIT')
            try:
                obj = bpy.data.objects[barney_armature_name]
                editbone = bpy.data.objects[body_armature_name].data.edit_bones[barney_bone_name]
                Common.switch('OBJECT')
                bone = obj.pose.bones[barney_bone_name]
                bone.rotation_mode = "XYZ"
                newmatrix = Matrix.Translation((editbone.matrix[0][3],editbone.matrix[1][3],editbone.matrix[2][3]))
                bone.matrix = newmatrix
                bone.rotation_euler = (0,0,0)
            except:
                Common.switch('OBJECT')

        print("applying barney pose as rest pose")
        Common.switch('OBJECT')
        original_scene_armature_name = bpy.context.scene.armature
        bpy.context.scene.armature = barney_armature_name
        Common.unselect_all()
        Common.set_active(bpy.data.objects[barney_armature_name])
        Common.switch('POSE')
        bpy.ops.cats_manual.pose_to_rest()
        bpy.context.scene.armature = original_scene_armature_name
        Common.switch('OBJECT')

        print("putting barney armature bones on your model")
        bpy.context.scene.merge_armature_into = barney_armature_name
        bpy.context.scene.merge_armature = body_armature_name
        bpy.context.scene.merge_same_bones = True
        bpy.context.scene.merge_armatures_join_meshes = False
        bpy.context.scene.merge_armatures_remove_zero_weight_bones = False
        bpy.ops.cats_custom.merge_armatures()
        barney_armature.name = body_armature_name

        print("putting armature back under reference collection")
        for collection in bpy.data.collections:
            try:
                collection.objects.unlink(bpy.data.objects[body_armature_name])
            except:
                pass
        try:
            bpy.context.collection.objects.unlink(bpy.data.objects[body_armature_name])
        except:
            pass
        refcoll.objects.link(bpy.data.objects[body_armature_name])

        print("Duplicating reference collection to make phys collection")
        body_armature = bpy.data.objects[body_armature_name]
        physcoll = bpy.data.collections.get(sanitized_model_name+"_phys")
        if not physcoll:
            physcoll = bpy.data.collections.new(sanitized_model_name+"_phys")
        bpy.context.collection.children.link(physcoll)
        Common.switch('OBJECT')
        Common.unselect_all()
        Common.set_active(body_armature)
        Common.select(parentobj,True)
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'})
        for obj in context.selected_objects:
            try:
                refcoll.objects.unlink(obj)
            except:
                pass
            try:
                bpy.context.collection.objects.unlink(obj)
            except:
                pass
            physcoll.objects.link(obj)


        print("making arms collection and copying over from reference")
        armcoll = bpy.data.collections.get(sanitized_model_name+"_arms")
        if not armcoll:
            armcoll = bpy.data.collections.new(sanitized_model_name+"_arms")
        bpy.context.collection.children.link(armcoll)
        Common.unselect_all()
        Common.set_active(body_armature)
        Common.select(parentobj,True)
        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'})
        for obj in context.selected_objects:
            try:
                refcoll.objects.unlink(obj)
            except:
                pass
            try:
                bpy.context.collection.objects.unlink(obj)
            except:
                pass
            armcoll.objects.link(obj)

        print("making phys parts")
        #bone names to make phys parts for. Max of 30 pleasee!!! Gmod cannot handle more than 30 but can do up to and including 30.
        bone_names_for_phys = [
        "ValveBiped.Bip01_L_UpperArm",
        "ValveBiped.Bip01_R_UpperArm",
        "ValveBiped.Bip01_L_Forearm",
        "ValveBiped.Bip01_R_Forearm",
        "ValveBiped.Bip01_L_Hand",
        "ValveBiped.Bip01_R_Hand",
        "ValveBiped.Bip01_L_Thigh",
        "ValveBiped.Bip01_R_Thigh",
        "ValveBiped.Bip01_L_Calf",
        "ValveBiped.Bip01_R_Calf",
        "ValveBiped.Bip01_L_Foot",
        "ValveBiped.Bip01_R_Foot",
        "ValveBiped.Bip01_Spine",
        "ValveBiped.Bip01_Spine1",
        "ValveBiped.Bip01_Pelvis",
        "ValveBiped.Bip01_Neck1",
        "ValveBiped.Bip01_Head1"
        ]
        convexobjects = dict()
        original_object_phys = None
        phys_armature = None
        for obj in physcoll.objects:
            if obj.type == "ARMATURE":
                phys_armature = obj
                break

        for obj in physcoll.objects:
            if obj.type == 'MESH':
                #deselect all objects and select our obj
                original_object_phys = obj
                #delete all bad vertex groups we are not using by merging
                Common.switch('OBJECT')
                Common.unselect_all()
                Common.set_active(obj)
                Common.switch('EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bones_to_merge_valve = []
                for index,group in enumerate(obj.vertex_groups):
                    if "tail" in group.name.lower():
                        Common.switch('OBJECT')
                        Common.unselect_all()
                        Common.set_active(obj)
                        Common.switch('EDIT')
                        bpy.ops.mesh.select_all(action='DESELECT')
                        obj.vertex_groups.active_index = index
                        bpy.ops.object.vertex_group_select()
                        bpy.ops.object.vertex_group_remove_from()
                    elif not (group.name in bone_names_for_phys):
                        Common.switch('OBJECT')
                        Common.unselect_all()
                        Common.set_active(phys_armature)
                        Common.switch('EDIT')
                        bpy.ops.armature.select_all(action='DESELECT')
                        bone = phys_armature.data.edit_bones.get(group.name)
                        if bone is not None:
                            #select arm bone

                            bones_to_merge_valve.append(bone.name)
                        else:
                            pass #if the group no longer has a bone who cares. usually....
                Common.switch('OBJECT')
                Common.unselect_all()
                Common.set_active(phys_armature)
                Common.switch('EDIT')
                for bonename in bones_to_merge_valve:
                    bone = phys_armature.data.edit_bones.get(bonename)
                    bone.select = True
                    bone.select_head = True
                    bone.select_tail = True
                    phys_armature.data.edit_bones.active = bone
                    bpy.ops.cats_manual.merge_weights()

                #separating into seperate phys objects to join later.
                Common.switch('OBJECT')
                Common.unselect_all()
                Common.set_active(obj)
                Common.switch('EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.vertex_group_normalize()
                bpy.ops.object.vertex_group_quantize(group_select_mode='ALL', steps=1)
                bpy.ops.object.vertex_group_clean(group_select_mode='ALL', limit=0.1)
                for bone in bone_names_for_phys:
                    bpy.ops.mesh.select_all(action='DESELECT')
                    #select vertices belonging to bone
                    try:
                        for index,group in enumerate(obj.vertex_groups):
                            if group.name == bone:
                                obj.vertex_groups.active_index = index
                                bpy.ops.object.vertex_group_select()
                                break
                    except:
                        print("failed to find vertex group "+bone+" On phys obj. Skipping.")
                        continue
                    #duplicate and make convex hull then separate
                    try:
                        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1})
                        bpy.ops.mesh.convex_hull()
                        bpy.ops.mesh.faces_shade_smooth()
                        bpy.ops.mesh.separate(type = 'SELECTED')
                    except Exception:
                        print("phys joint failed for bone "+bone+". Ignoring!!")
                        continue
                break
        selected_objects_memory = context.selected_objects
        for obj in selected_objects_memory:
            convexobjects[obj.vertex_groups[obj.vertex_groups.active_index].name+""] = obj
        #clear selection
        Common.unselect_all()

        print("joining phys parts and assigning to vertex groups")
        #clear vertex groups and assign each object to their corosponding vertex group.
        for bonename,obj in convexobjects.items():
            Common.unselect_all()
            Common.set_active(obj)
            Common.switch('EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            obj.vertex_groups.clear()
            obj.vertex_groups.new(name=bonename)
            obj.vertex_groups.active_index = 0
            bpy.ops.object.vertex_group_assign()
            Common.switch('OBJECT')

        #clear selection
        Common.unselect_all()
        #since objects already have their armature modifiers, just join into one
        for bonename,obj in convexobjects.items():
            Common.select(obj,True)
        print("if this doesn't work, then you have bad weights!!")
        Common.set_active(list(convexobjects.values())[0])
        bpy.ops.object.join() #join all objects separated into one.
        Common.unselect_all()#unselect all and delete original object
        Common.set_active(original_object_phys)
        bpy.ops.object.delete(use_global=False)

        print("deleting rest of mesh for arms collection except arm bones")
        parentobj = None
        arms_armature = None
        for obj in armcoll.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                arms_armature = obj
        obj = parentobj



        print("step 1 arms: getting entire arm list of bones for each side.")
        arm_bone_names = []
        Common.switch('OBJECT')
        Common.unselect_all()
        Common.set_active(arms_armature,True)
        Common.switch('EDIT')
        #get armature bone names here since we have armature in edit mode.
        #this is changed later to exlude arm bones
        arms_armature_bone_names_list = [j.name for j in arms_armature.data.edit_bones]

        bpy.ops.armature.select_all(action='DESELECT')
        for side in ["L","R"]:
            upper_arm_name = "ValveBiped.Bip01_"+side+"_UpperArm"
            #get arm bone for this side
            bone = arms_armature.data.edit_bones.get(upper_arm_name)
            if bone is not None:
                #select arm bone
                bone.select = True
                bone.select_head = True
                bone.select_tail = True
                arms_armature.data.edit_bones.active = bone
            else:
                print("Getting upper arm for side "+side+" Has failed! Exiting!")
                return

            #select arm bone children and add to list of arm bone names
            bpy.ops.armature.select_similar(type='CHILDREN')
            for bone in bpy.context.selected_editable_bones:
                arm_bone_names.append(bone.name)

        if obj.type == 'MESH': #we know parent obj is a mesh this is just for solidarity.
            #deselect all objects and select our obj
            Common.switch('OBJECT')
            Common.unselect_all()
            Common.set_active(obj)
            Common.switch('EDIT')

            bpy.ops.mesh.select_all(action='DESELECT') #deselecting entire mesh so we can select the mesh parts belonging to our arm bones

            #remove arms from armature bone names list
            for i in arm_bone_names:
                if i in arms_armature_bone_names_list:
                    arms_armature_bone_names_list.remove(i)


            for bonename in arms_armature_bone_names_list:
                #select vertices belonging to bone
                try:
                    for index,group in enumerate(obj.vertex_groups):
                        if group.name == bonename:
                            obj.vertex_groups.active_index = index
                            bpy.ops.object.vertex_group_select()
                            break
                except:
                    print("failed to find vertex group "+bone+" On arms. Skipping.")
                    continue
            bpy.ops.mesh.delete(type='VERT')
            Common.switch('OBJECT')
        #select all arm bones and invert selection, then delete bones in edit mode.
        print("deleting leftover bones for arms and finding chest location.")
        parentobj = None
        arms_armature = None
        for obj in armcoll.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                arms_armature = obj
        obj = parentobj
        Common.switch('OBJECT')
        Common.unselect_all()
        Common.set_active(arms_armature)
        Common.switch('EDIT')
        chestloc = None
        bpy.ops.armature.select_all(action='DESELECT')
        for bone in arms_armature.data.edit_bones:
            bone.select = False
            bone.select_head = False
            bone.select_tail = False
            #arm_bone_names = ["ValveBiped.Bip01_"+side+"_UpperArm","ValveBiped.Bip01_"+side+"_Forearm","ValveBiped.Bip01_"+side+"_Finger4","ValveBiped.Bip01_"+side+"_Finger41","ValveBiped.Bip01_"+side+"_Finger42","ValveBiped.Bip01_"+side+"_Finger3","ValveBiped.Bip01_"+side+"_Finger31","ValveBiped.Bip01_"+side+"_Finger32","ValveBiped.Bip01_"+side+"_Finger2","ValveBiped.Bip01_"+side+"_Finger21","ValveBiped.Bip01_"+side+"_Finger22","ValveBiped.Bip01_"+side+"_Finger1","ValveBiped.Bip01_"+side+"_Finger11","ValveBiped.Bip01_"+side+"_Finger12","ValveBiped.Bip01_"+side+"_Finger0","ValveBiped.Bip01_"+side+"_Finger01","ValveBiped.Bip01_"+side+"_Finger02"]
            if bone.name in arm_bone_names:
                bone.select = True
                bone.select_head = True
                bone.select_tail = True
                arms_armature.data.edit_bones.active = bone
            if bone.name == "ValveBiped.Bip01_Spine1" and chestloc == None:
                chestloc = (bone.matrix[0][3],bone.matrix[1][3],bone.matrix[2][3])
            if bone.name == "ValveBiped.Bip01_Spine2":
                chestloc = (bone.matrix[0][3],bone.matrix[1][3],bone.matrix[2][3])
        #once we are done selecting bones, invert and delete so we delete non arm bones.
        bpy.ops.armature.select_all(action='INVERT')
        bpy.ops.armature.delete()
        Common.switch('OBJECT')


        print("moving arms armature to origin and applying transforms")
        parentobj = None
        arms_armature = None
        for obj in armcoll.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                arms_armature = obj
        obj = parentobj
        #move arms armature to origin
        arms_armature.location = [(-1*chestloc[0]),(-1*chestloc[1]),(-1*chestloc[2])]
        Common.select(parentobj,True)
        Common.select(arms_armature,True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


        print("configuring game and compiler paths")
        bpy.context.scene.vs.export_format = "SMD"
        bpy.context.scene.vs.engine_path = steam_librarypath+"/bin/"
        bpy.context.scene.vs.game_path = steam_librarypath+"/garrysmod/"


        print("generating compiling script file for body (.qc file)")
        jiggle_bone_list = ""
        jiggle_bone_entry = """\n$jigglebone \"{bone name here}\" {
    is_flexible
    {
        length 10
        tip_mass 20
        pitch_stiffness 50
        pitch_damping 10
        yaw_stiffness 50
        yaw_damping 10
        along_stiffness 100
        along_damping 0
        pitch_constraint -20 20
    }
}\n"""
        print("finding tail jiggle bones")
        refcoll = bpy.data.collections[sanitized_model_name+"_ref"]
        body_armature = None
        parentobj = None
        for obj in refcoll.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                body_armature = obj
        Common.switch("OBJECT")
        Common.unselect_all()
        Common.set_active(body_armature,True)
        Common.switch('EDIT')
        for bone in body_armature.data.edit_bones:
            if "tail" in bone.name.lower():
                 jiggle_bone_list += jiggle_bone_entry.replace("{bone name here}", bone.name)


        qcfile = """$modelname \""""+sanitized_model_name+"""/"""+sanitized_model_name+""".mdl\"
$BodyGroup \""""+refcoll.name+"""\"
{
    studio \""""+refcoll.name+""".smd\"
}
$surfaceprop \"flesh\"

$contents \"solid\"

$illumposition -0.007 -0.637 35.329

$eyeposition 0 0 70

$ambientboost

$mostlyopaque

$cdmaterials \"models\\"""+sanitized_model_name+"""\\\"

$attachment \"eyes\" \"ValveBiped.Bip01_Head1\" 3.47 -3.99 -0.1 rotate 0 -80.1 -90
$attachment \"mouth\" \"ValveBiped.Bip01_Head1\" 0.8 -5.8 -0.15 rotate 0 -80 -90
$attachment \"chest\" \"ValveBiped.Bip01_Spine2\" 5 4 0 rotate 0 90 90
$attachment \"anim_attachment_head\" \"ValveBiped.Bip01_Head1\" 0 0 0 rotate -90 -90 0

$cbox 0 0 0 0 0 0

$bbox -13 -13 0 13 13 72

{put define bones here}

$bonemerge \"ValveBiped.Bip01_Pelvis\"
$bonemerge \"ValveBiped.Bip01_Spine\"
$bonemerge \"ValveBiped.Bip01_Spine1\"
$bonemerge \"ValveBiped.Bip01_Spine2\"
$bonemerge \"ValveBiped.Bip01_Spine4\"
$bonemerge \"ValveBiped.Bip01_R_Clavicle\"
$bonemerge \"ValveBiped.Bip01_R_UpperArm\"
$bonemerge \"ValveBiped.Bip01_R_Forearm\"
$bonemerge \"ValveBiped.Bip01_R_Hand\"
$bonemerge \"ValveBiped.Anim_Attachment_RH\"\n\n"""+jiggle_bone_list+"""\n\n
$ikchain \"rhand\" \"ValveBiped.Bip01_R_Hand\" knee 0.707 0.707 0
$ikchain \"lhand\" \"ValveBiped.Bip01_L_Hand\" knee 0.707 0.707 0
$ikchain \"rfoot\" \"ValveBiped.Bip01_R_Foot\" knee 0.707 -0.707 0
$ikchain \"lfoot\" \"ValveBiped.Bip01_L_Foot\" knee 0.707 -0.707 0

{put_anims_here}

$includemodel \"m_anm.mdl\"
$includemodel \"m_shd.mdl\"
$includemodel \"m_pst.mdl\"
$includemodel \"m_gst.mdl\"
$includemodel \"player/m_ss.mdl\"
$includemodel \"player/cs_fix.mdl\"
$includemodel \"player/global_include.mdl\"
$includemodel \"humans/male_shared.mdl\"
$includemodel \"humans/male_ss.mdl\"
$includemodel \"humans/male_gestures.mdl\"
$includemodel \"humans/male_postures.mdl\"

$collisionjoints \""""+physcoll.name+""".smd\"
{
    $mass 90
    $inertia 10
    $damping 0.01
    $rotdamping 1.5

    $jointconstrain \"ValveBiped.Bip01_R_UpperArm\" x limit -39 39 0
    $jointconstrain \"ValveBiped.Bip01_R_UpperArm\" y limit -79 95 0
    $jointconstrain \"ValveBiped.Bip01_R_UpperArm\" z limit -93 23 0

    $jointconstrain \"ValveBiped.Bip01_L_UpperArm\" x limit -30 30 0
    $jointconstrain \"ValveBiped.Bip01_L_UpperArm\" y limit -95 84 0
    $jointconstrain \"ValveBiped.Bip01_L_UpperArm\" z limit -86 26 0

    $jointconstrain \"ValveBiped.Bip01_L_Forearm\" x limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_L_Forearm\" y limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_L_Forearm\" z limit -149 4 0

    $jointconstrain \"ValveBiped.Bip01_L_Hand\" x limit -37 37 0
    $jointconstrain \"ValveBiped.Bip01_L_Hand\" y limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_L_Hand\" z limit -57 59 0

    $jointconstrain \"ValveBiped.Bip01_R_Forearm\" x limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_R_Forearm\" y limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_R_Forearm\" z limit -149 4 0

    $jointconstrain \"ValveBiped.Bip01_R_Hand\" x limit -60 60 0
    $jointconstrain \"ValveBiped.Bip01_R_Hand\" y limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_R_Hand\" z limit -57 70 0

    $jointconstrain \"ValveBiped.Bip01_R_Thigh\" x limit -12 12 0
    $jointconstrain \"ValveBiped.Bip01_R_Thigh\" y limit -8 75 0
    $jointconstrain \"ValveBiped.Bip01_R_Thigh\" z limit -97 32 0

    $jointconstrain \"ValveBiped.Bip01_R_Calf\" x limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_R_Calf\" y limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_R_Calf\" z limit -12 126 0

    $jointconstrain \"ValveBiped.Bip01_Head1\" x limit -20 20 0
    $jointconstrain \"ValveBiped.Bip01_Head1\" y limit -25 25 0
    $jointconstrain \"ValveBiped.Bip01_Head1\" z limit -13 30 0

    $jointconstrain \"ValveBiped.Bip01_L_Thigh\" x limit -12 12 0
    $jointconstrain \"ValveBiped.Bip01_L_Thigh\" y limit -73 6 0
    $jointconstrain \"ValveBiped.Bip01_L_Thigh\" z limit -93 30 0

    $jointconstrain \"ValveBiped.Bip01_L_Calf\" x limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_L_Calf\" y limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_L_Calf\" z limit -8 126 0

    $jointconstrain \"ValveBiped.Bip01_L_Foot\" x limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_L_Foot\" y limit -19 19 0
    $jointconstrain \"ValveBiped.Bip01_L_Foot\" z limit -15 35 0

    $jointconstrain \"ValveBiped.Bip01_R_Foot\" x limit 0 0 0
    $jointconstrain \"ValveBiped.Bip01_R_Foot\" y limit -25 6 0
    $jointconstrain \"ValveBiped.Bip01_R_Foot\" z limit -15 35 0

    $jointcollide \"ValveBiped.Bip01_R_Forearm\" \"ValveBiped.Bip01_R_Thigh\"
    $jointcollide \"ValveBiped.Bip01_R_Forearm\" \"ValveBiped.Bip01_L_Thigh\"
    $jointcollide \"ValveBiped.Bip01_L_Forearm\" \"ValveBiped.Bip01_R_Thigh\"
    $jointcollide \"ValveBiped.Bip01_L_Forearm\" \"ValveBiped.Bip01_L_Thigh\"
    $jointcollide \"ValveBiped.Bip01_R_Foot\" \"ValveBiped.Bip01_L_Calf\"
    $jointcollide \"ValveBiped.Bip01_L_Foot\" \"ValveBiped.Bip01_R_Calf\"
    $jointcollide \"ValveBiped.Bip01_L_Foot\" \"ValveBiped.Bip01_R_Foot\"
    $jointcollide \"ValveBiped.Bip01_R_Calf\" \"ValveBiped.Bip01_L_Calf\"
    $jointcollide \"ValveBiped.Bip01_R_Thigh\" \"ValveBiped.Bip01_L_Thigh\"
    $jointcollide \"ValveBiped.Bip01_R_Forearm\" \"ValveBiped.Bip01_Pelvis\"
    $jointcollide \"ValveBiped.Bip01_L_Forearm\" \"ValveBiped.Bip01_Pelvis\"
}"""
        body_animation_qc="""$sequence \"reference\" {
    \"anims/reference.smd\"
    fadein 0.2
    fadeout 0.2
    fps 1
}

$animation \"a_proportions\" \""""+refcoll.name+""".smd\"{
    fps 30

    subtract \"reference\" 0
}
$Sequence \"ragdoll\" {
    \"anims/idle.smd\"
    activity \"ACT_DIERAGDOLL\" 1
    fadein 0.2
    fadeout 0.2
    fps 30
}
$sequence \"proportions\"{
    \"a_proportions\"
    predelta
    autoplay
    fadein 0.2
    fadeout 0.2
}"""




        print("writing body script file iteration 1. If this errors, please save your file!")
        target_dir = bpy.path.abspath("//CATS Bake/" + platform_name + "/"+sanitized_model_name+"/")
        os.makedirs(target_dir,0o777,True)
        compilefile = open(target_dir+sanitized_model_name+".qc", "w")
        compilefile.write(qcfile.replace("{put_anims_here}","").replace("{put define bones here}",""))
        compilefile.close()

        print("configuring export path for body. If this throws an error, save your file!!")
        bpy.context.scene.vs.export_path = "//CATS Bake/" + platform_name + "/"+sanitized_model_name+"/"#two backslashes to escape the backslash because a backslash escapes.
        bpy.context.scene.vs.qc_path = "//CATS Bake/" + platform_name + "/"+sanitized_model_name+"/"+sanitized_model_name+".qc"

        print("exporting body models")
        Common.switch('OBJECT')

        #can't iterate so it had to be copied twice
        #body model
        parentobj = None
        body_armature = None
        bpy.context.scene.vs.export_list_active = 0
        bpy.context.scene.vs.export_list_active = 1
        bpy.ops.export_scene.smd()
        collection = bpy.data.collections[sanitized_model_name+"_ref"]
        for obj in collection.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                body_armature = obj
        print("exporting "+collection.name)
        Common.unselect_all()
        for index,listitem in enumerate(bpy.context.scene.vs.export_list):
            if listitem.name == collection.name+".smd":
                bpy.context.scene.vs.export_list_active = index
        body_armature.data.vs.implicit_zero_bone = False
        bpy.ops.export_scene.smd()

        #phys model
        parentobj = None
        body_armature = None
        collection = bpy.data.collections[sanitized_model_name+"_phys"]
        for obj in collection.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                body_armature = obj
        print("exporting "+collection.name)
        Common.unselect_all()
        for index,listitem in enumerate(bpy.context.scene.vs.export_list):
            if listitem.name == collection.name+".smd":
                bpy.context.scene.vs.export_list_active = index
        body_armature.data.vs.implicit_zero_bone = False
        bpy.ops.export_scene.smd()



        print("making animation for idle body")
        Common.switch('OBJECT')
        parentobj = None
        body_armature = None
        refcoll = bpy.data.collections[sanitized_model_name+"_ref"]
        for obj in refcoll.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                body_armature = obj
        if bpy.data.actions.get("idle"):
            Common.unselect_all()
            Common.set_active(body_armature)
            try:
                body_armature.animation_data_create()
            except:
                pass
            body_armature.animation_data.action = bpy.data.actions["idle"]
        else:
            Common.unselect_all()
            Common.set_active(body_armature)
            try:
                body_armature.animation_data_create()
            except:
                pass
            body_armature.animation_data.action = bpy.data.actions.new(name="idle")

        Common.unselect_all()
        Common.set_active(body_armature,True)
        Common.switch('POSE')
        for bone in body_armature.pose.bones:
            bone.rotation_mode = "XYZ"
            bone.keyframe_insert(data_path="rotation_euler", frame=1)
            bone.keyframe_insert(data_path="location", frame=1)


        print("exporting idle body animation")
        body_armature.animation_data.action.name = "idle"

        bpy.context.scene.vs.subdir = "anims"
        Common.unselect_all()
        bpy.context.scene.vs.export_list_active = 0
        bpy.context.scene.vs.export_list_active = 1
        body_armature.data.vs.implicit_zero_bone = False
        for index,listitem in enumerate(bpy.context.scene.vs.export_list):
            if listitem.name == "anims\\"+body_armature.animation_data.action.name+".smd":
                bpy.context.scene.vs.export_list_active = index
        bpy.context.scene.vs.action_selection = "CURRENT"
        body_armature.data.vs.implicit_zero_bone = False
        bpy.ops.export_scene.smd()

        print("deleting old reference animations")
        Common.switch('OBJECT')
        animationnames = [j.name for j in bpy.data.actions]
        for animationname in animationnames:
            if "." in animationname:
                if animationname.split(".")[0] == "reference":
                    bpy.data.actions.remove(bpy.data.actions[animationname])
            if animationname == "reference":
                bpy.data.actions.remove(bpy.data.actions[animationname])

        print("making animation for reference body")
        Common.switch('OBJECT')
        parentobj = None
        body_armature = None
        refcoll = bpy.data.collections[sanitized_model_name+"_ref"]
        for obj in refcoll.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                body_armature = obj
        Common.switch('OBJECT')
        Common.unselect_all()
        Common.set_active(body_armature)

        bpy.ops.import_scene.smd('EXEC_DEFAULT',files=[{'name': "reference.smd"}], append = "APPEND",directory=os.path.dirname(os.path.abspath(__file__))+"/../extern_tools/valve_resources/")

        for barney_bone_name in barney_pose_bone_names:
            bone = body_armature.pose.bones.get(barney_bone_name)
            bone.rotation_mode = "XYZ"
            bone.keyframe_insert(data_path="rotation_euler", frame=1)
            bone.keyframe_insert(data_path="location", frame=1)

        print("exporting refrence body animation")
        bpy.context.scene.vs.subdir = "anims"
        bpy.context.scene.vs.export_list_active = 0
        bpy.context.scene.vs.export_list_active = 1
        body_armature.data.vs.implicit_zero_bone = False
        Common.unselect_all()
        #print("HELLOOOOOOOOOOOOOOOOOOOOOOOOOOO "+str(body_armature.data.vs.implicit_zero_bone))
        for index,listitem in enumerate(bpy.context.scene.vs.export_list):
            print(listitem.name)
            if listitem.name == "anims\\"+body_armature.animation_data.action.name+".smd":
                bpy.context.scene.vs.export_list_active = index
        bpy.context.scene.vs.action_selection = "CURRENT"
        body_armature.data.vs.implicit_zero_bone = False
        bpy.ops.export_scene.smd()
        # Lazy fix for a race condition before studiomdl.exe is called
        time.sleep(10)
        print("Generating bone definitions so your model doesn't collapse on itself. ")
        output = subprocess.run([steam_librarypath+"/bin/studiomdl.exe", "-game", steam_librarypath+"/garrysmod", "-definebones", "-nop4", "-verbose", bpy.path.abspath(bpy.context.scene.vs.qc_path)],stdout=subprocess.PIPE)

        print("Writing DefineBones.qci")
        define_bones_file = open(bpy.path.abspath("//CATS Bake/" + platform_name + "/"+sanitized_model_name+"/DefineBones.qci"), "w")
        index = output.stdout.decode('utf-8').find('$')
        define_bones_file.write(output.stdout.decode('utf-8')[index:])
        define_bones_file.close()


        print("Rewriting QC to include animations since we finished compiling define bones")
        compilefile = open(bpy.path.abspath("//CATS Bake/" + platform_name + "/"+sanitized_model_name+"/"+sanitized_model_name+".qc"), "w")
        compilefile.write(qcfile.replace("{put_anims_here}",body_animation_qc).replace("{put define bones here}","$include \"DefineBones.qci\""))
        compilefile.close()

        print("Compiling model! (THIS CAN TAKE A LONG TIME AND IS PRONE TO ERRORS!!!!)")
        bpy.ops.smd.compile_qc(filepath=bpy.path.abspath(bpy.context.scene.vs.qc_path))
        #to prevent errors due to missing data because it changes
        refcoll = bpy.data.collections[sanitized_model_name+"_phys"]

        print("Moving compiled model to addon folder.")
        #path after models must match model path in QC.
        #thanks to "https://stackoverflow.com/a/41827240" for helping me make sure this would work correctly.
        source_dir = steam_librarypath+"/garrysmod/models/"+sanitized_model_name
        target_dir = addonpath+"models/"+sanitized_model_name
        file_names = os.listdir(source_dir)
        os.makedirs(target_dir,0o777,True)
        for file_name in file_names:
            if os.path.exists(os.path.join(target_dir, file_name)):
                os.remove(os.path.join(target_dir, file_name))
            shutil.move(os.path.join(source_dir, file_name), target_dir)


        print("Making lua file for adding playermodel to playermodel list in game")
        os.makedirs(addonpath+"lua/autorun", exist_ok=True)
        luafile = open(addonpath+"lua/autorun/"+sanitized_model_name+"_playermodel_adder.lua","w")
        luafile_content = """player_manager.AddValidModel( \""""+offical_model_name+"""\", \""""+"models/"+sanitized_model_name+"/"+sanitized_model_name+""".mdl\" );
list.Set( "PlayerOptionsModel", \""""+offical_model_name+"""\", \""""+"models/"+sanitized_model_name+"/"+sanitized_model_name+""".mdl\");
player_manager.AddValidHands( \""""+offical_model_name+"""\", \""""+"models/"+sanitized_model_name+"/"+sanitized_model_name+"""_arms.mdl\", 0, "00000000" );"""
        luafile.write(luafile_content)
        luafile.close()

        print("resizing arms")

        arms_scale_factor = None
        collection = bpy.data.collections[sanitized_model_name+"_arms"]
        parentobj = None
        for obj in collection.objects:
            if obj.type == "ARMATURE":
                parentobj = obj
                break
        Common.switch('OBJECT')
        Common.unselect_all()
        Common.unselect_all()
        Common.set_active(parentobj)
        try:
            Common.switch('EDIT')
            obj = parentobj
            editbone1 = parentobj.data.edit_bones["ValveBiped.Bip01_L_UpperArm"]
            editbone2 = parentobj.data.edit_bones["ValveBiped.Bip01_L_Forearm"]
            loc1 = [editbone1.matrix[0][3],editbone1.matrix[1][3],editbone1.matrix[2][3]]
            loc2 = [editbone2.matrix[0][3],editbone2.matrix[1][3],editbone2.matrix[2][3]]
            Common.switch('OBJECT')
            distance = sqrt(((loc2[0]-loc1[0])*(loc2[0]-loc1[0]))+((loc2[1]-loc1[1])*(loc2[1]-loc1[1]))+((loc2[2]-loc1[2])*(loc2[2]-loc1[2])))
            arms_scale_factor = 11.692535032476918/distance #random number is distance between upper and lower arm for barney armature

        except Exception as e:
            print("ARMS SOMEHOW DON'T HAVE ARM BONES. SCALER BROKE. PLEASE SEE USER \"434468177062133772\" ON CATS DISCORD.")
            print("ERROR IS AS FOLLOWS: ",e)
        if arms_scale_factor is not None:
            parentobj.scale = (arms_scale_factor,arms_scale_factor,arms_scale_factor)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True, properties=False)

        print("configuring export path for arms. If this throws an error, save your file!!")
        bpy.context.scene.vs.export_path = bpy.path.abspath("//CATS Bake/" + platform_name + "/"+sanitized_model_name+"_arms/")#two backslashes to escape the backslash because a backslash escapes.
        bpy.context.scene.vs.qc_path = bpy.path.abspath("//CATS Bake/" + platform_name + "/"+sanitized_model_name+"_arms/"+sanitized_model_name+"_arms.qc")

        print("exporting arm model")
        parentobj = None
        body_armature = None
        collection = bpy.data.collections[sanitized_model_name+"_arms"]
        for obj in collection.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                body_armature = obj
        Common.unselect_all()
        print("exporting "+collection.name)
        for index,listitem in enumerate(bpy.context.scene.vs.export_list):
            if listitem.name == collection.name+".smd":
                bpy.context.scene.vs.export_list_active = index
        body_armature.data.vs.implicit_zero_bone = False
        bpy.ops.export_scene.smd()

        print("making animation for idle arms")
        Common.switch('OBJECT')
        parentobj = None
        body_armature = None
        refcoll = bpy.data.collections[sanitized_model_name+"_arms"]
        for obj in refcoll.objects:
            if obj.type == "MESH":
                parentobj = obj
            if obj.type == "ARMATURE":
                body_armature = obj
        if bpy.data.actions.get("idle_arms"):
            Common.unselect_all()
            Common.set_active(body_armature)
            try:
                body_armature.animation_data_create()
            except:
                pass
            body_armature.animation_data.action = bpy.data.actions["idle_arms"]
        else:
            Common.unselect_all()
            Common.set_active(body_armature)
            try:
                body_armature.animation_data_create()
            except:
                pass
            body_armature.animation_data.action = bpy.data.actions.new(name="idle_arms")

        Common.unselect_all()
        Common.set_active(body_armature)
        Common.switch('POSE')
        for bone in body_armature.pose.bones:
            bone.rotation_mode = "XYZ"
            bone.keyframe_insert(data_path="rotation_euler", frame=1)
            bone.keyframe_insert(data_path="location", frame=1)

        print("exporting idle arms animation")
        body_armature.animation_data.action.name = "idle_arms"
        bpy.context.scene.vs.subdir = "anims"
        bpy.context.scene.vs.export_list_active = 0
        bpy.context.scene.vs.export_list_active = 1
        body_armature.data.vs.implicit_zero_bone = False
        #print("HELLOOOOOOOOOOOOOOOOOOOOOOOOOOO "+str(body_armature.data.vs.implicit_zero_bone))
        Common.unselect_all()
        for index,listitem in enumerate(bpy.context.scene.vs.export_list):
            print(listitem.name)
            if listitem.name == "anims\\"+body_armature.animation_data.action.name+".smd":
                bpy.context.scene.vs.export_list_active = index
        bpy.context.scene.vs.action_selection = "CURRENT"
        body_armature.data.vs.implicit_zero_bone = False
        bpy.ops.export_scene.smd()

        print("generating qc file for arms")
        qcfile = """$modelname \""""+sanitized_model_name+"""/"""+sanitized_model_name+"""_arms.mdl\"

$BodyGroup \""""+sanitized_model_name+"""_arms\"
{
    studio \""""+sanitized_model_name+"""_arms.smd\"
}


$SurfaceProp \"flesh\"

$Contents \"solid\"

$EyePosition 0 0 70

$MaxEyeDeflection 90

$MostlyOpaque

$CDMaterials \"models\\"""+sanitized_model_name+"""\\\"

$CBox 0 0 0 0 0 0

$BBox -13 -13 0 13 13 72

$Sequence \"idle\" {
    \"anims/idle_arms.smd\"
    fps 1
}"""
        print("writing qc file for arms. If this errors, please save your file!")
        compilefile = open(bpy.path.abspath("//CATS Bake/" + platform_name + "/"+sanitized_model_name+"_arms/"+sanitized_model_name+"_arms.qc"), "w")
        compilefile.write(qcfile)
        compilefile.close()

        print("Compiling arms model! (THIS CAN TAKE A LONG TIME AND IS PRONE TO ERRORS!!!!)")
        bpy.ops.smd.compile_qc(filepath=bpy.path.abspath(bpy.context.scene.vs.qc_path))

        print("Moving compiled arms model to addon folder.")
        #path after models must match model path in QC.
        #thanks to "https://stackoverflow.com/a/41827240" for helping me make sure this would work correctly.
        #this is the same as body because they should both be put in the same folder. This could be called once at the end of the script but eh i don't think it's needed.
        source_dir = steam_librarypath+"/garrysmod/models/"+sanitized_model_name
        target_dir = addonpath+"models/"+sanitized_model_name
        file_names = os.listdir(source_dir)
        os.makedirs(target_dir,0o777,True)
        for file_name in file_names:
            if os.path.exists(os.path.join(target_dir, file_name)):
                os.remove(os.path.join(target_dir, file_name))
            shutil.move(os.path.join(source_dir, file_name), target_dir)


        print("======================FINISHED GMOD PROCESS======================")
        return {'FINISHED'}


# def popup_install_xps(self, context):
#     layout = self.layout
#     col = layout.column(align=True)
#
#     row = col.row(align=True)
#     row.label(text="The plugin 'XPS Tools' is required for this function.")
#     col.separator()
#     row = col.row(align=True)
#     row.label(text="If it is not enabled please enable it in your User Preferences.")
#     row = col.row(align=True)
#     row.label(text="If it is not installed please click here to download it and then install it manually.")
#     col.separator()
#     row = col.row(align=True)
#     row.operator('importer.download_xps_tools', icon=globs.ICON_URL)
#
#
# def popup_install_source(self, context):
#     layout = self.layout
#     col = layout.column(align=True)
#
#     row = col.row(align=True)
#     row.label(text="The plugin 'Blender Source Tools' is required for this function.")
#     col.separator()
#     row = col.row(align=True)
#     row.label(text="If it is not enabled please enable it in your User Preferences.")
#     row = col.row(align=True)
#     row.label(text="If it is not installed please click here to download it and then install it manually.")
#     col.separator()
#     row = col.row(align=True)
#     row.operator('importer.download_source_tools', icon=globs.ICON_URL)
#
#
# def popup_install_vrm(self, context):
#     layout = self.layout
#     col = layout.column(align=True)
#
#     row = col.row(align=True)
#     row.label(text="The plugin 'VRM Importer' is required for this function.")
#     col.separator()
#     row = col.row(align=True)
#     row.label(text="If it is not enabled please enable it in your User Preferences.")
#     row = col.row(align=True)
#     row.label(text="Currently you have to select 'Testing' in the addons settings")
#     row = col.row(align=True)
#     row.label(text="If it is not installed please click here to download it and then install it manually.")
#     col.separator()
#     row = col.row(align=True)
#     row.operator('importer.download_vrm', icon=globs.ICON_URL)


@register_wrap
class XpsToolsButton(bpy.types.Operator):
    bl_idname = 'cats_importer.download_xps_tools'
    bl_label = t('XpsToolsButton.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('XpsToolsButton.URL'))

        self.report({'INFO'}, t('XpsToolsButton.success'))
        return {'FINISHED'}


@register_wrap
class SourceToolsButton(bpy.types.Operator):
    bl_idname = 'cats_importer.download_source_tools'
    bl_label = t('SourceToolsButton.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open(t('SourceToolsButton.URL'))

        self.report({'INFO'}, t('SourceToolsButton.success'))
        return {'FINISHED'}


@register_wrap
class VrmToolsButton(bpy.types.Operator):
    bl_idname = 'cats_importer.download_vrm'
    bl_label = t('VrmToolsButton.label')
    bl_options = {'INTERNAL'}

    def execute(self, context):
        if Common.version_2_79_or_older():
            webbrowser.open(t('VrmToolsButton.URL_2.79'))
        else:
            webbrowser.open(t('VrmToolsButton.URL_2.8'))

        self.report({'INFO'}, t('VrmToolsButton.success'))
        return {'FINISHED'}


# Export checks
_meshes_count = 0
_tris_count = 0
_mat_list = []
_broken_shapes = []
_textures_found = False
_eye_meshes_not_named_body = []

max_mats = 4
max_tris = 70000
max_meshes_light = 2
max_meshes_hard = 8


@register_wrap
class ExportModel(bpy.types.Operator):
    bl_idname = 'cats_importer.export_model'
    bl_label = t('ExportModel.label')
    bl_description = t('ExportModel.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    action = bpy.props.EnumProperty(
        items=(('CHECK', '', 'Please Ignore'),
               ('NO_CHECK', '', 'Please Ignore')))

    filepath = bpy.props.StringProperty()

    def execute(self, context):
        meshes = Common.get_meshes_objects()

        # Check for warnings
        if not self.action == 'NO_CHECK':
            global _meshes_count, _tris_count, _mat_list, _broken_shapes, _textures_found, _eye_meshes_not_named_body

            # Reset export checks
            _meshes_count = 0
            _tris_count = 0
            _mat_list = []
            _broken_shapes = []
            _textures_found = False
            _eye_meshes_not_named_body = []

            body_extists = False
            for mesh in meshes:
                if mesh.name == 'Body':
                    body_extists = True
                    break

            # Check for export warnings
            for mesh in meshes:
                # Check mesh count
                _meshes_count += 1

                # Check tris count
                _tris_count += len(mesh.data.polygons)

                # Check material count
                for mat_slot in mesh.material_slots:
                    if mat_slot and mat_slot.material and mat_slot.material.users and mat_slot.material.name not in _mat_list:
                        _mat_list.append(mat_slot.material.name)

                        # Check if any textures are found
                        if version_2_79_or_older():
                            if not _textures_found:
                                for tex_slot in mat_slot.material.texture_slots:
                                    if tex_slot and tex_slot.texture and tex_slot.texture.image:
                                        tex_path = bpy.path.abspath(tex_slot.texture.image.filepath)
                                        if os.path.isfile(tex_path):
                                            _textures_found = True
                                            break
                        else:
                            _textures_found = True
                            # TODO

                if Common.has_shapekeys(mesh):
                    # Check if there are broken shapekeys
                    for shapekey in mesh.data.shape_keys.key_blocks[1:]:
                        vert_count = 0
                        for vert in shapekey.data:
                            vert_count += 1
                            for coord in vert.co:
                                if coord >= 10000:
                                    _broken_shapes.append(shapekey.name)
                                    vert_count = 1000
                                    break
                            # Only check the first 10 vertices of this shapekey
                            if vert_count == 1000:
                                break

                    # Check if there are meshes with eye tracking, but are not named Body
                    if not body_extists:
                        for shapekey in mesh.data.shape_keys.key_blocks[1:]:
                            if mesh.name not in _eye_meshes_not_named_body:
                                if shapekey.name.startswith(('vrc.blink', 'vrc.lower')):
                                    _eye_meshes_not_named_body.append(mesh.name)
                                    break

            # Check if a warning should be shown
            if _meshes_count > max_meshes_light \
                    or _tris_count > max_tris \
                    or len(_mat_list) > max_mats \
                    or len(_broken_shapes) > 0 \
                    or not _textures_found and Settings.get_embed_textures()\
                    or len(_eye_meshes_not_named_body) > 0:
                bpy.ops.cats_importer.display_error('INVOKE_DEFAULT')
                return {'FINISHED'}

        # Continue if there are no errors or the check was skipped

        # Monkey patch FBX exporter again to import empty shape keys
        Fbx_patch.patch_fbx_exporter()

        # Check if copy protection is enabled
        mesh_smooth_type = 'OFF'
        protected_export = False
        for mesh in meshes:
            if protected_export:
                break
            if Common.has_shapekeys(mesh):
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if shapekey.name == 'Basis Original':
                        protected_export = True
                        break
        if protected_export:
            mesh_smooth_type = 'FACE'

        # Check if textures are found and if they should be embedded
        path_mode = 'AUTO'
        if _textures_found and Settings.get_embed_textures():
            path_mode = 'COPY'

        # Open export window
        try:
            if self.filepath:
                bpy.ops.export_scene.fbx('EXEC_DEFAULT',
                                         filepath=self.filepath,
                                         object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
                                         use_mesh_modifiers=False,
                                         add_leaf_bones=False,
                                         bake_anim=False,
                                         apply_scale_options='FBX_SCALE_ALL',
                                         path_mode=path_mode,
                                         embed_textures=True,
                                         mesh_smooth_type=mesh_smooth_type)
            else:
                bpy.ops.export_scene.fbx('INVOKE_DEFAULT',
                                         object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
                                         use_mesh_modifiers=False,
                                         add_leaf_bones=False,
                                         bake_anim=False,
                                         apply_scale_options='FBX_SCALE_ALL',
                                         path_mode=path_mode,
                                         embed_textures=True,
                                         mesh_smooth_type=mesh_smooth_type)
        except (TypeError, ValueError):
            bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
        except AttributeError:
            self.report({'ERROR'}, t('ExportModel.error.notEnabled'))

        return {'FINISHED'}


@register_wrap
class ErrorDisplay(bpy.types.Operator):
    bl_idname = "cats_importer.display_error"
    bl_label = t('ErrorDisplay.label')
    bl_options = {'INTERNAL'}

    tris_count = 0
    mat_list = []
    mat_count = 0
    meshes_count = 0
    broken_shapes = []
    textures_found = False
    eye_meshes_not_named_body = []

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        global _meshes_count, _tris_count, _mat_list, _broken_shapes, _textures_found, _eye_meshes_not_named_body
        self.meshes_count = _meshes_count
        self.tris_count = _tris_count
        self.mat_list = _mat_list
        self.mat_count = len(_mat_list)
        self.broken_shapes = _broken_shapes
        self.textures_found = _textures_found
        self.eye_meshes_not_named_body = _eye_meshes_not_named_body

        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 6.1))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if self.tris_count > max_tris:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.polygons1'), icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.polygons2', number=str(self.tris_count)))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.polygons3'))
            col.separator()
            col.separator()
            col.separator()

        # if self.mat_count > 10:
        #     row = col.row(align=True)
        #     row.scale_y = 0.75
        #     row.label(text="Too many materials!", icon='ERROR')
        #     col.separator()
        #
        #     row = col.row(align=True)
        #     row.scale_y = 0.75
        #     row.label(text="You have " + str(self.mat_count) + " materials on this model! (max 10)")
        #     row = col.row(align=True)
        #     row.scale_y = 0.75
        #     row.label(text="You should create a texture atlas before you export this model.")
        #     col.separator()
        #     row = col.row(align=True)
        #     row.scale_y = 0.75
        #     row.label(text="The Auto Atlas in CATS is now better and easier than ever, so please make use of it.")
        #     col.separator()
        #     col.separator()
        #     col.separator()

        if self.mat_count > max_mats:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.materials1'), icon='INFO')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.materials2', number=str(self.mat_count)))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.materials3'))
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.materials4'))
            col.separator()
            col.separator()
            col.separator()

        if self.meshes_count > max_meshes_light:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.meshes1'), icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.meshes2', number=str(self.meshes_count)))
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            if self.meshes_count <= max_meshes_hard:
                row.label(text=t('ErrorDisplay.meshes3'))
            else:
                row.label(text=t('ErrorDisplay.meshes3_alt'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.meshes4'))
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1
            row.operator(armature_manual.JoinMeshes.bl_idname, text=t('ErrorDisplay.JoinMeshes.label'), icon='AUTOMERGE_ON')
            col.separator()
            col.separator()
            col.separator()

        if self.broken_shapes:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.brokenShapekeys1'), icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.brokenShapekeys2', number=str(len(self.broken_shapes))))
            col.separator()

            for shapekey in self.broken_shapes:
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="  - " + shapekey)

            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.brokenShapekeys3'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.brokenShapekeys4'))
            col.separator()
            col.separator()
            col.separator()

        if not self.textures_found and Settings.get_embed_textures():
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.textures1'), icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.textures2'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.textures3'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.textures4'))
            col.separator()
            col.separator()
            col.separator()

        if len(self.eye_meshes_not_named_body) == 1:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.eyes1'), icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.eyes2', name=self.eye_meshes_not_named_body[0]))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t( 'ErrorDisplay.eyes3'))
            col.separator()
            col.separator()
            col.separator()

        elif len(self.eye_meshes_not_named_body) > 1:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.eyes1'), icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.eyes2_alt'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.eyes3_alt'))
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text=t('ErrorDisplay.eyes4_alt'))
            col.separator()
            col.separator()
            col.separator()

        row = col.row(align=True)
        row.operator(ExportModel.bl_idname, text=t('ErrorDisplay.continue'), icon=globs.ICON_EXPORT).action = 'NO_CHECK'
