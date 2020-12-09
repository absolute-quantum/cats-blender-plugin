# -*- coding: utf-8 -*-
import struct
import os
import logging

class InvalidFileError(Exception):
    pass
class UnsupportedVersionError(Exception):
    pass

class FileStream:
    def __init__(self, path, file_obj, pmx_header):
        self.__path = path
        self.__file_obj = file_obj
        self.__header = pmx_header

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

class FileReadStream(FileStream):
    def __init__(self, path, pmx_header=None):
        self.__fin = open(path, 'rb')
        FileStream.__init__(self, path, self.__fin, pmx_header)

    def __readIndex(self, size, typedict):
        index = None
        if size in typedict :
            index, = struct.unpack(typedict[size], self.__fin.read(size))
        else:
            raise ValueError('invalid data size %s'%str(size))
        return index

    def __readSignedIndex(self, size):
        return self.__readIndex(size, { 1 :"<b", 2 :"<h", 4 :"<i"})

    def __readUnsignedIndex(self, size):
        return self.__readIndex(size, { 1 :"<B", 2 :"<H", 4 :"<I"})


    # READ methods for indexes
    def readVertexIndex(self):
        return self.__readUnsignedIndex(self.header().vertex_index_size)

    def readBoneIndex(self):
        return self.__readSignedIndex(self.header().bone_index_size)

    def readTextureIndex(self):
        return self.__readSignedIndex(self.header().texture_index_size)

    def readMorphIndex(self):
        return self.__readSignedIndex(self.header().morph_index_size)

    def readRigidIndex(self):
        return self.__readSignedIndex(self.header().rigid_index_size)

    def readMaterialIndex(self):
        return self.__readSignedIndex(self.header().material_index_size)

    # READ / WRITE methods for general types
    def readInt(self):
        v, = struct.unpack('<i', self.__fin.read(4))
        return v

    def readShort(self):
        v, = struct.unpack('<h', self.__fin.read(2))
        return v

    def readUnsignedShort(self):
        v, = struct.unpack('<H', self.__fin.read(2))
        return v

    def readStr(self):
        length = self.readInt()
        buf, = struct.unpack('<%ds'%length, self.__fin.read(length))
        return str(buf, self.header().encoding.charset, errors='replace')

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

class FileWriteStream(FileStream):
    def __init__(self, path, pmx_header=None):
        self.__fout = open(path, 'wb')
        FileStream.__init__(self, path, self.__fout, pmx_header)

    def __writeIndex(self, index, size, typedict):
        if size in typedict :
            self.__fout.write(struct.pack(typedict[size], int(index)))
        else:
            raise ValueError('invalid data size %s'%str(size))
        return

    def __writeSignedIndex(self, index, size):
        return self.__writeIndex(index, size, { 1 :"<b", 2 :"<h", 4 :"<i"})

    def __writeUnsignedIndex(self, index, size):
        return self.__writeIndex(index, size, { 1 :"<B", 2 :"<H", 4 :"<I"})

    # WRITE methods for indexes
    def writeVertexIndex(self, index):
        return self.__writeUnsignedIndex(index, self.header().vertex_index_size)

    def writeBoneIndex(self, index):
        return self.__writeSignedIndex(index, self.header().bone_index_size)

    def writeTextureIndex(self, index):
        return self.__writeSignedIndex(index, self.header().texture_index_size)

    def writeMorphIndex(self, index):
        return self.__writeSignedIndex(index, self.header().morph_index_size)

    def writeRigidIndex(self, index):
        return self.__writeSignedIndex(index, self.header().rigid_index_size)

    def writeMaterialIndex(self, index):
        return self.__writeSignedIndex(index, self.header().material_index_size)


    def writeInt(self, v):
        self.__fout.write(struct.pack('<i', int(v)))

    def writeShort(self, v):
        self.__fout.write(struct.pack('<h', int(v)))

    def writeUnsignedShort(self, v):
        self.__fout.write(struct.pack('<H', int(v)))

    def writeStr(self, v):
        data = v.encode(self.header().encoding.charset)
        self.writeInt(len(data))
        self.__fout.write(data)

    def writeFloat(self, v):
        self.__fout.write(struct.pack('<f', float(v)))

    def writeVector(self, v):
        self.__fout.write(struct.pack('<'+'f'*len(v), *v))

    def writeByte(self, v):
        self.__fout.write(struct.pack('<B', int(v)))

    def writeBytes(self, v):
        self.__fout.write(v)

    def writeSignedByte(self, v):
        self.__fout.write(struct.pack('<b', int(v)))

class Encoding:
    _MAP = [
        (0, 'utf-16-le'),
        (1, 'utf-8'),
        ]

    def __init__(self, arg):
        self.index = 0
        self.charset = ''
        t = None
        if isinstance(arg, str):
            t = list(filter(lambda x: x[1]==arg, self._MAP))
            if len(t) == 0:
                raise ValueError('invalid charset %s'%arg)
        elif isinstance(arg, int):
            t = list(filter(lambda x: x[0]==arg, self._MAP))
            if len(t) == 0:
                raise ValueError('invalid index %d'%arg)
        else:
            raise ValueError('invalid argument type')
        t = t[0]
        self.index = t[0]
        self.charset  = t[1]

    def __repr__(self):
        return '<Encoding charset %s>'%self.charset

class Coordinate:
    """ """
    def __init__(self, xAxis, zAxis):
        self.x_axis = xAxis
        self.z_axis = zAxis

