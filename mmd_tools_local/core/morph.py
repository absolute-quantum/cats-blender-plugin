# -*- coding: utf-8 -*-

import bpy

class FnMorph(object):
    
    def __init__(self, morph, model):
        self.__morph = morph
        self.__rig = model

    @classmethod
    def storeShapeKeyOrder(cls, obj, shape_key_names):
        if len(shape_key_names) < 1:
            return
        assert(bpy.context.scene.objects.active == obj)
        if obj.data.shape_keys is None:
            bpy.ops.object.shape_key_add()

        if bpy.app.version < (2, 73, 0):
            def __move_to_bottom(key_blocks, name):
                obj.active_shape_key_index = key_blocks.find(name)
                for move in range(len(key_blocks)-1-obj.active_shape_key_index):
                    bpy.ops.object.shape_key_move(type='DOWN')
        else:
            def __move_to_bottom(key_blocks, name):
                obj.active_shape_key_index = key_blocks.find(name)
                bpy.ops.object.shape_key_move(type='BOTTOM')

        key_blocks = obj.data.shape_keys.key_blocks
        for name in shape_key_names:
            if name not in key_blocks:
                obj.shape_key_add(name)
            elif len(key_blocks) > 1:
                __move_to_bottom(key_blocks, name)

    @classmethod
    def fixShapeKeyOrder(cls, obj, shape_key_names):
        if len(shape_key_names) < 1:
            return
        assert(bpy.context.scene.objects.active == obj)
        shape_keys = obj.data.shape_keys
        if shape_keys is None:
            return
        key_blocks = shape_keys.key_blocks
        if bpy.app.version < (2, 73, 0):
            len_key_blocks = len(key_blocks)
            for ii, name in enumerate(reversed(shape_key_names)):
                idx = key_blocks.find(name)
                if idx < 0:
                    continue
                obj.active_shape_key_index = idx
                offset = (len_key_blocks - 1 - idx) - ii
                move_type = 'UP' if offset < 0 else 'DOWN'
                for move in range(abs(offset)):
                    bpy.ops.object.shape_key_move(type=move_type)
        else:
            for name in shape_key_names:
                idx = key_blocks.find(name)
                if idx < 0:
                    continue
                obj.active_shape_key_index = idx
                bpy.ops.object.shape_key_move(type='BOTTOM')

    def update_mat_related_mesh(self, new_mesh=None):
        for offset in self.__morph.data:
            # Use the new_mesh if provided  
            meshObj = new_mesh          
            if new_mesh is None:
                # Try to find the mesh by material name
                meshObj = self.__rig.findMesh(offset.material)
            
            if meshObj is None:
                # Given this point we need to loop through all the meshes
                for mesh in self.__rig.meshes():
                    if mesh.data.materials.find(offset.material) >= 0:
                        meshObj = mesh
                        break

            # Finally update the reference
            if meshObj is not None:
                offset.related_mesh = meshObj.data.name

