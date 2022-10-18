# -*- coding: utf-8 -*-

from typing import Optional, Union
import bpy

matmul = (lambda a, b: a*b) if bpy.app.version < (2, 80, 0) else (lambda a, b: a.__matmul__(b))

class Props: # For API changes of only name changed properties
    if bpy.app.version < (2, 80, 0):
        show_in_front = 'show_x_ray'
        display_type = 'draw_type'
        display_size = 'draw_size'
        empty_display_type = 'empty_draw_type'
        empty_display_size = 'empty_draw_size'
    else:
        show_in_front = 'show_in_front'
        display_type = 'display_type'
        display_size = 'display_size'
        empty_display_type = 'empty_display_type'
        empty_display_size = 'empty_display_size'


class __EditMode:
    def __init__(self, obj):
        if not isinstance(obj, bpy.types.Object):
            raise ValueError
        self.__prevMode = obj.mode
        self.__obj = obj
        self.__obj_select = obj.select
        with select_object(obj):
            if obj.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')

    def __enter__(self):
        return self.__obj.data

    def __exit__(self, type, value, traceback):
        if self.__prevMode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT') # update edited data
        bpy.ops.object.mode_set(mode=self.__prevMode)
        self.__obj.select = self.__obj_select

class __SelectObjects:
    def __init__(self, active_object, selected_objects=[]):
        if not isinstance(active_object, bpy.types.Object):
            raise ValueError
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

        for i in bpy.context.selected_objects:
            i.select = False

        self.__active_object = active_object
        self.__selected_objects = tuple(set(selected_objects)|set([active_object]))

        self.__hides = []
        scene = SceneOp(bpy.context)
        for i in self.__selected_objects:
            self.__hides.append(i.hide)
            scene.select_object(i)
        scene.active_object = active_object

    def __enter__(self):
        return self.__active_object

    def __exit__(self, type, value, traceback):
        for i, j in zip(self.__selected_objects, self.__hides):
            i.hide = j

def find_user_layer_collection(target_object: bpy.types.Object) -> Optional[bpy.types.LayerCollection]:
    context: bpy.types.Context = bpy.context
    scene_layer_collection: bpy.types.LayerCollection = context.view_layer.layer_collection

    def find_layer_collection_by_name(layer_collection: bpy.types.LayerCollection, name: str) -> Optional[bpy.types.LayerCollection]:
        if layer_collection.name == name:
            return layer_collection

        child_layer_collection: bpy.types.LayerCollection
        for child_layer_collection in layer_collection.children:
            found = find_layer_collection_by_name(child_layer_collection, name)
            if found is not None:
                return found

        return None

    user_collection: bpy.types.Collection
    for user_collection in target_object.users_collection:
        found = find_layer_collection_by_name(scene_layer_collection, user_collection.name)
        if found is not None:
            return found
    
    return None

class __ActivateLayerCollection:
    def __init__(self, target_layer_collection: Optional[bpy.types.LayerCollection]):
        self.__original_layer_collection = bpy.context.view_layer.active_layer_collection
        self.__target_layer_collection = target_layer_collection if target_layer_collection else self.__original_layer_collection

    def __enter__(self):
        if bpy.context.view_layer.active_layer_collection.name != self.__target_layer_collection.name:
            bpy.context.view_layer.active_layer_collection = self.__target_layer_collection
        return self.__target_layer_collection

    def __exit__(self, _type, _value, _traceback):
        if bpy.context.view_layer.active_layer_collection.name != self.__original_layer_collection.name:
            bpy.context.view_layer.active_layer_collection = self.__original_layer_collection

def addon_preferences(attrname, default=None):
    if hasattr(bpy.context, 'preferences'):
        addon = bpy.context.preferences.addons.get(__package__, None)
    else:
        addon = bpy.context.user_preferences.addons.get(__package__, None)
    return getattr(addon.preferences, attrname, default) if addon else default

def setParent(obj, parent):
    with select_object(parent, objects=[parent, obj]):
        bpy.ops.object.parent_set(type='OBJECT', xmirror=False, keep_transform=False)

def setParentToBone(obj, parent, bone_name):
    with select_object(parent, objects=[parent, obj]):
        bpy.ops.object.mode_set(mode='POSE')
        parent.data.bones.active = parent.data.bones[bone_name]
        bpy.ops.object.parent_set(type='BONE', xmirror=False, keep_transform=False)
        bpy.ops.object.mode_set(mode='OBJECT')

