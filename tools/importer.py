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
import tools.eyetracking
import bpy_extras.io_utils

mmd_tools_installed = False
try:
    import mmd_tools_local

    mmd_tools_installed = True
except:
    pass


class ImportModel(bpy.types.Operator):
    bl_idname = 'importer.import_model'
    bl_label = 'Import Model'
    bl_description = 'Import a model of the selected type'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()
        if context.scene.import_mode == 'MMD':
            if not mmd_tools_installed:
                bpy.ops.enable.mmd('INVOKE_DEFAULT')
                return {'FINISHED'}

            try:
                bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT', scale=0.08, types={'MESH', 'ARMATURE', 'MORPHS'}, log_level='WARNING')
            except AttributeError:
                bpy.ops.enable.mmd('INVOKE_DEFAULT')
            except (TypeError, ValueError):
                bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT')

        elif context.scene.import_mode == 'XPS':
            try:
                bpy.ops.xps_tools.import_model('INVOKE_DEFAULT')
            except AttributeError:
                bpy.ops.install.xps('INVOKE_DEFAULT')

        elif context.scene.import_mode == 'SOURCE':
            try:
                bpy.ops.import_scene.smd('INVOKE_DEFAULT')
            except AttributeError:
                bpy.ops.install.source('INVOKE_DEFAULT')

        elif context.scene.import_mode == 'FBX':
            try:
                bpy.ops.import_scene.fbx('INVOKE_DEFAULT', automatic_bone_orientation=True)
            except (TypeError, ValueError):
                bpy.ops.import_scene.fbx('INVOKE_DEFAULT')

        return {'FINISHED'}


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

    if bpy.app.version < (2, 79, 9):
        filter_glob = bpy.props.StringProperty(
            default="*.pmx;*.pmd;*.xps;*.mesh;*.ascii;*.smd;*.qc;*.vta;*.dmx;*.fbx",
            options={'HIDDEN'}
        )
    else:
        filter_glob = bpy.props.StringProperty(
            default="*.pmx;*.pmd;*.xps;*.mesh;*.ascii;*.smd;*.qc;*.vta;*.dmx;*.fbx;*.dae",
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
        for f in self.files:
            file_name = f['name']
            filepath = os.path.join(self.directory, file_name)
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
                                                   filepath=filepath)
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
                                             filepath=filepath,
                                             automatic_bone_orientation=True)
                except (TypeError, ValueError):
                    bpy.ops.import_scene.fbx('INVOKE_DEFAULT')
                except RuntimeError as e:
                    if 'unsupported, must be 7100 or later' in str(e):
                        tools.common.show_error(6.2, ['The FBX file version is unsupported!',
                                                      'Please use a tool such as the "Autodesk FBX Converter" to make it compatible.'])
                    print(str(e))

            # DAE - not working currently because of bug:
            # https://blender.stackexchange.com/questions/110788/file-browser-filter-not-working-correctly
            elif file_ending == 'dae':
                try:
                    bpy.ops.wm.collada_import('EXEC_DEFAULT',
                                              filepath=filepath,
                                              fix_orientation=True,
                                              auto_connect=True)
                except (TypeError, ValueError):
                    bpy.ops.wm.collada_import('INVOKE_DEFAULT')

        return {'FINISHED'}


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


class ImportMMD(bpy.types.Operator):
    bl_idname = 'importer.import_mmd'
    bl_label = 'MMD'
    bl_description = 'Import a MMD model (.pmx/.pmd)'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()

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


class ImportXPS(bpy.types.Operator):
    bl_idname = 'importer.import_xps'
    bl_label = 'XNALara'
    bl_description = 'Import a XNALara model (.xps/.mesh/.ascii)'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()
        try:
            bpy.ops.xps_tools.import_model('INVOKE_DEFAULT')
        except AttributeError:
            bpy.ops.install.xps('INVOKE_DEFAULT')

        return {'FINISHED'}


class ImportSource(bpy.types.Operator):
    bl_idname = 'importer.import_source'
    bl_label = 'Source'
    bl_description = 'Import a Source model (.smd/.qc/.vta/.dmx)'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()
        try:
            bpy.ops.import_scene.smd('INVOKE_DEFAULT')
        except AttributeError:
            bpy.ops.install.source('INVOKE_DEFAULT')

        return {'FINISHED'}


