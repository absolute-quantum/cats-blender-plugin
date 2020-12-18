# -*- coding: utf-8 -*-
import struct
import collections

class InvalidFileError(Exception):
    pass

## vmd仕様の文字列をstringに変換
def _toShiftJisString(byteString):
    return byteString.split(b'\x00')[0].decode('shift_jis', errors='replace')

def _toShiftJisBytes(string):
    return string.encode('shift_jis', errors='replace')


class Header:
    VMD_SIGN = b'Vocaloid Motion Data 0002'
    def __init__(self):
        self.signature = None
        self.model_name = ''

    def load(self, fin):
        self.signature, = struct.unpack('<30s', fin.read(30))
        if self.signature[:len(self.VMD_SIGN)] != self.VMD_SIGN:
            raise InvalidFileError('File signature "%s" is invalid.'%self.signature)
        self.model_name = _toShiftJisString(struct.unpack('<20s', fin.read(20))[0])

    def save(self, fin):
        fin.write(struct.pack('<30s', self.VMD_SIGN))
        fin.write(struct.pack('<20s', _toShiftJisBytes(self.model_name)))

    def __repr__(self):
        return '<Header model_name %s>'%(self.model_name)


class BoneFrameKey:
    def __init__(self):
        self.frame_number = 0
        self.location = []
        self.rotation = []
        self.interp = []

    def load(self, fin):
        self.frame_number, = struct.unpack('<L', fin.read(4))
        self.location = list(struct.unpack('<fff', fin.read(4*3)))
        self.rotation = list(struct.unpack('<ffff', fin.read(4*4)))
        if not any(self.rotation):
            self.rotation = (0, 0, 0, 1)
        self.interp = list(struct.unpack('<64b', fin.read(64)))

    def save(self, fin):
        fin.write(struct.pack('<L', self.frame_number))
        fin.write(struct.pack('<fff', *self.location))
        fin.write(struct.pack('<ffff', *self.rotation))
        fin.write(struct.pack('<64b', *self.interp))

    def __repr__(self):
        return '<BoneFrameKey frame %s, loa %s, rot %s>'%(
            str(self.frame_number),
            str(self.location),
            str(self.rotation),
            )


class ShapeKeyFrameKey:
    def __init__(self):
        self.frame_number = 0
        self.weight = 0.0

    def load(self, fin):
        self.frame_number, = struct.unpack('<L', fin.read(4))
        self.weight, = struct.unpack('<f', fin.read(4))

    def save(self, fin):
        fin.write(struct.pack('<L', self.frame_number))
        fin.write(struct.pack('<f', self.weight))

    def __repr__(self):
        return '<ShapeKeyFrameKey frame %s, weight %s>'%(
            str(self.frame_number),
            str(self.weight),
            )


class CameraKeyFrameKey:
    def __init__(self):
        self.frame_number = 0
        self.distance = 0.0
        self.location = []
        self.rotation = []
        self.interp = []
        self.angle = 0.0
        self.persp = True

    def load(self, fin):
        self.frame_number, = struct.unpack('<L', fin.read(4))
        self.distance, = struct.unpack('<f', fin.read(4))
        self.location = list(struct.unpack('<fff', fin.read(4*3)))
        self.rotation = list(struct.unpack('<fff', fin.read(4*3)))
        self.interp = list(struct.unpack('<24b', fin.read(24)))
        self.angle, = struct.unpack('<L', fin.read(4))
        self.persp, = struct.unpack('<b', fin.read(1))
        self.persp = (self.persp == 0)

    def save(self, fin):
        fin.write(struct.pack('<L', self.frame_number))
        fin.write(struct.pack('<f', self.distance))
        fin.write(struct.pack('<fff', *self.location))
        fin.write(struct.pack('<fff', *self.rotation))
        fin.write(struct.pack('<24b', *self.interp))
        fin.write(struct.pack('<L', self.angle))
        fin.write(struct.pack('<b', 0 if self.persp else 1))

    def __repr__(self):
        return '<CameraKeyFrameKey frame %s, distance %s, loc %s, rot %s, angle %s, persp %s>'%(
            str(self.frame_number),
            str(self.distance),
            str(self.location),
            str(self.rotation),
            str(self.angle),
            str(self.persp),
            )


