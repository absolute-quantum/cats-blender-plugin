# -*- coding: utf-8 -*-

import itertools
import logging
import time
from typing import Any, Dict, Iterable, List, Optional, Set, Union

import bpy
import idprop
import mathutils
from mmd_tools_local import bpyutils
from mmd_tools_local.bpyutils import Props, SceneOp, matmul
from mmd_tools_local.core import rigid_body
from mmd_tools_local.core.bone import FnBone, MigrationFnBone
from mmd_tools_local.core.morph import FnMorph


class InvalidRigidSettingException(ValueError):
    pass


def _copy_property_group(destination: bpy.types.PropertyGroup, source: bpy.types.PropertyGroup, overwrite: bool = True, replace_name2values: Dict[str,Dict[Any,Any]] = dict()):
    destination_rna_properties = destination.bl_rna.properties
    for name in source.keys():
        is_attr = hasattr(source, name)
        value = getattr(source, name) if is_attr else source[name]
        if isinstance(value, bpy.types.PropertyGroup):
            _copy_property_group(getattr(destination, name) if is_attr else destination[name], value, overwrite=overwrite, replace_name2values=replace_name2values)
        elif isinstance(value, bpy.types.bpy_prop_collection):
            _copy_collection_property(getattr(destination, name) if is_attr else destination[name], value, overwrite=overwrite, replace_name2values=replace_name2values)
        elif isinstance(value, idprop.types.IDPropertyArray):
            pass
            # _copy_collection_property(getattr(destination, name) if is_attr else destination[name], value, overwrite=overwrite, replace_name2values=replace_name2values)
        else:
            value2values = replace_name2values.get(name)
            if value2values is not None:
                replace_value = value2values.get(value)
                if replace_value is not None:
                    value = replace_value

            if overwrite or destination_rna_properties[name].default == getattr(destination, name) if is_attr else destination[name]:
                if is_attr:
                    setattr(destination, name, value)
                else:
                    destination[name] = value


def _copy_collection_property(destination: bpy.types.bpy_prop_collection, source: bpy.types.bpy_prop_collection, overwrite: bool = True, replace_name2values: Dict[str,Dict[Any,Any]] = dict()):
    if overwrite:
        destination.clear()

    len_source = len(source)
    if len_source == 0:
        return

    source_names: Set[str] = set(source.keys())
    if len(source_names) == len_source and source[0].name != '':
        # names work
        destination_names: Set[str] = set(destination.keys())

        missing_names = source_names - destination_names

        destination_index = 0
        for name, value in source.items():
            if name in missing_names:
                new_element = destination.add()
                new_element['name'] = name

            _copy_property(destination[name], value, overwrite=overwrite, replace_name2values=replace_name2values)
            destination.move(destination.find(name), destination_index)
            destination_index += 1
    else:
        # names not work
        while len_source > len(destination):
            destination.add()

        for index, name in enumerate(source.keys()):
            _copy_property(destination[index], source[index], overwrite=True, replace_name2values=replace_name2values)


def _copy_property(destination: Union[bpy.types.PropertyGroup, bpy.types.bpy_prop_collection], source: Union[bpy.types.PropertyGroup, bpy.types.bpy_prop_collection], overwrite: bool = True, replace_name2values: Dict[str,Dict[Any,Any]] = dict()):
    if isinstance(destination, bpy.types.PropertyGroup):
        _copy_property_group(destination, source, overwrite=overwrite, replace_name2values=replace_name2values)
    elif isinstance(destination, bpy.types.bpy_prop_collection):
        _copy_collection_property(destination, source, overwrite=overwrite, replace_name2values=replace_name2values)
    else:
        raise ValueError(f'Unsupported destination: {destination}')