class Header:
    PMX_SIGN = b'PMX '
    VERSION = 2.0
    def __init__(self, model=None):
        self.sign = self.PMX_SIGN
        self.version = 0

        self.encoding = Encoding('utf-16-le')
        self.additional_uvs = 0

        self.vertex_index_size = 1
        self.texture_index_size = 1
        self.material_index_size = 1
        self.bone_index_size = 1
        self.morph_index_size = 1
        self.rigid_index_size = 1

        if model is not None:
            self.updateIndexSizes(model)

    def updateIndexSizes(self, model):
        self.vertex_index_size = self.__getIndexSize(len(model.vertices), False)
        self.texture_index_size = self.__getIndexSize(len(model.textures), True)
        self.material_index_size = self.__getIndexSize(len(model.materials), True)
        self.bone_index_size = self.__getIndexSize(len(model.bones), True)
        self.morph_index_size = self.__getIndexSize(len(model.morphs), True)
        self.rigid_index_size = self.__getIndexSize(len(model.rigids), True)

    @staticmethod
    def __getIndexSize(num, signed):
        s = 1
        if signed:
            s = 2
        if (1<<8)/s > num:
            return 1
        elif (1<<16)/s > num:
            return 2
        else:
            return 4

    def load(self, fs):
        logging.info('loading pmx header information...')
        self.sign = fs.readBytes(4)
        logging.debug('File signature is %s', self.sign)
        if self.sign[:3] != self.PMX_SIGN[:3]:
            logging.info('File signature is invalid')
            logging.error('This file is unsupported format, or corrupt file.')
            raise InvalidFileError('File signature is invalid.')
        self.version = fs.readFloat()
        logging.info('pmx format version: %f', self.version)
        if self.version != self.VERSION:
            logging.error('PMX version %.1f is unsupported', self.version)
            raise UnsupportedVersionError('unsupported PMX version: %.1f'%self.version)
        if fs.readByte() != 8 or self.sign[3] != self.PMX_SIGN[3]:
            logging.warning(' * This file might be corrupted.')
        self.encoding = Encoding(fs.readByte())
        self.additional_uvs = fs.readByte()
        self.vertex_index_size = fs.readByte()
        self.texture_index_size = fs.readByte()
        self.material_index_size = fs.readByte()
        self.bone_index_size = fs.readByte()
        self.morph_index_size = fs.readByte()
        self.rigid_index_size = fs.readByte()

        logging.info('----------------------------')
        logging.info('pmx header information')
        logging.info('----------------------------')
        logging.info('pmx version: %.1f', self.version)
        logging.info('encoding: %s', str(self.encoding))
        logging.info('number of uvs: %d', self.additional_uvs)
        logging.info('vertex index size: %d byte(s)', self.vertex_index_size)
        logging.info('texture index: %d byte(s)', self.texture_index_size)
        logging.info('material index: %d byte(s)', self.material_index_size)
        logging.info('bone index: %d byte(s)', self.bone_index_size)
        logging.info('morph index: %d byte(s)', self.morph_index_size)
        logging.info('rigid index: %d byte(s)', self.rigid_index_size)
        logging.info('----------------------------')

    def save(self, fs):
        fs.writeBytes(self.PMX_SIGN)
        fs.writeFloat(self.VERSION)
        fs.writeByte(8)
        fs.writeByte(self.encoding.index)
        fs.writeByte(self.additional_uvs)
        fs.writeByte(self.vertex_index_size)
        fs.writeByte(self.texture_index_size)
        fs.writeByte(self.material_index_size)
        fs.writeByte(self.bone_index_size)
        fs.writeByte(self.morph_index_size)
        fs.writeByte(self.rigid_index_size)

    def __repr__(self):
        return '<Header encoding %s, uvs %d, vtx %d, tex %d, mat %d, bone %d, morph %d, rigid %d>'%(
            str(self.encoding),
            self.additional_uvs,
            self.vertex_index_size,
            self.texture_index_size,
            self.material_index_size,
            self.bone_index_size,
            self.morph_index_size,
            self.rigid_index_size,
            )