class LampKeyFrameKey:
    def __init__(self):
        self.frame_number = 0
        self.color = []
        self.direction = []

    def load(self, fin):
        self.frame_number, = struct.unpack('<L', fin.read(4))
        self.color = list(struct.unpack('<fff', fin.read(4*3)))
        self.direction = list(struct.unpack('<fff', fin.read(4*3)))

    def save(self, fin):
        fin.write(struct.pack('<L', self.frame_number))
        fin.write(struct.pack('<fff', *self.color))
        fin.write(struct.pack('<fff', *self.direction))

    def __repr__(self):
        return '<LampKeyFrameKey frame %s, color %s, direction %s>'%(
            str(self.frame_number),
            str(self.color),
            str(self.direction),
            )


class SelfShadowFrameKey:
    def __init__(self):
        self.frame_number = 0
        self.mode = 0 # 0: none, 1: mode1, 2: mode2
        self.distance = 0.0

    def load(self, fin):
        self.frame_number, = struct.unpack('<L', fin.read(4))
        self.mode, = struct.unpack('<b', fin.read(1))
        if self.mode not in range(3):
            print(' * Invalid self shadow mode %d at frame %d'%(self.mode, self.frame_number))
            raise struct.error
        distance, = struct.unpack('<f', fin.read(4))
        self.distance = 10000 - distance*100000
        print('    ', self)

    def save(self, fin):
        fin.write(struct.pack('<L', self.frame_number))
        fin.write(struct.pack('<b', self.mode))
        distance = (10000 - self.distance)/100000
        fin.write(struct.pack('<f', distance))

    def __repr__(self):
        return '<SelfShadowFrameKey frame %s, mode %s, distance %s>'%(
            str(self.frame_number),
            str(self.mode),
            str(self.distance),
            )


class PropertyFrameKey:
    def __init__(self):
        self.frame_number = 0
        self.visible = True
        self.ik_states = [] # list of (ik_name, enable/disable)

    def load(self, fin):
        self.frame_number, = struct.unpack('<L', fin.read(4))
        self.visible, = struct.unpack('<b', fin.read(1))
        count, = struct.unpack('<L', fin.read(4))
        for i in range(count):
            ik_name = _toShiftJisString(struct.unpack('<20s', fin.read(20))[0])
            state, = struct.unpack('<b', fin.read(1))
            self.ik_states.append((ik_name, state))

    def save(self, fin):
        fin.write(struct.pack('<L', self.frame_number))
        fin.write(struct.pack('<b', 1 if self.visible else 0))
        fin.write(struct.pack('<L', len(self.ik_states)))
        for ik_name, state in self.ik_states:
            fin.write(struct.pack('<20s', _toShiftJisBytes(ik_name)))
            fin.write(struct.pack('<b', 1 if state else 0))

    def __repr__(self):
        return '<PropertyFrameKey frame %s, visible %s, ik_states %s>'%(
            str(self.frame_number),
            str(self.visible),
            str(self.ik_states),
            )


class _AnimationBase(collections.defaultdict):
    def __init__(self):
        collections.defaultdict.__init__(self, list)

    @staticmethod
    def frameClass():
        raise NotImplementedError

    def load(self, fin):
        count, = struct.unpack('<L', fin.read(4))
        print('loading %s... %d'%(self.__class__.__name__, count))
        for i in range(count):
            name = _toShiftJisString(struct.unpack('<15s', fin.read(15))[0])
            cls = self.frameClass()
            frameKey = cls()
            frameKey.load(fin)
            self[name].append(frameKey)

    def save(self, fin):
        count = sum([len(i) for i in self.values()])
        fin.write(struct.pack('<L', count))
        for name, frameKeys in self.items():
            name_data = struct.pack('<15s', _toShiftJisBytes(name))
            for frameKey in frameKeys:
                fin.write(name_data)
                frameKey.save(fin)