class FnModel:
    @staticmethod
    def copy_mmd_root(destination_root_object: bpy.types.Object, source_root_object: bpy.types.Object, overwrite: bool = True, replace_name2values: Dict[str,Dict[Any,Any]] = dict()):
        _copy_property(destination_root_object.mmd_root, source_root_object.mmd_root, overwrite=overwrite, replace_name2values=replace_name2values)

    @classmethod
    def find_root(cls, obj: bpy.types.Object) -> Optional[bpy.types.Object]:
        if not obj:
            return None
        if obj.mmd_type == 'ROOT':
            return obj
        return cls.find_root(obj.parent)

    @staticmethod
    def find_armature(root) -> Optional[bpy.types.Object]:
        return next(filter(lambda o: o.type == 'ARMATURE', root.children), None)

    @staticmethod
    def find_rigid_group(root) -> Optional[bpy.types.Object]:
        return next(filter(lambda o: o.type == 'EMPTY' and o.mmd_type == 'RIGID_GRP_OBJ', root.children), None)

    @staticmethod
    def find_joint_group(root) -> Optional[bpy.types.Object]:
        return next(filter(lambda o: o.type == 'EMPTY' and o.mmd_type == 'JOINT_GRP_OBJ', root.children), None)

    @staticmethod
    def find_temporary_group(root) -> Optional[bpy.types.Object]:
        return next(filter(lambda o: o.type == 'EMPTY' and o.mmd_type == 'TEMPORARY_GRP_OBJ', root.children), None)

    @classmethod
    def all_children(cls, obj: bpy.types.Object) -> Iterable[bpy.types.Object]:
        child: bpy.types.Object
        for child in obj.children:
            yield child
            yield from cls.all_children(child)

    @classmethod
    def filtered_children(cls, filter, obj: bpy.types.Object) -> Iterable[bpy.types.Object]:
        child: bpy.types.Object
        for child in obj.children:
            if filter(child):
                yield child
            else:
                yield from cls.filtered_children(filter, child)

    @classmethod
    def child_meshes(cls, obj: bpy.types.Object) -> Iterable[bpy.types.Object]:
        return cls.filtered_children(lambda x: x.type == 'MESH' and x.mmd_type == 'NONE', obj)

    @staticmethod
    def is_rigid_body_object(obj):
        return obj and obj.mmd_type == 'RIGID_BODY'

    @staticmethod
    def is_joint_object(obj):
        return obj and obj.mmd_type == 'JOINT'

    @staticmethod
    def is_temporary_object(obj):
        return obj and obj.mmd_type in {'TRACK_TARGET', 'NON_COLLISION_CONSTRAINT', 'SPRING_CONSTRAINT', 'SPRING_GOAL'}

    @staticmethod
    def get_rigid_body_size(obj):
        assert(obj.mmd_type == 'RIGID_BODY')

        x0, y0, z0 = obj.bound_box[0]
        x1, y1, z1 = obj.bound_box[6]
        assert(x1 >= x0 and y1 >= y0 and z1 >= z0)

        shape = obj.mmd_rigid.shape
        if shape == 'SPHERE':
            radius = (z1 - z0)/2
            return (radius, 0.0, 0.0)
        elif shape == 'BOX':
            x, y, z = (x1 - x0)/2, (y1 - y0)/2, (z1 - z0)/2
            return (x, y, z)
        elif shape == 'CAPSULE':
            diameter = (x1 - x0)
            radius = diameter/2
            height = abs((z1 - z0) - diameter)
            return (radius, height, 0.0)
        else:
            raise Exception('Invalid shape type.')

    @staticmethod
    def join_models(parent_root_object: bpy.types.Object, child_root_objects: List[bpy.types.Object]):
        parent_model = Model(parent_root_object)
        parent_rigid_group_object = parent_model.rigidGroupObject()
        parent_joint_group_object = parent_model.jointGroupObject()

        parent_armature_object = parent_model.armature()
        bpy.ops.object.transform_apply({
            'active_object': parent_armature_object,
            'selected_editable_objects': [parent_armature_object],
        }, location=True, rotation=True, scale=True)

        child_root_object: bpy.types.Object
        for child_root_object in child_root_objects:
            child_model = Model(child_root_object)
            child_armature_object = child_model.armature()
            child_armature_matrix = child_armature_object.matrix_parent_inverse.copy()

            bpy.ops.object.transform_apply({
                'active_object': child_armature_object,
                'selected_editable_objects': [child_armature_object],
            }, location=True, rotation=True, scale=True)

            # replace mesh armature modifier.object
            mesh: bpy.types.Object
            for mesh in FnModel.child_meshes(child_armature_object):
                bpy.ops.object.transform_apply({
                    'active_object': mesh,
                    'selected_editable_objects': [mesh],
                }, location=True, rotation=True, scale=True)

            # join armatures
            bpy.ops.object.join({
                'active_object': parent_armature_object,
                'selected_editable_objects': [parent_armature_object, child_armature_object],
            })

            for mesh in FnModel.child_meshes(parent_armature_object):
                armature_modifier: bpy.types.ArmatureModifier = (
                    mesh.modifiers['mmd_bone_order_override'] if 'mmd_bone_order_override' in mesh.modifiers else
                    mesh.modifiers.new('mmd_bone_order_override', 'ARMATURE')
                )
                if armature_modifier.object is None:
                    armature_modifier.object = parent_armature_object
                    mesh.matrix_parent_inverse = child_armature_matrix

            child_model = Model(child_root_object)
            if child_model.hasRigidGroupObject():
                bpy.ops.object.parent_set({
                    'object': parent_rigid_group_object,
                    'selected_editable_objects': [parent_rigid_group_object, *child_model.rigidBodies()],
                }, type='OBJECT', keep_transform=True)
                bpy.data.objects.remove(child_model.rigidGroupObject())

            if child_model.hasJointGroupObject():
                bpy.ops.object.parent_set({
                    'object': parent_joint_group_object,
                    'selected_editable_objects': [parent_joint_group_object, *child_model.joints()],
                }, type='OBJECT', keep_transform=True)
                bpy.data.objects.remove(child_model.jointGroupObject())

            if child_model.hasTemporaryGroupObject():
                bpy.ops.object.parent_set({
                    'object': parent_model.temporaryGroupObject(),
                    'selected_editable_objects': [parent_model.temporaryGroupObject(), *child_model.temporaryObjects()],
                }, type='OBJECT', keep_transform=True)

                temporary_group_object = child_model.temporaryGroupObject()
                for obj in list(FnModel.all_children(temporary_group_object)):
                    bpy.data.objects.remove(obj)
                bpy.data.objects.remove(temporary_group_object)

            FnModel.copy_mmd_root(parent_root_object, child_root_object, overwrite=False)

            # Remove unused objects from child models
            if len(child_root_object.children) == 0:
                bpy.data.objects.remove(child_root_object)

    @staticmethod
    def _add_armature_modifier(mesh_object: bpy.types.Object, armature_object: bpy.types.Object) -> bpy.types.ArmatureModifier:
        if any(m.type == 'ARMATURE' for m in mesh_object.modifiers):
            # already has armature modifier.
            return

        modifier: bpy.types.ArmatureModifier = mesh_object.modifiers.new(name='Armature', type='ARMATURE')
        modifier.object = armature_object
        modifier.use_vertex_groups = True
        modifier.name = 'mmd_bone_order_override'

        return modifier

    @staticmethod
    def attach_meshes(parent_root_object: bpy.types.Object, mesh_objects: Iterable[bpy.types.Object], add_armature_modifier: bool):
        armature_object: bpy.types.Object = FnModel.find_armature(parent_root_object)

        def __get_root_object(obj: bpy.types.Object) -> bpy.types.Object:
            if obj.parent is None:
                return obj
            return __get_root_object(obj.parent)

        for mesh_object in mesh_objects:
            if mesh_object.type != 'MESH':
                continue
            if mesh_object.mmd_type != 'NONE':
                continue
            if FnModel.find_root(mesh_object) is not None:
                continue

            mesh_root_object = __get_root_object(mesh_object)
            original_matrix_world = mesh_root_object.matrix_world
            mesh_root_object.parent_type = 'OBJECT'
            mesh_root_object.parent = armature_object
            mesh_root_object.matrix_world = original_matrix_world

            if add_armature_modifier:
                FnModel._add_armature_modifier(mesh_object, armature_object)


