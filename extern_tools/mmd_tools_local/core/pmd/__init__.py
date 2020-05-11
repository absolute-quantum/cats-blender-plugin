# -*- coding: utf-8 -*-
import struct
import os
import re
import logging
import collections

class InvalidFileError(Exception):
    pass
class UnsupportedVersionError(Exception):
    pass

class FileStream:
    def __init__(self, path, file_obj):
        self.__path = path
        self.__file_obj = file_obj
        self.__header = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def path(self):
        return self.__path

    def header(self):
        if self.__header is None:
            raise Exception
        return self.__header

    def setHeader(self, pmx_header):
        self.__header = pmx_header

    def close(self):
        if self.__file_obj is not None:
            logging.debug('close the file("%s")', self.__path)
            self.__file_obj.close()
            self.__file_obj = None


class  FileReadStream(FileStream):
    def __init__(self, path, pmx_header=None):
        self.__fin = open(path, 'rb')
        FileStream.__init__(self, path, self.__fin)


    # READ / WRITE methods for general types
    def readInt(self):
        v, = struct.unpack('<i', self.__fin.read(4))
        return v

    def readUnsignedInt(self):
        v, = struct.unpack('<I', self.__fin.read(4))
        return v

    def readShort(self):
        v, = struct.unpack('<h', self.__fin.read(2))
        return v

    def readUnsignedShort(self):
        v, = struct.unpack('<H', self.__fin.read(2))
        return v

    def readStr(self, size):
        buf = self.__fin.read(size)
        if buf[0] == b'\xfd':
            return ''
        return buf.split(b'\x00')[0].decode('shift_jis', errors='replace')

    def readFloat(self):
        v, = struct.unpack('<f', self.__fin.read(4))
        return v

    def readVector(self, size):
        return struct.unpack('<'+'f'*size, self.__fin.read(4*size))

    def readByte(self):
        v, = struct.unpack('<B', self.__fin.read(1))
        return v

    def readBytes(self, length):
        return self.__fin.read(length)

    def readSignedByte(self):
        v, = struct.unpack('<b', self.__fin.read(1))
        return v


class Header:
    PMD_SIGN = b'Pmd'
    VERSION = 1.0

    def __init__(self):
        self.sign = self.PMD_SIGN
        self.version = self.VERSION
        self.model_name = ''
        self.comment = ''

    def load(self, fs):
        sign = fs.readBytes(3)
        if sign != self.PMD_SIGN:
            raise InvalidFileError('Not PMD file')
        version = fs.readFloat()
        if version != self.version:
            raise InvalidFileError('Not suppored version')

        self.model_name = fs.readStr(20)
        self.comment = fs.readStr(256)

class Vertex:
    def __init__(self):
        self.position = [0.0, 0.0, 0.0]
        self.normal = [1.0, 0.0, 0.0]
        self.uv = [0.0, 0.0]
        self.bones = [-1, -1]
        self.weight = 0 # min:0, max:100
        self.enable_edge = 0 # 0: on, 1: off

    def load(self, fs):
        self.position = fs.readVector(3)
        self.normal = fs.readVector(3)
        self.uv = fs.readVector(2)
        self.bones[0] = fs.readUnsignedShort()
        self.bones[1] = fs.readUnsignedShort()
        self.weight = fs.readByte()
        self.enable_edge = fs.readByte()

class Material:
    def __init__(self):
        self.diffuse = []
        self.shininess = 0
        self.specular = []
        self.ambient = []
        self.toon_index = 0
        self.edge_flag = 0
        self.vertex_count = 0
        self.texture_path = ''
        self.sphere_path = ''
        self.sphere_mode = 1

    def load(self, fs):
        self.diffuse = fs.readVector(4)
        self.shininess = fs.readFloat()
        self.specular = fs.readVector(3)
        self.ambient = fs.readVector(3)
        self.toon_index = fs.readSignedByte()
        self.edge_flag = fs.readByte()
        self.vertex_count = fs.readUnsignedInt()
        tex_path = fs.readStr(20)
        tex_path = tex_path.replace('\\', os.path.sep)
        t = tex_path.split('*')
        if not re.search(r'\.sp([ha])$', t[0], flags=re.I):
            self.texture_path = t.pop(0)
        if len(t) > 0:
            self.sphere_path = t.pop(0)
            if 'aA'.find(self.sphere_path[-1]) != -1:
                self.sphere_mode = 2