class _AnimationListBase(list):
    def __init__(self):
        list.__init__(self)

    @staticmethod
    def frameClass():
        raise NotImplementedError

    def load(self, fin):
        count, = struct.unpack('<L', fin.read(4))
        print('loading %s... %d'%(self.__class__.__name__, count))
        for i in range(count):
            cls = self.frameClass()
            frameKey = cls()
            frameKey.load(fin)
            self.append(frameKey)

    def save(self, fin):
        fin.write(struct.pack('<L', len(self)))
        for frameKey in self:
            frameKey.save(fin)


class BoneAnimation(_AnimationBase):
    def __init__(self):
        _AnimationBase.__init__(self)

    @staticmethod
    def frameClass():
        return BoneFrameKey


class ShapeKeyAnimation(_AnimationBase):
    def __init__(self):
        _AnimationBase.__init__(self)

    @staticmethod
    def frameClass():
        return ShapeKeyFrameKey


class CameraAnimation(_AnimationListBase):
    def __init__(self):
        _AnimationListBase.__init__(self)

    @staticmethod
    def frameClass():
        return CameraKeyFrameKey


class LampAnimation(_AnimationListBase):
    def __init__(self):
        _AnimationListBase.__init__(self)

    @staticmethod
    def frameClass():
        return LampKeyFrameKey


class SelfShadowAnimation(_AnimationListBase):
    def __init__(self):
        _AnimationListBase.__init__(self)

    @staticmethod
    def frameClass():
        return SelfShadowFrameKey


class PropertyAnimation(_AnimationListBase):
    def __init__(self):
        _AnimationListBase.__init__(self)

    @staticmethod
    def frameClass():
        return PropertyFrameKey


class File:
    def __init__(self):
        self.filepath = None
        self.header = None
        self.boneAnimation = None
        self.shapeKeyAnimation = None
        self.cameraAnimation = None
        self.lampAnimation = None
        self.selfShadowAnimation = None
        self.propertyAnimation = None

    def load(self, **args):
        path = args['filepath']

        with open(path, 'rb') as fin:
            self.filepath = path
            self.header = Header()
            self.boneAnimation = BoneAnimation()
            self.shapeKeyAnimation = ShapeKeyAnimation()
            self.cameraAnimation = CameraAnimation()
            self.lampAnimation = LampAnimation()
            self.selfShadowAnimation = SelfShadowAnimation()
            self.propertyAnimation = PropertyAnimation()

            self.header.load(fin)
            try:
                self.boneAnimation.load(fin)
                self.shapeKeyAnimation.load(fin)
                self.cameraAnimation.load(fin)
                self.lampAnimation.load(fin)
                self.selfShadowAnimation.load(fin)
                self.propertyAnimation.load(fin)
            except struct.error:
                pass # no valid camera/lamp data

    def save(self, **args):
        path = args.get('filepath', self.filepath)

        header = self.header or Header()
        boneAnimation = self.boneAnimation or BoneAnimation()
        shapeKeyAnimation = self.shapeKeyAnimation or ShapeKeyAnimation()
        cameraAnimation = self.cameraAnimation or CameraAnimation()
        lampAnimation = self.lampAnimation or LampAnimation()
        selfShadowAnimation = self.selfShadowAnimation or SelfShadowAnimation()
        propertyAnimation = self.propertyAnimation or PropertyAnimation()

        with open(path, 'wb') as fin:
            header.save(fin)
            boneAnimation.save(fin)
            shapeKeyAnimation.save(fin)
            cameraAnimation.save(fin)
            lampAnimation.save(fin)
            selfShadowAnimation.save(fin)
            propertyAnimation.save(fin)

