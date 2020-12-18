from .tools import common as Common
from .tools import atlas as Atlas
from .tools import eyetracking as Eyetracking
from .tools import rootbone as Rootbone
from .tools import settings as Settings
from .tools import importer as Importer
from .translations import t

from bpy.types import Scene, Material
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, CollectionProperty


def register():
    Scene.armature = EnumProperty(
        name=t('Scene.armature.label'),
        description=t('Scene.armature.desc'),
        items=Common.get_armature_list,
        update=Common.update_material_list
    )

    Scene.zip_content = EnumProperty(
        name=t('Scene.zip_content.label'),
        description=t('Scene.zip_content.desc'),
        items=Importer.get_zip_content
    )

    Scene.keep_upper_chest = BoolProperty(
        name=t('Scene.keep_upper_chest.label'),
        description=t('Scene.keep_upper_chest.desc'),
        default=False
    )

    Scene.combine_mats = BoolProperty(
        name=t('Scene.combine_mats.label'),
        description=t('Scene.combine_mats.desc'),
        default=True
    )

    Scene.remove_zero_weight = BoolProperty(
        name=t('Scene.remove_zero_weight.label'),
        description=t('Scene.remove_zero_weight.desc'),
        default=True
    )

    Scene.keep_end_bones = BoolProperty(
        name=t('Scene.keep_end_bones.label'),
        description=t('Scene.keep_end_bones.desc'),
        default=False
    )

    Scene.keep_twist_bones = BoolProperty(
        name=t('Scene.keep_twist_bones.label'),
        description=t('Scene.keep_twist_bones.desc'),
        default=False
    )

    Scene.fix_twist_bones = BoolProperty(
        name=t('Scene.fix_twist_bones.label'),
        description=t('Scene.fix_twist_bones.desc'),
        default=True
    )

    Scene.join_meshes = BoolProperty(
        name=t('Scene.join_meshes.label'),
        description=t('Scene.join_meshes.desc'),
        default=True
    )

    Scene.connect_bones = BoolProperty(
        name=t('Scene.connect_bones.label'),
        description=t('Scene.connect_bones.desc'),
        default=True
    )

    Scene.fix_materials = BoolProperty(
        name=t('Scene.fix_materials.label'),
        description=t('Scene.fix_materials.desc'),
        default=True
    )

    Scene.remove_rigidbodies_joints = BoolProperty(
        name=t('Scene.remove_rigidbodies_joints.label'),
        description=t('Scene.remove_rigidbodies_joints.desc'),
        default=True
    )

    Scene.use_google_only = BoolProperty(
        name=t('Scene.use_google_only.label'),
        description=t('Scene.use_google_only.desc'),
        default=False
    )

    Scene.show_more_options = BoolProperty(
        name=t('Scene.show_more_options.label'),
        description=t('Scene.show_more_options.desc'),
        default=False
    )

    Scene.merge_mode = EnumProperty(
        name=t('Scene.merge_mode.label'),
        description=t('Scene.merge_mode.desc'),
        items=[
            ("ARMATURE", t('Scene.merge_mode.armature.label'), t('Scene.merge_mode.armature.desc')),
            ("MESH", t('Scene.merge_mode.mesh.label'), t('Scene.merge_mode.mesh.desc'))
        ]
    )

    Scene.merge_armature_into = EnumProperty(
        name=t('Scene.merge_armature_into.label'),
        description=t('Scene.merge_armature_into.desc'),
        items=Common.get_armature_list
    )

    Scene.merge_armature = EnumProperty(
        name=t('Scene.merge_armature.label'),
        description=t('Scene.merge_armature.desc'),
        items=Common.get_armature_merge_list
    )

    Scene.attach_to_bone = EnumProperty(
        name=t('Scene.attach_to_bone.label'),
        description=t('Scene.attach_to_bone.desc'),
        items=Common.get_bones_merge
    )

    Scene.attach_mesh = EnumProperty(
        name=t('Scene.attach_mesh.label'),
        description=t('Scene.attach_mesh.desc'),
        items=Common.get_top_meshes
    )

    Scene.merge_same_bones = BoolProperty(
        name=t('Scene.merge_same_bones.label'),
        description=t('Scene.merge_same_bones.desc'),
        default=False
    )

    Scene.apply_transforms = BoolProperty(
        name=t('Scene.apply_transforms.label'),
        description=t('Scene.apply_transforms.desc'),
        default=False
    )

    Scene.merge_armatures_join_meshes = BoolProperty(
        name=t('Scene.merge_armatures_join_meshes.label'),
        description=t('Scene.merge_armatures_join_meshes.desc'),
        default=True
    )

    Scene.merge_armatures_remove_zero_weight_bones = BoolProperty(
        name=t('Scene.merge_armatures_remove_zero_weight_bones.label'),
        description=t('Scene.merge_armatures_remove_zero_weight_bones.desc'),
        default=True
    )

    # Decimation
    Scene.decimation_mode = EnumProperty(
        name=t('Scene.decimation_mode.label'),
        description=t('Scene.decimation_mode.desc'),
        items=[
            ("SMART", t('Scene.decimation_mode.smart.label'), t('Scene.decimation_mode.smart.desc')),
            ("SAFE", t('Scene.decimation_mode.safe.label'), t('Scene.decimation_mode.safe.desc')),
            ("HALF", t('Scene.decimation_mode.half.label'), t('Scene.decimation_mode.half.desc')),
            ("FULL", t('Scene.decimation_mode.full.label'), t('Scene.decimation_mode.full.desc')),
            ("CUSTOM", t('Scene.decimation_mode.custom.label'), t('Scene.decimation_mode.custom.desc'))
        ],
        default='SMART'
    )

    Scene.decimation_animation_weighting = BoolProperty(
        name=t('Scene.decimation_animation_weighting.label'),
        description=t('Scene.decimation_animation_weighting.desc'),
        default=False
    )

    Scene.decimation_animation_weighting_factor = FloatProperty(
        name=t('Scene.decimation_animation_weighting_factor.label'),
        description=t('Scene.decimation_animation_weighting_factor.desc'),
        default=0.25,
        min=0,
        max=1,
        step=0.05,
        precision=2,
        subtype='FACTOR'
    )

    Scene.bake_animation_weighting = BoolProperty(
        name=t('Scene.decimation_animation_weighting.label'),
        description=t('Scene.decimation_animation_weighting.desc'),
        default=False
    )

    Scene.bake_animation_weighting_factor = FloatProperty(
        name=t('Scene.decimation_animation_weighting_factor.label'),
        description=t('Scene.decimation_animation_weighting_factor.desc'),
        default=0.25,
        min=0,
        max=1,
        step=0.05,
        precision=2,
        subtype='FACTOR'
    )

    Scene.bake_max_tris = IntProperty(
        name=t('Scene.max_tris.label'),
        description=t('Scene.max_tris.desc'),
        default=5000,
        min=1,
        max=70000
    )

    # Bake
    Scene.bake_resolution = IntProperty(
        name=t('Scene.bake_resolution.label'),
        description=t('Scene.bake_resolution.desc'),
        default=2048,
        min=128,
        max=4096
    )

    Scene.bake_use_decimation = BoolProperty(
        name=t('Scene.bake_use_decimation.label'),
        description=t('Scene.bake_use_decimation.desc'),
        default=True
    )

    Scene.bake_generate_uvmap = BoolProperty(
        name=t('Scene.bake_generate_uvmap.label'),
        description=t('Scene.bake_generate_uvmap.desc'),
        default=True
    )

    Scene.bake_uv_overlap_correction = EnumProperty(
        name=t('Scene.bake_uv_overlap_correction.label'),
        description=t('Scene.bake_uv_overlap_correction.desc'),
        items=[
            ("NONE", t("Scene.bake_uv_overlap_correction.none.label"), t("Scene.bake_uv_overlap_correction.none.desc")),
            ("UNMIRROR", t("Scene.bake_uv_overlap_correction.unmirror.label"), t("Scene.bake_uv_overlap_correction.unmirror.desc")),
            ("REPROJECT", t("Scene.bake_uv_overlap_correction.reproject.label"), t("Scene.bake_uv_overlap_correction.reproject.desc")),
        ],
        default="UNMIRROR"
    )

    Scene.bake_prioritize_face = BoolProperty(
        name=t('Scene.bake_prioritize_face.label'),
        description=t('Scene.bake_prioritize_face.desc'),
        default=True
    )

    Scene.bake_face_scale = FloatProperty(
        name=t('Scene.bake_face_scale.label'),
        description=t('Scene.bake_face_scale.desc'),
        default=3.0,
        min=0.5,
        max=4.0,
        step=0.25,
        precision=2,
        subtype='FACTOR'
    )

    Scene.bake_quick_compare = BoolProperty(
        name=t('Scene.bake_quick_compare.label'),
        description=t('Scene.bake_quick_compare.desc'),
        default=True
    )

    Scene.bake_illuminate_eyes = BoolProperty(
        name=t('Scene.bake_illuminate_eyes.label'),
        description=t('Scene.bake_illuminate_eyes.desc'),
        default=True
    )

    Scene.bake_pass_smoothness = BoolProperty(
        name=t('Scene.bake_pass_smoothness.label'),
        description=t('Scene.bake_pass_smoothness.desc'),
        default=True
    )

    Scene.bake_pass_diffuse = BoolProperty(
        name=t('Scene.bake_pass_diffuse.label'),
        description=t('Scene.bake_pass_diffuse.desc'),
        default=True
    )

    Scene.bake_preserve_seams = BoolProperty(
        name=t('Scene.bake_preserve_seams.label'),
        description=t('Scene.bake_preserve_seams.desc'),
        default=False
    )

    Scene.bake_pass_normal = BoolProperty(
        name=t('Scene.bake_pass_normal.label'),
        description=t('Scene.bake_pass_normal.desc'),
        default=True
    )

    Scene.bake_normal_apply_trans = BoolProperty(
        name=t('Scene.bake_normal_apply_trans.label'),
        description=t('Scene.bake_normal_apply_trans.desc'),
        default=True
    )

    Scene.bake_pass_ao = BoolProperty(
        name=t('Scene.bake_pass_ao.label'),
        description=t('Scene.bake_pass_ao.desc'),
        default=False
    )

    Scene.bake_pass_questdiffuse = BoolProperty(
        name=t('Scene.bake_pass_questdiffuse.label'),
        description=t('Scene.bake_pass_questdiffuse.desc'),
        default=True
    )

    Scene.bake_pass_emit = BoolProperty(
        name=t('Scene.bake_pass_emit.label'),
        description=t('Scene.bake_pass_emit.desc'),
        default=False
    )

    Scene.bake_diffuse_alpha_pack = EnumProperty(
        name=t('Scene.bake_diffuse_alpha_pack.label'),
        description=t('Scene.bake_diffuse_alpha_pack.desc'),
        items=[
            ("NONE", t("Scene.bake_diffuse_alpha_pack.none.label"), t("Scene.bake_diffuse_alpha_pack.none.desc")),
            ("TRANSPARENCY", t("Scene.bake_diffuse_alpha_pack.transparency.label"), t("Scene.bake_diffuse_alpha_pack.transparency.desc")),
            ("SMOOTHNESS", t("Scene.bake_diffuse_alpha_pack.smoothness.label"), t("Scene.bake_diffuse_alpha_pack.smoothness.desc")),
        ],
        default="NONE"
    )

    Scene.bake_metallic_alpha_pack = EnumProperty(
        name=t('Scene.bake_metallic_alpha_pack.label'),
        description=t('Scene.bake_metallic_alpha_pack.desc'),
        items=[
            ("NONE", t("Scene.bake_metallic_alpha_pack.none.label"), t("Scene.bake_metallic_alpha_pack.none.desc")),
            ("SMOOTHNESS", t("Scene.bake_metallic_alpha_pack.smoothness.label"), t("Scene.bake_metallic_alpha_pack.smoothness.desc"))
        ],
        default="NONE"
    )

    Scene.bake_pass_alpha = BoolProperty(
        name=t('Scene.bake_pass_alpha.label'),
        description=t('Scene.bake_pass_alpha.desc'),
        default=False
    )

    Scene.bake_pass_metallic = BoolProperty(
        name=t('Scene.bake_pass_metallic.label'),
        description=t('Scene.bake_pass_metallic.desc'),
        default=False
    )

    Scene.bake_questdiffuse_opacity = FloatProperty(
        name=t('Scene.bake_questdiffuse_opacity.label'),
        description=t('Scene.bake_questdiffuse_opacity.desc'),
        default=0.75,
        min=0.0,
        max=1.0,
        step=0.05,
        precision=2,
        subtype='FACTOR'
    )


    Scene.selection_mode = EnumProperty(
        name=t('Scene.selection_mode.label'),
        description=t('Scene.selection_mode.desc'),
        items=[
            ("SHAPES", t('Scene.selection_mode.shapekeys.label'), t('Scene.selection_mode.shapekeys.desc')),
            ("MESHES", t('Scene.selection_mode.meshes.label'), t('Scene.selection_mode.meshes.desc'))
        ]
    )

    Scene.add_shape_key = EnumProperty(
        name=t('Scene.add_shape_key.label'),
        description=t('Scene.add_shape_key.desc'),
        items=Common.get_shapekeys_decimation
    )

    Scene.add_mesh = EnumProperty(
        name=t('Scene.add_mesh.label'),
        description=t('Scene.add_mesh.desc'),
        items=Common.get_meshes_decimation
    )

    Scene.decimate_fingers = BoolProperty(
        name=t('Scene.decimate_fingers.label'),
        description=t('Scene.decimate_fingers.desc')
    )

    Scene.decimate_hands = BoolProperty(
        name=t('Scene.decimate_hands.label'),
        description=t('Scene.decimate_hands.desc')
    )

    Scene.decimation_remove_doubles = BoolProperty(
        name=t('Scene.decimation_remove_doubles.label'),
        description=t('Scene.decimation_remove_doubles.desc'),
        default=True
    )

    Scene.max_tris = IntProperty(
        name=t('Scene.max_tris.label'),
        description=t('Scene.max_tris.desc'),
        default=70000,
        min=1,
        max=200000
    )

    # Eye Tracking
    Scene.eye_mode = EnumProperty(
        name=t('Scene.eye_mode.label'),
        description=t('Scene.eye_mode.desc'),
        items=[
            ("CREATION", t('Scene.eye_mode.creation.label'), t('Scene.eye_mode.creation.desc')),
            ("TESTING", t('Scene.eye_mode.testing.label'), t('Scene.eye_mode.testing.desc'))
        ],
        update=Eyetracking.stop_testing
    )

    Scene.mesh_name_eye = EnumProperty(
        name=t('Scene.mesh_name_eye.label'),
        description=t('Scene.mesh_name_eye.desc'),
        items=Common.get_meshes
    )

    Scene.head = EnumProperty(
        name=t('Scene.head.label'),
        description=t('Scene.head.desc'),
        items=Common.get_bones_head
    )

    Scene.eye_left = EnumProperty(
        name=t('Scene.eye_left.label'),
        description=t('Scene.eye_left.desc'),
        items=Common.get_bones_eye_l
    )

    Scene.eye_right = EnumProperty(
        name=t('Scene.eye_right.label'),
        description=t('Scene.eye_right.desc'),
        items=Common.get_bones_eye_r
    )

    Scene.wink_left = EnumProperty(
        name=t('Scene.wink_left.label'),
        description=t('Scene.wink_left.desc'),
        items=Common.get_shapekeys_eye_blink_l
    )

    Scene.wink_right = EnumProperty(
        name=t('Scene.wink_right.label'),
        description=t('Scene.wink_right.desc'),
        items=Common.get_shapekeys_eye_blink_r
    )

    Scene.lowerlid_left = EnumProperty(
        name=t('Scene.lowerlid_left.label'),
        description=t('Scene.lowerlid_left.desc'),
        items=Common.get_shapekeys_eye_low_l
    )

    Scene.lowerlid_right = EnumProperty(
        name=t('Scene.lowerlid_right.label'),
        description=t('Scene.lowerlid_right.desc'),
        items=Common.get_shapekeys_eye_low_r
    )

    Scene.disable_eye_movement = BoolProperty(
        name=t('Scene.disable_eye_movement.label'),
        description=t('Scene.disable_eye_movement.desc'),
        subtype='DISTANCE'
    )

    Scene.disable_eye_blinking = BoolProperty(
        name=t('Scene.disable_eye_blinking.label'),
        description=t('Scene.disable_eye_blinking.desc'),
        subtype='NONE'
    )

    Scene.eye_distance = FloatProperty(
        name=t('Scene.eye_distance.label'),
        description=t('Scene.eye_distance.desc'),
        default=0.8,
        min=0.0,
        max=2.0,
        step=1.0,
        precision=2,
        subtype='FACTOR'
    )

    Scene.eye_rotation_x = IntProperty(
        name=t('Scene.eye_rotation_x.label'),
        description=t('Scene.eye_rotation_x.desc'),
        default=0,
        min=-19,
        max=25,
        step=1,
        subtype='FACTOR',
        update=Eyetracking.set_rotation
    )

    Scene.eye_rotation_y = IntProperty(
        name=t('Scene.eye_rotation_y.label'),
        description=t('Scene.eye_rotation_y.desc'),
        default=0,
        min=-19,
        max=19,
        step=1,
        subtype='FACTOR',
        update=Eyetracking.set_rotation
    )

    Scene.iris_height = IntProperty(
        name=t('Scene.iris_height.label'),
        description=t('Scene.iris_height.desc'),
        default=0,
        min=0,
        max=100,
        step=1,
        subtype='FACTOR'
    )

    Scene.eye_blink_shape = FloatProperty(
        name=t('Scene.eye_blink_shape.label'),
        description=t('Scene.eye_blink_shape.desc'),
        default=1.0,
        min=0.0,
        max=1.0,
        step=1.0,
        precision=2,
        subtype='FACTOR'
    )

    Scene.eye_lowerlid_shape = FloatProperty(
        name=t('Scene.eye_lowerlid_shape.label'),
        description=t('Scene.eye_lowerlid_shape.desc'),
        default=1.0,
        min=0.0,
        max=1.0,
        step=1.0,
        precision=2,
        subtype='FACTOR'
    )

    # Visemes
    Scene.mesh_name_viseme = EnumProperty(
        name=t('Scene.mesh_name_viseme.label'),
        description=t('Scene.mesh_name_viseme.desc'),
        items=Common.get_meshes
    )

    Scene.mouth_a = EnumProperty(
        name=t('Scene.mouth_a.label'),
        description=t('Scene.mouth_a.desc'),
        items=Common.get_shapekeys_mouth_ah,
    )

    Scene.mouth_o = EnumProperty(
        name=t('Scene.mouth_o.label'),
        description=t('Scene.mouth_o.desc'),
        items=Common.get_shapekeys_mouth_oh,
    )

    Scene.mouth_ch = EnumProperty(
        name=t('Scene.mouth_ch.label'),
        description=t('Scene.mouth_ch.desc'),
        items=Common.get_shapekeys_mouth_ch,
    )

    Scene.shape_intensity = FloatProperty(
        name=t('Scene.shape_intensity.label'),
        description=t('Scene.shape_intensity.desc'),
        default=1.0,
        min=0.0,
        max=10.0,
        step=0.1,
        precision=2,
        subtype='FACTOR'
    )

    # Bone Parenting
    Scene.root_bone = EnumProperty(
        name=t('Scene.root_bone.label'),
        description=t('Scene.root_bone.desc'),
        items=Rootbone.get_parent_root_bones,
    )

    # Optimize
    Scene.optimize_mode = EnumProperty(
        name=t('Scene.optimize_mode.label'),
        description=t('Scene.optimize_mode.desc'),
        items=[
            ("ATLAS", t('Scene.optimize_mode.atlas.label'), t('Scene.optimize_mode.atlas.desc')),
            ("MATERIAL", t('Scene.optimize_mode.material.label'), t('Scene.optimize_mode.material.desc')),
            ("BONEMERGING", t('Scene.optimize_mode.bonemerging.label'), t('Scene.optimize_mode.bonemerging.desc')),
        ]
    )

    # Atlas
    # Material.add_to_atlas = BoolProperty(
    #     description=t('Add this material to the atlas'),
    #     default=False
    # )

    # Scene.material_list_index = IntProperty(
    #     default=0
    # )

    # Scene.material_list = CollectionProperty(
    #     type=Atlas.MaterialsGroup
    # )

    # Scene.clear_materials = BoolProperty(
    #     description=t('Clear materials checkbox'),
    #     default=True
    # )

    # Bone Merging
    Scene.merge_ratio = FloatProperty(
        name=t('Scene.merge_ratio.label'),
        description=t('Scene.merge_ratio.desc'),
        default=50,
        min=1,
        max=100,
        step=1,
        precision=0,
        subtype='PERCENTAGE'
    )

    Scene.merge_mesh = EnumProperty(
        name=t('Scene.merge_mesh.label'),
        description=t('Scene.merge_mesh.desc'),
        items=Common.get_meshes
    )

    Scene.merge_bone = EnumProperty(
        name=t('Scene.merge_bone.label'),
        description=t('Scene.merge_bone.desc'),
        items=Rootbone.get_parent_root_bones,
    )

    # Settings
    Scene.show_mmd_tabs = BoolProperty(
        name=t('Scene.show_mmd_tabs.label'),
        description=t('Scene.show_mmd_tabs.desc'),
        default=True,
        update=Common.toggle_mmd_tabs_update
    )
    Scene.embed_textures = BoolProperty(
        name=t('Scene.embed_textures.label'),
        description=t('Scene.embed_textures.desc'),
        default=False,
        update=Settings.update_settings
    )
    Scene.use_custom_mmd_tools = BoolProperty(
        name=t('Scene.use_custom_mmd_tools.label'),
        description=t('Scene.use_custom_mmd_tools.desc'),
        default=False,
        update=Settings.update_settings
    )

    Scene.debug_translations = BoolProperty(
        name=t('Scene.debug_translations.label'),
        description=t('Scene.debug_translations.desc'),
        default=False
    )

    # Scene.disable_vrchat_features = BoolProperty(
    #     name=t('Disable VRChat Only Features'),
    #     description='This will disable features which are solely used for VRChat.'
    #                 '\nThe following will be disabled:'
    #                 '\n- Eye Tracking'
    #                 '\n- Visemes',
    #     default=False,
    #     update=Settings.update_settings
    # )

    # Copy Protection - obsolete
    # Scene.protection_mode = EnumProperty(
    #     name=t("Randomization Level"),
    #     description=t("Randomization Level"),
    #     items=[
    #         ("FULL", "Full", "This will randomize every vertex of your model and it will be completely unusable for thieves.\n"
    #                          'However this method might cause problems with the Outline option from Cubed shader.\n'
    #                          'If you have any issues ingame try again with option "Partial".'),
    #         ("PARTIAL", "Partial", 'Use this if you experience issues ingame with the Full option!\n'
    #                                '\n'
    #                                "This will only randomize a number of vertices and therefore will have a few unprotected areas,\n"
    #                                "but it's still unusable to thieves as a whole.\n"
    #                                'This method however reduces the glitches that can occur ingame by a lot.')
    #     ],
    #     default='FULL'
    # )