class Model:
    def __init__(self):
        self.filepath = ''
        self.header = None

        self.name = ''
        self.name_e = ''
        self.comment = ''
        self.comment_e = ''

        self.vertices = []
        self.faces = []
        self.textures = []
        self.materials = []
        self.bones = []
        self.morphs = []

        self.display = []
        dsp_root = Display()
        dsp_root.isSpecial = True
        dsp_root.name = 'Root'
        dsp_root.name_e = 'Root'
        self.display.append(dsp_root)
        dsp_face = Display()
        dsp_face.isSpecial = True
        dsp_face.name = '表情'
        dsp_face.name_e = 'Facial'
        self.display.append(dsp_face)

        self.rigids = []
        self.joints = []

    def load(self, fs):
        self.filepath = fs.path()
        self.header = fs.header()

        self.name = fs.readStr()
        self.name_e = fs.readStr()

        self.comment = fs.readStr()
        self.comment_e = fs.readStr()

        logging.info('Model name: %s', self.name)
        logging.info('Model name(english): %s', self.name_e)
        logging.info('Comment:%s', self.comment)
        logging.info('Comment(english):%s', self.comment_e)

        logging.info('')
        logging.info('------------------------------')
        logging.info('Load Vertices')
        logging.info('------------------------------')
        num_vertices = fs.readInt()
        self.vertices = []
        for i in range(num_vertices):
            v = Vertex()
            v.load(fs)
            self.vertices.append(v)
        logging.info('----- Loaded %d vertices', len(self.vertices))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Faces')
        logging.info('------------------------------')
        num_faces = fs.readInt()
        self.faces = []
        for i in range(int(num_faces/3)):
            f1 = fs.readVertexIndex()
            f2 = fs.readVertexIndex()
            f3 = fs.readVertexIndex()
            self.faces.append((f3, f2, f1))
        logging.info(' Load %d faces', len(self.faces))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Textures')
        logging.info('------------------------------')
        num_textures = fs.readInt()
        self.textures = []
        for i in range(num_textures):
            t = Texture()
            t.load(fs)
            self.textures.append(t)
            logging.info('Texture %d: %s', i, t.path)
        logging.info(' ----- Loaded %d textures', len(self.textures))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Materials')
        logging.info('------------------------------')
        num_materials = fs.readInt()
        self.materials = []
        for i in range(num_materials):
            m = Material()
            m.load(fs, num_textures)
            self.materials.append(m)

            logging.info('Material %d: %s', i, m.name)
            logging.debug('  Name(english): %s', m.name_e)
            logging.debug('  Comment: %s', m.comment)
            logging.debug('  Vertex Count: %d', m.vertex_count)
            logging.debug('  Diffuse: (%.2f, %.2f, %.2f, %.2f)', *m.diffuse)
            logging.debug('  Specular: (%.2f, %.2f, %.2f)', *m.specular)
            logging.debug('  Shininess: %f', m.shininess)
            logging.debug('  Ambient: (%.2f, %.2f, %.2f)', *m.ambient)
            logging.debug('  Double Sided: %s', str(m.is_double_sided))
            logging.debug('  Drop Shadow: %s', str(m.enabled_drop_shadow))
            logging.debug('  Self Shadow: %s', str(m.enabled_self_shadow))
            logging.debug('  Self Shadow Map: %s', str(m.enabled_self_shadow_map))
            logging.debug('  Edge: %s', str(m.enabled_toon_edge))
            logging.debug('  Edge Color: (%.2f, %.2f, %.2f, %.2f)', *m.edge_color)
            logging.debug('  Edge Size: %.2f', m.edge_size)
            if m.texture != -1:
                logging.debug('  Texture Index: %d', m.texture)
            else:
                logging.debug('  Texture: None')
            if m.sphere_texture != -1:
                logging.debug('  Sphere Texture Index: %d', m.sphere_texture)
                logging.debug('  Sphere Texture Mode: %d', m.sphere_texture_mode)
            else:
                logging.debug('  Sphere Texture: None')
            logging.debug('')

        logging.info('----- Loaded %d  materials.', len(self.materials))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Bones')
        logging.info('------------------------------')
        num_bones = fs.readInt()
        self.bones = []
        for i in range(num_bones):
            b = Bone()
            b.load(fs)
            self.bones.append(b)

            logging.info('Bone %d: %s', i, b.name)
            logging.debug('  Name(english): %s', b.name_e)
            logging.debug('  Location: (%f, %f, %f)', *b.location)
            logging.debug('  displayConnection: %s', str(b.displayConnection))
            logging.debug('  Parent: %s', str(b.parent))
            logging.debug('  Transform Order: %s', str(b.transform_order))
            logging.debug('  Rotatable: %s', str(b.isRotatable))
            logging.debug('  Movable: %s', str(b.isMovable))
            logging.debug('  Visible: %s', str(b.visible))
            logging.debug('  Controllable: %s', str(b.isControllable))
            logging.debug('  Additional Location: %s', str(b.hasAdditionalLocation))
            logging.debug('  Additional Rotation: %s', str(b.hasAdditionalRotate))
            if b.additionalTransform is not None:
                logging.debug('  Additional Transform: Bone:%d, influence: %f', *b.additionalTransform)
            logging.debug('  IK: %s', str(b.isIK))
            if b.isIK:
                logging.debug('    Unit Angle: %f', b.rotationConstraint)
                logging.debug('    Target: %d', b.target)
                for j, link in enumerate(b.ik_links):
                    logging.debug('    IK Link %d: %d, %s - %s', j, link.target, str(link.minimumAngle), str(link.maximumAngle))
            logging.debug('')
        logging.info('----- Loaded %d bones.', len(self.bones))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Morphs')
        logging.info('------------------------------')
        num_morph = fs.readInt()
        self.morphs = []
        display_categories = {0: 'System', 1: 'Eyebrow', 2: 'Eye', 3: 'Mouth', 4: 'Other'}
        for i in range(num_morph):
            m = Morph.create(fs)
            self.morphs.append(m)

            logging.info('%s %d: %s', m.__class__.__name__, i, m.name)
            logging.debug('  Name(english): %s', m.name_e)
            logging.debug('  Category: %s (%d)', display_categories.get(m.category, '#Invalid'), m.category)
            logging.debug('')
        logging.info('----- Loaded %d morphs.', len(self.morphs))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Display Items')
        logging.info('------------------------------')
        num_disp = fs.readInt()
        self.display = []
        for i in range(num_disp):
            d = Display()
            d.load(fs)
            self.display.append(d)

            logging.info('Display Item %d: %s', i, d.name)
            logging.debug('  Name(english): %s', d.name_e)
            logging.debug('')
        logging.info('----- Loaded %d display items.', len(self.display))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Rigid Bodies')
        logging.info('------------------------------')
        num_rigid = fs.readInt()
        self.rigids = []
        rigid_types = {0: 'Sphere', 1: 'Box', 2: 'Capsule'}
        rigid_modes = {0: 'Static', 1: 'Dynamic', 2: 'Dynamic(track to bone)'}
        for i in range(num_rigid):
            r = Rigid()
            r.load(fs)
            self.rigids.append(r)
            logging.info('Rigid Body %d: %s', i, r.name)
            logging.debug('  Name(english): %s', r.name_e)
            logging.debug('  Type: %s', rigid_types[r.type])
            logging.debug('  Mode: %s (%d)', rigid_modes.get(r.mode, '#Invalid'), r.mode)
            logging.debug('  Related bone: %s', r.bone)
            logging.debug('  Collision group: %d', r.collision_group_number)
            logging.debug('  Collision group mask: 0x%x', r.collision_group_mask)
            logging.debug('  Size: (%f, %f, %f)', *r.size)
            logging.debug('  Location: (%f, %f, %f)', *r.location)
            logging.debug('  Rotation: (%f, %f, %f)', *r.rotation)
            logging.debug('  Mass: %f', r.mass)
            logging.debug('  Bounce: %f', r.bounce)
            logging.debug('  Friction: %f', r.friction)
            logging.debug('')

        logging.info('----- Loaded %d rigid bodies.', len(self.rigids))

        logging.info('')
        logging.info('------------------------------')
        logging.info(' Load Joints')
        logging.info('------------------------------')
        num_joints = fs.readInt()
        self.joints = []
        for i in range(num_joints):
            j = Joint()
            j.load(fs)
            self.joints.append(j)

            logging.info('Joint %d: %s', i, j.name)
            logging.debug('  Name(english): %s', j.name_e)
            logging.debug('  Rigid A: %s', j.src_rigid)
            logging.debug('  Rigid B: %s', j.dest_rigid)
            logging.debug('  Location: (%f, %f, %f)', *j.location)
            logging.debug('  Rotation: (%f, %f, %f)', *j.rotation)
            logging.debug('  Location Limit: (%f, %f, %f) - (%f, %f, %f)', *(j.minimum_location + j.maximum_location))
            logging.debug('  Rotation Limit: (%f, %f, %f) - (%f, %f, %f)', *(j.minimum_rotation + j.maximum_rotation))
            logging.debug('  Spring: (%f, %f, %f)', *j.spring_constant)
            logging.debug('  Spring(rotation): (%f, %f, %f)', *j.spring_rotation_constant)
            logging.debug('')

        logging.info('----- Loaded %d joints.', len(self.joints))

    def save(self, fs):
        fs.writeStr(self.name)
        fs.writeStr(self.name_e)

        fs.writeStr(self.comment)
        fs.writeStr(self.comment_e)

        logging.info('''exportings pmx model data...
name: %s
name(english): %s
comment:
%s
comment(english):
%s
''', self.name, self.name_e, self.comment, self.comment_e)

        logging.info('exporting vertices... %d', len(self.vertices))
        fs.writeInt(len(self.vertices))
        for i in self.vertices:
            i.save(fs)
        logging.info('finished exporting vertices.')

        logging.info('exporting faces... %d', len(self.faces))
        fs.writeInt(len(self.faces)*3)
        for f3, f2, f1 in self.faces:
            fs.writeVertexIndex(f1)
            fs.writeVertexIndex(f2)
            fs.writeVertexIndex(f3)
        logging.info('finished exporting faces.')

        logging.info('exporting textures... %d', len(self.textures))
        fs.writeInt(len(self.textures))
        for i in self.textures:
            i.save(fs)
        logging.info('finished exporting textures.')

        logging.info('exporting materials... %d', len(self.materials))
        fs.writeInt(len(self.materials))
        for i in self.materials:
            i.save(fs)
        logging.info('finished exporting materials.')

        logging.info('exporting bones... %d', len(self.bones))
        fs.writeInt(len(self.bones))
        for i in self.bones:
            i.save(fs)
        logging.info('finished exporting bones.')

        logging.info('exporting morphs... %d', len(self.morphs))
        fs.writeInt(len(self.morphs))
        for i in self.morphs:
            i.save(fs)
        logging.info('finished exporting morphs.')

        logging.info('exporting display items... %d', len(self.display))
        fs.writeInt(len(self.display))
        for i in self.display:
            i.save(fs)
        logging.info('finished exporting display items.')

        logging.info('exporting rigid bodies... %d', len(self.rigids))
        fs.writeInt(len(self.rigids))
        for i in self.rigids:
            i.save(fs)
        logging.info('finished exporting rigid bodies.')

        logging.info('exporting joints... %d', len(self.joints))
        fs.writeInt(len(self.joints))
        for i in self.joints:
            i.save(fs)
        logging.info('finished exporting joints.')
        logging.info('finished exporting the model.')


    def __repr__(self):
        return '<Model name %s, name_e %s, comment %s, comment_e %s, textures %s>'%(
            self.name,
            self.name_e,
            self.comment,
            self.comment_e,
            str(self.textures),
            )