class Bone:
    def __init__(self):
        self.name = ''
        self.name_e = ''
        self.parent = 0xffff
        self.tail_bone = 0xffff
        self.type = 1
        self.ik_bone = 0
        self.position = []

    def load(self, fs):
        self.name = fs.readStr(20)
        self.parent = fs.readUnsignedShort()
        if self.parent == 0xffff:
            self.parent = -1
        self.tail_bone = fs.readUnsignedShort()
        if self.tail_bone == 0xffff:
            self.tail_bone = -1
        self.type = fs.readByte()
        if self.type == 9:
            self.ik_bone = fs.readShort()
        else:
            self.ik_bone = fs.readUnsignedShort()
        self.position = fs.readVector(3)

class IK:
    def __init__(self):
        self.bone = 0
        self.target_bone = 0
        self.ik_chain = 0
        self.iterations = 0
        self.control_weight = 0.0
        self.ik_child_bones = []

    def __str__(self):
        return '<IK bone: %d, target: %d, chain: %s, iter: %d, weight: %f, ik_children: %s'%(
            self.bone,
            self.target_bone,
            self.ik_chain,
            self.iterations,
            self.control_weight,
            self.ik_child_bones)

    def load(self, fs):
        self.bone = fs.readUnsignedShort()
        self.target_bone = fs.readUnsignedShort()
        self.ik_chain = fs.readByte()
        self.iterations = fs.readUnsignedShort()
        self.control_weight = fs.readFloat()
        self.ik_child_bones = []
        for i in range(self.ik_chain):
            self.ik_child_bones.append(fs.readUnsignedShort())

class MorphData:
    def __init__(self):
        self.index = 0
        self.offset = []

    def load(self, fs):
        self.index = fs.readUnsignedInt()
        self.offset = fs.readVector(3)

class VertexMorph:
    def __init__(self):
        self.name = ''
        self.name_e = ''
        self.type = 0
        self.data = []

    def load(self, fs):
        self.name = fs.readStr(20)
        data_size = fs.readUnsignedInt()
        self.type = fs.readByte()
        for i in range(data_size):
            t = MorphData()
            t.load(fs)
            self.data.append(t)

class RigidBody:
    def __init__(self):
        self.name = ''
        self.bone = -1
        self.collision_group_number = 0
        self.collision_group_mask = 0
        self.type = 0
        self.size = []
        self.location = []
        self.rotation = []
        self.mass = 0.0
        self.velocity_attenuation = 0.0
        self.rotation_attenuation = 0.0
        self.friction = 0.0
        self.bounce = 0.0
        self.mode = 0

    def load(self, fs):
        self.name = fs.readStr(20)
        self.bone = fs.readUnsignedShort()
        if self.bone == 0xffff:
            self.bone = -1
        self.collision_group_number = fs.readByte()
        self.collision_group_mask = fs.readUnsignedShort()
        self.type = fs.readByte()
        self.size = fs.readVector(3)
        self.location = fs.readVector(3)
        self.rotation = fs.readVector(3)
        self.mass = fs.readFloat()
        self.velocity_attenuation = fs.readFloat()
        self.rotation_attenuation = fs.readFloat()
        self.bounce = fs.readFloat()
        self.friction = fs.readFloat()
        self.mode = fs.readByte()