class ImportFBX(bpy.types.Operator):
    bl_idname = 'importer.import_fbx'
    bl_label = 'FBX'
    bl_description = 'Import a FBX model (.fbx)'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        tools.common.remove_unused_objects()
        try:
            bpy.ops.import_scene.fbx('INVOKE_DEFAULT', automatic_bone_orientation=True)
        except (TypeError, ValueError):
            bpy.ops.import_scene.fbx('INVOKE_DEFAULT')

        return {'FINISHED'}


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
        row.label("The plugin 'XPS Tools' is required for this function.")
        col.separator()
        row = col.row(align=True)
        row.label("If it is not enabled please enable it in your User Preferences.")
        row = col.row(align=True)
        row.label("If it is not installed please download and install it manually.")
        col.separator()
        row = col.row(align=True)
        row.operator('importer.xps_tools', icon='LOAD_FACTORY')


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
        row.label("The plugin 'Source Tools' is required for this function.")
        col.separator()
        row = col.row(align=True)
        row.label("If it is not enabled please enable it in your User Preferences.")
        row = col.row(align=True)
        row.label("If it is not installed please download and install it manually.")
        col.separator()
        row = col.row(align=True)
        row.operator('importer.source_tools', icon='LOAD_FACTORY')


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
        row.label("The plugin 'mmd_tools' is required for this function.")
        row = col.row(align=True)
        row.label("Please restart Blender.")


def popup_install_xps(self, context):
    layout = self.layout
    col = layout.column(align=True)

    row = col.row(align=True)
    row.label("The plugin 'XPS Tools' is required for this function.")
    col.separator()
    row = col.row(align=True)
    row.label("If it is not enabled please enable it in your User Preferences.")
    row = col.row(align=True)
    row.label("If it is not installed please click here to download it and then install it manually.")
    col.separator()
    row = col.row(align=True)
    row.operator('importer.xps_tools', icon='LOAD_FACTORY')


def popup_install_source(self, context):
    layout = self.layout
    col = layout.column(align=True)

    row = col.row(align=True)
    row.label("The plugin 'Blender Source Tools' is required for this function.")
    col.separator()
    row = col.row(align=True)
    row.label("If it is not enabled please enable it in your User Preferences.")
    row = col.row(align=True)
    row.label("If it is not installed please click here to download it and then install it manually.")
    col.separator()
    row = col.row(align=True)
    row.operator('importer.source_tools', icon='LOAD_FACTORY')


class XpsToolsButton(bpy.types.Operator):
    bl_idname = 'importer.xps_tools'
    bl_label = 'Download XPS Tools'

    def execute(self, context):
        webbrowser.open('https://github.com/johnzero7/XNALaraMesh')

        self.report({'INFO'}, 'XPS Tools link opened')
        return {'FINISHED'}


class SourceToolsButton(bpy.types.Operator):
    bl_idname = 'importer.source_tools'
    bl_label = 'Download Source Tools'

    def execute(self, context):
        webbrowser.open('http://steamreview.org/BlenderSourceTools/')

        self.report({'INFO'}, 'Source Tools link opened')
        return {'FINISHED'}