class Vertex:
    def __init__(self):
        self.co = [0.0, 0.0, 0.0]
        self.normal = [0.0, 0.0, 0.0]
        self.uv = [0.0, 0.0]
        self.additional_uvs = []
        self.weight = None
        self.edge_scale = 1

    def __repr__(self):
        return '<Vertex co %s, normal %s, uv %s, additional_uvs %s, weight %s, edge_scale %s>'%(
            str(self.co),
            str(self.normal),
            str(self.uv),
            str(self.additional_uvs),
            str(self.weight),
            str(self.edge_scale),
            )

    def load(self, fs):
        self.co = fs.readVector(3)
        self.normal = fs.readVector(3)
        self.uv = fs.readVector(2)
        self.additional_uvs = []
        for i in range(fs.header().additional_uvs):
            self.additional_uvs.append(fs.readVector(4))
        self.weight = BoneWeight()
        self.weight.load(fs)
        self.edge_scale = fs.readFloat()

    def save(self, fs):
        fs.writeVector(self.co)
        fs.writeVector(self.normal)
        fs.writeVector(self.uv)
        for i in self.additional_uvs:
            fs.writeVector(i)
        for i in range(fs.header().additional_uvs-len(self.additional_uvs)):
            fs.writeVector((0,0,0,0))
        self.weight.save(fs)
        fs.writeFloat(self.edge_scale)

class BoneWeightSDEF:
    def __init__(self, weight=0, c=None, r0=None, r1=None):
        self.weight = weight
        self.c = c
        self.r0 = r0
        self.r1 = r1

class BoneWeight:
    BDEF1 = 0
    BDEF2 = 1
    BDEF4 = 2
    SDEF  = 3

    TYPES = [
        (BDEF1, 'BDEF1'),
        (BDEF2, 'BDEF2'),
        (BDEF4, 'BDEF4'),
        (SDEF, 'SDEF'),
        ]

    def __init__(self):
        self.bones = []
        self.weights = []
        self.type = self.BDEF1

    def convertIdToName(self, type_id):
        t = list(filter(lambda x: x[0]==type_id, self.TYPES))
        if len(t) > 0:
            return t[0][1]
        else:
            return None

    def convertNameToId(self, type_name):
        t = list(filter(lambda x: x[1]==type_name, self.TYPES))
        if len(t) > 0:
            return t[0][0]
        else:
            return None

    def load(self, fs):
        self.type = fs.readByte()
        self.bones = []
        self.weights = []

        if self.type == self.BDEF1:
            self.bones.append(fs.readBoneIndex())
        elif self.type == self.BDEF2:
            self.bones.append(fs.readBoneIndex())
            self.bones.append(fs.readBoneIndex())
            self.weights.append(fs.readFloat())
        elif self.type == self.BDEF4:
            self.bones.append(fs.readBoneIndex())
            self.bones.append(fs.readBoneIndex())
            self.bones.append(fs.readBoneIndex())
            self.bones.append(fs.readBoneIndex())
            self.weights = fs.readVector(4)
        elif self.type == self.SDEF:
            self.bones.append(fs.readBoneIndex())
            self.bones.append(fs.readBoneIndex())
            self.weights = BoneWeightSDEF()
            self.weights.weight = fs.readFloat()
            self.weights.c = fs.readVector(3)
            self.weights.r0 = fs.readVector(3)
            self.weights.r1 = fs.readVector(3)
        else:
            raise ValueError('invalid weight type %s'%str(self.type))

    def save(self, fs):
        fs.writeByte(self.type)
        if self.type == self.BDEF1:
            fs.writeBoneIndex(self.bones[0])
        elif self.type == self.BDEF2:
            for i in range(2):
                fs.writeBoneIndex(self.bones[i])
            fs.writeFloat(self.weights[0])
        elif self.type == self.BDEF4:
            for i in range(4):
                fs.writeBoneIndex(self.bones[i])
            for i in range(4):
                fs.writeFloat(self.weights[i])
        elif self.type == self.SDEF:
            for i in range(2):
                fs.writeBoneIndex(self.bones[i])
            if not isinstance(self.weights, BoneWeightSDEF):
                raise ValueError
            fs.writeFloat(self.weights.weight)
            fs.writeVector(self.weights.c)
            fs.writeVector(self.weights.r0)
            fs.writeVector(self.weights.r1)
        else:
            raise ValueError('invalid weight type %s'%str(self.type))