def edit_object(obj):
    """ Set the object interaction mode to 'EDIT'

     It is recommended to use 'edit_object' with 'with' statement like the following code.

        with edit_object:
            some functions...
    """
    return __EditMode(obj)

def select_object(obj, objects=[]):
    """ Select objects.

     It is recommended to use 'select_object' with 'with' statement like the following code.
     This function can select "hidden" objects safely.

        with select_object(obj):
            some functions...
    """
    return __SelectObjects(obj, objects)

def activate_layer_collection(target: Union[bpy.types.Object, bpy.types.LayerCollection, None]):
    if isinstance(target,  bpy.types.Object):
        layer_collection = find_user_layer_collection(target)
    elif isinstance(target,  bpy.types.LayerCollection):
        layer_collection = target
    else:
        layer_collection = None

    return __ActivateLayerCollection(layer_collection)

def duplicateObject(obj, total_len):
    for i in bpy.context.selected_objects:
        i.select = False
    obj.select = True
    assert(len(bpy.context.selected_objects) == 1)
    assert(bpy.context.selected_objects[0] == obj)
    last_selected = objs = [obj]
    while len(objs) < total_len:
        bpy.ops.object.duplicate()
        objs.extend(bpy.context.selected_objects)
        remain = total_len - len(objs) - len(bpy.context.selected_objects)
        if remain < 0:
            last_selected = bpy.context.selected_objects
            for i in range(-remain):
                last_selected[i].select = False
        else:
            for i in range(min(remain, len(last_selected))):
                last_selected[i].select = True
        last_selected = bpy.context.selected_objects
    assert(len(objs) == total_len)
    return objs

def makeCapsuleBak(segment=16, ring_count=8, radius=1.0, height=1.0, target_scene=None):
    import math
    target_scene = SceneOp(target_scene)
    mesh = bpy.data.meshes.new(name='Capsule')
    meshObj = bpy.data.objects.new(name='Capsule', object_data=mesh)
    vertices = []
    top = (0, 0, height/2+radius)
    vertices.append(top)

    f = lambda i: radius*i/ring_count
    for i in range(ring_count, 0, -1):
        z = f(i-1)
        t = math.sqrt(radius**2 - z**2)
        for j in range(segment):
            theta = 2*math.pi/segment*j
            x = t * math.sin(-theta)
            y = t * math.cos(-theta)
            vertices.append((x,y,z+height/2))

    for i in range(ring_count):
        z = -f(i)
        t = math.sqrt(radius**2 - z**2)
        for j in range(segment):
            theta = 2*math.pi/segment*j
            x = t * math.sin(-theta)
            y = t * math.cos(-theta)
            vertices.append((x,y,z-height/2))

    bottom = (0, 0, -(height/2+radius))
    vertices.append(bottom)

    faces = []
    for i in range(1, segment):
        faces.append([0, i, i+1])
    faces.append([0, segment, 1])
    offset = segment + 1
    for i in range(ring_count*2-1):
        for j in range(segment-1):
            t = offset + j
            faces.append([t-segment, t, t+1, t-segment+1])
        faces.append([offset-1, offset+segment-1, offset, offset-segment])
        offset += segment
    for i in range(segment-1):
        t = offset + i
        faces.append([t-segment, offset, t-segment+1])
    faces.append([offset-1, offset, offset-segment])

    mesh.from_pydata(vertices, [], faces)
    target_scene.link_object(meshObj)
    return meshObj

def createObject(name='Object', object_data=None, target_scene=None):
    target_scene = SceneOp(target_scene)
    obj = bpy.data.objects.new(name=name, object_data=object_data)
    target_scene.link_object(obj)
    target_scene.active_object = obj
    return obj

def makeSphere(segment=8, ring_count=5, radius=1.0, target_object=None):
    import bmesh
    if target_object is None:
        target_object = createObject(name='Sphere')

    mesh = target_object.data
    bm = bmesh.new()
    if bpy.app.version >= (3, 0, 0):
        bmesh.ops.create_uvsphere(
            bm,
            u_segments=segment,
            v_segments=ring_count,
            radius=radius,
            )
    else:
        # SUPPORT_UNTIL: 3.3 LTS
        bmesh.ops.create_uvsphere(
            bm,
            u_segments=segment,
            v_segments=ring_count,
            diameter=radius,
            )
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    return target_object

