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

# Code author: Hotox
# Repo: https://github.com/michaeldegroot/cats-blender-plugin

import os
import bpy
import webbrowser
import tools.common
import tools.settings
import tools.eyetracking
import bpy_extras.io_utils
from tools.common import version_2_79_or_older
from tools.register import register_wrap

mmd_tools_installed = False
try:
    import mmd_tools_local
    mmd_tools_installed = True
except:
    pass


ICON_URL = 'URL'
ICON_EXPORT = 'EXPORT'
if version_2_79_or_older():
    ICON_URL = 'LOAD_FACTORY'
    ICON_EXPORT = 'LOAD_FACTORY'


@register_wrap
class ImportAnyModel(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = 'importer.import_any_model'
    bl_label = 'Import Any Model'
    bl_description = 'Import a model of any supported type.' \
                     '\n' \
                     '\nSupported types:' \
                     '\n- MMD: .pmx/.pmd' \
                     '\n- XNALara: .xps/.mesh/.ascii' \
                     '\n- Source: .smd/.qc/.vta/.dmx' \
                     '\n- FBX .fbx'
    # '\n- DAE .dae'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    files = bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory = bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    if version_2_79_or_older():
        filter_glob = bpy.props.StringProperty(
            default="*.pmx;*.pmd;*.xps;*.mesh;*.ascii;*.smd;*.qc;*.vta;*.dmx;*.fbx",
            options={'HIDDEN'}
        )
    else:
        filter_glob = bpy.props.StringProperty(
            default="*.pmx;*.pmd;*.xps;*.mesh;*.ascii;*.smd;*.qc;*.vta;*.dmx;*.fbx;*.dae;*.vrm",
            options={'HIDDEN'}
        )
    text1 = bpy.props.BoolProperty(
        name='IMPORTANT INFO (hover here)',
        description='If you want to modify the import settings, use the button next to the Import button.\n\n',
        default=False
    )

    def execute(self, context):
        print(self.directory)
        tools.common.remove_unused_objects()

        # Make sure that the first layer is visible
        if version_2_79_or_older():
            context.scene.layers[0] = True

        # Import the file using their corresponding importer
        for f in self.files:
            file_name = f['name']
            file_path = os.path.join(self.directory, file_name)
            file_ending = file_name.split('.')[-1].lower()

            # MMD
            if file_ending == 'pmx' or file_ending == 'pmd':
                try:
                    bpy.ops.mmd_tools.import_model('EXEC_DEFAULT',
                                                   files=[{'name': file_name}],
                                                   directory=self.directory,
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
                    bpy.ops.xps_tools.import_model('EXEC_DEFAULT',
                                                   filepath=file_path,
                                                   colorizeMesh=False)
                except AttributeError:
                    bpy.ops.install.xps('INVOKE_DEFAULT')

            # Source Engine
            elif file_ending == 'smd' or file_ending == 'qc' or file_ending == 'qci' or file_ending == 'vta' or file_ending == 'dmx':
                try:
                    bpy.ops.import_scene.smd('EXEC_DEFAULT',
                                             files=[{'name': file_name}],
                                             directory=self.directory)
                except AttributeError:
                    bpy.ops.install.source('INVOKE_DEFAULT')

            # FBX
            elif file_ending == 'fbx':
                try:
                    bpy.ops.import_scene.fbx('EXEC_DEFAULT',
                                             filepath=file_path,
                                             automatic_bone_orientation=True)
                except (TypeError, ValueError):
                    bpy.ops.import_scene.fbx('INVOKE_DEFAULT')
                except RuntimeError as e:
                    if 'unsupported, must be 7100 or later' in str(e):
                        tools.common.show_error(6.2, ['The FBX file version is unsupported!',
                                                      'Please use a tool such as the "Autodesk FBX Converter" to make it compatible.'])
                    print(str(e))

            # DAE - not working in 2.79 because of bug:
            # https://blender.stackexchange.com/questions/110788/file-browser-filter-not-working-correctly
            elif file_ending == 'dae':
                try:
                    bpy.ops.wm.collada_import('EXEC_DEFAULT',
                                              filepath=file_path,
                                              fix_orientation=True,
                                              auto_connect=True)
                except (TypeError, ValueError):
                    bpy.ops.wm.collada_import('INVOKE_DEFAULT')

            elif file_ending == 'vrm':
                try:
                    bpy.ops.import_scene.vrm('EXEC_DEFAULT',
                                             filepath=file_path)
                except (TypeError, ValueError):
                    bpy.ops.import_scene.vrm('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class ModelsPopup(bpy.types.Operator):
    bl_idname = "model.popup"
    bl_label = "Select which you want to import:"
    bl_description = 'Show individual import options'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 3, height=-550)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator('importer.import_mmd')
        row.operator('importer.import_xps')
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator('importer.import_source')
        row.operator('importer.import_fbx')
        row = col.row(align=True)
        row.scale_y = 1.3
        row.operator('importer.import_vrm')


@register_wrap
class ImportMMD(bpy.types.Operator):
    bl_idname = 'importer.import_mmd'
    bl_label = 'MMD'
    bl_description = 'Import a MMD model (.pmx/.pmd)'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()

        # Make sure that the first layer is visible
        if version_2_79_or_older():
            context.scene.layers[0] = True

        if not mmd_tools_installed:
            bpy.ops.enable.mmd('INVOKE_DEFAULT')
            return {'FINISHED'}

        try:
            bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT', scale=0.08, types={'MESH', 'ARMATURE', 'MORPHS'}, log_level='WARNING')
        except AttributeError:
            bpy.ops.enable.mmd('INVOKE_DEFAULT')
        except (TypeError, ValueError):
            bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class ImportXPS(bpy.types.Operator):
    bl_idname = 'importer.import_xps'
    bl_label = 'XNALara'
    bl_description = 'Import a XNALara model (.xps/.mesh/.ascii)'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()

        # Make sure that the first layer is visible
        if version_2_79_or_older():
            context.scene.layers[0] = True

        try:
            bpy.ops.xps_tools.import_model('INVOKE_DEFAULT', colorizeMesh=False)
        except AttributeError:
            bpy.ops.install.xps('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class ImportSource(bpy.types.Operator):
    bl_idname = 'importer.import_source'
    bl_label = 'Source'
    bl_description = 'Import a Source model (.smd/.qc/.vta/.dmx)'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()

        # Make sure that the first layer is visible
        if version_2_79_or_older():
            context.scene.layers[0] = True

        try:
            bpy.ops.import_scene.smd('INVOKE_DEFAULT')
        except AttributeError:
            bpy.ops.install.source('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class ImportFBX(bpy.types.Operator):
    bl_idname = 'importer.import_fbx'
    bl_label = 'FBX'
    bl_description = 'Import a FBX model (.fbx)'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()

        # Make sure that the first layer is visible
        if version_2_79_or_older():
            context.scene.layers[0] = True

        try:
            bpy.ops.import_scene.fbx('INVOKE_DEFAULT', automatic_bone_orientation=True)
        except (TypeError, ValueError):
            bpy.ops.import_scene.fbx('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class ImportVRM(bpy.types.Operator):
    bl_idname = 'importer.import_vrm'
    bl_label = 'VRM'
    bl_description = 'Import a VRM model (.vrm)'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()

        # Make sure that the first layer is visible
        if version_2_79_or_older():
            context.scene.layers[0] = True

        try:
            bpy.ops.import_scene.vrm('INVOKE_DEFAULT')
        except AttributeError:
            bpy.ops.install.vrm('INVOKE_DEFAULT')

        return {'FINISHED'}


@register_wrap
class InstallXPS(bpy.types.Operator):
    bl_idname = "install.xps"
    bl_label = "XPS Tools is not installed or enabled!"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 4.5, height=-550)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(text="The plugin 'XPS Tools' is required for this function.")
        col.separator()
        row = col.row(align=True)
        row.label(text="If it is not enabled please enable it in your User Preferences.")
        row = col.row(align=True)
        row.label(text="If it is not installed please download and install it manually.")
        col.separator()
        row = col.row(align=True)
        row.operator('importer.download_xps_tools', icon=ICON_URL)


@register_wrap
class InstallSource(bpy.types.Operator):
    bl_idname = "install.source"
    bl_label = "Source Tools is not installed or enabled!"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 4.5, height=-550)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(text="The plugin 'Source Tools' is required for this function.")
        col.separator()
        row = col.row(align=True)
        row.label(text="If it is not enabled please enable it in your User Preferences.")
        row = col.row(align=True)
        row.label(text="If it is not installed please download and install it manually.")
        col.separator()
        row = col.row(align=True)
        row.operator('importer.download_source_tools', icon=ICON_URL)


@register_wrap
class InstallVRM(bpy.types.Operator):
    bl_idname = "install.vrm"
    bl_label = "VRM Importer is not installed or enabled!"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 4.5, height=-550)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(text="The plugin 'VRM Importer' is required for this function.")
        col.separator()
        row = col.row(align=True)
        row.label(text="If it is not enabled please enable it in your User Preferences.")
        row = col.row(align=True)
        row.label(text="Currently you have to select 'Testing' in the addons settings")
        col.separator()
        row = col.row(align=True)
        row.label(text="If it is not installed please download and install it manually.")
        col.separator()
        row = col.row(align=True)
        row.operator('importer.download_vrm', icon=ICON_URL)


@register_wrap
class EnableMMD(bpy.types.Operator):
    bl_idname = "enable.mmd"
    bl_label = "Mmd_tools is not enabled!"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 4, height=-550)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(text="The plugin 'mmd_tools' is required for this function.")
        row = col.row(align=True)
        row.label(text="Please restart Blender.")


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
#     row.operator('importer.download_xps_tools', icon=ICON_URL)
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
#     row.operator('importer.download_source_tools', icon=ICON_URL)
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
#     row.operator('importer.download_vrm', icon=ICON_URL)


@register_wrap
class XpsToolsButton(bpy.types.Operator):
    bl_idname = 'importer.download_xps_tools'
    bl_label = 'Download XPS Tools'

    def execute(self, context):
        webbrowser.open('https://github.com/johnzero7/XNALaraMesh')

        self.report({'INFO'}, 'XPS Tools link opened')
        return {'FINISHED'}


@register_wrap
class SourceToolsButton(bpy.types.Operator):
    bl_idname = 'importer.download_source_tools'
    bl_label = 'Download Source Tools'

    def execute(self, context):
        webbrowser.open('http://steamreview.org/BlenderSourceTools/')

        self.report({'INFO'}, 'Source Tools link opened')
        return {'FINISHED'}


@register_wrap
class SourceToolsButton(bpy.types.Operator):
    bl_idname = 'importer.download_vrm'
    bl_label = 'Download VRM Importer'

    def execute(self, context):
        webbrowser.open('https://github.com/iCyP/VRM_IMPORTER')

        self.report({'INFO'}, 'VRM Importer link opened')
        return {'FINISHED'}


# Export checks
_meshes_count = 0
_meshes_too_big = {}
_mat_list = []
_broken_shapes = []
_textures_found = False


@register_wrap
class ExportModel(bpy.types.Operator):
    bl_idname = 'importer.export_model'
    bl_label = 'Export Model'
    bl_description = 'Export this model as .fbx for Unity.\n' \
                     '\n' \
                     'Automatically sets the optimal export settings'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    action = bpy.props.EnumProperty(
        items=(('CHECK', '', 'Please Ignore'),
               ('NO_CHECK', '', 'Please Ignore')))

    def execute(self, context):
        # Check for warnings
        if not self.action == 'NO_CHECK':
            global _meshes_count, _meshes_too_big, _mat_list, _broken_shapes, _textures_found

            # Reset export checks
            _meshes_count = 0
            _meshes_too_big = {}
            _mat_list = []
            _broken_shapes = []
            _textures_found = False

            # Check for export warnings
            for mesh in tools.common.get_meshes_objects():
                # Check mesh count
                _meshes_count += 1

                # Check tris count
                tris = len(mesh.data.polygons)
                if tris >= 65535:
                    _meshes_too_big[mesh.name] = tris

                # Check material count
                for mat_slot in mesh.material_slots:
                    if mat_slot and mat_slot.material and mat_slot.material.name not in _mat_list:
                        _mat_list.append(mat_slot.material.name)

                # Check if any textures are found
                        if version_2_79_or_older():
                            if not _textures_found:
                                for tex_slot in mat_slot.material.texture_slots:
                                    if tex_slot and tex_slot.texture:
                                        tex_path = bpy.path.abspath(tex_slot.texture.image.filepath)
                                        if os.path.isfile(tex_path):
                                            _textures_found = True
                                            break
                        else:
                            _textures_found = True
                            # TODO

                # Check if there are broken shapekeys
                if tools.common.has_shapekeys(mesh):
                    for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                        if i == 0:
                            continue
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

            # Check if a warning should be shown
            if _meshes_count > 1 \
                    or len(_meshes_too_big) > 0 \
                    or len(_mat_list) > 4 \
                    or len(_broken_shapes) > 0\
                    or not _textures_found and tools.settings.get_embed_textures():
                bpy.ops.display.error('INVOKE_DEFAULT')
                return {'FINISHED'}

        # Continue if there are no errors or the check was skipped

        # Check if copy protection is enabled
        mesh_smooth_type = 'OFF'
        protected_export = False
        for mesh in tools.common.get_meshes_objects():
            if protected_export:
                break
            if tools.common.has_shapekeys(mesh):
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if shapekey.name == 'Basis Original':
                        protected_export = True
                        break
        if protected_export:
            mesh_smooth_type = 'FACE'

        # Check if textures are found and if they should be embedded
        path_mode = 'AUTO'
        if _textures_found and tools.settings.get_embed_textures():
            path_mode = 'COPY'

        # Open export window
        try:
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

        return {'FINISHED'}


@register_wrap
class ErrorDisplay(bpy.types.Operator):
    bl_idname = "display.error"
    bl_label = "Warning:"

    meshes_too_big = {}
    mat_list = []
    meshes_count = 0
    broken_shapes = []
    textures_found = False

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        global _meshes_count, _meshes_too_big, _mat_list, _broken_shapes, _textures_found
        self.meshes_count = _meshes_count
        self.meshes_too_big = _meshes_too_big
        self.mat_list = _mat_list
        self.broken_shapes = _broken_shapes
        self.textures_found = _textures_found

        dpi_value = bpy.context.user_preferences.system.dpi
        return context.window_manager.invoke_props_dialog(self, width=dpi_value * 6.1, height=-550)

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        if self.meshes_too_big:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="Meshes are too big!", icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="The following meshes have more than 65534 tris:")
            col.separator()

            for mesh, tris in self.meshes_too_big.items():
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="  - " + mesh + ' (' + str(tris) + ' tris)')

            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="Unity will split these meshes in half and you will loose your shape keys.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="You should decimate them before you export this model.")
            col.separator()
            col.separator()

        if len(self.mat_list) > 4:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="Model unoptimized!", icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="This model has " + str(len(self.mat_list)) + " materials!")
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="It will be extremely unoptimized and cause lag for you and others.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="Please be considerate and create a texture atlas.")
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="The Auto Atlas in CATS is now better and easier than ever, so please make use of it.")
            col.separator()
            col.separator()
            col.separator()

        if self.meshes_count > 1:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="Model unoptimized!", icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="This model has " + str(self.meshes_count) + " meshes!")
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="It will be extremely unoptimized and cause lag for you and others.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="Please be considerate and join your meshes, it's easy:")
            col.separator()
            row = col.row(align=True)
            row.scale_y = 1
            row.operator('armature_manual.join_meshes', text='Join Meshes', icon='AUTOMERGE_ON')
            col.separator()
            col.separator()
            col.separator()

        if self.broken_shapes:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="Broken shapekeys!", icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="This model has " + str(len(self.broken_shapes)) + " broken shapekey(s):")
            col.separator()

            for shapekey in self.broken_shapes:
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label(text="  - " + shapekey)

            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="You will not be able to upload this model until you fix these shapekeys.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="Either delete or repair them before export.")
            col.separator()
            col.separator()
            col.separator()

        if not self.textures_found and tools.settings.get_embed_textures():
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="No textures found!", icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="This model has no textures assigned but you have 'Embed Textures' enabled.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="Therefore, no textures will embedded into the FBX.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label(text="This is not an issue, but you will have to import the textures manually into Unity.")
            col.separator()
            col.separator()
            col.separator()

        row = col.row(align=True)
        row.operator('importer.export_model', text='Continue to Export', icon=ICON_EXPORT).action = 'NO_CHECK'