class Texture:
    def __init__(self):
        self.path = ''

    def __repr__(self):
        return '<Texture path %s>'%str(self.path)

    def load(self, fs):
        self.path = fs.readStr()
        self.path = self.path.replace('\\', os.path.sep)
        if not os.path.isabs(self.path):
            self.path = os.path.normpath(os.path.join(os.path.dirname(fs.path()), self.path))

    def save(self, fs):
        try:
            relPath = os.path.relpath(self.path, os.path.dirname(fs.path()))
        except ValueError:
            relPath = self.path
        relPath = relPath.replace(os.path.sep, '\\') # always save using windows path conventions
        logging.info('writing to pmx file the relative texture path: %s', relPath)
        fs.writeStr(relPath)

class SharedTexture(Texture):
    def __init__(self):
        self.number = 0
        self.prefix = ''

class Material:
    SPHERE_MODE_OFF = 0
    SPHERE_MODE_MULT = 1
    SPHERE_MODE_ADD = 2
    SPHERE_MODE_SUBTEX = 3

    def __init__(self):
        self.name = ''
        self.name_e = ''

        self.diffuse = []
        self.specular = []
        self.shininess = 0
        self.ambient = []

        self.is_double_sided = True
        self.enabled_drop_shadow = True
        self.enabled_self_shadow_map = True
        self.enabled_self_shadow = True
        self.enabled_toon_edge = False

        self.edge_color = []
        self.edge_size = 1

        self.texture = -1
        self.sphere_texture = -1
        self.sphere_texture_mode = 0
        self.is_shared_toon_texture = True
        self.toon_texture = 0

        self.comment = ''
        self.vertex_count = 0

    def __repr__(self):
        return '<Material name %s, name_e %s, diffuse %s, specular %s, shininess %s, ambient %s, double_side %s, drop_shadow %s, self_shadow_map %s, self_shadow %s, toon_edge %s, edge_color %s, edge_size %s, toon_texture %s, comment %s>'%(
            self.name,
            self.name_e,
            str(self.diffuse),
            str(self.specular),
            str(self.shininess),
            str(self.ambient),
            str(self.is_double_sided),
            str(self.enabled_drop_shadow),
            str(self.enabled_self_shadow_map),
            str(self.enabled_self_shadow),
            str(self.enabled_toon_edge),
            str(self.edge_color),
            str(self.edge_size),
            str(self.texture),
            str(self.sphere_texture),
            str(self.toon_texture),
            str(self.comment),)

    def load(self, fs, num_textures):
        def __tex_index(index):
            return index if 0 <= index < num_textures else -1

        self.name = fs.readStr()
        self.name_e = fs.readStr()

        self.diffuse = fs.readVector(4)
        self.specular = fs.readVector(3)
        self.shininess = fs.readFloat()
        self.ambient = fs.readVector(3)

        flags = fs.readByte()
        self.is_double_sided = bool(flags & 1)
        self.enabled_drop_shadow = bool(flags & 2)
        self.enabled_self_shadow_map = bool(flags & 4)
        self.enabled_self_shadow = bool(flags & 8)
        self.enabled_toon_edge = bool(flags & 16)

        self.edge_color = fs.readVector(4)
        self.edge_size = fs.readFloat()

        self.texture = __tex_index(fs.readTextureIndex())
        self.sphere_texture = __tex_index(fs.readTextureIndex())
        self.sphere_texture_mode = fs.readSignedByte()

        self.is_shared_toon_texture = fs.readSignedByte()
        self.is_shared_toon_texture = (self.is_shared_toon_texture == 1)
        if self.is_shared_toon_texture:
            self.toon_texture = fs.readSignedByte()
        else:
            self.toon_texture = __tex_index(fs.readTextureIndex())

        self.comment = fs.readStr()
        self.vertex_count = fs.readInt()

    def save(self, fs):
        fs.writeStr(self.name)
        fs.writeStr(self.name_e)

        fs.writeVector(self.diffuse)
        fs.writeVector(self.specular)
        fs.writeFloat(self.shininess)
        fs.writeVector(self.ambient)

        flags = 0
        flags |= int(self.is_double_sided)
        flags |= int(self.enabled_drop_shadow) << 1
        flags |= int(self.enabled_self_shadow_map) << 2
        flags |= int(self.enabled_self_shadow) << 3
        flags |= int(self.enabled_toon_edge) << 4
        fs.writeByte(flags)

        fs.writeVector(self.edge_color)
        fs.writeFloat(self.edge_size)

        fs.writeTextureIndex(self.texture)
        fs.writeTextureIndex(self.sphere_texture)
        fs.writeSignedByte(self.sphere_texture_mode)

        if self.is_shared_toon_texture:
            fs.writeSignedByte(1)
            fs.writeSignedByte(self.toon_texture)
        else:
            fs.writeSignedByte(0)
            fs.writeTextureIndex(self.toon_texture)

        fs.writeStr(self.comment)
        fs.writeInt(self.vertex_count)