def makeBox(size=(1,1,1), target_object=None):
    import bmesh
    from mathutils import Matrix
    if target_object is None:
        target_object = createObject(name='Box')

    mesh = target_object.data
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm,
        size=2,
        matrix=Matrix([[size[0],0,0,0], [0,size[1],0,0], [0,0,size[2],0], [0,0,0,1]]),
        )
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(mesh)
    bm.free()
    return target_object

def makeCapsule(segment=8, ring_count=2, radius=1.0, height=1.0, target_object=None):
    import bmesh
    import math
    if target_object is None:
        target_object = createObject(name='Capsule')
    height = max(height, 1e-3)

    mesh = target_object.data
    bm = bmesh.new()
    verts = bm.verts
    top = (0, 0, height/2+radius)
    verts.new(top)

    #f = lambda i: radius*i/ring_count
    f = lambda i: radius*math.sin(0.5*math.pi*i/ring_count)
    for i in range(ring_count, 0, -1):
        z = f(i-1)
        t = math.sqrt(radius**2 - z**2)
        for j in range(segment):
            theta = 2*math.pi/segment*j
            x = t * math.sin(-theta)
            y = t * math.cos(-theta)
            verts.new((x,y,z+height/2))

    for i in range(ring_count):
        z = -f(i)
        t = math.sqrt(radius**2 - z**2)
        for j in range(segment):
            theta = 2*math.pi/segment*j
            x = t * math.sin(-theta)
            y = t * math.cos(-theta)
            verts.new((x,y,z-height/2))

    bottom = (0, 0, -(height/2+radius))
    verts.new(bottom)
    if hasattr(verts, 'ensure_lookup_table'):
        verts.ensure_lookup_table()

    faces = bm.faces
    for i in range(1, segment):
        faces.new([verts[x] for x in (0, i, i+1)])
    faces.new([verts[x] for x in (0, segment, 1)])
    offset = segment + 1
    for i in range(ring_count*2-1):
        for j in range(segment-1):
            t = offset + j
            faces.new([verts[x] for x in (t-segment, t, t+1, t-segment+1)])
        faces.new([verts[x] for x in (offset-1, offset+segment-1, offset, offset-segment)])
        offset += segment
    for i in range(segment-1):
        t = offset + i
        faces.new([verts[x] for x in (t-segment, offset, t-segment+1)])
    faces.new([verts[x] for x in (offset-1, offset, offset-segment)])

    for f in bm.faces:
        f.smooth = True
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    return target_object


class ObjectOp:

    def __init__(self, obj):
        self.__obj = obj

    def __clean_drivers(self, key):
        for d in getattr(key.id_data.animation_data, 'drivers', ()):
            if d.data_path.startswith(key.path_from_id()):
                key.id_data.driver_remove(d.data_path, -1)

    if bpy.app.version < (2, 75, 0):
        def shape_key_remove(self, key):
            obj = self.__obj
            assert(key.id_data == obj.data.shape_keys)
            key_blocks = key.id_data.key_blocks
            relative_key_map = {k.name:getattr(k.relative_key, 'name', '') for k in key_blocks}
            last_index, obj.active_shape_key_index = obj.active_shape_key_index, key_blocks.find(key.name)
            if last_index >= obj.active_shape_key_index:
                last_index = max(0, last_index-1)
            bpy.context.scene.objects.active, last = obj, bpy.context.scene.objects.active
            self.__clean_drivers(key)
            bpy.ops.object.shape_key_remove()
            bpy.context.scene.objects.active = last
            for k in key_blocks:
                k.relative_key = key_blocks.get(relative_key_map[k.name], key_blocks[0])
            obj.active_shape_key_index = min(last_index, len(key_blocks)-1)
    else:
        def shape_key_remove(self, key):
            obj = self.__obj
            assert(key.id_data == obj.data.shape_keys)
            key_blocks = key.id_data.key_blocks
            last_index = obj.active_shape_key_index
            if last_index >= key_blocks.find(key.name):
                last_index = max(0, last_index-1)
            self.__clean_drivers(key)
            obj.shape_key_remove(key)
            obj.active_shape_key_index = min(last_index, len(key_blocks)-1)

