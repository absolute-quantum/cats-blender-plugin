# GPL License

import bpy
import operator
import webbrowser
import numpy as np

from . import common as Common
from . import eyetracking as Eyetracking
from .common import version_2_79_or_older
from .register import register_wrap
from .translations import t

# Bone names from https://github.com/triazo/immersive_scaler/
bone_names = {
    "right_shoulder": ["rightshoulder", "shoulderr", "rshoulder"],
    "right_arm": ["rightarm", "armr", "rarm", "upperarmr", "rightupperarm", "uparmr", "ruparm"],
    "right_elbow": ["rightelbow", "elbowr", "relbow", "lowerarmr", "rightlowerarm", "lowerarmr", "lowarmr", "rlowarm"],
    "right_wrist": ["rightwrist", "wristr", "rwrist", "handr", "righthand", "rhand"],

    #hand l fingers
    "pinkie_1_r": ["littlefinger1r"],
    "pinkie_2_r": ["littlefinger2r"],
    "pinkie_3_r": ["littlefinger3r"],

    "ring_1_r": ["ringfinger1r"],
    "ring_2_r": ["ringfinger2r"],
    "ring_3_r": ["ringfinger3r"],

    "middle_1_r": ["middlefinger1r"],
    "middle_2_r": ["middlefinger2r"],
    "middle_3_r": ["middlefinger3r"],

    "index_1_r": ["indexfinger1r"],
    "index_2_r": ["indexfinger2r"],
    "index_3_r": ["indexfinger3r"],

    "thumb_1_r": ['thumb0r'],
    "thumb_2_r": ['thumb1r'],
    "thumb_3_r": ['thumb2r'],

    "right_leg": ["rightleg", "legr", "rleg", "upperlegr", "thighr", "rightupperleg", "uplegr", "rupleg"],
    "right_knee": ["rightknee", "kneer", "rknee", "lowerlegr", "calfr", "rightlowerleg", "lowlegr", "rlowleg"],
    "right_ankle": ["rightankle", "ankler", "rankle", "rightfoot", "footr", "rightfoot", "rightfeet", "feetright", "rfeet", "feetr"],
    "right_toe": ["righttoe", "toeright", "toer", "rtoe", "toesr", "rtoes"],

    "left_shoulder": ["leftshoulder", "shoulderl", "rshoulder"],
    "left_arm": ["leftarm", "arml", "rarm", "upperarml", "leftupperarm", "uparml", "luparm"],
    "left_elbow": ["leftelbow", "elbowl", "relbow", "lowerarml", "leftlowerarm", "lowerarml", "lowarml", "llowarm"],
    "left_wrist": ["leftwrist", "wristl", "rwrist", "handl", "lefthand", "lhand"],

    #hand l fingers
    "pinkie_1_l": ["littlefinger1l"],
    "pinkie_2_l": ["littlefinger2l"],
    "pinkie_3_l": ["littlefinger3l"],

    "ring_1_l": ["ringfinger1l"],
    "ring_2_l": ["ringfinger2l"],
    "ring_3_l": ["ringfinger3l"],

    "middle_1_l": ["middlefinger1l"],
    "middle_2_l": ["middlefinger2l"],
    "middle_3_l": ["middlefinger3l"],

    "index_1_l": ["indexfinger1l"],
    "index_2_l": ["indexfinger2l"],
    "index_3_l": ["indexfinger3l"],

    "thumb_1_l": ['thumb0l'],
    "thumb_2_l": ['thumb1l'],
    "thumb_3_l": ['thumb2l'],

    "left_leg": ["leftleg", "legl", "rleg", "upperlegl", "thighl","leftupperleg", "uplegl", "lupleg"],
    "left_knee": ["leftknee", "kneel", "rknee", "lowerlegl", "calfl", "leftlowerleg", 'lowlegl', 'llowleg'],
    "left_ankle": ["leftankle", "anklel", "rankle", "leftfoot", "footl", "leftfoot", "leftfeet", "feetleft", "lfeet", "feetl"],
    "left_toe": ["lefttoe", "toeleft", "toel", "ltoe", "toesl", "ltoes"],

    'hips': ["pelvis", "hips"],
    'spine': ["torso", "spine"],
    'chest': ["chest"],
    'upper_chest': ["upperchest"],
    'neck': ["neck"],
    'head': ["head"],
    'left_eye': ["eyeleft", "lefteye", "eyel", "leye"],
    'right_eye': ["eyeright", "righteye", "eyer", "reye"],
}

def simplify_bonename(n):
    return n.lower().translate(dict.fromkeys(map(ord, u" _.")))

@register_wrap
class DigitigradeTutorialButton(bpy.types.Operator):
    bl_idname = 'cats_manual.digitigrade_tutorial'
    bl_label = "How to use"
    bl_description = "This will open a basic tutorial on how to setup and use aim constraints for Digitigrade avatars. Desktop-only!"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        webbrowser.open("https://www.furaffinity.net/view/44035707/")
        return {'FINISHED'}