class Bone:
    def __init__(self):
        self.name = ''
        self.name_e = ''

        self.location = []
        self.parent = None
        self.transform_order = 0

        # 接続先表示方法
        # 座標オフセット(float3)または、boneIndex(int)
        self.displayConnection = -1

        self.isRotatable = True
        self.isMovable = True
        self.visible = True
        self.isControllable = True

        self.isIK = False

        # 回転付与
        self.hasAdditionalRotate = False

        # 移動付与
        self.hasAdditionalLocation = False

        # 回転付与および移動付与の付与量
        self.additionalTransform = None

        # 軸固定
        # 軸ベクトルfloat3
        self.axis = None

        # ローカル軸
        self.localCoordinate = None

        self.transAfterPhis = False

        # 外部親変形
        self.externalTransKey = None

        # 以下IKボーンのみ有効な変数
        self.target = None
        self.loopCount = 8
        # IKループ計三時の1回あたりの制限角度(ラジアン)
        self.rotationConstraint = 0.03

        # IKLinkオブジェクトの配列
        self.ik_links = []

    def __repr__(self):
        return '<Bone name %s, name_e %s>'%(
            self.name,
            self.name_e,)

    def load(self, fs):
        self.name = fs.readStr()
        self.name_e = fs.readStr()

        self.location = fs.readVector(3)
        self.parent = fs.readBoneIndex()
        self.transform_order = fs.readInt()

        flags = fs.readShort()
        if flags & 0x0001:
            self.displayConnection = fs.readBoneIndex()
        else:
            self.displayConnection = fs.readVector(3)

        self.isRotatable    = ((flags & 0x0002) != 0)
        self.isMovable      = ((flags & 0x0004) != 0)
        self.visible        = ((flags & 0x0008) != 0)
        self.isControllable = ((flags & 0x0010) != 0)

        self.isIK           = ((flags & 0x0020) != 0)

        self.hasAdditionalRotate = ((flags & 0x0100) != 0)
        self.hasAdditionalLocation = ((flags & 0x0200) != 0)
        if self.hasAdditionalRotate or self.hasAdditionalLocation:
            t = fs.readBoneIndex()
            v = fs.readFloat()
            self.additionalTransform = (t, v)
        else:
            self.additionalTransform = None


        if flags & 0x0400:
            self.axis = fs.readVector(3)
        else:
            self.axis = None

        if flags & 0x0800:
            xaxis = fs.readVector(3)
            zaxis = fs.readVector(3)
            self.localCoordinate = Coordinate(xaxis, zaxis)
        else:
            self.localCoordinate = None

        self.transAfterPhis = ((flags & 0x1000) != 0)

        if flags & 0x2000:
            self.externalTransKey = fs.readInt()
        else:
            self.externalTransKey = None

        if self.isIK:
            self.target = fs.readBoneIndex()
            self.loopCount = fs.readInt()
            self.rotationConstraint = fs.readFloat()

            iklink_num = fs.readInt()
            self.ik_links = []
            for i in range(iklink_num):
                link = IKLink()
                link.load(fs)
                self.ik_links.append(link)

    def save(self, fs):
        fs.writeStr(self.name)
        fs.writeStr(self.name_e)

        fs.writeVector(self.location)
        fs.writeBoneIndex(-1 if self.parent is None else self.parent)
        fs.writeInt(self.transform_order)

        flags = 0
        flags |= int(isinstance(self.displayConnection, int))
        flags |= int(self.isRotatable) << 1
        flags |= int(self.isMovable) << 2
        flags |= int(self.visible) << 3
        flags |= int(self.isControllable) << 4
        flags |= int(self.isIK) << 5

        flags |= int(self.hasAdditionalRotate) << 8
        flags |= int(self.hasAdditionalLocation) << 9
        flags |= int(self.axis is not None) << 10
        flags |= int(self.localCoordinate is not None) << 11

        flags |= int(self.transAfterPhis) << 12
        flags |= int(self.externalTransKey is not None) << 13

        fs.writeShort(flags)

        if flags & 0x0001:
            fs.writeBoneIndex(self.displayConnection)
        else:
            fs.writeVector(self.displayConnection)

        if self.hasAdditionalRotate or self.hasAdditionalLocation:
            fs.writeBoneIndex(self.additionalTransform[0])
            fs.writeFloat(self.additionalTransform[1])

        if flags & 0x0400:
            fs.writeVector(self.axis)

        if flags & 0x0800:
            fs.writeVector(self.localCoordinate.x_axis)
            fs.writeVector(self.localCoordinate.z_axis)

        if flags & 0x2000:
            fs.writeInt(self.externalTransKey)

        if self.isIK:
            fs.writeBoneIndex(self.target)
            fs.writeInt(self.loopCount)
            fs.writeFloat(self.rotationConstraint)

            fs.writeInt(len(self.ik_links))
            for i in self.ik_links:
                i.save(fs)


class IKLink:
    def __init__(self):
        self.target = None
        self.maximumAngle = None
        self.minimumAngle = None

    def __repr__(self):
        return '<IKLink target %s>'%(str(self.target))

    def load(self, fs):
        self.target = fs.readBoneIndex()
        flag = fs.readByte()
        if flag == 1:
            self.minimumAngle = fs.readVector(3)
            self.maximumAngle = fs.readVector(3)
        else:
            self.minimumAngle = None
            self.maximumAngle = None

    def save(self, fs):
        fs.writeBoneIndex(self.target)
        if isinstance(self.minimumAngle, (tuple, list)) and isinstance(self.maximumAngle, (tuple, list)):
            fs.writeByte(1)
            fs.writeVector(self.minimumAngle)
            fs.writeVector(self.maximumAngle)
        else:
            fs.writeByte(0)