class TransformConstraintOp:

    __MIN_MAX_MAP = {} if bpy.app.version < (2, 71, 0) else {'ROTATION':'_rot', 'SCALE':'_scale'}

    @staticmethod
    def create(constraints, name, map_type):
        c = constraints.get(name, None)
        if c and c.type != 'TRANSFORM':
            constraints.remove(c)
            c = None
        if c is None:
            c = constraints.new('TRANSFORM')
            c.name = name
        c.use_motion_extrapolate = True
        c.target_space = c.owner_space = 'LOCAL'
        c.map_from = c.map_to = map_type
        c.map_to_x_from = 'X'
        c.map_to_y_from = 'Y'
        c.map_to_z_from = 'Z'
        c.influence = 1
        return c

    @classmethod
    def min_max_attributes(cls, map_type, name_id=''):
        key = (map_type, name_id)
        ret = cls.__MIN_MAX_MAP.get(key, None)
        if ret is None:
            defaults = (i+j+k for i in ('from_', 'to_') for j in ('min_', 'max_') for k in 'xyz')
            extension = cls.__MIN_MAX_MAP.get(map_type, '')
            ret = cls.__MIN_MAX_MAP[key] = tuple(n+extension for n in defaults if name_id in n)
        return ret

    @classmethod
    def update_min_max(cls, constraint, value, influence=1):
        c = constraint
        if not c or c.type != 'TRANSFORM':
            return

        for attr in cls.min_max_attributes(c.map_from, 'from_min'):
            setattr(c, attr, -value)
        for attr in cls.min_max_attributes(c.map_from, 'from_max'):
            setattr(c, attr, value)

        if influence is None:
            return

        for attr in cls.min_max_attributes(c.map_to, 'to_min'):
            setattr(c, attr, -value*influence)
        for attr in cls.min_max_attributes(c.map_to, 'to_max'):
            setattr(c, attr, value*influence)

if bpy.app.version < (2, 80, 0):
    class SceneOp:
        def __init__(self, context=None):
            self.__context = context or bpy.context
            self.__scene = self.__context.scene

        def __ensure_selectable(self, obj):
            obj.hide = obj.hide_select = False
            if obj not in self.__context.selectable_objects:
                selected_objects = self.__context.selected_objects
                self.__scene.layers[next(i for i, enabled in enumerate(obj.layers) if enabled)] = True
                if len(self.__context.selected_objects) != len(selected_objects):
                    for i in self.__context.selected_objects:
                        if i not in selected_objects:
                            i.select = False

        def select_object(self, obj):
            self.__ensure_selectable(obj)
            obj.select = True

        def link_object(self, obj):
            self.__scene.objects.link(obj)

        @property
        def active_object(self):
            return self.__scene.objects.active

        @active_object.setter
        def active_object(self, obj):
            self.select_object(obj)
            self.__scene.objects.active = obj

        @property
        def id_scene(self):
            return self.__scene

        @property
        def id_objects(self):
            return self.__scene.objects
else:
    class SceneOp:
        def __init__(self, context=None):
            self.__context = context or bpy.context
            self.__scene = self.__context.scene
            self.__collection = self.__context.collection
            self.__view_layer = self.__context.view_layer

        def __ensure_selectable(self, obj):
            obj.hide_viewport = obj.hide_select = False
            obj.hide_set(False)
            if obj not in self.__context.selectable_objects:
                def __unhide(lc):
                    lc.hide_viewport = lc.collection.hide_viewport = lc.collection.hide_select = False
                    return True
                def __layer_check(layer_collection):
                    for lc in layer_collection.children:
                        if __layer_check(lc):
                            return __unhide(lc)
                    if obj in layer_collection.collection.objects.values():
                        if layer_collection.exclude:
                            layer_collection.exclude = False
                        return True
                    return False
                selected_objects = self.__context.selected_objects
                __layer_check(self.__view_layer.layer_collection)
                if len(self.__context.selected_objects) != len(selected_objects):
                    for i in self.__context.selected_objects:
                        if i not in selected_objects:
                            i.select_set(False)

        def select_object(self, obj):
            self.__ensure_selectable(obj)
            obj.select_set(True)

        def link_object(self, obj):
            self.__collection.objects.link(obj)

        @property
        def active_object(self):
            return self.__view_layer.objects.active

        @active_object.setter
        def active_object(self, obj):
            self.select_object(obj)
            self.__view_layer.objects.active = obj

        @property
        def id_scene(self):
            return self.__scene

        @property
        def id_objects(self):
            return self.__scene.objects