class ExportModel(bpy.types.Operator):
    bl_idname = 'importer.export_model'
    bl_label = 'Export Model'
    bl_description = 'Export this model as .fbx for Unity.\n' \
                     '\n' \
                     'Automatically sets the optimal export settings'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    action = bpy.props.EnumProperty(
        items=(('CHECK', '', ''),
               ('NO_CHECK', '', '')))

    def execute(self, context):
        # Check for warnings
        print(self.action)
        if not self.action == 'NO_CHECK':
            mat_list = []
            meshes = tools.common.get_meshes_objects()

            if len(meshes) > 10:
                bpy.ops.display.error('INVOKE_DEFAULT')
                return {'FINISHED'}

            for mesh in meshes:
                if len(mesh.data.polygons) >= 65535:
                    bpy.ops.display.error('INVOKE_DEFAULT')
                    return {'FINISHED'}
                for mat_slot in mesh.material_slots:
                    if mat_slot and mat_slot.material and mat_slot.material.name not in mat_list:
                        mat_list.append(mat_slot.material.name)

                for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                    if i == 0:
                        continue
                    for i2, vert in enumerate(shapekey.data):
                        for coord in vert.co:
                            if coord > 10000:
                                bpy.ops.display.error('INVOKE_DEFAULT')
                                return {'FINISHED'}
                        if i2 >= 4:
                            break

            if len(mat_list) > 10:
                bpy.ops.display.error('INVOKE_DEFAULT')
                return {'FINISHED'}

        # Open export window
        protected_export = False
        for mesh in tools.common.get_meshes_objects():
            if protected_export:
                break
            if mesh.data.shape_keys:
                for shapekey in mesh.data.shape_keys.key_blocks:
                    if shapekey.name == 'Basis Original':
                        protected_export = True
                        break

        try:
            if protected_export:
                bpy.ops.export_scene.fbx('INVOKE_DEFAULT',
                                         object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
                                         use_mesh_modifiers=False,
                                         add_leaf_bones=False,
                                         bake_anim=False,
                                         apply_scale_options='FBX_SCALE_ALL',
                                         path_mode='COPY',
                                         embed_textures=True,
                                         mesh_smooth_type='FACE')
            else:
                bpy.ops.export_scene.fbx('INVOKE_DEFAULT',
                                         object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
                                         use_mesh_modifiers=False,
                                         add_leaf_bones=False,
                                         bake_anim=False,
                                         apply_scale_options='FBX_SCALE_ALL',
                                         path_mode='COPY',
                                         embed_textures=True)
        except (TypeError, ValueError):
            bpy.ops.export_scene.fbx('INVOKE_DEFAULT')

        return {'FINISHED'}


class ErrorDisplay(bpy.types.Operator):
    bl_idname = "display.error"
    bl_label = "Warning:"

    meshes_too_big = {}
    mat_list = []
    meshes_count = 0
    broken_shapes = []

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        self.meshes_too_big = {}
        for mesh in tools.common.get_meshes_objects():
            tris = len(mesh.data.polygons)
            if tris >= 65535:
                self.meshes_too_big[mesh.name] = tris
            for mat_slot in mesh.material_slots:
                if mat_slot and mat_slot.material and mat_slot.material.name not in self.mat_list:
                    self.mat_list.append(mat_slot.material.name)
            self.meshes_count += 1

            for i, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
                if i == 0:
                    continue
                for i2, vert in enumerate(shapekey.data):
                    for coord in vert.co:
                        if coord > 10000:
                            print(shapekey.name, coord)
                            self.broken_shapes.append(shapekey.name)
                            i2 = 10
                            break
                    if i2 >= 4:
                        break

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
            row.label("Meshes are too big!", icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("The following meshes have more than 65534 tris:")
            col.separator()

            for mesh, tris in self.meshes_too_big.items():
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label("  - " + mesh + ' (' + str(tris) + ' tris)')

            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("Unity will split these meshes in half and you will loose your shape keys.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("You should decimate them before you export this model.")
            col.separator()
            col.separator()

        if len(self.mat_list) > 10:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("Model unoptimized!", icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("This model has " + str(len(self.mat_list)) + " materials!")
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("It will be extremely unoptimized and cause lag for you and others.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("Please be considerate and create a texture atlas.")
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("The Auto Atlas in CATS is now better and easier than ever, so please make use of it.")
            col.separator()
            col.separator()

        if self.meshes_count > 10:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("Model unoptimized!", icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("This model has " + str(self.meshes_count) + " meshes!")
            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("It will be extremely unoptimized and cause lag for you and others.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("Please be considerate and join your meshes.")
            col.separator()
            col.separator()

        if self.broken_shapes:
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("Broken shapekeys!", icon='ERROR')
            col.separator()

            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("This model has " + str(len(self.broken_shapes)) + " broken shapekey(s):")
            col.separator()

            for shapekey in self.broken_shapes:
                row = col.row(align=True)
                row.scale_y = 0.75
                row.label("  - " + shapekey)

            col.separator()
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("You will not be able to upload this model until you fix these shapekeys.")
            row = col.row(align=True)
            row.scale_y = 0.75
            row.label("Either delete or repair them before export.")
            col.separator()
            col.separator()

        row = col.row(align=True)
        row.operator('importer.export_model', text='Continue to Export', icon='LOAD_FACTORY').action = 'NO_CHECK'