class Morph:
    CATEGORY_SYSTEM = 0
    CATEGORY_EYEBROW = 1
    CATEGORY_EYE = 2
    CATEGORY_MOUTH = 3
    CATEGORY_OHTER = 4

    def __init__(self, name, name_e, category, **kwargs):
        self.offsets = []
        self.name = name
        self.name_e = name_e
        self.category = category

    def __repr__(self):
        return '<Morph name %s, name_e %s>'%(self.name, self.name_e)

    def type_index(self):
        raise NotImplementedError

    @staticmethod
    def create(fs):
        _CLASSES = {
            0: GroupMorph,
            1: VertexMorph,
            2: BoneMorph,
            3: UVMorph,
            4: UVMorph,
            5: UVMorph,
            6: UVMorph,
            7: UVMorph,
            8: MaterialMorph,
            }

        name = fs.readStr()
        name_e = fs.readStr()
        logging.debug('morph: %s', name)
        category = fs.readSignedByte()
        typeIndex = fs.readSignedByte()
        ret = _CLASSES[typeIndex](name, name_e, category, type_index = typeIndex)
        ret.load(fs)
        return ret

    def load(self, fs):
        """ Implement for loading morph data.
        """
        raise NotImplementedError

    def save(self, fs):
        fs.writeStr(self.name)
        fs.writeStr(self.name_e)
        fs.writeSignedByte(self.category)
        fs.writeSignedByte(self.type_index())
        fs.writeInt(len(self.offsets))
        for i in self.offsets:
            i.save(fs)

class VertexMorph(Morph):
    def __init__(self, *args, **kwargs):
        Morph.__init__(self, *args, **kwargs)

    def type_index(self):
        return 1

    def load(self, fs):
        num = fs.readInt()
        for i in range(num):
            t = VertexMorphOffset()
            t.load(fs)
            self.offsets.append(t)

class VertexMorphOffset:
    def __init__(self):
        self.index = 0
        self.offset = []

    def load(self, fs):
        self.index = fs.readVertexIndex()
        self.offset = fs.readVector(3)

    def save(self, fs):
        fs.writeVertexIndex(self.index)
        fs.writeVector(self.offset)

class UVMorph(Morph):
    def __init__(self, *args, **kwargs):
        self.uv_index = kwargs.get('type_index', 3) - 3
        Morph.__init__(self, *args, **kwargs)

    def type_index(self):
        return self.uv_index + 3

    def load(self, fs):
        self.offsets = []
        num = fs.readInt()
        for i in range(num):
            t = UVMorphOffset()
            t.load(fs)
            self.offsets.append(t)

class UVMorphOffset:
    def __init__(self):
        self.index = 0
        self.offset = []

    def load(self, fs):
        self.index = fs.readVertexIndex()
        self.offset = fs.readVector(4)

    def save(self, fs):
        fs.writeVertexIndex(self.index)
        fs.writeVector(self.offset)

class BoneMorph(Morph):
    def __init__(self, *args, **kwargs):
        Morph.__init__(self, *args, **kwargs)

    def type_index(self):
        return 2

    def load(self, fs):
        self.offsets = []
        num = fs.readInt()
        for i in range(num):
            t = BoneMorphOffset()
            t.load(fs)
            self.offsets.append(t)

class BoneMorphOffset:
    def __init__(self):
        self.index = None
        self.location_offset = []
        self.rotation_offset = []

    def load(self, fs):
        self.index = fs.readBoneIndex()
        self.location_offset = fs.readVector(3)
        self.rotation_offset = fs.readVector(4)
        if not any(self.rotation_offset):
            self.rotation_offset = (0, 0, 0, 1)

    def save(self, fs):
        fs.writeBoneIndex(self.index)
        fs.writeVector(self.location_offset)
        fs.writeVector(self.rotation_offset)

class MaterialMorph(Morph):
    def __init__(self, *args, **kwargs):
        Morph.__init__(self, *args, **kwargs)

    def type_index(self):
        return 8

    def load(self, fs):
        self.offsets = []
        num = fs.readInt()
        for i in range(num):
            t = MaterialMorphOffset()
            t.load(fs)
            self.offsets.append(t)

class MaterialMorphOffset:
    TYPE_MULT = 0
    TYPE_ADD = 1

    def __init__(self):
        self.index = 0
        self.offset_type = 0
        self.diffuse_offset = []
        self.specular_offset = []
        self.shininess_offset = 0
        self.ambient_offset = []
        self.edge_color_offset = []
        self.edge_size_offset = []
        self.texture_factor = []
        self.sphere_texture_factor = []
        self.toon_texture_factor = []

    def load(self, fs):
        self.index = fs.readMaterialIndex()
        self.offset_type = fs.readSignedByte()
        self.diffuse_offset = fs.readVector(4)
        self.specular_offset = fs.readVector(3)
        self.shininess_offset = fs.readFloat()
        self.ambient_offset = fs.readVector(3)
        self.edge_color_offset = fs.readVector(4)
        self.edge_size_offset = fs.readFloat()
        self.texture_factor = fs.readVector(4)
        self.sphere_texture_factor = fs.readVector(4)
        self.toon_texture_factor = fs.readVector(4)

    def save(self, fs):
        fs.writeMaterialIndex(self.index)
        fs.writeSignedByte(self.offset_type)
        fs.writeVector(self.diffuse_offset)
        fs.writeVector(self.specular_offset)
        fs.writeFloat(self.shininess_offset)
        fs.writeVector(self.ambient_offset)
        fs.writeVector(self.edge_color_offset)
        fs.writeFloat(self.edge_size_offset)
        fs.writeVector(self.texture_factor)
        fs.writeVector(self.sphere_texture_factor)
        fs.writeVector(self.toon_texture_factor)

class GroupMorph(Morph):
    def __init__(self, *args, **kwargs):
        Morph.__init__(self, *args, **kwargs)

    def type_index(self):
        return 0

    def load(self, fs):
        self.offsets = []
        num = fs.readInt()
        for i in range(num):
            t = GroupMorphOffset()
            t.load(fs)
            self.offsets.append(t)

class GroupMorphOffset:
    def __init__(self):
        self.morph = None
        self.factor = 0.0

    def load(self, fs):
        self.morph = fs.readMorphIndex()
        self.factor = fs.readFloat()

    def save(self, fs):
        fs.writeMorphIndex(self.morph)
        fs.writeFloat(self.factor)


