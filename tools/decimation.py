# MIT License

# Copyright (c) 2018 Hotox

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
# Edits by:

import bpy
import tools.common
from mmd_tools_local import utils


class AutoDecimateButton(bpy.types.Operator):
    bl_idname = 'auto.decimate'
    bl_label = 'Quick Decimation'
    bl_description = 'This will automatically decimate your model while preserving the shape keys.\n' \
                     'You should manually remove unimportant meshes first.'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        i = 0
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                if ob.parent is not None and ob.parent.type == 'ARMATURE':
                    i += 1
        return i == 1

    @staticmethod
    def __can_remove(key_block):
        if 'mmd_' in key_block.name:
            return True
        if key_block.relative_key == key_block:
            return False  # Basis
        for v0, v1 in zip(key_block.relative_key.data, key_block.data):
            if v0.co != v1.co:
                return False
        return True

    def __shape_key_clean(self, context, obj, key_blocks):
        for kb in key_blocks:
            if self.__can_remove(kb):
                obj.shape_key_remove(kb)

    def __shape_key_clean_old(self, context, obj, key_blocks):
        context.scene.objects.active = obj
        for i in reversed(range(len(key_blocks))):
            kb = key_blocks[i]
            if self.__can_remove(kb):
                obj.active_shape_key_index = i
                bpy.ops.object.shape_key_remove()

    __do_shape_key_clean = __shape_key_clean_old if bpy.app.version < (2, 75, 0) else __shape_key_clean

    def execute(self, context):
        # Remove Rigidbodies and joints
        tools.common.unhide_all()
        tools.common.switch('OBJECT')
        for obj in bpy.data.objects:
            if 'rigidbodies' in obj.name or 'joints' in obj.name:
                tools.common.delete_hierarchy(obj)

        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            tools.common.unselect_all()
            meshes = tools.common.get_meshes_objects()
            if len(meshes) == 0:
                return {'FINISHED'}
            obj = meshes[0]
            tools.common.select(obj)

        for mod in obj.modifiers:
            if 'Decimate' in mod.name:
                bpy.ops.object.modifier_remove(modifier=mod.name)
            else:
                mod.show_expanded = False

        tools.common.set_default_stage()

        utils.separateByMaterials(obj)
        for ob in context.selected_objects:
            if ob.type != 'MESH' or ob.data.shape_keys is None:
                continue
            if not ob.data.shape_keys.use_relative:
                continue  # not be considered yet
            key_blocks = ob.data.shape_keys.key_blocks
            counts = len(key_blocks)
            self.__do_shape_key_clean(context, ob, key_blocks)
            counts -= len(key_blocks)

        utils.clearUnusedMeshes()

        self.decimate(context)

        return {'FINISHED'}

    def decimate(self, context):
        print('START DECIMATION')
        full_decimation = context.scene.full_decimation
        half_decimation = context.scene.half_decimation
        meshes = []
        current_tris_count = 0
        tris_count = 0

        for mesh in tools.common.get_meshes_objects():
            tools.common.select(mesh)

            tris = len(bpy.context.active_object.data.polygons)
            current_tris_count += tris

            if mesh.data.shape_keys is not None:
                if full_decimation:
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
                elif half_decimation and len(mesh.data.shape_keys.key_blocks) < 4:
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
                elif len(mesh.data.shape_keys.key_blocks) == 1:
                    bpy.ops.object.shape_key_remove(all=True)
                    meshes.append((mesh, tris))
                    tris_count += tris
            else:
                meshes.append((mesh, tris))
                tris_count += tris

            tools.common.unselect_all()

        meshes.sort(key=lambda x: x[1])

        for mesh in reversed(meshes):
            mesh_obj = mesh[0]
            tris = mesh[1]

            tools.common.select(mesh_obj)
            print(mesh_obj.name)

            decimation = (context.scene.max_tris - current_tris_count + tris_count) / tris_count
            print(decimation)

            bpy.ops.object.modifier_add(type='DECIMATE')

            bpy.context.object.modifiers["Decimate"].ratio = decimation
            bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True

            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
            tris_after = len(bpy.context.active_object.data.polygons)
            print(tris)
            print(tris_after)

            current_tris_count = current_tris_count - tris + tris_after
            tris_count = tris_count - tris

            tools.common.unselect_all()

        mesh = tools.common.join_meshes(context)
        if mesh is not None:
            tools.common.repair_viseme_order(mesh.name)

        if decimation < 0:
            self.report({'ERROR'}, 'Model decimated but desired polycount could not be reached.\n'
                                   'You can go back and try again with enabled Full/Half Decimation or manually remove the shape keys from unimportant meshes first.')