class Joint:
    def __init__(self):
        self.name = ''
        self.src_rigid = None
        self.dest_rigid = None

        self.location = []
        self.rotation = []

        self.maximum_location = []
        self.minimum_location = []
        self.maximum_rotation = []
        self.minimum_rotation = []

        self.spring_constant = []
        self.spring_rotation_constant = []

    def load(self, fs):
        try: self._load(fs)
        except struct.error: # possibly contains truncated data
            if self.src_rigid is None or self.dest_rigid is None: raise
            self.location = self.location or (0, 0, 0)
            self.rotation = self.rotation or (0, 0, 0)
            self.maximum_location = self.maximum_location or (0, 0, 0)
            self.minimum_location = self.minimum_location or (0, 0, 0)
            self.maximum_rotation = self.maximum_rotation or (0, 0, 0)
            self.minimum_rotation = self.minimum_rotation or (0, 0, 0)
            self.spring_constant = self.spring_constant or (0, 0, 0)
            self.spring_rotation_constant = self.spring_rotation_constant or (0, 0, 0)

    def _load(self, fs):
        self.name = fs.readStr(20)

        self.src_rigid = fs.readUnsignedInt()
        self.dest_rigid = fs.readUnsignedInt()

        self.location = fs.readVector(3)
        self.rotation = fs.readVector(3)

        self.minimum_location = fs.readVector(3)
        self.maximum_location = fs.readVector(3)
        self.minimum_rotation = fs.readVector(3)
        self.maximum_rotation = fs.readVector(3)

        self.spring_constant = fs.readVector(3)
        self.spring_rotation_constant = fs.readVector(3)