class Display:
    def __init__(self):
        self.name = ''
        self.name_e = ''

        self.isSpecial = False

        self.data = []

    def __repr__(self):
        return '<Display name %s, name_e %s>'%(
            self.name,
            self.name_e,
            )

    def load(self, fs):
        self.name = fs.readStr()
        self.name_e = fs.readStr()

        self.isSpecial = (fs.readByte() == 1)
        num = fs.readInt()
        self.data = []
        for i in range(num):
            disp_type = fs.readByte()
            index = None
            if disp_type == 0:
                index = fs.readBoneIndex()
            elif disp_type == 1:
                index = fs.readMorphIndex()
            else:
                raise Exception('invalid value.')
            self.data.append((disp_type, index))
        logging.debug('the number of display elements: %d', len(self.data))

    def save(self, fs):
        fs.writeStr(self.name)
        fs.writeStr(self.name_e)

        fs.writeByte(int(self.isSpecial))
        fs.writeInt(len(self.data))

        for disp_type, index in self.data:
            fs.writeByte(disp_type)
            if disp_type == 0:
                fs.writeBoneIndex(index)
            elif disp_type == 1:
                fs.writeMorphIndex(index)
            else:
                raise Exception('invalid value.')

class Rigid:
    TYPE_SPHERE = 0
    TYPE_BOX = 1
    TYPE_CAPSULE = 2

    MODE_STATIC = 0
    MODE_DYNAMIC = 1
    MODE_DYNAMIC_BONE = 2
    def __init__(self):
        self.name = ''
        self.name_e = ''

        self.bone = None
        self.collision_group_number = 0
        self.collision_group_mask = 0

        self.type = 0
        self.size = []

        self.location = []
        self.rotation = []

        self.mass = 1
        self.velocity_attenuation = []
        self.rotation_attenuation = []
        self.bounce = []
        self.friction = []

        self.mode = 0

    def __repr__(self):
        return '<Rigid name %s, name_e %s>'%(
            self.name,
            self.name_e,
            )

    def load(self, fs):
        self.name = fs.readStr()
        self.name_e = fs.readStr()

        boneIndex = fs.readBoneIndex()
        if boneIndex != -1:
            self.bone = boneIndex
        else:
            self.bone = None

        self.collision_group_number = fs.readSignedByte()
        self.collision_group_mask = fs.readUnsignedShort()

        self.type = fs.readSignedByte()
        self.size = fs.readVector(3)

        self.location = fs.readVector(3)
        self.rotation = fs.readVector(3)

        self.mass = fs.readFloat()
        self.velocity_attenuation = fs.readFloat()
        self.rotation_attenuation = fs.readFloat()
        self.bounce = fs.readFloat()
        self.friction = fs.readFloat()

        self.mode = fs.readSignedByte()

    def save(self, fs):
        fs.writeStr(self.name)
        fs.writeStr(self.name_e)

        if self.bone is None:
            fs.writeBoneIndex(-1)
        else:
            fs.writeBoneIndex(self.bone)

        fs.writeSignedByte(self.collision_group_number)
        fs.writeUnsignedShort(self.collision_group_mask)

        fs.writeSignedByte(self.type)
        fs.writeVector(self.size)

        fs.writeVector(self.location)
        fs.writeVector(self.rotation)

        fs.writeFloat(self.mass)
        fs.writeFloat(self.velocity_attenuation)
        fs.writeFloat(self.rotation_attenuation)
        fs.writeFloat(self.bounce)
        fs.writeFloat(self.friction)

        fs.writeSignedByte(self.mode)

class Joint:
    MODE_SPRING6DOF = 0
    def __init__(self):
        self.name = ''
        self.name_e = ''

        self.mode = 0

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
        self.name = fs.readStr()
        self.name_e = fs.readStr()

        self.mode = fs.readSignedByte()

        self.src_rigid = fs.readRigidIndex()
        self.dest_rigid = fs.readRigidIndex()
        if self.src_rigid == -1:
            self.src_rigid = None
        if self.dest_rigid == -1:
            self.dest_rigid = None

        self.location = fs.readVector(3)
        self.rotation = fs.readVector(3)

        self.minimum_location = fs.readVector(3)
        self.maximum_location = fs.readVector(3)
        self.minimum_rotation = fs.readVector(3)
        self.maximum_rotation = fs.readVector(3)

        self.spring_constant = fs.readVector(3)
        self.spring_rotation_constant = fs.readVector(3)

    def save(self, fs):
        fs.writeStr(self.name)
        fs.writeStr(self.name_e)

        fs.writeSignedByte(self.mode)

        if self.src_rigid is not None:
            fs.writeRigidIndex(self.src_rigid)
        else:
            fs.writeRigidIndex(-1)
        if self.dest_rigid is not None:
            fs.writeRigidIndex(self.dest_rigid)
        else:
            fs.writeRigidIndex(-1)

        fs.writeVector(self.location)
        fs.writeVector(self.rotation)

        fs.writeVector(self.minimum_location)
        fs.writeVector(self.maximum_location)
        fs.writeVector(self.minimum_rotation)
        fs.writeVector(self.maximum_rotation)

        fs.writeVector(self.spring_constant)
        fs.writeVector(self.spring_rotation_constant)



def load(path):
    with FileReadStream(path) as fs:
        logging.info('****************************************')
        logging.info(' mmd_tools.pmx module')
        logging.info('----------------------------------------')
        logging.info(' Start to load model data form a pmx file')
        logging.info('            by the mmd_tools.pmx modlue.')
        logging.info('')
        header = Header()
        header.load(fs)
        fs.setHeader(header)
        model = Model()
        try:
            model.load(fs)
        except struct.error as e:
            logging.error(' * Corrupted file: %s', e)
            #raise
        logging.info(' Finished loading.')
        logging.info('----------------------------------------')
        logging.info(' mmd_tools.pmx module')
        logging.info('****************************************')
        return model

def save(path, model, add_uv_count=0):
    with FileWriteStream(path) as fs:
        header = Header(model)
        header.additional_uvs = max(0, min(4, add_uv_count)) # UV1~UV4
        header.save(fs)
        fs.setHeader(header)
        model.save(fs)