# SUPPORT_UNTIL: 4.3 LTS
def isRigidBodyObject(obj):
    return FnModel.is_rigid_body_object(obj)

# SUPPORT_UNTIL: 4.3 LTS
def isJointObject(obj):
    return FnModel.is_joint_object(obj)

# SUPPORT_UNTIL: 4.3 LTS
def isTemporaryObject(obj):
    return FnModel.is_temporary_object(obj)

# SUPPORT_UNTIL: 4.3 LTS
def getRigidBodySize(obj):
    return FnModel.get_rigid_body_size(obj)


class Model:
    def __init__(self, root_obj):
        if root_obj.mmd_type != 'ROOT':
            raise ValueError('must be MMD ROOT type object')
        self.__root: bpy.types.Object = getattr(root_obj, 'original', root_obj)
        self.__arm: Optional[bpy.types.Object] = None
        self.__rigid_grp: Optional[bpy.types.Object] = None
        self.__joint_grp: Optional[bpy.types.Object] = None
        self.__temporary_grp: Optional[bpy.types.Object] = None

    @staticmethod
    def create(name, name_e='', scale=1, obj_name=None, armature=None, add_root_bone=False):
        scene = SceneOp(bpy.context)
        if obj_name is None:
            obj_name = name

        root = bpy.data.objects.new(name=obj_name, object_data=None)
        root.mmd_type = 'ROOT'
        root.mmd_root.name = name
        root.mmd_root.name_e = name_e
        setattr(root, Props.empty_display_size, scale/0.2)
        scene.link_object(root)

        armObj = armature
        if armObj:
            m = armObj.matrix_world
            armObj.parent_type = 'OBJECT'
            armObj.parent = root
            #armObj.matrix_world = m
            root.matrix_world = m
            armObj.matrix_local.identity()
        else:
            arm = bpy.data.armatures.new(name=obj_name)
            armObj = bpy.data.objects.new(name=obj_name+'_arm', object_data=arm)
            armObj.parent = root
            scene.link_object(armObj)
        armObj.lock_rotation = armObj.lock_location = armObj.lock_scale = [True, True, True]
        setattr(armObj, Props.show_in_front, True)
        setattr(armObj, Props.display_type, 'WIRE')

        if add_root_bone:
            bone_name = u'全ての親'
            with bpyutils.edit_object(armObj) as data:
                bone = data.edit_bones.new(name=bone_name)
                bone.head = [0.0, 0.0, 0.0]
                bone.tail = [0.0, 0.0, getattr(root, Props.empty_display_size)]
            armObj.pose.bones[bone_name].mmd_bone.name_j = bone_name
            armObj.pose.bones[bone_name].mmd_bone.name_e = 'Root'

        bpyutils.select_object(root)
        return Model(root)

    @classmethod
    def findRoot(cls, obj):
        return FnModel.find_root(obj)

    def initialDisplayFrames(self, reset=True):
        frames = self.__root.mmd_root.display_item_frames
        if reset and len(frames):
            self.__root.mmd_root.active_display_item_frame = 0
            frames.clear()

        frame_root = frames.get('Root', None) or frames.add()
        frame_root.name = 'Root'
        frame_root.name_e = 'Root'
        frame_root.is_special = True

        frame_facial = frames.get(u'表情', None) or frames.add()
        frame_facial.name = u'表情'
        frame_facial.name_e = 'Facial'
        frame_facial.is_special = True

        arm = self.armature()
        if arm and len(arm.data.bones) and len(frame_root.data) < 1:
            item = frame_root.data.add()
            item.type = 'BONE'
            item.name = arm.data.bones[0].name

        if not reset:
            frames.move(frames.find('Root'), 0)
            frames.move(frames.find(u'表情'), 1)

    @property
    def morph_slider(self):
        return FnMorph.get_morph_slider(self)

    def loadMorphs(self):
        FnMorph.load_morphs(self)

    def createRigidBodyPool(self, counts: int) -> List[bpy.types.Object]:
        if counts < 1:
            return []
        obj = bpyutils.createObject(name='Rigidbody', object_data=bpy.data.meshes.new(name='Rigidbody'))
        obj.parent = self.rigidGroupObject()
        obj.mmd_type = 'RIGID_BODY'
        obj.rotation_mode = 'YXZ'
        setattr(obj, Props.display_type, 'SOLID')
        obj.show_transparent = True
        obj.hide_render = True
        if hasattr(obj, 'display'):
            obj.display.show_shadows = False
        if hasattr(obj, 'cycles_visibility'):
            for attr_name in ('camera', 'diffuse', 'glossy', 'scatter', 'shadow', 'transmission'):
                if hasattr(obj.cycles_visibility, attr_name):
                    setattr(obj.cycles_visibility, attr_name, False)

        if bpy.app.version < (2, 71, 0):
            obj.mmd_rigid.shape = 'BOX'
            obj.mmd_rigid.size = (1, 1, 1)
        bpy.ops.rigidbody.object_add(type='ACTIVE')
        if counts == 1:
            return [obj]
        return bpyutils.duplicateObject(obj, counts)

    def createRigidBody(self, **kwargs):
        ''' Create a object for MMD rigid body dynamics.
        ### Parameters ###
         @param shape_type the shape type.
         @param location location of the rigid body object.
         @param rotation rotation of the rigid body object.
         @param size
         @param dynamics_type the type of dynamics mode. (STATIC / DYNAMIC / DYNAMIC2)
         @param collision_group_number
         @param collision_group_mask list of boolean values. (length:16)
         @param name Object name (Optional)
         @param name_e English object name (Optional)
         @param bone
        '''

        shape_type = kwargs['shape_type']
        location = kwargs['location']
        rotation = kwargs['rotation']
        size = kwargs['size']
        dynamics_type = kwargs['dynamics_type']
        collision_group_number = kwargs.get('collision_group_number')
        collision_group_mask = kwargs.get('collision_group_mask')
        name = kwargs.get('name')
        name_e = kwargs.get('name_e')
        bone = kwargs.get('bone')

        friction = kwargs.get('friction')
        mass = kwargs.get('mass')
        angular_damping = kwargs.get('angular_damping')
        linear_damping = kwargs.get('linear_damping')
        bounce = kwargs.get('bounce')

        obj: Optional[bpy.types.Object] = kwargs.get('obj', None)
        if obj is None:
            obj, = self.createRigidBodyPool(1)

        obj.location = location
        obj.rotation_euler = rotation

        obj.mmd_rigid.shape = rigid_body.collisionShape(shape_type)
        obj.mmd_rigid.size = size
        obj.mmd_rigid.type = str(dynamics_type) if dynamics_type in range(3) else '1'

        if collision_group_number is not None:
            obj.mmd_rigid.collision_group_number = collision_group_number
        if collision_group_mask is not None:
            obj.mmd_rigid.collision_group_mask = collision_group_mask
        if name is not None:
            obj.name = name
            obj.mmd_rigid.name_j = name
        if name_e is not None:
            obj.mmd_rigid.name_e = name_e

        obj.mmd_rigid.bone = bone if bone else ''

        rb = obj.rigid_body
        if friction is not None:
            rb.friction = friction
        if mass is not None:
            rb.mass = mass
        if angular_damping is not None:
            rb.angular_damping = angular_damping
        if linear_damping is not None:
            rb.linear_damping = linear_damping
        if bounce:
            rb.restitution = bounce

        obj.select = False
        return obj

    def createJointPool(self, counts):
        if counts < 1:
            return []
        obj = bpyutils.createObject(name='Joint', object_data=None)
        obj.parent = self.jointGroupObject()
        obj.mmd_type = 'JOINT'
        obj.rotation_mode = 'YXZ'
        setattr(obj, Props.empty_display_type, 'ARROWS')
        setattr(obj, Props.empty_display_size, 0.1*getattr(self.__root, Props.empty_display_size))
        obj.hide_render = True

        if bpy.ops.rigidbody.world_add.poll():
            bpy.ops.rigidbody.world_add()
        bpy.ops.rigidbody.constraint_add(type='GENERIC_SPRING')
        rbc = obj.rigid_body_constraint
        rbc.disable_collisions = False
        rbc.use_limit_ang_x = True
        rbc.use_limit_ang_y = True
        rbc.use_limit_ang_z = True
        rbc.use_limit_lin_x = True
        rbc.use_limit_lin_y = True
        rbc.use_limit_lin_z = True
        rbc.use_spring_x = True
        rbc.use_spring_y = True
        rbc.use_spring_z = True
        if hasattr(rbc, 'use_spring_ang_x'):
            rbc.use_spring_ang_x = True
            rbc.use_spring_ang_y = True
            rbc.use_spring_ang_z = True
        if counts == 1:
            return [obj]
        return bpyutils.duplicateObject(obj, counts)

    def createJoint(self, **kwargs):
        ''' Create a joint object for MMD rigid body dynamics.
        ### Parameters ###
         @param shape_type the shape type.
         @param location location of the rigid body object.
         @param rotation rotation of the rigid body object.
         @param size
         @param dynamics_type the type of dynamics mode. (STATIC / DYNAMIC / DYNAMIC2)
         @param collision_group_number
         @param collision_group_mask list of boolean values. (length:16)
         @param name Object name
         @param name_e English object name (Optional)
         @param bone
        '''

        location = kwargs['location']
        rotation = kwargs['rotation']

        rigid_a = kwargs['rigid_a']
        rigid_b = kwargs['rigid_b']

        max_loc = kwargs['maximum_location']
        min_loc = kwargs['minimum_location']
        max_rot = kwargs['maximum_rotation']
        min_rot = kwargs['minimum_rotation']
        spring_angular = kwargs['spring_angular']
        spring_linear = kwargs['spring_linear']

        name = kwargs['name']
        name_e = kwargs.get('name_e')

        obj = kwargs.get('obj', None)
        if obj is None:
            obj, = self.createJointPool(1)

        obj.name = 'J.' + name
        obj.mmd_joint.name_j = name
        if name_e is not None:
            obj.mmd_joint.name_e = name_e

        obj.location = location
        obj.rotation_euler = rotation

        rbc = obj.rigid_body_constraint

        rbc.object1 = rigid_a
        rbc.object2 = rigid_b

        rbc.limit_lin_x_upper = max_loc[0]
        rbc.limit_lin_y_upper = max_loc[1]
        rbc.limit_lin_z_upper = max_loc[2]

        rbc.limit_lin_x_lower = min_loc[0]
        rbc.limit_lin_y_lower = min_loc[1]
        rbc.limit_lin_z_lower = min_loc[2]

        rbc.limit_ang_x_upper = max_rot[0]
        rbc.limit_ang_y_upper = max_rot[1]
        rbc.limit_ang_z_upper = max_rot[2]

        rbc.limit_ang_x_lower = min_rot[0]
        rbc.limit_ang_y_lower = min_rot[1]
        rbc.limit_ang_z_lower = min_rot[2]

        obj.mmd_joint.spring_linear = spring_linear
        obj.mmd_joint.spring_angular = spring_angular

        obj.select = False
        return obj

    def create_ik_constraint(self, bone, ik_target):
        """ create IK constraint

         Args:
             bone: A pose bone to add a IK constraint
             id_target: A pose bone for IK target

         Returns:
             The bpy.types.KinematicConstraint object created. It is set target
             and subtarget options.

        """
        ik_target_name = ik_target.name
        ik_const = bone.constraints.new('IK')
        ik_const.target = self.__arm
        ik_const.subtarget = ik_target_name
        return ik_const

    def allObjects(self, obj: Optional[bpy.types.Object] = None) -> Iterable[bpy.types.Object]:
        if obj is None:
            obj: bpy.types.Object = self.__root
        yield obj
        yield from FnModel.all_children(obj)

    def rootObject(self):
        return self.__root

    def armature(self):
        if self.__arm is None:
            self.__arm = FnModel.find_armature(self.__root)
        return self.__arm

    def hasRigidGroupObject(self):
        return FnModel.find_rigid_group(self.__root) is not None

    def rigidGroupObject(self):
        if self.__rigid_grp is None:
            self.__rigid_grp = FnModel.find_rigid_group(self.__root)
            if self.__rigid_grp is None:
                rigids = bpy.data.objects.new(name='rigidbodies', object_data=None)
                SceneOp(bpy.context).link_object(rigids)
                rigids.mmd_type = 'RIGID_GRP_OBJ'
                rigids.parent = self.__root
                rigids.hide = rigids.hide_select = True
                rigids.lock_rotation = rigids.lock_location = rigids.lock_scale = [True, True, True]
                self.__rigid_grp = rigids
        return self.__rigid_grp

    def hasJointGroupObject(self):
        return FnModel.find_joint_group(self.__root) is not None

    def jointGroupObject(self):
        if self.__joint_grp is None:
            self.__joint_grp = FnModel.find_joint_group(self.__root)
            if self.__joint_grp is None:
                joints = bpy.data.objects.new(name='joints', object_data=None)
                SceneOp(bpy.context).link_object(joints)
                joints.mmd_type = 'JOINT_GRP_OBJ'
                joints.parent = self.__root
                joints.hide = joints.hide_select = True
                joints.lock_rotation = joints.lock_location = joints.lock_scale = [True, True, True]
                self.__joint_grp = joints
        return self.__joint_grp

    def hasTemporaryGroupObject(self):
        return FnModel.find_temporary_group(self.__root) is not None

    def temporaryGroupObject(self):
        if self.__temporary_grp is None:
            self.__temporary_grp = FnModel.find_temporary_group(self.__root)
            if self.__temporary_grp is None:
                temporarys = bpy.data.objects.new(name='temporary', object_data=None)
                SceneOp(bpy.context).link_object(temporarys)
                temporarys.mmd_type = 'TEMPORARY_GRP_OBJ'
                temporarys.parent = self.__root
                temporarys.hide = temporarys.hide_select = True
                temporarys.lock_rotation = temporarys.lock_location = temporarys.lock_scale = [True, True, True]
                self.__temporary_grp = temporarys
        return self.__temporary_grp

    def meshes(self):
        arm = self.armature()
        if arm is None:
            return []
        return FnModel.child_meshes(arm)

    def attachMeshes(self, meshes: Iterable[bpy.types.Object], add_armature_modifier: bool = True):
        FnModel.attach_meshes(self.rootObject(), meshes, add_armature_modifier)

    def firstMesh(self):
        for i in self.meshes():
            return i
        return None

    def findMesh(self, mesh_name):
        """
        Helper method to find a mesh by name
        """
        if mesh_name == '':
            return None
        for mesh in self.meshes():
            if mesh.name == mesh_name or mesh.data.name == mesh_name:
                return mesh
        return None

    def findMeshByIndex(self, index):
        """
        Helper method to find the mesh by index
        """
        if index < 0:
            return None
        for i, mesh in enumerate(self.meshes()):
            if i == index:
                return mesh
        return None

    def getMeshIndex(self, mesh_name):
        """
        Helper method to get the index of a mesh. Returns -1 if not found
        """
        if mesh_name == '':
            return -1
        for i, mesh in enumerate(self.meshes()):
            if mesh.name == mesh_name or mesh.data.name == mesh_name:
                return i
        return -1

    def rigidBodies(self):
        if self.__root.mmd_root.is_built:
            return itertools.chain(FnModel.filtered_children(isRigidBodyObject, self.armature()), FnModel.filtered_children(isRigidBodyObject, self.rigidGroupObject()))
        return FnModel.filtered_children(isRigidBodyObject, self.rigidGroupObject())

    def joints(self):
        return FnModel.filtered_children(isJointObject, self.jointGroupObject())

    def temporaryObjects(self, rigid_track_only=False):
        rigid_body_objects = FnModel.filtered_children(isTemporaryObject, self.rigidGroupObject()) if self.hasRigidGroupObject() else []

        if rigid_track_only:
            return rigid_body_objects
        return itertools.chain(rigid_body_objects, FnModel.filtered_children(isTemporaryObject, self.temporaryGroupObject()))

    def materials(self):
        """
        Helper method to list all materials in all meshes
        """
        material_list = []
        for mesh in self.meshes():
            for mat in mesh.data.materials:
                if mat not in material_list:
                    # control the case of a material shared among different meshes
                    material_list.append(mat)
        return material_list

    def renameBone(self, old_bone_name, new_bone_name):
        if old_bone_name == new_bone_name:
            return
        armature = self.armature()
        bone = armature.pose.bones[old_bone_name]
        bone.name = new_bone_name
        new_bone_name = bone.name

        mmd_root = self.rootObject().mmd_root
        for frame in mmd_root.display_item_frames:
            for item in frame.data:
                if item.type == 'BONE' and item.name == old_bone_name:
                    item.name = new_bone_name
        for mesh in self.meshes():
            if old_bone_name in mesh.vertex_groups:
                mesh.vertex_groups[old_bone_name].name = new_bone_name

    def build(self, non_collision_distance_scale, collision_margin):
        rigidbody_world_enabled = rigid_body.setRigidBodyWorldEnabled(False)
        if self.__root.mmd_root.is_built:
            self.clean()
        self.__root.mmd_root.is_built = True
        logging.info('****************************************')
        logging.info(' Build rig')
        logging.info('****************************************')
        start_time = time.time()
        self.__preBuild()
        self.buildRigids(non_collision_distance_scale, collision_margin)
        self.buildJoints()
        self.__postBuild()
        logging.info(' Finished building in %f seconds.', time.time() - start_time)
        rigid_body.setRigidBodyWorldEnabled(rigidbody_world_enabled)

    def clean(self):
        rigidbody_world_enabled = rigid_body.setRigidBodyWorldEnabled(False)
        logging.info('****************************************')
        logging.info(' Clean rig')
        logging.info('****************************************')
        start_time = time.time()

        pose_bones = []
        arm = self.armature()
        if arm is not None:
            pose_bones = arm.pose.bones
        for i in pose_bones:
            if 'mmd_tools_rigid_track' in i.constraints:
                const = i.constraints['mmd_tools_rigid_track']
                i.constraints.remove(const)

        rigid_track_counts = 0
        for i in self.rigidBodies():
            rigid_type = int(i.mmd_rigid.type)
            if 'mmd_tools_rigid_parent' not in i.constraints:
                rigid_track_counts += 1
                logging.info('%3d# Create a "CHILD_OF" constraint for %s', rigid_track_counts, i.name)
                i.mmd_rigid.bone = i.mmd_rigid.bone
            relation = i.constraints['mmd_tools_rigid_parent']
            relation.mute = True
            if rigid_type == rigid_body.MODE_STATIC:
                i.parent_type = 'OBJECT'
                i.parent = self.rigidGroupObject()
            elif rigid_type in [rigid_body.MODE_DYNAMIC, rigid_body.MODE_DYNAMIC_BONE]:
                arm = relation.target
                bone_name = relation.subtarget
                if arm is not None and bone_name != '':
                    for c in arm.pose.bones[bone_name].constraints:
                        if c.type == 'IK':
                            c.mute = False
            self.__restoreTransforms(i)

        for i in self.joints():
            self.__restoreTransforms(i)

        self.__removeTemporaryObjects()

        arm = self.armature()
        if arm is not None:  # update armature
            arm.update_tag()
            bpy.context.scene.frame_set(bpy.context.scene.frame_current)

        mmd_root = self.rootObject().mmd_root
        if mmd_root.show_temporary_objects:
            mmd_root.show_temporary_objects = False
        logging.info(' Finished cleaning in %f seconds.', time.time() - start_time)
        mmd_root.is_built = False
        rigid_body.setRigidBodyWorldEnabled(rigidbody_world_enabled)

    def __removeTemporaryObjects(self):
        if bpy.app.version < (2, 78, 0):
            self.__removeChildrenOfTemporaryGroupObject()  # for speeding up only
            for i in self.temporaryObjects():
                bpy.context.scene.objects.unlink(i)
                bpy.data.objects.remove(i)
        elif bpy.app.version < (2, 80, 0):
            for i in self.temporaryObjects():
                bpy.data.objects.remove(i, do_unlink=True)
        elif bpy.app.version < (2, 81, 0):
            tmp_objs = tuple(self.temporaryObjects())
            for i in tmp_objs:
                for c in i.users_collection:
                    c.objects.unlink(i)
            bpy.ops.object.delete({'selected_objects': tmp_objs, 'active_object': self.rootObject()})
            for i in tmp_objs:
                if i.users < 1:
                    bpy.data.objects.remove(i)
        else:
            bpy.ops.object.delete({'selected_objects': tuple(self.temporaryObjects()), 'active_object': self.rootObject()})

    def __removeChildrenOfTemporaryGroupObject(self):
        tmp_grp_obj = self.temporaryGroupObject()
        tmp_cnt = len(tmp_grp_obj.children)
        if tmp_cnt == 0:
            return
        logging.debug(' Removing %d children of temporary group object', tmp_cnt)
        start_time = time.time()
        total_cnt = len(bpy.data.objects)
        layer_index = bpy.context.scene.active_layer
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass
        for i in bpy.context.selected_objects:
            i.select = False
        for i in tmp_grp_obj.children:
            i.hide_select = i.hide = False
            i.select = i.layers[layer_index] = True
        assert(len(bpy.context.selected_objects) == tmp_cnt)
        bpy.ops.object.delete()
        assert(len(bpy.data.objects) == total_cnt - tmp_cnt)
        logging.debug('   - Done in %f seconds.', time.time() - start_time)

    def __restoreTransforms(self, obj):
        for attr in ('location', 'rotation_euler'):
            attr_name = '__backup_%s__' % attr
            val = obj.get(attr_name, None)
            if val is not None:
                setattr(obj, attr, val)
                del obj[attr_name]

    def __backupTransforms(self, obj):
        for attr in ('location', 'rotation_euler'):
            attr_name = '__backup_%s__' % attr
            if attr_name in obj:  # should not happen in normal build/clean cycle
                continue
            obj[attr_name] = getattr(obj, attr, None)

    def __preBuild(self):
        self.__fake_parent_map = {}
        self.__rigid_body_matrix_map = {}
        self.__empty_parent_map = {}

        no_parents = []
        for i in self.rigidBodies():
            self.__backupTransforms(i)
            # mute relation
            relation = i.constraints['mmd_tools_rigid_parent']
            relation.mute = True
            # mute IK
            if int(i.mmd_rigid.type) in [rigid_body.MODE_DYNAMIC, rigid_body.MODE_DYNAMIC_BONE]:
                arm = relation.target
                bone_name = relation.subtarget
                if arm is not None and bone_name != '':
                    for c in arm.pose.bones[bone_name].constraints:
                        if c.type == 'IK':
                            c.mute = True
                            c.influence = c.influence  # trigger update
                else:
                    no_parents.append(i)
        # update changes of armature constraints
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)

        parented = []
        for i in self.joints():
            self.__backupTransforms(i)
            rbc = i.rigid_body_constraint
            if rbc is None:
                continue
            obj1, obj2 = rbc.object1, rbc.object2
            if obj2 in no_parents:
                if obj1 not in no_parents and obj2 not in parented:
                    self.__fake_parent_map.setdefault(obj1, []).append(obj2)
                    parented.append(obj2)
            elif obj1 in no_parents:
                if obj1 not in parented:
                    self.__fake_parent_map.setdefault(obj2, []).append(obj1)
                    parented.append(obj1)

        #assert(len(no_parents) == len(parented))

    def __postBuild(self):
        self.__fake_parent_map = None
        self.__rigid_body_matrix_map = None

        # update changes
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)

        # parenting empty to rigid object at once for speeding up
        for empty, rigid_obj in self.__empty_parent_map.items():
            matrix_world = empty.matrix_world
            empty.parent = rigid_obj
            empty.matrix_world = matrix_world
        self.__empty_parent_map = None

        arm = self.armature()
        if arm:
            for p_bone in arm.pose.bones:
                c = p_bone.constraints.get('mmd_tools_rigid_track', None)
                if c:
                    c.mute = False

    def updateRigid(self, rigid_obj: bpy.types.Object, collision_margin: float):
        assert(rigid_obj.mmd_type == 'RIGID_BODY')
        rb = rigid_obj.rigid_body
        if rb is None:
            return

        rigid = rigid_obj.mmd_rigid
        rigid_type = int(rigid.type)
        relation = rigid_obj.constraints['mmd_tools_rigid_parent']

        if relation.target is None:
            relation.target = self.armature()

        arm = relation.target
        if relation.subtarget not in arm.pose.bones:
            bone_name = ''
        else:
            bone_name = relation.subtarget

        if rigid_type == rigid_body.MODE_STATIC:
            rb.kinematic = True
        else:
            rb.kinematic = False

        if collision_margin == 0.0:
            rb.use_margin = False
        else:
            rb.use_margin = True
            rb.collision_margin = collision_margin

        if arm is not None and bone_name != '':
            target_bone = arm.pose.bones[bone_name]

            if rigid_type == rigid_body.MODE_STATIC:
                m = matmul(target_bone.matrix, target_bone.bone.matrix_local.inverted())
                self.__rigid_body_matrix_map[rigid_obj] = m
                orig_scale = rigid_obj.scale.copy()
                to_matrix_world = matmul(rigid_obj.matrix_world, rigid_obj.matrix_local.inverted())
                matrix_world = matmul(to_matrix_world, matmul(m, rigid_obj.matrix_local))
                rigid_obj.parent = arm
                rigid_obj.parent_type = 'BONE'
                rigid_obj.parent_bone = bone_name
                rigid_obj.matrix_world = matrix_world
                rigid_obj.scale = orig_scale
                #relation.mute = False
                #relation.inverse_matrix = matmul(arm.matrix_world, target_bone.bone.matrix_local).inverted()
                fake_children = self.__fake_parent_map.get(rigid_obj, None)
                if fake_children:
                    for fake_child in fake_children:
                        logging.debug('          - fake_child: %s', fake_child.name)
                        t, r, s = matmul(m, fake_child.matrix_local).decompose()
                        fake_child.location = t
                        fake_child.rotation_euler = r.to_euler(fake_child.rotation_mode)

            elif rigid_type in [rigid_body.MODE_DYNAMIC, rigid_body.MODE_DYNAMIC_BONE]:
                m = matmul(target_bone.matrix, target_bone.bone.matrix_local.inverted())
                self.__rigid_body_matrix_map[rigid_obj] = m
                t, r, s = matmul(m, rigid_obj.matrix_local).decompose()
                rigid_obj.location = t
                rigid_obj.rotation_euler = r.to_euler(rigid_obj.rotation_mode)
                fake_children = self.__fake_parent_map.get(rigid_obj, None)
                if fake_children:
                    for fake_child in fake_children:
                        logging.debug('          - fake_child: %s', fake_child.name)
                        t, r, s = matmul(m, fake_child.matrix_local).decompose()
                        fake_child.location = t
                        fake_child.rotation_euler = r.to_euler(fake_child.rotation_mode)

                if 'mmd_tools_rigid_track' not in target_bone.constraints:
                    empty = bpy.data.objects.new(name='mmd_bonetrack', object_data=None)
                    SceneOp(bpy.context).link_object(empty)
                    empty.matrix_world = target_bone.matrix
                    setattr(empty, Props.empty_display_type, 'ARROWS')
                    setattr(empty, Props.empty_display_size, 0.1*getattr(self.__root, Props.empty_display_size))
                    empty.mmd_type = 'TRACK_TARGET'
                    empty.hide = True
                    empty.parent = self.temporaryGroupObject()

                    rigid_obj.mmd_rigid.bone = bone_name
                    rigid_obj.constraints.remove(relation)

                    self.__empty_parent_map[empty] = rigid_obj

                    const_type = ('COPY_TRANSFORMS', 'COPY_ROTATION')[rigid_type-1]
                    const = target_bone.constraints.new(const_type)
                    const.mute = True
                    const.name = 'mmd_tools_rigid_track'
                    const.target = empty
                else:
                    empty = target_bone.constraints['mmd_tools_rigid_track'].target
                    ori_rigid_obj = self.__empty_parent_map[empty]
                    ori_rb = ori_rigid_obj.rigid_body
                    if ori_rb and rb.mass > ori_rb.mass:
                        logging.debug('        * Bone (%s): change target from [%s] to [%s]',
                                      target_bone.name, ori_rigid_obj.name, rigid_obj.name)
                        # re-parenting
                        rigid_obj.mmd_rigid.bone = bone_name
                        rigid_obj.constraints.remove(relation)
                        self.__empty_parent_map[empty] = rigid_obj
                        # revert change
                        ori_rigid_obj.mmd_rigid.bone = bone_name
                    else:
                        logging.debug('        * Bone (%s): track target [%s]',
                                      target_bone.name, ori_rigid_obj.name)

        rb.collision_shape = rigid.shape

    def __getRigidRange(self, obj):
        return (mathutils.Vector(obj.bound_box[0]) - mathutils.Vector(obj.bound_box[6])).length

    def __createNonCollisionConstraint(self, nonCollisionJointTable):
        total_len = len(nonCollisionJointTable)
        if total_len < 1:
            return

        start_time = time.time()
        logging.debug('-'*60)
        logging.debug(' creating ncc, counts: %d', total_len)

        ncc_obj = bpyutils.createObject(name='ncc', object_data=None)
        ncc_obj.location = [0, 0, 0]
        setattr(ncc_obj, Props.empty_display_type, 'ARROWS')
        setattr(ncc_obj, Props.empty_display_size, 0.5*getattr(self.__root, Props.empty_display_size))
        ncc_obj.mmd_type = 'NON_COLLISION_CONSTRAINT'
        ncc_obj.hide_render = True
        ncc_obj.parent = self.temporaryGroupObject()

        bpy.ops.rigidbody.constraint_add(type='GENERIC')
        rb = ncc_obj.rigid_body_constraint
        rb.disable_collisions = True

        ncc_objs = bpyutils.duplicateObject(ncc_obj, total_len)
        logging.debug(' created %d ncc.', len(ncc_objs))

        for ncc_obj, pair in zip(ncc_objs, nonCollisionJointTable):
            rbc = ncc_obj.rigid_body_constraint
            rbc.object1, rbc.object2 = pair
            ncc_obj.hide = ncc_obj.hide_select = True
        logging.debug(' finish in %f seconds.', time.time() - start_time)
        logging.debug('-'*60)

    def buildRigids(self, non_collision_distance_scale, collision_margin):
        logging.debug('--------------------------------')
        logging.debug(' Build riggings of rigid bodies')
        logging.debug('--------------------------------')
        rigid_objects = list(self.rigidBodies())
        rigid_object_groups = [[] for i in range(16)]
        for i in rigid_objects:
            rigid_object_groups[i.mmd_rigid.collision_group_number].append(i)

        jointMap = {}
        for joint in self.joints():
            rbc = joint.rigid_body_constraint
            if rbc is None:
                continue
            rbc.disable_collisions = False
            jointMap[frozenset((rbc.object1, rbc.object2))] = joint

        logging.info('Creating non collision constraints')
        # create non collision constraints
        nonCollisionJointTable = []
        non_collision_pairs = set()
        rigid_object_cnt = len(rigid_objects)
        for obj_a in rigid_objects:
            for n, ignore in enumerate(obj_a.mmd_rigid.collision_group_mask):
                if not ignore:
                    continue
                for obj_b in rigid_object_groups[n]:
                    if obj_a == obj_b:
                        continue
                    pair = frozenset((obj_a, obj_b))
                    if pair in non_collision_pairs:
                        continue
                    if pair in jointMap:
                        joint = jointMap[pair]
                        joint.rigid_body_constraint.disable_collisions = True
                    else:
                        distance = (obj_a.location - obj_b.location).length
                        if distance < non_collision_distance_scale * (self.__getRigidRange(obj_a) + self.__getRigidRange(obj_b)) * 0.5:
                            nonCollisionJointTable.append((obj_a, obj_b))
                    non_collision_pairs.add(pair)
        for cnt, i in enumerate(rigid_objects):
            logging.info('%3d/%3d: Updating rigid body %s', cnt+1, rigid_object_cnt, i.name)
            self.updateRigid(i, collision_margin)
        self.__createNonCollisionConstraint(nonCollisionJointTable)
        return rigid_objects

    def buildJoints(self):
        for i in self.joints():
            rbc = i.rigid_body_constraint
            if rbc is None:
                continue
            m = self.__rigid_body_matrix_map.get(rbc.object1, None)
            if m is None:
                m = self.__rigid_body_matrix_map.get(rbc.object2, None)
                if m is None:
                    continue
            t, r, s = matmul(m, i.matrix_local).decompose()
            i.location = t
            i.rotation_euler = r.to_euler(i.rotation_mode)

    def cleanAdditionalTransformConstraints(self):
        arm = self.armature()
        if arm:
            FnBone.clean_additional_transformation(arm)

    def applyAdditionalTransformConstraints(self):
        arm = self.armature()
        if not arm:
            return
        MigrationFnBone.fix_mmd_ik_limit_override(arm)
        FnBone.apply_additional_transformation(arm)