@register_wrap
class StartPoseMode(bpy.types.Operator):
    bl_idname = 'cats_manual.start_pose_mode'
    bl_label = t('StartPoseMode.label')
    bl_description = t('StartPoseMode.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        start_pose_mode(reset_pose=True)
        return {'FINISHED'}


@register_wrap
class StartPoseModeNoReset(bpy.types.Operator):
    bl_idname = 'cats_manual.start_pose_mode_no_reset'
    bl_label = t('StartPoseMode.label')
    bl_description = t('StartPoseModeNoReset.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        start_pose_mode(reset_pose=False)
        return {'FINISHED'}


def start_pose_mode(reset_pose=True):
    saved_data = Common.SavedData()

    current = ""
    if bpy.context.active_object and bpy.context.active_object.mode == 'EDIT' and bpy.context.active_object.type == 'ARMATURE' and len(
            bpy.context.selected_editable_bones) > 0:
        current = bpy.context.selected_editable_bones[0].name

    if version_2_79_or_older():
        bpy.context.space_data.use_pivot_point_align = False
        bpy.context.space_data.show_manipulator = True
    else:
        pass
        # TODO

    armature = Common.set_default_stage()
    Common.switch('POSE')
    armature.data.pose_position = 'POSE'

    for mesh in Common.get_meshes_objects():
        if Common.has_shapekeys(mesh):
            for shape_key in mesh.data.shape_keys.key_blocks:
                shape_key.value = 0

    for pb in armature.data.bones:
        pb.select = True

    if reset_pose:
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()

    bone = armature.data.bones.get(current)
    if bone is not None:
        for pb in armature.data.bones:
            if bone.name != pb.name:
                pb.select = False
    else:
        for index, pb in enumerate(armature.data.bones):
            if index != 0:
                pb.select = False

    if version_2_79_or_older():
        bpy.context.space_data.transform_manipulators = {'ROTATE'}
    else:
        bpy.ops.wm.tool_set_by_id(name="builtin.rotate")

    saved_data.load(hide_only=True)
    Common.hide(armature, False)


@register_wrap
class StopPoseMode(bpy.types.Operator):
    bl_idname = 'cats_manual.stop_pose_mode'
    bl_label = t('StopPoseMode.label')
    bl_description = t('StopPoseMode.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        stop_pose_mode(reset_pose=True)
        return {'FINISHED'}


@register_wrap
class StopPoseModeNoReset(bpy.types.Operator):
    bl_idname = 'cats_manual.stop_pose_mode_no_reset'
    bl_label = t('StopPoseMode.label')
    bl_description = t('StopPoseModeNoReset.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature() is None:
            return False
        return True

    def execute(self, context):
        stop_pose_mode(reset_pose=False)
        return {'FINISHED'}


def stop_pose_mode(reset_pose=True):
    saved_data = Common.SavedData()
    armature = Common.get_armature()
    Common.set_active(armature)

    # Make all objects visible
    bpy.ops.object.hide_view_clear()

    for pb in armature.data.bones:
        pb.hide = False
        pb.select = True

    if reset_pose:
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.pose.transforms_clear()

    for pb in armature.data.bones:
        pb.select = False

    armature = Common.set_default_stage()
    # armature.data.pose_position = 'REST'

    for mesh in Common.get_meshes_objects():
        if Common.has_shapekeys(mesh):
            for shape_key in mesh.data.shape_keys.key_blocks:
                shape_key.value = 0

    if version_2_79_or_older():
        bpy.context.space_data.transform_manipulators = {'TRANSLATE'}
    else:
        bpy.ops.wm.tool_set_by_id(name="builtin.select_box")

    Eyetracking.eye_left = None

    saved_data.load(hide_only=True)


@register_wrap
class PoseToShape(bpy.types.Operator):
    bl_idname = 'cats_manual.pose_to_shape'
    bl_label = t('PoseToShape.label')
    bl_description = t('PoseToShape.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = Common.get_armature()
        return armature and armature.mode == 'POSE'

    def execute(self, context):
        # pose_to_shapekey('Pose')
        bpy.ops.cats_manual.pose_name_popup('INVOKE_DEFAULT')

        return {'FINISHED'}


def pose_to_shapekey(name):
    saved_data = Common.SavedData()

    for mesh in Common.get_meshes_objects():
        Common.unselect_all()
        Common.set_active(mesh)

        Common.switch('EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.remove_doubles(threshold=0)
        Common.switch('OBJECT')

        # Apply armature mod
        mod = mesh.modifiers.new(name, 'ARMATURE')
        mod.object = Common.get_armature()
        Common.apply_modifier(mod, as_shapekey=True)

    armature = Common.set_default_stage()
    Common.switch('POSE')
    armature.data.pose_position = 'POSE'

    saved_data.load(ignore=armature.name)
    return armature


@register_wrap
class PoseNamePopup(bpy.types.Operator):
    bl_idname = "cats_manual.pose_name_popup"
    bl_label = t('PoseNamePopup.label')
    bl_description = t('PoseNamePopup.desc')
    bl_options = {'INTERNAL'}

    bpy.types.Scene.pose_to_shapekey_name = bpy.props.StringProperty(name="Pose Name")

    def execute(self, context):
        name = context.scene.pose_to_shapekey_name
        if not name:
            name = 'Pose'
        pose_to_shapekey(name)
        self.report({'INFO'}, t('PoseNamePopup.success'))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.scene.pose_to_shapekey_name = 'Pose'
        dpi_value = Common.get_user_preferences().system.dpi
        return context.window_manager.invoke_props_dialog(self, width=int(dpi_value * 4))

    def check(self, context):
        # Important for changing options
        return True

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.3
        row.prop(context.scene, 'pose_to_shapekey_name')


@register_wrap
class PoseToRest(bpy.types.Operator):
    bl_idname = 'cats_manual.pose_to_rest'
    bl_label = t('PoseToRest.label')
    bl_description = t('PoseToRest.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        armature = Common.get_armature()
        return armature and armature.mode == 'POSE'

    def execute(self, context):
        saved_data = Common.SavedData()

        armature_obj = Common.get_armature()
        mesh_objs = Common.get_meshes_objects(armature_name=armature_obj.name)
        for mesh_obj in mesh_objs:
            me = mesh_obj.data
            if me:
                if me.shape_keys and me.shape_keys.key_blocks:
                    # The mesh has shape keys
                    shape_keys = me.shape_keys
                    key_blocks = shape_keys.key_blocks
                    if len(key_blocks) == 1:
                        # The mesh only has a basis shape key, so we can remove it and then add it back afterwards
                        # Get basis shape key
                        basis_shape_key = key_blocks[0]
                        # Save the name of the basis shape key
                        original_basis_name = basis_shape_key.name
                        # Remove the basis shape key so there are now no shape keys
                        mesh_obj.shape_key_remove(basis_shape_key)
                        # Apply the pose to the mesh
                        PoseToRest.apply_armature_to_mesh_with_no_shape_keys(armature_obj, mesh_obj)
                        # Add the basis shape key back with the same name as before
                        mesh_obj.shape_key_add(name=original_basis_name)
                    else:
                        # Apply the pose to the mesh, taking into account the shape keys
                        PoseToRest.apply_armature_to_mesh_with_shape_keys(armature_obj, mesh_obj, context.scene)
                else:
                    # The mesh doesn't have shape keys, so we can easily apply the pose to the mesh
                    PoseToRest.apply_armature_to_mesh_with_no_shape_keys(armature_obj, mesh_obj)
        # Once the mesh and shape keys (if any) have been applied, the last step is to apply the current pose of the
        # bones as the new rest pose.
        #
        # From the poll function, armature_obj must already be in pose mode, but it's possible it might not be the
        # active object e.g., the user has multiple armatures opened in pose mode, but a different armature is currently
        # active. We can use an operator override to tell the operator to treat armature_obj as if it's the active
        # object even if it's not, skipping the need to actually set armature_obj as the active object.
        bpy.ops.pose.armature_apply({'active_object': armature_obj})

        # Stop pose mode after operation
        bpy.ops.cats_manual.stop_pose_mode()

        saved_data.load(hide_only=True)

        self.report({'INFO'}, t('PoseToRest.success'))
        return {'FINISHED'}

    @staticmethod
    def apply_armature_to_mesh_with_no_shape_keys(armature_obj, mesh_obj):
        armature_mod = mesh_obj.modifiers.new('PoseToRest', 'ARMATURE')
        armature_mod.object = armature_obj
        # In the unlikely case that there was already a modifier with the same name as the new modifier, the new
        # modifier will have ended up with a different name
        mod_name = armature_mod.name
        # Context override to let us run the modifier operators on mesh_obj, even if it's not the active object
        context_override = {'object': mesh_obj}
        # Moving the modifier to the first index will prevent an Info message about the applied modifier not being
        # first and potentially having unexpected results.
        if bpy.app.version >= (2, 90, 0):
            # modifier_move_to_index was added in Blender 2.90
            bpy.ops.object.modifier_move_to_index(context_override, modifier=mod_name, index=0)
        else:
            # The newly created modifier will be at the bottom of the list
            armature_mod_index = len(mesh_obj.modifiers) - 1
            # Move the modifier up until it's at the top of the list
            for _ in range(armature_mod_index):
                bpy.ops.object.modifier_move_up(context_override, modifier=mod_name)
        bpy.ops.object.modifier_apply(context_override, modifier=mod_name)

    @staticmethod
    def apply_armature_to_mesh_with_shape_keys(armature_obj, mesh_obj, scene):
        # The active shape key will be changed, so save the current active index, so it can be restored afterwards
        old_active_shape_key_index = mesh_obj.active_shape_key_index

        # Shape key pinning shows the active shape key in the viewport without blending; effectively what you see when
        # in edit mode. Combined with an armature modifier, we can use this to figure out the correct positions for all
        # the shape keys.
        # Save the current value, so it can be restored afterwards.
        old_show_only_shape_key = mesh_obj.show_only_shape_key
        mesh_obj.show_only_shape_key = True

        # Temporarily remove vertex_groups from and disable mutes on shape keys because they affect pinned shape keys
        me = mesh_obj.data
        shape_key_vertex_groups = []
        shape_key_mutes = []
        key_blocks = me.shape_keys.key_blocks
        for shape_key in key_blocks:
            shape_key_vertex_groups.append(shape_key.vertex_group)
            shape_key.vertex_group = ''
            shape_key_mutes.append(shape_key.mute)
            shape_key.mute = False

        # Temporarily disable all modifiers from showing in the viewport so that they have no effect
        mods_to_reenable_viewport = []
        for mod in mesh_obj.modifiers:
            if mod.show_viewport:
                mod.show_viewport = False
                mods_to_reenable_viewport.append(mod)

        # Temporarily add a new armature modifier
        armature_mod = mesh_obj.modifiers.new('PoseToRest', 'ARMATURE')
        armature_mod.object = armature_obj

        # cos are xyz positions and get flattened when using the foreach_set/foreach_get functions, so the array length
        # will be 3 times the number of vertices
        co_length = len(me.vertices) * 3
        # We can re-use the same array over and over
        eval_verts_cos_array = np.empty(co_length, dtype=np.single)

        if Common.version_2_79_or_older():
            def get_eval_cos_array():
                # Create a new mesh with modifiers and shape keys applied
                evaluated_mesh = mesh_obj.to_mesh(scene, True, 'PREVIEW')

                # Get the cos of the vertices from the evaluated mesh
                evaluated_mesh.vertices.foreach_get('co', eval_verts_cos_array)
                # Delete the newly created mesh
                bpy.data.meshes.remove(evaluated_mesh)
                return eval_verts_cos_array
        else:
            # depsgraph lets us evaluate objects and get their state after the effect of modifiers and shape keys
            depsgraph = None
            evaluated_mesh_obj = None

            def get_eval_cos_array():
                nonlocal depsgraph
                nonlocal evaluated_mesh_obj
                # Get the depsgraph and evaluate the mesh if we haven't done so already
                if depsgraph is None or evaluated_mesh_obj is None:
                    depsgraph = bpy.context.evaluated_depsgraph_get()
                    evaluated_mesh_obj = mesh_obj.evaluated_get(depsgraph)
                else:
                    # If we already have the depsgraph and evaluated mesh, in order for the change to the active shape
                    # key to take effect, the depsgraph has to be updated
                    depsgraph.update()
                # Get the cos of the vertices from the evaluated mesh
                evaluated_mesh_obj.data.vertices.foreach_get('co', eval_verts_cos_array)
                return eval_verts_cos_array

        for i, shape_key in enumerate(key_blocks):
            # As shape key pinning is enabled, when we change the active shape key, it will change the state of the mesh
            mesh_obj.active_shape_key_index = i
            # The cos of the vertices of the evaluated mesh include the effect of the pinned shape key and all the
            # modifiers (in this case, only the armature modifier we added since all the other modifiers are disabled in
            # the viewport).
            # This combination gives the same effect as if we'd applied the armature modifier to a mesh with the same
            # shape as the active shape key, so we can simply set the shape key to the evaluated mesh position.
            #
            # Get the evaluated cos
            evaluated_cos = get_eval_cos_array()
            # And set the shape key to those same cos
            shape_key.data.foreach_set('co', evaluated_cos)
            # If it's the basis shape key, we also have to set the mesh vertices to match, otherwise the two will be
            # desynced until Edit mode has been entered and exited, which can cause odd behaviour when creating shape
            # keys with from_mix=False or when removing all shape keys.
            if i == 0:
                mesh_obj.data.vertices.foreach_set('co', evaluated_cos)

        # Restore temporarily changed attributes and remove the added armature modifier
        for mod in mods_to_reenable_viewport:
            mod.show_viewport = True
        mesh_obj.modifiers.remove(armature_mod)
        for shape_key, vertex_group, mute in zip(me.shape_keys.key_blocks, shape_key_vertex_groups, shape_key_mutes):
            shape_key.vertex_group = vertex_group
            shape_key.mute = mute
        mesh_obj.active_shape_key_index = old_active_shape_key_index
        mesh_obj.show_only_shape_key = old_show_only_shape_key


@register_wrap
class JoinMeshes(bpy.types.Operator):
    bl_idname = 'cats_manual.join_meshes'
    bl_label = t('JoinMeshes.label')
    bl_description = t('JoinMeshes.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        meshes = Common.get_meshes_objects(check=False)
        return meshes and len(meshes) > 0

    def execute(self, context):
        saved_data = Common.SavedData()
        mesh = Common.join_meshes()
        if not mesh:
            saved_data.load()
            self.report({'ERROR'}, t('JoinMeshes.failure'))
            return {'CANCELLED'}

        saved_data.load()
        Common.unselect_all()
        Common.set_active(mesh)
        self.report({'INFO'}, t('JoinMeshes.success'))
        return {'FINISHED'}


@register_wrap
class JoinMeshesSelected(bpy.types.Operator):
    bl_idname = 'cats_manual.join_meshes_selected'
    bl_label = t('JoinMeshesSelected.label')
    bl_description = t('JoinMeshesSelected.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        meshes = Common.get_meshes_objects(check=False)
        return meshes and len(meshes) > 0

    def execute(self, context):
        saved_data = Common.SavedData()

        if not Common.get_meshes_objects(mode=3):
            saved_data.load()
            self.report({'ERROR'}, t('JoinMeshesSelected.error.noSelect'))
            return {'FINISHED'}

        mesh = Common.join_meshes(mode=1)
        if not mesh:
            saved_data.load()
            self.report({'ERROR'}, t('JoinMeshesSelected.error.cantJoin'))
            return {'CANCELLED'}

        saved_data.load()
        Common.unselect_all()
        Common.set_active(mesh)
        self.report({'INFO'}, t('JoinMeshesSelected.success'))
        return {'FINISHED'}


@register_wrap
class SeparateByMaterials(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_materials'
    bl_label = t('SeparateByMaterials.label')
    bl_description = t('SeparateByMaterials.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes and len(meshes) >= 1

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.noMesh'))
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.multipleMesh'))
                return {'FINISHED'}
            obj = meshes[0]

        obj_name = obj.name

        Common.separate_by_materials(context, obj)

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, t('SeparateByMaterials.success'))
        return {'FINISHED'}


@register_wrap
class SeparateByLooseParts(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_loose_parts'
    bl_label = t('SeparateByLooseParts.label')
    bl_description = t('SeparateByLooseParts.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.noMesh'))
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.multipleMesh'))
                return {'FINISHED'}
            obj = meshes[0]
        obj_name = obj.name

        Common.separate_by_loose_parts(context, obj)

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, t('SeparateByLooseParts.success'))
        return {'FINISHED'}


@register_wrap
class SeparateByShapekeys(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_shape_keys'
    bl_label = t('SeparateByShapekeys.label')
    bl_description = t('SeparateByShapekeys.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.noMesh'))
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.multipleMesh'))
                return {'FINISHED'}
            obj = meshes[0]
        obj_name = obj.name

        done_message = t('SeparateByShapekeys.success')
        if not Common.separate_by_shape_keys(context, obj):
            done_message = t('SeparateByX.warn.noSeparation')

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, done_message)
        return {'FINISHED'}


@register_wrap
class SeparateByCopyProtection(bpy.types.Operator):
    bl_idname = 'cats_manual.separate_by_copy_protection'
    bl_label = t('SeparateByCopyProtection.label')
    bl_description = t('SeparateByCopyProtection.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()
        obj = context.active_object

        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.noMesh'))
                return {'FINISHED'}
            if len(meshes) > 1:
                saved_data.load()
                self.report({'ERROR'}, t('SeparateByX.error.multipleMesh'))
                return {'FINISHED'}
            obj = meshes[0]
        obj_name = obj.name

        done_message = t('SeparateByCopyProtection.success')
        if not Common.separate_by_cats_protection(context, obj):
            done_message = t('SeparateByX.warn.noSeparation')

        saved_data.load(ignore=[obj_name])
        self.report({'INFO'}, done_message)
        return {'FINISHED'}


@register_wrap
class MergeWeights(bpy.types.Operator):
    bl_idname = 'cats_manual.merge_weights'
    bl_label = t('MergeWeights.label')
    bl_description = t('MergeWeights.desc')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active_obj = context.active_object
        if not active_obj or not context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and context.selected_editable_bones:
            return True
        if active_obj.mode == 'POSE' and context.selected_pose_bones:
            return True

        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = context.object

        Common.switch('EDIT')

        # Find which bones to work on and put their name and their parent in a list
        parenting_list = {}
        for bone in context.selected_editable_bones:
            parent = bone.parent
            while parent and parent.parent and parent in context.selected_editable_bones:
                parent = parent.parent
            if not parent:
                continue
            parenting_list[bone.name] = parent.name

        # Merge all the bones in the parenting list
        merge_weights(armature, parenting_list)

        saved_data.load()

        self.report({'INFO'}, t('MergeWeights.success', number=str(len(parenting_list))))
        return {'FINISHED'}


@register_wrap
class MergeWeightsToActive(bpy.types.Operator):
    bl_idname = 'cats_manual.merge_weights_to_active'
    bl_label = t('MergeWeightsToActive.label')
    bl_description = t('MergeWeightsToActive.desc')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        if not active_obj or not bpy.context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and bpy.context.selected_editable_bones and len(bpy.context.selected_editable_bones) > 1:
            if bpy.context.active_bone in bpy.context.selected_editable_bones:
                return True
        elif active_obj.mode == 'POSE' and bpy.context.selected_pose_bones and len(bpy.context.selected_pose_bones) > 1:
            if bpy.context.active_pose_bone in bpy.context.selected_pose_bones:
                return True

        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = bpy.context.object

        Common.switch('EDIT')

        # Find which bones to work on and put their name and their parent in a list and parent the bones to the active one
        parenting_list = {}
        for bone in bpy.context.selected_editable_bones:
            if bone.name == bpy.context.active_bone.name:
                continue
            parenting_list[bone.name] = bpy.context.active_bone.name
            bone.parent = bpy.context.active_bone

        # Merge all the bones in the parenting list
        merge_weights(armature, parenting_list)

        # Load original modes
        saved_data.load()

        self.report({'INFO'}, t('MergeWeightsToActive.success', number=str(len(parenting_list))))
        return {'FINISHED'}


def merge_weights(armature, parenting_list):
    Common.switch('OBJECT')
    # Merge the weights on the meshes
    for mesh in Common.get_meshes_objects(armature_name=armature.name, visible_only=bpy.context.scene.merge_visible_meshes_only):
        Common.set_active(mesh)

        for bone, parent in parenting_list.items():
            if not mesh.vertex_groups.get(bone):
                continue
            if not mesh.vertex_groups.get(parent):
                mesh.vertex_groups.new(name=parent)
            Common.mix_weights(mesh, bone, parent)

    # Select armature
    Common.unselect_all()
    Common.set_active(armature)
    Common.switch('EDIT')

    # Delete merged bones
    if not bpy.context.scene.keep_merged_bones:
        for bone in parenting_list.keys():
            armature.data.edit_bones.remove(armature.data.edit_bones.get(bone))


@register_wrap
class ApplyTransformations(bpy.types.Operator):
    bl_idname = 'cats_manual.apply_transformations'
    bl_label = t('ApplyTransformations.label')
    bl_description = t('ApplyTransformations.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature():
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.apply_transforms()

        saved_data.load()
        self.report({'INFO'}, t('ApplyTransformations.success'))
        return {'FINISHED'}


@register_wrap
class ApplyAllTransformations(bpy.types.Operator):
    bl_idname = 'cats_manual.apply_all_transformations'
    bl_label = t('ApplyAllTransformations.label')
    bl_description = t('ApplyAllTransformations.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.apply_all_transforms()

        saved_data.load()
        self.report({'INFO'}, t('ApplyAllTransformations.success'))
        return {'FINISHED'}


@register_wrap
class RemoveZeroWeightBones(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_zero_weight_bones'
    bl_label = t('RemoveZeroWeightBones.label')
    bl_description = t('RemoveZeroWeightBones.desc')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature():
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.set_default_stage()
        count = Common.delete_zero_weight()
        Common.set_default_stage()

        saved_data.load()
        self.report({'INFO'}, t('RemoveZeroWeightBones.success', number=str(count)))
        return {'FINISHED'}


@register_wrap
class RemoveZeroWeightGroups(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_zero_weight_groups'
    bl_label = t('RemoveZeroWeightGroups.label')
    bl_description = t('RemoveZeroWeightGroups.desc')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return Common.get_meshes_objects(mode=2, check=False)

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.set_default_stage()
        count = Common.remove_unused_vertex_groups()

        saved_data.load()
        self.report({'INFO'}, t('RemoveZeroWeightGroups.success', number=str(count)))
        return {'FINISHED'}

    # Maybe only remove groups from selected meshes instead of from all of them
    # THis still needs some work
    #
    # @classmethod
    # def poll2(cls, context):
    #     return Common.get_meshes_objects(mode=3, check=False)
    #
    # def execute2(self, context):
    #     saved_data = Common.SavedData()
    #     remove_count = 0
    #
    #     for mesh in Common.get_meshes_objects(mode=3):
    #         remove_count += Common.remove_unused_vertex_groups_of_mesh(mesh)
    #
    #     saved_data.load()
    #     self.report({'INFO'}, 'Removed ' + str(remove_count) + ' zero weight vertex groups.')
    #     return {'FINISHED'}

@register_wrap
class RemoveConstraints(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_constraints'
    bl_label = t('RemoveConstraints.label')
    bl_description = t('RemoveConstraints.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if Common.get_armature():
            return True
        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        Common.set_default_stage()
        Common.delete_bone_constraints()
        Common.set_default_stage()

        saved_data.load()
        self.report({'INFO'}, t('RemoveConstraints.success'))
        return {'FINISHED'}

@register_wrap
class RecalculateNormals(bpy.types.Operator):
    bl_idname = 'cats_manual.recalculate_normals'
    bl_label = t('RecalculateNormals.label')
    bl_description = t('RecalculateNormals.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        obj = context.active_object
        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                return {'FINISHED'}
            obj = meshes[0]
        mesh = obj

        Common.unselect_all()
        Common.set_active(mesh)
        Common.switch('EDIT')
        Common.switch('EDIT')

        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)

        Common.set_default_stage()

        saved_data.load()
        self.report({'INFO'}, t('RecalculateNormals.success'))
        return {'FINISHED'}


@register_wrap
class FlipNormals(bpy.types.Operator):
    bl_idname = 'cats_manual.flip_normals'
    bl_label = t('FlipNormals.label')
    bl_description = t('FlipNormals.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        obj = context.active_object
        if not obj or (obj and obj.type != 'MESH'):
            Common.unselect_all()
            meshes = Common.get_meshes_objects()
            if len(meshes) == 0:
                saved_data.load()
                return {'FINISHED'}
            obj = meshes[0]
        mesh = obj

        Common.unselect_all()
        Common.set_active(mesh)
        Common.switch('EDIT')
        Common.switch('EDIT')

        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.mesh.flip_normals()

        Common.set_default_stage()

        saved_data.load()
        self.report({'INFO'}, t('FlipNormals.success'))
        return {'FINISHED'}


@register_wrap
class RemoveDoubles(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_doubles'
    bl_label = t('RemoveDoubles.label')
    bl_description = t('RemoveDoubles.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        removed_tris = 0
        meshes = Common.get_meshes_objects(mode=3)
        if not meshes:
            meshes = [Common.get_meshes_objects()[0]]

        Common.set_default_stage()

        for mesh in meshes:
            removed_tris += Common.remove_doubles(mesh, 0.0001, save_shapes=True)

        Common.set_default_stage()

        saved_data.load()

        self.report({'INFO'}, t('RemoveDoubles.success', number=str(removed_tris)))
        return {'FINISHED'}


@register_wrap
class RemoveDoublesNormal(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_doubles_normal'
    bl_label = t('RemoveDoublesNormal.label')
    bl_description = t('RemoveDoublesNormal.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return True

        meshes = Common.get_meshes_objects(check=False)
        return meshes

    def execute(self, context):
        saved_data = Common.SavedData()

        removed_tris = 0
        meshes = Common.get_meshes_objects(mode=3)
        if not meshes:
            meshes = [Common.get_meshes_objects()[0]]

        Common.set_default_stage()

        for mesh in meshes:
            removed_tris += Common.remove_doubles(mesh, 0.0001, save_shapes=True)

        Common.set_default_stage()

        saved_data.load()

        self.report({'INFO'}, t('RemoveDoublesNormal.success', number=str(removed_tris)))
        return {'FINISHED'}


@register_wrap
class FixVRMShapesButton(bpy.types.Operator):
    bl_idname = 'cats_manual.fix_vrm_shapes'
    bl_label = t('FixVRMShapesButton.label')
    bl_description = t('FixVRMShapesButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return Common.get_meshes_objects(check=False)

    def execute(self, context):
        saved_data = Common.SavedData()

        mesh = Common.get_meshes_objects()[0]
        slider_max_eyes = 0.33333
        slider_max_mouth = 0.94

        if not Common.has_shapekeys(mesh):
            self.report({'INFO'}, t('FixVRMShapesButton.warn.notDetected'))
            saved_data.load()
            return {'CANCELLED'}

        Common.set_active(mesh)
        bpy.ops.object.shape_key_clear()

        shapekeys = enumerate(mesh.data.shape_keys.key_blocks)

        # Find shapekeys to merge
        shapekeys_to_merge_eyes = {}
        shapekeys_to_merge_mouth = {}
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if index == 0:
                continue

            # Set max slider
            if shapekey.name.startswith('eye_'):
                shapekey.slider_max = slider_max_eyes
            else:
                shapekey.slider_max = slider_max_mouth

            # Split name
            name_split = shapekey.name.split('00')
            if len(name_split) < 2:
                continue
            pre_name = name_split[0]
            post_name = name_split[1]

            # Put shapekey in corresponding list
            if pre_name == "eye_face.f":
                shapekeys_to_merge_eyes[post_name] = []
            elif pre_name == "kuti_face.f":
                shapekeys_to_merge_mouth[post_name] = []

        # Add all matching shapekeys to the merge list
        for index, shapekey in enumerate(mesh.data.shape_keys.key_blocks):
            if index == 0:
                continue

            name_split = shapekey.name.split('00')
            if len(name_split) < 2:
                continue
            pre_name = name_split[0]
            post_name = name_split[1]

            if post_name in shapekeys_to_merge_eyes.keys():
                if pre_name == 'eye_face.f' or pre_name == 'eye_siroL.sL' or pre_name == 'eye_line_u.elu':
                    shapekeys_to_merge_eyes[post_name].append(shapekey.name)

            elif post_name in shapekeys_to_merge_mouth.keys():
                if pre_name == 'kuti_face.f' or pre_name == 'kuti_ha.ha' or pre_name == 'kuti_sita.t':
                    shapekeys_to_merge_mouth[post_name].append(shapekey.name)

        # Merge all the shape keys
        shapekeys_used = []
        for name, shapekeys_merge in shapekeys_to_merge_eyes.items():
            if len(shapekeys_merge) <= 1:
                continue

            for shapekey_name in shapekeys_merge:
                mesh.data.shape_keys.key_blocks[shapekey_name].value = slider_max_eyes
                shapekeys_used.append(shapekey_name)

            mesh.shape_key_add(name='eyes_' + name[1:], from_mix=True)
            mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
            bpy.ops.object.shape_key_move(type='TOP')
            bpy.ops.object.shape_key_clear()

        for name, shapekeys_merge in shapekeys_to_merge_mouth.items():
            if len(shapekeys_merge) <= 1:
                continue

            for shapekey_name in shapekeys_merge:
                mesh.data.shape_keys.key_blocks[shapekey_name].value = slider_max_mouth
                shapekeys_used.append(shapekey_name)

            mesh.shape_key_add(name='mouth_' + name[1:], from_mix=True)
            mesh.active_shape_key_index = len(mesh.data.shape_keys.key_blocks) - 1
            bpy.ops.object.shape_key_move(type='TOP')
            bpy.ops.object.shape_key_clear()

        # Remove all the used shapekeys
        for index in reversed(range(0, len(mesh.data.shape_keys.key_blocks))):
            mesh.active_shape_key_index = index
            shapekey = mesh.active_shape_key
            if shapekey.name in shapekeys_used:
                bpy.ops.object.shape_key_remove(all=False)

        saved_data.load()

        self.report({'INFO'}, t('FixVRMShapesButton.success'))
        return {'FINISHED'}

def duplicatebone(b):
    arm = bpy.context.object.data
    cb = arm.edit_bones.new(b.name)

    cb.head = b.head
    cb.tail = b.tail
    cb.matrix = b.matrix
    cb.parent = b.parent
    return cb

@register_wrap
class CreateDigitigradeLegs(bpy.types.Operator):
    """Create digitigrade legs while in edit mode with digitigrade thighs selected."""
    bl_idname = "armature.createdigitigradelegs"
    bl_label = "Create Digitigrade Legs"

    @classmethod
    def poll(cls, context):
        if(context.active_object is None):
            return False
        if(context.selected_editable_bones is not None):
            if(len(context.selected_editable_bones) == 2):
                return True
        return False

    def execute(self, context):

        for digi0 in context.selected_editable_bones:
            digi1 = None
            digi2 = None
            digi3 = None

            try:
                digi1 = digi0.children[0]
                digi2 = digi1.children[0]
                digi3 = digi2.children[0]
            except:
                print("bone format incorrect! Please select a chain of 4 continious bones!")
            digi4 = None
            try:
                digi4 = digi3.children[0]
            except:
                print("no toe bone. Continuing.")
            digi0.select = True
            digi1.select = True
            digi2.select = True
            digi3.select = True
            if(digi4):
                digi4.select = True
            bpy.ops.armature.roll_clear()
            bpy.ops.armature.select_all(action='DESELECT')

            scene = context.scene
            #creating transform for upper leg
            digi0.select = True
            bpy.ops.transform.create_orientation(name="CATS_digi0", overwrite=True)
            bpy.ops.armature.select_all(action='DESELECT')


            #duplicate digi0 and assign it to thigh
            thigh = duplicatebone(digi0)
            bpy.ops.armature.select_all(action='DESELECT')

            #make digi2 parrallel to digi1
            digi2.align_orientation(digi0)

            #extrude thigh
            thigh.select_tail = True
            bpy.ops.armature.extrude_move(ARMATURE_OT_extrude={"forked":False},TRANSFORM_OT_translate=None)
            #set new bone to calf varible
            bpy.ops.armature.select_more()
            calf = context.selected_bones[0]
            bpy.ops.armature.select_all(action='DESELECT')

            #set calf end to  digi2 end
            calf.tail = digi2.tail

            #make copy of calf, flip it, and then align bone so that it's head is moved to match in align phase
            flipedcalf = duplicatebone(calf)
            bpy.ops.armature.select_all(action='DESELECT')
            flipedcalf.select = True
            bpy.ops.armature.switch_direction()
            bpy.ops.armature.select_all(action='DESELECT')
            flippeddigi1 = duplicatebone(digi1)
            bpy.ops.armature.select_all(action='DESELECT')
            flippeddigi1.select = True
            bpy.ops.armature.switch_direction()
            bpy.ops.armature.select_all(action='DESELECT')



            #align flipped calf to flipped middle leg to move the head
            flipedcalf.align_orientation(flippeddigi1)

            flipedcalf.length = flippeddigi1.length

            #assign calf tail to flipped calf head so it moves calf's head
            calf.head = flipedcalf.tail

            #delete helper bones
            bpy.ops.armature.select_all(action='DESELECT')
            flippeddigi1.select = True
            bpy.ops.armature.delete()
            bpy.ops.armature.select_all(action='DESELECT')
            flipedcalf.select = True
            bpy.ops.armature.delete()
            bpy.ops.armature.select_all(action='DESELECT')


            #Tada! It's done! Now to duplicate toes and change parents


            #duplicate old foot and reparent
            newfoot = duplicatebone(digi3)
            newfoot.parent = calf
            #create toe bone if it exists
            if(digi4):
                #duplicate old toe and reparent
                newtoe = duplicatebone(digi4)
                newtoe.parent = newfoot
            #finally done!
        return {'FINISHED'}


@register_wrap
class FixFBTButton(bpy.types.Operator):
    bl_idname = 'cats_manual.fix_fbt'
    bl_label = t('FixFBTButton.label')
    bl_description = t('FixFBTButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return Common.get_armature()

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = Common.set_default_stage()
        Common.switch('EDIT')

        x_cord, y_cord, z_cord, fbx = Common.get_bone_orientations(armature)

        hips = armature.data.edit_bones.get('Hips')
        spine = armature.data.edit_bones.get('Spine')
        left_leg = armature.data.edit_bones.get('Left leg')
        right_leg = armature.data.edit_bones.get('Right leg')
        left_leg_new = armature.data.edit_bones.get('Left leg 2')
        right_leg_new = armature.data.edit_bones.get('Right leg 2')
        left_leg_new_alt = armature.data.edit_bones.get('Left_Leg_2')
        right_leg_new_alt = armature.data.edit_bones.get('Right_Leg_2')

        if not hips or not spine or not left_leg or not right_leg:
            self.report({'ERROR'}, t('FixFBTButton.error.bonesNotFound'))
            saved_data.load()
            return {'CANCELLED'}

        if left_leg_new or right_leg_new or left_leg_new_alt or right_leg_new_alt:
            self.report({'ERROR'}, t('FixFBTButton.error.alreadyApplied'))
            saved_data.load()
            return {'CANCELLED'}

        # FBT Fix
        # Disconnect bones
        for child in hips.children:
            child.use_connect = False
        for child in left_leg.children:
            child.use_connect = False
        for child in right_leg.children:
            child.use_connect = False

        # Flip hips
        hips.head = spine.head
        hips.tail = spine.head
        hips.tail[z_cord] = left_leg.head[z_cord]

        if hips.tail[z_cord] > hips.head[z_cord]:
            hips.tail[z_cord] -= 0.1

        # Create new leg bones and put them at the old location
        if not left_leg_new:
            if left_leg_new_alt:
                left_leg_new = left_leg_new_alt
                left_leg_new.name = 'Left leg 2'
            else:
                left_leg_new = armature.data.edit_bones.new('Left leg 2')
        if not right_leg_new:
            if right_leg_new_alt:
                right_leg_new = right_leg_new_alt
                right_leg_new.name = 'Right leg 2'
            else:
                right_leg_new = armature.data.edit_bones.new('Right leg 2')

        left_leg_new.head = left_leg.head
        left_leg_new.tail = left_leg.tail

        right_leg_new.head = right_leg.head
        right_leg_new.tail = right_leg.tail

        # Set new location for old leg bones
        left_leg.tail = left_leg.head
        left_leg.tail[z_cord] = left_leg.head[z_cord] + 0.1

        right_leg.tail = right_leg.head
        right_leg.tail[z_cord] = right_leg.head[z_cord] + 0.1

        left_leg_new.parent = left_leg
        right_leg_new.parent = right_leg

        # Fixes bones disappearing, prevents bones from having their tail and head at the exact same position
        for bone in armature.data.edit_bones:
            if round(bone.head[x_cord], 5) == round(bone.tail[x_cord], 5) \
                    and round(bone.head[y_cord], 5) == round(bone.tail[y_cord], 5) \
                    and round(bone.head[z_cord], 5) == round(bone.tail[z_cord], 5):
                if bone.name == 'Hips':
                    bone.tail[z_cord] -= 0.1
                else:
                    bone.tail[z_cord] += 0.1

        Common.switch('OBJECT')

        saved_data.load()

        self.report({'INFO'}, t('FixFBTButton.success'))
        return {'FINISHED'}


@register_wrap
class RemoveFBTButton(bpy.types.Operator):
    bl_idname = 'cats_manual.remove_fbt'
    bl_label = t('RemoveFBTButton.label')
    bl_description = t('RemoveFBTButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return Common.get_armature()

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = Common.set_default_stage()
        Common.switch('EDIT')

        x_cord, y_cord, z_cord, fbx = Common.get_bone_orientations(armature)

        hips = armature.data.edit_bones.get('Hips')
        spine = armature.data.edit_bones.get('Spine')
        left_leg = armature.data.edit_bones.get('Left leg')
        right_leg = armature.data.edit_bones.get('Right leg')
        left_leg_new = armature.data.edit_bones.get('Left leg 2')
        right_leg_new = armature.data.edit_bones.get('Right leg 2')

        if not hips or not spine or not left_leg or not right_leg:
            saved_data.load()
            self.report({'ERROR'}, t('RemoveFBTButton.error.bonesNotFound'))
            saved_data.load()
            return {'CANCELLED'}

        if not left_leg_new or not right_leg_new:
            saved_data.load()
            self.report({'ERROR'}, t('RemoveFBTButton.error.notApplied'))
            return {'CANCELLED'}

        # Remove FBT Fix
        # Corrects hips
        if hips.head[z_cord] > hips.tail[z_cord]:
            # Put Hips in the center of the leg bones
            hips.head[x_cord] = (right_leg.head[x_cord] + left_leg.head[x_cord]) / 2

            # Put Hips at 33% between spine and legs
            hips.head[z_cord] = left_leg.head[z_cord] + (spine.head[z_cord] - left_leg.head[z_cord]) * 0.33

            # If Hips are below or at the leg bones, put them above
            if hips.head[z_cord] <= right_leg.head[z_cord]:
                hips.head[z_cord] = right_leg.head[z_cord] + 0.1

            # Make Hips point straight up
            hips.tail[x_cord] = hips.head[x_cord]
            hips.tail[y_cord] = hips.head[y_cord]
            hips.tail[z_cord] = spine.head[z_cord]

            if hips.tail[z_cord] < hips.head[z_cord]:
                hips.tail[z_cord] = hips.tail[z_cord] + 0.1

        # Put the original legs at their old location
        left_leg.head = left_leg_new.head
        left_leg.tail = left_leg_new.tail

        right_leg.head = right_leg_new.head
        right_leg.tail = right_leg_new.tail

        # Remove second leg bones
        armature.data.edit_bones.remove(left_leg_new)
        armature.data.edit_bones.remove(right_leg_new)

        # Fixes bones disappearing, prevents bones from having their tail and head at the exact same position
        for bone in armature.data.edit_bones:
            if round(bone.head[x_cord], 5) == round(bone.tail[x_cord], 5) \
                    and round(bone.head[y_cord], 5) == round(bone.tail[y_cord], 5) \
                    and round(bone.head[z_cord], 5) == round(bone.tail[z_cord], 5):
                bone.tail[z_cord] += 0.1

        Common.switch('OBJECT')

        saved_data.load()

        self.report({'INFO'}, t('RemoveFBTButton.success'))
        return {'FINISHED'}


@register_wrap
class DuplicateBonesButton(bpy.types.Operator):
    bl_idname = 'cats_manual.duplicate_bones'
    bl_label = t('DuplicateBonesButton.label')
    bl_description = t('DuplicateBonesButton.desc')
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        if not active_obj or not bpy.context.active_object.type == 'ARMATURE':
            return False
        if active_obj.mode == 'EDIT' and bpy.context.selected_editable_bones:
            return True
        elif active_obj.mode == 'POSE' and bpy.context.selected_pose_bones:
            return True

        return False

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = bpy.context.object

        Common.switch('EDIT')

        bone_count = len(bpy.context.selected_editable_bones)

        # Create the duplicate bones
        duplicate_vertex_groups = {}
        for bone in bpy.context.selected_editable_bones:
            separator = '_'
            if bone.name.endswith('_'):
                separator = ''
            bone_new = armature.data.edit_bones.new(bone.name + separator + 'copy')
            bone_new.parent = bone.parent

            bone_new.head = bone.head
            bone_new.tail = bone.tail
            duplicate_vertex_groups[bone.name] = bone_new.name

        # Fix bone parenting
        for bone_name in duplicate_vertex_groups.values():
            bone = armature.data.edit_bones.get(bone_name)
            if bone.parent.name in duplicate_vertex_groups.keys():
                bone.parent = armature.data.edit_bones.get(duplicate_vertex_groups[bone.parent.name])

        # Create the missing vertex groups and duplicate the weight
        Common.switch('OBJECT')
        for mesh in Common.get_meshes_objects(armature_name=armature.name):
            Common.set_active(mesh)

            for bone_from, bone_to in duplicate_vertex_groups.items():
                mesh.vertex_groups.new(name=bone_to)
                Common.mix_weights(mesh, bone_from, bone_to, delete_old_vg=False)

        saved_data.load()

        self.report({'INFO'}, t('DuplicateBonesButton.success', number=str(bone_count)))
        return {'FINISHED'}


@register_wrap
class ConnectBonesButton(bpy.types.Operator):
    bl_idname = 'cats_manual.connect_bones'
    bl_label = 'Connect Bones'
    bl_description = 'Connects all bones with their respective children'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        return active_obj and active_obj.type == 'ARMATURE'

    def execute(self, context):
        saved_data = Common.SavedData()

        armature = bpy.context.object

        Common.switch('EDIT')

        Common.fix_bone_orientations(armature)

        saved_data.load()

        self.report({'INFO'}, 'Connected all bones!')
        return {'FINISHED'}


@register_wrap
class ConvertToValveButton(bpy.types.Operator):
    bl_idname = 'cats_manual.convert_to_valve'
    bl_label = 'Convert Bones To Valve'
    bl_description = 'Converts all main bone names to default valve bone names.' \
                     '\nMake sure your model has the CATS standard bone names from after using Fix Model'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    armature_name = bpy.props.StringProperty(default = "")

    @classmethod
    def poll(cls, context):
        if not Common.get_armature():
            return False
        return True

    def execute(self, context):
        translate_bone_fails = 0
        if self.armature_name == "":
            armature = Common.get_armature()
        else:
            armature = bpy.data.objects[self.armature_name]

        reverse_bone_lookup = dict()
        for (preferred_name, name_list) in bone_names.items():
            for name in name_list:
                reverse_bone_lookup[name] = preferred_name

        valve_translations = {
            'hips': "ValveBiped.Bip01_Pelvis",
            'spine': "ValveBiped.Bip01_Spine",
            'chest': "ValveBiped.Bip01_Spine1",
            'upper_chest': "ValveBiped.Bip01_Spine2",
            'neck': "ValveBiped.Bip01_Neck1",
            'head': "ValveBiped.Bip01_Head1", #head1 is on purpose.
            'left_leg': "ValveBiped.Bip01_L_Thigh",
            'left_knee': "ValveBiped.Bip01_L_Calf",
            'left_ankle': "ValveBiped.Bip01_L_Foot",
            'left_toe': "ValveBiped.Bip01_L_Toe0",
            'right_leg': "ValveBiped.Bip01_R_Thigh",
            'right_knee': "ValveBiped.Bip01_R_Calf",
            'right_ankle': "ValveBiped.Bip01_R_Foot",
            'right_toe': "ValveBiped.Bip01_R_Toe0",
            'left_shoulder': "ValveBiped.Bip01_L_Clavicle",
            'left_arm': "ValveBiped.Bip01_L_UpperArm",
            'left_elbow': "ValveBiped.Bip01_L_Forearm",
            'left_wrist': "ValveBiped.Bip01_L_Hand",
            'right_shoulder': "ValveBiped.Bip01_R_Clavicle",
            'right_arm': "ValveBiped.Bip01_R_UpperArm",
            'right_elbow': "ValveBiped.Bip01_R_Forearm",
            'right_wrist': "ValveBiped.Bip01_R_Hand",
            #need finger bones for Gmod Conversion Script
            'pinkie_1_l': "ValveBiped.Bip01_L_Finger4",
            'pinkie_2_l': "ValveBiped.Bip01_L_Finger41",
            'pinkie_3_l': "ValveBiped.Bip01_L_Finger42",
            'ring_1_l': "ValveBiped.Bip01_L_Finger3",
            'ring_2_l': "ValveBiped.Bip01_L_Finger31",
            'ring_3_l': "ValveBiped.Bip01_L_Finger32",
            'middle_1_l': "ValveBiped.Bip01_L_Finger2",
            'middle_2_l': "ValveBiped.Bip01_L_Finger21",
            'middle_3_l': "ValveBiped.Bip01_L_Finger22",
            'index_1_l': "ValveBiped.Bip01_L_Finger1",
            'index_2_l': "ValveBiped.Bip01_L_Finger11",
            'index_3_l': "ValveBiped.Bip01_L_Finger12",
            'thumb_1_l': "ValveBiped.Bip01_L_Finger0",
            'thumb_2_l': "ValveBiped.Bip01_L_Finger01",
            'thumb_3_l': "ValveBiped.Bip01_L_Finger02",

            'pinkie_1_r': "ValveBiped.Bip01_R_Finger4",
            'pinkie_2_r': "ValveBiped.Bip01_R_Finger41",
            'pinkie_3_r': "ValveBiped.Bip01_R_Finger42",
            'ring_1_r': "ValveBiped.Bip01_R_Finger3",
            'ring_2_r': "ValveBiped.Bip01_R_Finger31",
            'ring_3_r': "ValveBiped.Bip01_R_Finger32",
            'middle_1_r': "ValveBiped.Bip01_R_Finger2",
            'middle_2_r': "ValveBiped.Bip01_R_Finger21",
            'middle_3_r': "ValveBiped.Bip01_R_Finger22",
            'index_1_r': "ValveBiped.Bip01_R_Finger1",
            'index_2_r': "ValveBiped.Bip01_R_Finger11",
            'index_3_r': "ValveBiped.Bip01_R_Finger12",
            'thumb_1_r': "ValveBiped.Bip01_R_Finger0",
            'thumb_2_r': "ValveBiped.Bip01_R_Finger01",
            'thumb_3_r': "ValveBiped.Bip01_R_Finger02"
        }

        for bone in armature.data.bones:
            if simplify_bonename(bone.name) in reverse_bone_lookup and reverse_bone_lookup[simplify_bonename(bone.name)] in valve_translations:
                bone.name = valve_translations[reverse_bone_lookup[simplify_bonename(bone.name)]]
            else:
                translate_bone_fails += 1

        if translate_bone_fails > 0:
            self.report({'INFO'}, "Error! Failed to translate {translate_bone_fails} bones! Make sure your model has standard bone names!")

        self.report({'INFO'}, 'Connected all bones!')
        return {'FINISHED'}

@register_wrap
class TestButton(bpy.types.Operator):
    bl_idname = 'cats_manual.test'
    bl_label = 'Testing Stuff'
    bl_description = 'This is for tests by the devs only'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        self.copy_weights(context)

        self.report({'INFO'}, 'Test complete!')
        return {'FINISHED'}

    def copy_weights(self, context):
        # mesh_source = Common.get_objects()['ClothesCombined']
        # mesh_target = Common.get_objects()['ClothesW']
        #
        # mesh_source = Common.get_objects()['ClothesCombined']
        # mesh_target = Common.get_objects()['ClothesW']

        mesh_source = Common.get_objects()['Legs']
        mesh_target = Common.get_objects()['_LegsW']

        def group_source(vg):
            return mesh_source.vertex_groups[vg.group]

        def group_target(vg):
            return mesh_target.vertex_groups[vg.group]

        # Copy all vertex groups
        for vg in mesh_source.vertex_groups:
            if not mesh_target.vertex_groups.get(vg.name):
                mesh_target.vertex_groups.new(name=vg.name)

        # Copy vertex group weights
        i = 0
        for v in mesh_target.data.vertices:
            # print(i)

            # Find closest vert in source
            v_source = None
            v_dist = 100

            for v2 in mesh_source.data.vertices:
                if (v.co - v2.co).length < v_dist:
                    v_dist = (v.co - v2.co).length
                    v_source = v2
                    if v_dist < 0.0001:
                        break

            print(i, v_dist)

            for vg in v_source.groups:
                vg_target = group_target(vg)
                # print(vg_target.name, vg.weight)

                vg_target.add([v.index], vg.weight, 'REPLACE')

            i += 1
            # if i == 1000:
            #     break
