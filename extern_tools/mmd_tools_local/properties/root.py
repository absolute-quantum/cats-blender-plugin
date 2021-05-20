# -*- coding: utf-8 -*-
""" MMDモデルパラメータ用Prop
"""
import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, CollectionProperty, FloatProperty, IntProperty, StringProperty, EnumProperty

from mmd_tools_local import register_wrap
from mmd_tools_local import utils
from mmd_tools_local.bpyutils import SceneOp
from mmd_tools_local.core.material import FnMaterial
from mmd_tools_local.core.sdef import FnSDEF
from mmd_tools_local.properties.morph import BoneMorph
from mmd_tools_local.properties.morph import MaterialMorph
from mmd_tools_local.properties.morph import VertexMorph
from mmd_tools_local.properties.morph import UVMorph
from mmd_tools_local.properties.morph import GroupMorph
import mmd_tools_local.core.model as mmd_model

def __driver_variables(id_data, path, index=-1):
    d = id_data.driver_add(path, index)
    variables = d.driver.variables
    for x in variables:
        variables.remove(x)
    return d.driver, variables

def __add_single_prop(variables, id_obj, data_path, prefix):
    var = variables.new()
    var.name = prefix + str(len(variables))
    var.type = 'SINGLE_PROP'
    target = var.targets[0]
    target.id_type = 'OBJECT'
    target.id = id_obj
    target.data_path = data_path
    return var

