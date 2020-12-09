# -*- coding: utf-8 -*-

import bpy
import mathutils

from mmd_tools_local import bpyutils
from mmd_tools_local.core import rigid_body
from mmd_tools_local.core.bone import FnBone
from mmd_tools_local.core.morph import FnMorph
from mmd_tools_local.bpyutils import matmul
from mmd_tools_local.bpyutils import SceneOp

import logging
import time


def isRigidBodyObject(obj):
    return obj and obj.mmd_type == 'RIGID_BODY'

def isJointObject(obj):
    return obj and obj.mmd_type == 'JOINT'

def isTemporaryObject(obj):
    return obj and obj.mmd_type in {'TRACK_TARGET', 'NON_COLLISION_CONSTRAINT', 'SPRING_CONSTRAINT', 'SPRING_GOAL'}


def getRigidBodySize(obj):
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

class InvalidRigidSettingException(ValueError):
    pass

class Model:
    def __init__(self, root_obj):
        if root_obj.mmd_type != 'ROOT':
            raise ValueError('must be MMD ROOT type object')
        self.__root = getattr(root_obj, 'original', root_obj)
        self.__arm = None
        self.__rigid_grp = None
        self.__joint_grp = None
        self.__temporary_grp = None

    @staticmethod
    def create(name, name_e='', scale=1, obj_name=None, armature=None, add_root_bone=False):
        scene = SceneOp(bpy.context)
        if obj_name is None:
            obj_name = name

        root = bpy.data.objects.new(name=obj_name, object_data=None)
        root.mmd_type = 'ROOT'
        root.mmd_root.name = name
        root.mmd_root.name_e = name_e
        root.empty_draw_size = scale / 0.2
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
            #arm.draw_type = 'STICK'
            armObj = bpy.data.objects.new(name=obj_name+'_arm', object_data=arm)
            armObj.parent = root
            scene.link_object(armObj)
        armObj.lock_rotation = armObj.lock_location = armObj.lock_scale = [True, True, True]
        armObj.show_x_ray = True
        armObj.draw_type = 'WIRE'

        if add_root_bone:
            bone_name = u'全ての親'
            with bpyutils.edit_object(armObj) as data:
                bone = data.edit_bones.new(name=bone_name)
                bone.head = [0.0, 0.0, 0.0]
                bone.tail = [0.0, 0.0, root.empty_draw_size]
            armObj.pose.bones[bone_name].mmd_bone.name_j = bone_name
            armObj.pose.bones[bone_name].mmd_bone.name_e = 'Root'

        bpyutils.select_object(root)
        return Model(root)

    @classmethod
    def findRoot(cls, obj):
        if obj:
            if obj.mmd_type == 'ROOT':
                return obj
            return cls.findRoot(obj.parent)
        return None

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

    def createRigidBodyPool(self, counts):
        if counts < 1:
            return []
        obj = bpyutils.createObject(name='Rigidbody', object_data=bpy.data.meshes.new(name='Rigidbody'))
        obj.parent = self.rigidGroupObject()
        obj.mmd_type = 'RIGID_BODY'
        obj.rotation_mode = 'YXZ'
        obj.draw_type = 'SOLID'
        #obj.show_wire = True
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

        obj = kwargs.get('obj', None)
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
        obj.empty_draw_type = 'ARROWS'
        obj.empty_draw_size = 0.1 * self.__root.empty_draw_size
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

    def create_ik_constraint(self, bone, ik_target, threshold=0.1):
        """ create IK constraint

        If the distance of the ik_target head and the bone tail is greater than threashold,
        then a dummy ik target bone is created.

         Args:
             bone: A pose bone to add a IK constraint
             id_target: A pose bone for IK target
             threshold: Threshold of creating a dummy bone

         Returns:
             The bpy.types.KinematicConstraint object created. It is set target
             and subtarget options.

        """
        ik_target_name = ik_target.name
        if 0 and (ik_target.head - bone.tail).length > threshold:
            logging.debug('*** create a ik_target_dummy of bone %s', ik_target.name)
            with bpyutils.edit_object(self.__arm) as data:
                dummy_target = data.edit_bones.new(name=ik_target.name + '.ik_target_dummy')
                dummy_target.head = bone.tail
                dummy_target.tail = dummy_target.head + mathutils.Vector([0, 0, 1])
                dummy_target.layers = (
                    False, False, False, False, False, False, False, False,
                    True, False, False, False, False, False, False, False,
                    False, False, False, False, False, False, False, False,
                    False, False, False, False, False, False, False, False
                    )
                dummy_target.parent = data.edit_bones[ik_target.name]
                ik_target_name = dummy_target.name
            dummy_ik_target = self.__arm.pose.bones[ik_target_name]
            dummy_ik_target.is_mmd_shadow_bone = True
            dummy_ik_target.mmd_shadow_bone_type = 'IK_TARGET'

        ik_const = bone.constraints.new('IK')
        ik_const.target = self.__arm
        ik_const.subtarget = ik_target_name
        return ik_const

    def __allObjects(self, obj):
        r = []
        for i in obj.children:
            r.append(i)
            r += self.__allObjects(i)
        return r

    def allObjects(self, obj=None):
        if obj is None:
            obj = self.__root
        return [obj] + self.__allObjects(obj)

    def rootObject(self):
        return self.__root

    def armature(self):
        if self.__arm is None:
            for i in filter(lambda x: x.type == 'ARMATURE', self.__root.children):
                self.__arm = i
                break
        return self.__arm

    def rigidGroupObject(self):
        if self.__rigid_grp is None:
            for i in filter(lambda x: x.mmd_type == 'RIGID_GRP_OBJ', self.__root.children):
                self.__rigid_grp = i
                break
            if self.__rigid_grp is None:
                rigids = bpy.data.objects.new(name='rigidbodies', object_data=None)
                SceneOp(bpy.context).link_object(rigids)
                rigids.mmd_type = 'RIGID_GRP_OBJ'
                rigids.parent = self.__root
                rigids.hide = rigids.hide_select = True
                rigids.lock_rotation = rigids.lock_location = rigids.lock_scale = [True, True, True]
                self.__rigid_grp = rigids
        return self.__rigid_grp

    def jointGroupObject(self):
        if self.__joint_grp is None:
            for i in filter(lambda x: x.mmd_type == 'JOINT_GRP_OBJ', self.__root.children):
                self.__joint_grp = i
                break
            if self.__joint_grp is None:
                joints = bpy.data.objects.new(name='joints', object_data=None)
                SceneOp(bpy.context).link_object(joints)
                joints.mmd_type = 'JOINT_GRP_OBJ'
                joints.parent = self.__root
                joints.hide = joints.hide_select = True
                joints.lock_rotation = joints.lock_location = joints.lock_scale = [True, True, True]
                self.__joint_grp = joints
        return self.__joint_grp

    def temporaryGroupObject(self):
        if self.__temporary_grp is None:
            for i in filter(lambda x: x.mmd_type == 'TEMPORARY_GRP_OBJ', self.__root.children):
                self.__temporary_grp = i
                break
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
        return filter(lambda x: x.type == 'MESH' and x.mmd_type == 'NONE', self.allObjects(arm))

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
            return filter(isRigidBodyObject, self.allObjects(self.armature())+self.allObjects(self.rigidGroupObject()))
        return filter(isRigidBodyObject, self.allObjects(self.rigidGroupObject()))

    def joints(self):
        return filter(isJointObject, self.allObjects(self.jointGroupObject()))

    def temporaryObjects(self, rigid_track_only=False):
        if rigid_track_only:
            return filter(isTemporaryObject, self.allObjects(self.rigidGroupObject()))
        return filter(isTemporaryObject, self.allObjects(self.rigidGroupObject())+self.allObjects(self.temporaryGroupObject()))

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

    def build(self):
        rigidbody_world_enabled = rigid_body.setRigidBodyWorldEnabled(False)
        if self.__root.mmd_root.is_built:
            self.clean()
        self.__root.mmd_root.is_built = True
        logging.info('****************************************')
        logging.info(' Build rig')
        logging.info('****************************************')
        start_time = time.time()
        self.__preBuild()
        self.buildRigids(bpyutils.addon_preferences('non_collision_threshold', 1.5))
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
        if arm is not None: # update armature
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
            self.__removeChildrenOfTemporaryGroupObject() # for speeding up only
            for i in self.temporaryObjects():
                bpy.context.scene.objects.unlink(i)
                bpy.data.objects.remove(i)
        elif bpy.app.version < (2, 80, 0):
            for i in self.temporaryObjects():
                bpy.data.objects.remove(i, do_unlink=True)
        else:
            tmp_objs = tuple(self.temporaryObjects())
            for i in tmp_objs:
                for c in i.users_collection:
                    c.objects.unlink(i)
            bpy.ops.object.delete({'selected_objects':tmp_objs, 'active_object':self.rootObject()})
            for i in tmp_objs:
                if i.users < 1:
                    bpy.data.objects.remove(i)

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
            attr_name = '__backup_%s__'%attr
            val = obj.get(attr_name, None)
            if val is not None:
                setattr(obj, attr, val)
                del obj[attr_name]

    def __backupTransforms(self, obj):
        for attr in ('location', 'rotation_euler'):
            attr_name = '__backup_%s__'%attr
            if attr_name in obj: # should not happen in normal build/clean cycle
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
                            c.influence = c.influence # trigger update
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

    def updateRigid(self, rigid_obj):
        assert(rigid_obj.mmd_type == 'RIGID_BODY')
        rb = rigid_obj.rigid_body
        if rb is None:
            return

        rigid = rigid_obj.mmd_rigid
        rigid_type = int(rigid.type)
        relation = rigid_obj.constraints['mmd_tools_rigid_parent']
        arm = relation.target
        bone_name = relation.subtarget

        if rigid_type == rigid_body.MODE_STATIC:
            rb.kinematic = True
        else:
            rb.kinematic = False

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
                    empty = bpy.data.objects.new(
                        'mmd_bonetrack',
                        None)
                    SceneOp(bpy.context).link_object(empty)
                    empty.matrix_world = target_bone.matrix
                    empty.empty_draw_size = 0.1 * self.__root.empty_draw_size
                    empty.empty_draw_type = 'ARROWS'
                    empty.mmd_type = 'TRACK_TARGET'
                    empty.hide = True
                    empty.parent = self.temporaryGroupObject()

                    rigid_obj.mmd_rigid.bone = bone_name
                    rigid_obj.constraints.remove(relation)

                    self.__empty_parent_map[empty] = rigid_obj

                    const_type = ('COPY_TRANSFORMS', 'COPY_ROTATION')[rigid_type-1]
                    const = target_bone.constraints.new(const_type)
                    const.mute = True
                    const.name='mmd_tools_rigid_track'
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
        ncc_obj.empty_draw_size = 0.5 * self.__root.empty_draw_size
        ncc_obj.empty_draw_type = 'ARROWS'
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

    def buildRigids(self, distance_of_ignore_collisions=1.5):
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
                        if distance < distance_of_ignore_collisions * (self.__getRigidRange(obj_a) + self.__getRigidRange(obj_b)) * 0.5:
                            nonCollisionJointTable.append((obj_a, obj_b))
                    non_collision_pairs.add(pair)
        for cnt, i in enumerate(rigid_objects):
            logging.info('%3d/%3d: Updating rigid body %s', cnt+1, rigid_object_cnt, i.name)
            self.updateRigid(i)
        self.__createNonCollisionConstraint(nonCollisionJointTable)
        return rigid_objects

    def __makeSpring(self, target, base_obj, spring_stiffness):
        with bpyutils.select_object(target):
            bpy.ops.object.duplicate()
            spring_target = SceneOp(bpy.context).active_object
        t = spring_target.constraints.get('mmd_tools_rigid_parent')
        if t is not None:
            spring_target.constraints.remove(t)
        spring_target.mmd_type = 'SPRING_GOAL'
        spring_target.rigid_body.kinematic = True
        spring_target.rigid_body.collision_groups = (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True)
        spring_target.parent = base_obj
        spring_target.matrix_parent_inverse = mathutils.Matrix(base_obj.matrix_basis).inverted()
        spring_target.hide = True

        obj = bpy.data.objects.new(
            'S.'+target.name,
            None)
        SceneOp(bpy.context).link_object(obj)
        obj.location = target.location
        obj.empty_draw_size = 0.1
        obj.empty_draw_type = 'ARROWS'
        obj.hide_render = True
        obj.select = False
        obj.hide = True
        obj.mmd_type = 'SPRING_CONSTRAINT'
        obj.parent = self.temporaryGroupObject()

        with bpyutils.select_object(obj):
            bpy.ops.rigidbody.constraint_add(type='GENERIC_SPRING')
        rbc = obj.rigid_body_constraint
        rbc.object1 = target
        rbc.object2 = spring_target

        rbc.use_spring_x = True
        rbc.use_spring_y = True
        rbc.use_spring_z = True

        rbc.spring_stiffness_x = spring_stiffness[0]
        rbc.spring_stiffness_y = spring_stiffness[1]
        rbc.spring_stiffness_z = spring_stiffness[2]

    def updateJoint(self, joint_obj):
        # TODO: This process seems to be an incorrect method for creating spring constraints. Fix or delete this.
        rbc = joint_obj.rigid_body_constraint
        if rbc.object1.rigid_body.kinematic:
            self.__makeSpring(rbc.object2, rbc.object1, joint_obj.mmd_joint.spring_angular)
        if rbc.object2.rigid_body.kinematic:
            self.__makeSpring(rbc.object1, rbc.object2, joint_obj.mmd_joint.spring_angular)

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
        if arm:
            FnBone.apply_additional_transformation(arm)