class Model:
    def __init__(self):
        self.header = None
        self.vertices = []
        self.faces = []
        self.materials = []
        self.iks = []
        self.morphs = []
        self.facial_disp_names = []
        self.bone_disp_names = []
        self.bone_disp_lists = {}
        self.name = ''
        self.comment = ''
        self.name_e = ''
        self.comment_e = ''
        self.toon_textures = []
        self.rigid_bodies = []
        self.joints = []


    def load(self, fs):
        logging.info('importing pmd model from %s...', fs.path())

        header = Header()
        header.load(fs)

        self.name = header.model_name
        self.comment = header.comment

        logging.info('Model name: %s', self.name)
        logging.info('Comment: %s', self.comment)

        logging.info('')
        logging.info('------------------------------')
        logging.info('Load Vertices')
        logging.info('------------------------------')
        self.vertices = []
        vert_count = fs.readUnsignedInt()
        for i in range(vert_count):
            v = Vertex()
            v.load(fs)
            self.vertices.append(v)
        logging.info('the number of vetices: %d', len(self.vertices))
        logging.info('finished importing vertices.')

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Faces')
        logging.info('------------------------------')
        self.faces = []
        face_vert_count = fs.readUnsignedInt()
        for i in range(int(face_vert_count/3)):
            f1 = fs.readUnsignedShort()
            f2 = fs.readUnsignedShort()
            f3 = fs.readUnsignedShort()
            self.faces.append((f3, f2, f1))
        logging.info('the number of faces: %d', len(self.faces))
        logging.info('finished importing faces.')

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Materials')
        logging.info('------------------------------')
        self.materials = []
        material_count = fs.readUnsignedInt()
        for i in range(material_count):
            mat = Material()
            mat.load(fs)
            self.materials.append(mat)

            logging.info('Material %d', i)
            logging.debug('  Vertex Count: %d', mat.vertex_count)
            logging.debug('  Diffuse: (%.2f, %.2f, %.2f, %.2f)', *mat.diffuse)
            logging.debug('  Specular: (%.2f, %.2f, %.2f)', *mat.specular)
            logging.debug('  Shininess: %f', mat.shininess)
            logging.debug('  Ambient: (%.2f, %.2f, %.2f)', *mat.ambient)
            logging.debug('  Toon Index: %d', mat.toon_index)
            logging.debug('  Edge Type: %d', mat.edge_flag)
            logging.debug('  Texture Path: %s', str(mat.texture_path))
            logging.debug('  Sphere Texture Path: %s', str(mat.sphere_path))
            logging.debug('')
        logging.info('Loaded %d materials', len(self.materials))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Bones')
        logging.info('------------------------------')
        self.bones = []
        bone_count = fs.readUnsignedShort()
        for i in range(bone_count):
            bone = Bone()
            bone.load(fs)
            self.bones.append(bone)

            logging.info('Bone %d: %s', i, bone.name)
            logging.debug('  Name(english): %s', bone.name_e)
            logging.debug('  Location: (%f, %f, %f)', *bone.position)
            logging.debug('  Parent: %s', str(bone.parent))
            logging.debug('  Related Bone: %s', str(bone.tail_bone))
            logging.debug('  Type: %s', bone.type)
            logging.debug('  IK bone: %s', str(bone.ik_bone))
            logging.debug('')
        logging.info('----- Loaded %d bones', len(self.bones))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load IKs')
        logging.info('------------------------------')
        self.iks = []
        ik_count = fs.readUnsignedShort()
        for i in range(ik_count):
            ik = IK()
            ik.load(fs)
            self.iks.append(ik)

            logging.info('IK %d', i)
            logging.debug('  Bone: %s(index: %d)', self.bones[ik.bone].name, ik.bone)
            logging.debug('  Target Bone: %s(index: %d)', self.bones[ik.target_bone].name, ik.target_bone)
            logging.debug('  IK Chain: %d', ik.ik_chain)
            logging.debug('  IK Iterations: %d', ik.iterations)
            logging.debug('  Wegiht: %d', ik.control_weight)
            for j, c in enumerate(ik.ik_child_bones):
                logging.debug('    Bone %d: %s(index: %d)', j, self.bones[c].name, c)
            logging.debug('')
        logging.info('----- Loaded %d IKs', len(self.iks))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Morphs')
        logging.info('------------------------------')
        self.morphs = []
        morph_count = fs.readUnsignedShort()
        for i in range(morph_count):
            morph = VertexMorph()
            morph.load(fs)
            self.morphs.append(morph)
            logging.info('Vertex Morph %d: %s', i, morph.name)
        logging.info('----- Loaded %d morphs', len(self.morphs))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Display Items')
        logging.info('------------------------------')
        self.facial_disp_morphs = []
        t = fs.readByte()
        for i in range(t):
            u = fs.readUnsignedShort()
            self.facial_disp_morphs.append(u)
            logging.info('Facial %d: %s', i, self.morphs[u].name)

        self.bone_disp_lists = collections.OrderedDict()
        bone_disps = []
        t = fs.readByte()
        for i in range(t):
            name = fs.readStr(50)
            self.bone_disp_lists[name] = []
            bone_disps.append(name)
        self.bone_disp_names = [bone_disps, None]

        t = fs.readUnsignedInt()
        for i in range(t):
            bone_index = fs.readUnsignedShort()
            disp_index = fs.readByte()
            self.bone_disp_lists[bone_disps[disp_index-1]].append(bone_index)

        for i, (k, items) in enumerate(self.bone_disp_lists.items()):
            logging.info('  Frame %d: %s', i, k.rstrip())
            for j, b in enumerate(items):
                logging.info('    Bone %d: %s(index: %d)', j, self.bones[b].name, b)
        logging.info('----- Loaded display items')

        logging.info('')
        logging.info('===============================')
        logging.info(' Load Display Items')
        logging.info('   try to load extended data sections...')
        logging.info('')

        # try to load extended data sections.
        try:
            eng_flag = fs.readByte()
        except Exception:
            logging.info('found no extended data sections')
            logging.info('===============================')
            return
        logging.info('===============================')

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load a extended data for english')
        logging.info('------------------------------')
        if eng_flag:
            logging.info('found a extended data for english.')
            self.name_e = fs.readStr(20)
            self.comment_e = fs.readStr(256)
            for i in range(len(self.bones)):
                self.bones[i].name_e = fs.readStr(20)

            for i in range(1, len(self.morphs)):
                self.morphs[i].name_e = fs.readStr(20)

            logging.info(' Name(english): %s', self.name_e)
            logging.info(' Comment(english): %s', self.comment_e)

            bone_disps_e = []
            for i in range(len(bone_disps)):
                t = fs.readStr(50)
                bone_disps_e.append(t)
                logging.info(' Bone name(english) %d: %s', i, t)
            self.bone_disp_names[1] = bone_disps_e
        logging.info('----- Loaded english data.')

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load toon textures')
        logging.info('------------------------------')
        self.toon_textures = []
        for i in range(10):
            t = fs.readStr(100)
            t = t.replace('\\', os.path.sep)
            self.toon_textures.append(t)
            logging.info('Toon Texture %d: %s', i, t)
        logging.info('----- Loaded %d textures', len(self.toon_textures))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Rigid Bodies')
        logging.info('------------------------------')
        try:
            rigid_count = fs.readUnsignedInt()
        except struct.error:
            logging.info('no physics data')
            logging.info('===============================')
            return
        self.rigid_bodies = []
        for i in range(rigid_count):
            rigid = RigidBody()
            rigid.load(fs)
            self.rigid_bodies.append(rigid)
            logging.info('Rigid Body %d: %s', i, rigid.name)
            logging.debug('  Bone: %s', rigid.bone)
            logging.debug('  Collision group: %d', rigid.collision_group_number)
            logging.debug('  Collision group mask: 0x%x', rigid.collision_group_mask)
            logging.debug('  Size: (%f, %f, %f)', *rigid.size)
            logging.debug('  Location: (%f, %f, %f)', *rigid.location)
            logging.debug('  Rotation: (%f, %f, %f)', *rigid.rotation)
            logging.debug('  Mass: %f', rigid.mass)
            logging.debug('  Bounce: %f', rigid.bounce)
            logging.debug('  Friction: %f', rigid.friction)
            logging.debug('')
        logging.info('----- Loaded %d rigid bodies', len(self.rigid_bodies))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Joints')
        logging.info('------------------------------')
        joint_count = fs.readUnsignedInt()
        self.joints = []
        for i in range(joint_count):
            joint = Joint()
            joint.load(fs)
            self.joints.append(joint)
            logging.info('Joint %d: %s', i, joint.name)
            logging.debug('  Rigid A: %s', joint.src_rigid)
            logging.debug('  Rigid B: %s', joint.dest_rigid)
            logging.debug('  Location: (%f, %f, %f)', *joint.location)
            logging.debug('  Rotation: (%f, %f, %f)', *joint.rotation)
            logging.debug('  Location Limit: (%f, %f, %f) - (%f, %f, %f)', *(joint.minimum_location + joint.maximum_location))
            logging.debug('  Rotation Limit: (%f, %f, %f) - (%f, %f, %f)', *(joint.minimum_rotation + joint.maximum_rotation))
            logging.debug('  Spring: (%f, %f, %f)', *joint.spring_constant)
            logging.debug('  Spring(rotation): (%f, %f, %f)', *joint.spring_rotation_constant)
            logging.debug('')
        logging.info('----- Loaded %d joints', len(self.joints))

        logging.info('finished importing the model.')

def load(path):
    with FileReadStream(path) as fs:
        logging.info('****************************************')
        logging.info(' mmd_tools.pmd module')
        logging.info('----------------------------------------')
        logging.info(' Start load model data form a pmd file')
        logging.info('            by the mmd_tools.pmd modlue.')
        logging.info('')

        model = Model()
        try:
            model.load(fs)
        except struct.error as e:
            logging.error(' * Corrupted file: %s', e)
            #raise

        logging.info(' Finish loading.')
        logging.info('----------------------------------------')
        logging.info(' mmd_tools.pmd module')
        logging.info('****************************************')
        return model