def _toggleUsePropertyDriver(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    bones = getattr((rig.armature() or root).pose, 'bones', ())
    ik_map = {bones[c.subtarget]:(b, c) for b in bones for c in b.constraints if c.type == 'IK' and c.is_valid and c.subtarget in bones}
    prop_hide_viewport = 'hide_viewport' if hasattr(root, 'hide_viewport') else 'hide'
    if self.use_property_driver:
        for ik, (b, c) in ik_map.items():
            driver, variables = __driver_variables(c, 'influence')
            driver.expression = '%s' % __add_single_prop(variables, ik.id_data, ik.path_from_id('mmd_ik_toggle'), 'use_ik').name
            b = b if c.use_tail else b.parent
            for b in ([b]+b.parent_recursive)[:c.chain_count]:
                c = next((c for c in b.constraints if c.type == 'LIMIT_ROTATION' and not c.mute), None)
                if c:
                    driver, variables = __driver_variables(c, 'influence')
                    driver.expression = '%s' % __add_single_prop(variables, ik.id_data, ik.path_from_id('mmd_ik_toggle'), 'use_ik').name
        for i in rig.meshes():
            for prop_hide in (prop_hide_viewport, 'hide_render'):
                driver, variables = __driver_variables(i, prop_hide)
                driver.expression = 'not %s' % __add_single_prop(variables, root, 'mmd_root.show_meshes', 'show').name
    else:
        for ik, (b, c) in ik_map.items():
            c.driver_remove('influence')
            b = b if c.use_tail else b.parent
            for b in ([b]+b.parent_recursive)[:c.chain_count]:
                c = next((c for c in b.constraints if c.type == 'LIMIT_ROTATION' and not c.mute), None)
                if c: c.driver_remove('influence')
        for i in rig.meshes():
            for prop_hide in (prop_hide_viewport, 'hide_render'):
                i.driver_remove(prop_hide)

#===========================================
# Callback functions
#===========================================
def _toggleUseToonTexture(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    use_toon = self.use_toon_texture
    for i in rig.meshes():
        for m in i.data.materials:
            if m is None:
                continue
            FnMaterial(m).use_toon_texture(use_toon)

def _toggleUseSphereTexture(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    use_sphere = self.use_sphere_texture
    for i in rig.meshes():
        for m in i.data.materials:
            if m is None:
                continue
            FnMaterial(m).use_sphere_texture(use_sphere, i)

def _toggleUseSDEF(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    mute_sdef = not self.use_sdef
    for i in rig.meshes():
        FnSDEF.mute_sdef_set(i, mute_sdef)

def _toggleVisibilityOfMeshes(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    hide = not self.show_meshes
    for i in rig.meshes():
        i.hide = i.hide_render = hide
    if hide and not getattr(context, 'active_object', True):
        SceneOp(context).active_object = root

def _show_meshes_get(prop):
    return prop.get('show_meshes', True)

def _show_meshes_set(prop, v):
    if v != prop.get('show_meshes', None):
        prop['show_meshes'] = v
        _toggleVisibilityOfMeshes(prop, bpy.context)

def _toggleVisibilityOfRigidBodies(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    hide = not self.show_rigid_bodies
    for i in rig.rigidBodies():
        i.hide = hide
    if hide and context.active_object is None:
        SceneOp(context).active_object = root

def _toggleVisibilityOfJoints(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    hide = not self.show_joints
    for i in rig.joints():
        i.hide = hide
    if hide and context.active_object is None:
        SceneOp(context).active_object = root

def _toggleVisibilityOfTemporaryObjects(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    hide = not self.show_temporary_objects
    for i in rig.temporaryObjects(rigid_track_only=True):
        i.hide = hide
    if hide and context.active_object is None:
        SceneOp(context).active_object = root

def _toggleShowNamesOfRigidBodies(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    for i in rig.rigidBodies():
        i.show_name = root.mmd_root.show_names_of_rigid_bodies

def _toggleShowNamesOfJoints(self, context):
    root = self.id_data
    rig = mmd_model.Model(root)
    for i in rig.joints():
        i.show_name = root.mmd_root.show_names_of_joints

def _setVisibilityOfMMDRigArmature(prop, v):
    obj = prop.id_data
    rig = mmd_model.Model(obj)
    arm = rig.armature()
    if arm is None:
        return
    if bpy.context.active_object == arm:
        SceneOp(bpy.context).active_object = obj
    arm.hide = not v

def _getVisibilityOfMMDRigArmature(prop):
    if prop.id_data.mmd_type != 'ROOT':
        return False
    rig = mmd_model.Model(prop.id_data)
    arm = rig.armature()
    return not (arm is None or arm.hide)

def _setActiveRigidbodyObject(prop, v):
    obj = SceneOp(bpy.context).id_objects[v]
    if mmd_model.isRigidBodyObject(obj):
        obj.hide = False
        utils.selectAObject(obj)
    prop['active_rigidbody_object_index'] = v

def _getActiveRigidbodyObject(prop):
    objects = SceneOp(bpy.context).id_objects
    active_obj = objects.active
    if mmd_model.isRigidBodyObject(active_obj):
        prop['active_rigidbody_object_index'] = objects.find(active_obj.name)
    return prop.get('active_rigidbody_object_index', 0)

def _setActiveJointObject(prop, v):
    obj = SceneOp(bpy.context).id_objects[v]
    if mmd_model.isJointObject(obj):
        obj.hide = False
        utils.selectAObject(obj)
    prop['active_joint_object_index'] = v

def _getActiveJointObject(prop):
    objects = SceneOp(bpy.context).id_objects
    active_obj = objects.active
    if mmd_model.isJointObject(active_obj):
        prop['active_joint_object_index'] = objects.find(active_obj.name)
    return prop.get('active_joint_object_index', 0)

def _setActiveMorph(prop, v):
    if 'active_morph_indices' not in prop:
        prop['active_morph_indices'] = [0]*5
    prop['active_morph_indices'][prop.get('active_morph_type', 3)] = v

def _getActiveMorph(prop):
    if 'active_morph_indices' in prop:
        return prop['active_morph_indices'][prop.get('active_morph_type', 3)]
    return 0

def _setActiveMeshObject(prop, v):
    obj = SceneOp(bpy.context).id_objects[v]
    if obj.type == 'MESH' and obj.mmd_type == 'NONE':
        obj.hide = False
        utils.selectAObject(obj)
    prop['active_mesh_index'] = v

def _getActiveMeshObject(prop):
    objects = SceneOp(bpy.context).id_objects
    active_obj = objects.active
    if (active_obj and active_obj.type == 'MESH'
            and active_obj.mmd_type == 'NONE'):
        prop['active_mesh_index'] = objects.find(active_obj.name)
    return prop.get('active_mesh_index', -1)

#===========================================
# Property classes
#===========================================

@register_wrap
class MMDDisplayItem(PropertyGroup):
    """ PMX 表示項目(表示枠内の1項目)
    """
    type = EnumProperty(
        name='Type',
        description='Select item type',
        items = [
            ('BONE', 'Bone', '', 1),
            ('MORPH', 'Morph', '', 2),
            ],
        )

    morph_type = EnumProperty(
        name='Morph Type',
        description='Select morph type',
        items = [
            ('material_morphs', 'Material', 'Material Morphs', 0),
            ('uv_morphs', 'UV', 'UV Morphs', 1),
            ('bone_morphs', 'Bone', 'Bone Morphs', 2),
            ('vertex_morphs', 'Vertex', 'Vertex Morphs', 3),
            ('group_morphs', 'Group', 'Group Morphs', 4),
            ],
        default='vertex_morphs',
        )

@register_wrap
class MMDDisplayItemFrame(PropertyGroup):
    """ PMX 表示枠

     PMXファイル内では表示枠がリストで格納されています。
    """
    name_e = StringProperty(
        name='Name(Eng)',
        description='English Name',
        default='',
        )

    ## 特殊枠フラグ
    # 特殊枠はファイル仕様上の固定枠(削除、リネーム不可)
    is_special = BoolProperty(
        name='Special',
        description='Is special',
        default=False,
        )

    ## 表示項目のリスト
    data = CollectionProperty(
        name='Display Items',
        type=MMDDisplayItem,
        )

    ## 現在アクティブな項目のインデックス
    active_item = IntProperty(
        name='Active Display Item',
        min=0,
        default=0,
        )


@register_wrap
class MMDRoot(PropertyGroup):
    """ MMDモデルデータ

     モデルルート用に作成されたEmtpyオブジェクトで使用します
    """
    name = StringProperty(
        name='Name',
        description='The name of the MMD model',
        default='',
        )

    name_e = StringProperty(
        name='Name (English)',
        description='The english name of the MMD model',
        default='',
        )

    comment_text = StringProperty(
        name='Comment',
        description='The text datablock of the comment',
        default='',
        )

    comment_e_text = StringProperty(
        name='Comment (English)',
        description='The text datablock of the english comment',
        default='',
        )

    show_meshes = BoolProperty(
        name='Show Meshes',
        description='Show all meshes of the MMD model',
        #get=_show_meshes_get,
        #set=_show_meshes_set,
        update=_toggleVisibilityOfMeshes,
        )

    show_rigid_bodies = BoolProperty(
        name='Show Rigid Bodies',
        description='Show all rigid bodies of the MMD model',
        update=_toggleVisibilityOfRigidBodies,
        )

    show_joints = BoolProperty(
        name='Show Joints',
        description='Show all joints of the MMD model',
        update=_toggleVisibilityOfJoints,
        )

    show_temporary_objects = BoolProperty(
        name='Show Temps',
        description='Show all temporary objects of the MMD model',
        update=_toggleVisibilityOfTemporaryObjects,
        )

    show_armature = BoolProperty(
        name='Show Armature',
        description='Show the armature object of the MMD model',
        get=_getVisibilityOfMMDRigArmature,
        set=_setVisibilityOfMMDRigArmature,
        )

    show_names_of_rigid_bodies = BoolProperty(
        name='Show Rigid Body Names',
        description='Show rigid body names',
        update=_toggleShowNamesOfRigidBodies,
        )

    show_names_of_joints = BoolProperty(
        name='Show Joint Names',
        description='Show joint names',
        update=_toggleShowNamesOfJoints,
        )

    use_toon_texture = BoolProperty(
        name='Use Toon Texture',
        description='Use toon texture',
        update=_toggleUseToonTexture,
        default=True,
        )

    use_sphere_texture = BoolProperty(
        name='Use Sphere Texture',
        description='Use sphere texture',
        update=_toggleUseSphereTexture,
        default=True,
        )

    use_sdef = BoolProperty(
        name='Use SDEF',
        description='Use SDEF',
        update=_toggleUseSDEF,
        default=True,
        )

    use_property_driver = BoolProperty(
        name='Use Property Driver',
        description='Setup drivers for MMD property animation (Visibility and IK toggles)',
        update=_toggleUsePropertyDriver,
        default=False,
        )

    is_built = BoolProperty(
        name='Is Built',
        )

    active_rigidbody_index = IntProperty(
        name='Active Rigidbody Index',
        min=0,
        get=_getActiveRigidbodyObject,
        set=_setActiveRigidbodyObject,
        )

    active_joint_index = IntProperty(
        name='Active Joint Index',
        min=0,
        get=_getActiveJointObject,
        set=_setActiveJointObject,
        )

    #*************************
    # Display Items
    #*************************
    display_item_frames = CollectionProperty(
        name='Display Frames',
        type=MMDDisplayItemFrame,
        )

    active_display_item_frame = IntProperty(
        name='Active Display Item Frame',
        min=0,
        default=0,
        )

    #*************************
    # Morph
    #*************************
    material_morphs = CollectionProperty(
        name='Material Morphs',
        type=MaterialMorph,
        )
    uv_morphs = CollectionProperty(
        name='UV Morphs',
        type=UVMorph,
        )
    bone_morphs = CollectionProperty(
        name='Bone Morphs',
        type=BoneMorph,
        )
    vertex_morphs = CollectionProperty(
        name='Vertex Morphs',
        type=VertexMorph
        )
    group_morphs = CollectionProperty(
        name='Group Morphs',
        type=GroupMorph,
        )
    active_morph_type = EnumProperty(
        name='Active Morph Type',
        description='Select current morph type',
        items = [
            ('material_morphs', 'Material', 'Material Morphs', 0),
            ('uv_morphs', 'UV', 'UV Morphs', 1),
            ('bone_morphs', 'Bone', 'Bone Morphs', 2),
            ('vertex_morphs', 'Vertex', 'Vertex Morphs', 3),
            ('group_morphs', 'Group', 'Group Morphs', 4),
            ],
        default='vertex_morphs',
        )
    active_morph = IntProperty(
        name='Active Morph',
        min=0,
        set=_setActiveMorph,
        get=_getActiveMorph,
        )
    active_mesh_index = IntProperty(
        name='Active Mesh',
        description='Active Mesh in this model',
        set=_setActiveMeshObject,
        get=_getActiveMeshObject,
        )
