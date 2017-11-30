# -*- coding: utf-8 -*-

import bpy
from bpy.types import Operator
from mathutils import Vector, Quaternion

import mmd_tools_local.core.model as mmd_model
from mmd_tools_local import bpyutils
from mmd_tools_local import utils
from mmd_tools_local.utils import ItemOp, ItemMoveOp
from mmd_tools_local.core.material import FnMaterial
from mmd_tools_local.core.exceptions import MaterialNotFoundError, DivisionError

#Util functions
def divide_vector_components(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("Vectors should have the same number of components")
    result = []
    for v1, v2 in zip(vec1, vec2):
        if v2 == 0:
            if v1 == 0:
                v2 = 1 #If we have a 0/0 case we change the divisor to 1
            else:
                raise DivisionError("Invalid Input: a non-zero value can't be divided by zero")
        result.append(v1/v2)
    return result

def multiply_vector_components(vec1, vec2):
    if len(vec1) != len(vec2):
        raise ValueError("Vectors should have the same number of components")
    result = []
    for v1, v2 in zip(vec1, vec2):
        result.append(v1*v2)
    return result

def special_division(n1, n2):
    """This function returns 0 in case of 0/0. If non-zero divided by zero case is found, an Exception is raised
    """
    if n2 == 0:
        if n1 == 0:
            n2 = 1
        else:
            raise DivisionError("Invalid Input: a non-zero value can't be divided by zero")
    return n1/n2


class AddMorph(Operator):
    bl_idname = 'mmd_tools.morph_add'
    bl_label = 'Add Morph'
    bl_description = 'Add a morph item to active morph list'

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root
        morph_type = mmd_root.active_morph_type
        morphs = getattr(mmd_root, morph_type)
        morph, mmd_root.active_morph = ItemOp.add_after(morphs, mmd_root.active_morph)
        morph.name = 'New Morph'
        return {'FINISHED'}

class RemoveMorph(Operator):
    bl_idname = 'mmd_tools.morph_remove'
    bl_label = 'Remove Morph'
    bl_description = 'Remove active morph item from the list'

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root

        morph_type = mmd_root.active_morph_type
        if morph_type.startswith('material'):
            bpy.ops.mmd_tools.clear_temp_materials()
        elif morph_type.startswith('uv'):
            bpy.ops.mmd_tools.clear_uv_morph_view()

        morphs = getattr(mmd_root, morph_type)
        morphs.remove(mmd_root.active_morph)
        mmd_root.active_morph = max(0, mmd_root.active_morph-1)
        return {'FINISHED'}

class MoveMorph(Operator, ItemMoveOp):
    bl_idname = 'mmd_tools.morph_move'
    bl_label = 'Move Morph'
    bl_description = 'Move active morph item up/down in the list'

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root
        mmd_root.active_morph = self.move(
            getattr(mmd_root, mmd_root.active_morph_type),
            mmd_root.active_morph,
            self.type,
            )
        return {'FINISHED'}


class AddMorphOffset(Operator):
    bl_idname = 'mmd_tools.morph_offset_add'
    bl_label = 'Add Morph Offset'
    bl_description = 'Add a morph offset item to the list'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root
        morph_type = mmd_root.active_morph_type
        morph = ItemOp.get_by_index(getattr(mmd_root, morph_type), mmd_root.active_morph)
        if morph is None:
            return {'CANCELLED'}

        item, morph.active_data = ItemOp.add_after(morph.data, morph.active_data)

        if morph_type.startswith('material'):
            if obj.type == 'MESH' and obj.mmd_type == 'NONE':
                item.related_mesh = obj.data.name
                active_material = obj.active_material
                if active_material and '_temp' not in active_material.name:
                    item.material = active_material.name

        elif morph_type.startswith('bone'):
            pose_bone = context.active_pose_bone
            if pose_bone:
                item.bone = pose_bone.name
                item.location = pose_bone.location
                item.rotation = pose_bone.rotation_quaternion

        return { 'FINISHED' }

class RemoveMorphOffset(Operator):
    bl_idname = 'mmd_tools.morph_offset_remove'
    bl_label = 'Remove Morph Offset'
    bl_description = 'Remove active morph offset item from the list'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root = root.mmd_root
        morph_type = mmd_root.active_morph_type
        morph = ItemOp.get_by_index(getattr(mmd_root, morph_type), mmd_root.active_morph)
        if morph is None:
            return {'CANCELLED'}

        if morph_type.startswith('material'):
            bpy.ops.mmd_tools.clear_temp_materials()

        morph.data.remove(morph.active_data)
        morph.active_data = max(0, morph.active_data-1)
        return { 'FINISHED' }


class ApplyMaterialOffset(Operator):
    bl_idname = 'mmd_tools.apply_material_morph_offset'
    bl_label = 'Apply Material Offset'
    bl_description = 'Calculates the offsets and apply them, then the temporary material is removed'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        mmd_root = root.mmd_root
        morph = mmd_root.material_morphs[mmd_root.active_morph]
        mat_data = morph.data[morph.active_data]

        meshObj = rig.findMesh(mat_data.related_mesh)
        if meshObj is None:
            self.report({ 'ERROR' }, "The model mesh can't be found")
            return { 'CANCELLED' }
        try:
            work_mat_name = mat_data.material + '_temp'
            work_mat, base_mat = FnMaterial.swap_materials(meshObj, work_mat_name,
                                                           mat_data.material)
        except MaterialNotFoundError:
            self.report({ 'ERROR' }, "Material not found")
            return { 'CANCELLED' }

        copy_idx = meshObj.data.materials.find(work_mat.name)
        base_mmd_mat = base_mat.mmd_material
        work_mmd_mat = work_mat.mmd_material

        if mat_data.offset_type == "MULT":
            try:
                diffuse_offset = divide_vector_components(work_mmd_mat.diffuse_color, base_mmd_mat.diffuse_color) + [special_division(work_mmd_mat.alpha, base_mmd_mat.alpha)]
                specular_offset = divide_vector_components(work_mmd_mat.specular_color, base_mmd_mat.specular_color)
                edge_offset = divide_vector_components(work_mmd_mat.edge_color, base_mmd_mat.edge_color)
                mat_data.diffuse_color = diffuse_offset
                mat_data.specular_color = specular_offset
                mat_data.shininess = special_division(work_mmd_mat.shininess, base_mmd_mat.shininess)
                mat_data.ambient_color = divide_vector_components(work_mmd_mat.ambient_color, base_mmd_mat.ambient_color)
                mat_data.edge_color = edge_offset
                mat_data.edge_weight = special_division(work_mmd_mat.edge_weight, base_mmd_mat.edge_weight)

            except DivisionError:
                mat_data.offset_type = "ADD" # If there is any 0 division we automatically switch it to type ADD
            except ValueError:
                self.report({ 'ERROR' }, 'An unexpected error happened')
                # We should stop on our tracks and re-raise the exception
                raise

        if mat_data.offset_type == "ADD":
            diffuse_offset = list(work_mmd_mat.diffuse_color - base_mmd_mat.diffuse_color) + [work_mmd_mat.alpha - base_mmd_mat.alpha]
            specular_offset = list(work_mmd_mat.specular_color - base_mmd_mat.specular_color)
            edge_offset = Vector(work_mmd_mat.edge_color) - Vector(base_mmd_mat.edge_color)
            mat_data.diffuse_color = diffuse_offset
            mat_data.specular_color = specular_offset
            mat_data.shininess = work_mmd_mat.shininess - base_mmd_mat.shininess
            mat_data.ambient_color = work_mmd_mat.ambient_color - base_mmd_mat.ambient_color
            mat_data.edge_color = list(edge_offset)
            mat_data.edge_weight = work_mmd_mat.edge_weight - base_mmd_mat.edge_weight

        mat = meshObj.data.materials.pop(index=copy_idx)
        if mat.users < 1:
            bpy.data.materials.remove(mat)
        return { 'FINISHED' }

class CreateWorkMaterial(Operator):
    bl_idname = 'mmd_tools.create_work_material'
    bl_label = 'Create Work Material'
    bl_description = 'Creates a temporary material to edit this offset'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        mmd_root = root.mmd_root
        morph = mmd_root.material_morphs[mmd_root.active_morph]
        mat_data = morph.data[morph.active_data]

        meshObj = rig.findMesh(mat_data.related_mesh)
        if meshObj is None:
            self.report({ 'ERROR' }, "The model mesh can't be found")
            return { 'CANCELLED' }

        base_mat = meshObj.data.materials.get(mat_data.material, None)
        if base_mat is None:
            self.report({ 'ERROR' }, 'Material "%s" not found'%mat_data.material)
            return { 'CANCELLED' }

        work_mat_name = base_mat.name + '_temp'
        if work_mat_name in bpy.data.materials:
            self.report({ 'ERROR' }, 'Temporary material "%s" is in use'%work_mat_name)
            return { 'CANCELLED' }

        work_mat = base_mat.copy()
        work_mat.name = work_mat_name
        meshObj.data.materials.append(work_mat)
        FnMaterial.swap_materials(meshObj, base_mat.name, work_mat.name)
        base_mmd_mat = base_mat.mmd_material
        work_mmd_mat = work_mat.mmd_material
        work_mmd_mat.material_id = -1

        # Apply the offsets
        if mat_data.offset_type == "MULT":
            diffuse_offset = multiply_vector_components(base_mmd_mat.diffuse_color, mat_data.diffuse_color[0:3])
            specular_offset = multiply_vector_components(base_mmd_mat.specular_color, mat_data.specular_color)
            edge_offset = multiply_vector_components(base_mmd_mat.edge_color, mat_data.edge_color)
            ambient_offset = multiply_vector_components(base_mmd_mat.ambient_color, mat_data.ambient_color)
            work_mmd_mat.diffuse_color = diffuse_offset
            work_mmd_mat.alpha *= mat_data.diffuse_color[3]
            work_mmd_mat.specular_color = specular_offset
            work_mmd_mat.shininess *= mat_data.shininess
            work_mmd_mat.ambient_color = ambient_offset
            work_mmd_mat.edge_color = edge_offset
            work_mmd_mat.edge_weight *= mat_data.edge_weight
        elif mat_data.offset_type == "ADD":
            diffuse_offset = Vector(base_mmd_mat.diffuse_color) + Vector(mat_data.diffuse_color[0:3])
            specular_offset = Vector(base_mmd_mat.specular_color) + Vector(mat_data.specular_color)
            edge_offset = Vector(base_mmd_mat.edge_color) + Vector(mat_data.edge_color)
            ambient_offset = Vector(base_mmd_mat.ambient_color) + Vector(mat_data.ambient_color)
            work_mmd_mat.diffuse_color = list(diffuse_offset)
            work_mmd_mat.alpha += mat_data.diffuse_color[3]
            work_mmd_mat.specular_color = list(specular_offset)
            work_mmd_mat.shininess += mat_data.shininess
            work_mmd_mat.ambient_color = list(ambient_offset)
            work_mmd_mat.edge_color = list(edge_offset)
            work_mmd_mat.edge_weight += mat_data.edge_weight

        return { 'FINISHED' }

class ClearTempMaterials(Operator):
    bl_idname = 'mmd_tools.clear_temp_materials'
    bl_label = 'Clear Temp Materials'
    bl_description = 'Clears all the temporary materials'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        for meshObj in rig.meshes():
            mats_to_delete = []
            for mat in meshObj.data.materials:
                if mat and "_temp" in mat.name:
                    mats_to_delete.append(mat)
            for temp_mat in reversed(mats_to_delete):
                base_mat_name = temp_mat.name.split('_temp')[0]
                try:
                    FnMaterial.swap_materials(meshObj, temp_mat.name, base_mat_name)
                except MaterialNotFoundError:
                    self.report({ 'WARNING' } ,'Base material for %s was not found'%temp_mat.name)
                else:
                    temp_idx = meshObj.data.materials.find(temp_mat.name)
                    mat = meshObj.data.materials.pop(index=temp_idx)
                    if mat.users < 1:
                        bpy.data.materials.remove(mat)
        return { 'FINISHED' }


class ViewBoneMorph(Operator):
    bl_idname = 'mmd_tools.view_bone_morph'
    bl_label = 'View Bone Morph'
    bl_description = 'View the result of active bone morph'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root=root.mmd_root
        rig = mmd_model.Model(root)
        armature = rig.armature()
        utils.selectSingleBone(context, armature, None, True)
        morph = mmd_root.bone_morphs[mmd_root.active_morph]
        for morph_data in morph.data:
            p_bone = armature.pose.bones.get(morph_data.bone, None)
            if p_bone:
                p_bone.bone.select = True
                p_bone.location = morph_data.location
                p_bone.rotation_quaternion = morph_data.rotation
        return { 'FINISHED' }

class ApplyBoneMorph(Operator):
    bl_idname = 'mmd_tools.apply_bone_morph'
    bl_label = 'Apply Bone Morph'
    bl_description = 'Apply current pose to active bone morph'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        armature = rig.armature()
        mmd_root = root.mmd_root
        morph = mmd_root.bone_morphs[mmd_root.active_morph]
        morph.data.clear()
        def_loc = Vector((0,0,0))
        def_rot = Quaternion((1,0,0,0))
        for p_bone in armature.pose.bones:
            if p_bone.location != def_loc or p_bone.rotation_quaternion != def_rot:
                item = morph.data.add()
                item.bone = p_bone.name
                item.location = p_bone.location
                item.rotation = p_bone.rotation_quaternion
                p_bone.bone.select = True
            else:
                p_bone.bone.select = False
        return { 'FINISHED' }

class SelectRelatedBone(Operator):
    bl_idname = 'mmd_tools.select_bone_morph_offset_bone'
    bl_label = 'Select Related Bone'
    bl_description = 'Select the bone assigned to this offset in the armature'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root=root.mmd_root
        rig = mmd_model.Model(root)
        armature = rig.armature()
        morph = mmd_root.bone_morphs[mmd_root.active_morph]
        morph_data = morph.data[morph.active_data]
        utils.selectSingleBone(context, armature, morph_data.bone)
        return { 'FINISHED' }

class EditBoneOffset(Operator):
    bl_idname = 'mmd_tools.edit_bone_morph_offset'
    bl_label = 'Edit Related Bone'
    bl_description = 'Applies the location and rotation of this offset to the bone'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root=root.mmd_root
        rig = mmd_model.Model(root)
        armature = rig.armature()
        morph = mmd_root.bone_morphs[mmd_root.active_morph]
        morph_data = morph.data[morph.active_data]
        p_bone = armature.pose.bones[morph_data.bone]
        p_bone.location = morph_data.location
        p_bone.rotation_quaternion = morph_data.rotation
        utils.selectSingleBone(context, armature, p_bone.name)
        return { 'FINISHED' }

class ApplyBoneOffset(Operator):
    bl_idname = 'mmd_tools.apply_bone_morph_offset'
    bl_label = 'Apply Bone Morph Offset'
    bl_description = 'Stores the current bone location and rotation into this offset'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        mmd_root=root.mmd_root
        rig = mmd_model.Model(root)
        armature = rig.armature()
        morph = mmd_root.bone_morphs[mmd_root.active_morph]
        morph_data = morph.data[morph.active_data]
        p_bone = armature.pose.bones[morph_data.bone]
        morph_data.location = p_bone.location
        morph_data.rotation = p_bone.rotation_quaternion
        return { 'FINISHED' }


class ViewUVMorph(Operator):
    bl_idname = 'mmd_tools.view_uv_morph'
    bl_label = 'View UV Morph'
    bl_description = 'View the result of active UV morph'
    bl_options = {'PRESET'}

    with_animation = bpy.props.BoolProperty(
        name='With Animation',
        description='View the effect using Timeline window from frame 0 to frame 100 if enabled',
        default=False,
        options={'SKIP_SAVE'},
        )

    def invoke(self, context, event):
        vm = context.window_manager
        return vm.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        mmd_root = root.mmd_root
        meshObj = rig.firstMesh()
        if meshObj is None:
            self.report({ 'ERROR' }, "The model mesh can't be found")
            return { 'CANCELLED' }

        bpy.ops.mmd_tools.clear_uv_morph_view()

        selected = meshObj.select
        with bpyutils.select_object(meshObj) as data:
            morph = mmd_root.uv_morphs[mmd_root.active_morph]
            mesh = meshObj.data
            uv_textures = mesh.uv_textures

            base_uv_layers = [l for l in mesh.uv_layers if not l.name.startswith('_')]
            if morph.uv_index >= len(base_uv_layers):
                self.report({ 'ERROR' }, "Invalid uv index: %d"%morph.uv_index)
                return { 'CANCELLED' }

            uv_textures.active = uv_textures[base_uv_layers[morph.uv_index].name]
            uv_tex = uv_textures.new(name='__uv.%s'%uv_textures.active.name)
            if uv_tex is None:
                self.report({ 'ERROR' }, "Failed to create a temporary uv layer")
                return { 'CANCELLED' }

            if len(morph.data) > 0:
                base_uv_data = mesh.uv_layers.active.data
                temp_uv_data = mesh.uv_layers[uv_tex.name].data

                uv_id_map = {}
                for uv_idx, l in enumerate(mesh.loops):
                    uv_id_map.setdefault(l.vertex_index, []).append(uv_idx)

                if self.with_animation:
                    morph_name = '__uv.%s'%morph.name
                    a = mesh.animation_data_create()
                    act = bpy.data.actions.new(name=morph_name)
                    old_act = a.action
                    a.action = act

                    for data in morph.data:
                        offset = Vector(data.offset[:2]) # only use dx, dy
                        for i in uv_id_map.get(data.index, []):
                            t = temp_uv_data[i]
                            t.keyframe_insert('uv', frame=0, group=morph_name)
                            t.uv = base_uv_data[i].uv + offset
                            t.keyframe_insert('uv', frame=100, group=morph_name)

                    for fcurve in act.fcurves:
                        for kp in fcurve.keyframe_points:
                            kp.interpolation = 'LINEAR'
                        fcurve.lock = True

                    nla = a.nla_tracks.new()
                    nla.name = morph_name
                    nla.strips.new(name=morph_name, start=0, action=act)
                    a.action = old_act
                    context.scene.frame_current = 100
                else:
                    for data in morph.data:
                        offset = Vector(data.offset[:2]) # only use dx, dy
                        for i in uv_id_map.get(data.index, []):
                            temp_uv_data[i].uv = base_uv_data[i].uv + offset

            uv_textures.active = uv_tex
            uv_tex.active_render = True
        meshObj.hide = False
        meshObj.select = selected
        return { 'FINISHED' }

class ClearUVMorphView(Operator):
    bl_idname = 'mmd_tools.clear_uv_morph_view'
    bl_label = 'Clear UV Morph View'
    bl_description = 'Clear all temporary data of UV morphs'
    bl_options = {'PRESET'}

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        for m in rig.meshes():
            mesh = m.data
            uv_textures = mesh.uv_textures
            for t in uv_textures:
                if t.name.startswith('__uv.'):
                    uv_textures.remove(t)
            if len(uv_textures) > 0:
                uv_textures[0].active_render = True
                uv_textures.active_index = 0

            animation_data = mesh.animation_data
            if animation_data:
                nla_tracks = animation_data.nla_tracks
                for t in nla_tracks:
                    if t.name.startswith('__uv.'):
                        nla_tracks.remove(t)
                if animation_data.action and animation_data.action.name.startswith('__uv.'):
                    animation_data.action = None
                if animation_data.action is None and len(nla_tracks) == 0:
                    mesh.animation_data_clear()

        for act in bpy.data.actions:
            if act.name.startswith('__uv.') and act.users < 1:
                bpy.data.actions.remove(act)
        return { 'FINISHED' }

class EditUVMorph(Operator):
    bl_idname = 'mmd_tools.edit_uv_morph'
    bl_label = 'Edit UV Morph'
    bl_description = 'Edit UV morph on a temporary UV layer (use UV Editor to edit the result)'
    bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj.type != 'MESH':
            return False
        uv_textures = obj.data.uv_textures
        return uv_textures.active and uv_textures.active.name.startswith('__uv.')

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        mmd_root = root.mmd_root
        meshObj = rig.firstMesh()
        if meshObj != obj:
            self.report({ 'ERROR' }, "The model mesh can't be found")
            return { 'CANCELLED' }

        selected = meshObj.select
        with bpyutils.select_object(meshObj) as data:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(type='VERT', action='ENABLE')
            bpy.ops.mesh.reveal() # unhide all vertices
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            vertices = meshObj.data.vertices
            morph = mmd_root.uv_morphs[mmd_root.active_morph]
            for data in morph.data:
                if 0 <= data.index < len(vertices):
                    vertices[data.index].select = True
            bpy.ops.object.mode_set(mode='EDIT')
        meshObj.select = selected
        return { 'FINISHED' }

class ApplyUVMorph(Operator):
    bl_idname = 'mmd_tools.apply_uv_morph'
    bl_label = 'Apply UV Morph'
    bl_description = 'Calculate the UV offsets of selected vertices and apply to active UV morph'
    bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj.type != 'MESH':
            return False
        uv_textures = obj.data.uv_textures
        return uv_textures.active and uv_textures.active.name.startswith('__uv.')

    def execute(self, context):
        obj = context.active_object
        root = mmd_model.Model.findRoot(obj)
        rig = mmd_model.Model(root)
        mmd_root = root.mmd_root
        meshObj = rig.firstMesh()
        if meshObj != obj:
            self.report({ 'ERROR' }, "The model mesh can't be found")
            return { 'CANCELLED' }

        selected = meshObj.select
        with bpyutils.select_object(meshObj) as data:
            morph = mmd_root.uv_morphs[mmd_root.active_morph]
            morph.data.clear()
            mesh = meshObj.data

            base_uv_layers = [l for l in mesh.uv_layers if not l.name.startswith('_')]
            if morph.uv_index >= len(base_uv_layers):
                self.report({ 'ERROR' }, "Invalid uv index: %d"%morph.uv_index)
                return { 'CANCELLED' }
            base_uv_data = base_uv_layers[morph.uv_index].data
            temp_uv_data = mesh.uv_layers.active.data

            uv_id_map = {}
            for uv_idx, l in enumerate(mesh.loops):
                uv_id_map.setdefault(l.vertex_index, []).append(uv_idx)

            for bv in mesh.vertices:
                if not bv.select:
                    continue

                for uv_idx in uv_id_map.get(bv.index, []):
                    dx, dy = temp_uv_data[uv_idx].uv - base_uv_data[uv_idx].uv
                    if abs(dx) > 0.0001 or abs(dy) > 0.0001:
                        data = morph.data.add()
                        data.index = bv.index
                        data.offset = (dx, dy, 0, 0)
                        break

        meshObj.select = selected
        return { 'FINISHED' }
