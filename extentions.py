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

    # Bake
    Scene.bake_resolution = IntProperty(
        name="Resolution",
        description="Output resolution for the textures.\n" \
                    "- 2048 is typical for desktop use.\n" \
                    "- 1024 is reccomended for the Quest",
        default=2048,
        min=128,
        max=4096
    )

    Scene.bake_use_decimation = BoolProperty(
        name='Decimate',
        description='Reduce polycount before baking using decimation settings',
        default=True
    )

    Scene.bake_generate_uvmap = BoolProperty(
        name='Generate UVMap',
        description="Re-pack islands for your mesh to a new non-overlapping UVMap.\n" \
                    "Only disable if your UVs are non-overlapping already.\n" \
                    "This will leave any map named \"Detail Map\" alone.\n" \
                    "Uses UVPackMaster where available for more efficient UVs, make sure the window is showing",

        default=True
    )

    Scene.bake_smart_uvmap = BoolProperty(
        name='Smart UV Project',
        description="Generate a new UVMap with Blender's Smart UV Project option.\n" \
                    "Will avoid overlaps but doesn't give the best results.\n" \
                    "Use if overlaps are hard to avoid",
        default=False
    )

    Scene.bake_prioritize_face = BoolProperty(
        name='Prioritize Face/Eyes',
        description='Scale any UV islands attached to the head/eyes by a given factor.',
        default=True
    )

    Scene.bake_face_scale = FloatProperty(
        name="Face/Eyes Scale",
        description="How much to scale up the face/eyes textures.",
        default=3.0,
        min=0.5,
        max=4.0,
        step=0.25,
        precision=2,
        subtype='FACTOR'
    )

    Scene.bake_illuminate_eyes = BoolProperty(
        name='Set eyes to full brightness',
        description='Relight LeftEye and RightEye to be full brightness.\n' \
                    "Without this, the eyes will have the shadow of the surrounding socket baked in,\n"
                    "which doesn't animate well",
        default=True
    )

    Scene.bake_pass_smoothness = BoolProperty(
        name='Smoothness',
        description='Bakes Roughness and then inverts the values.\n' \
                    'To use this, it needs to be packed to the Alpha channel of either Diffuse or Metallic.\n' \
                    'Not neccesary if your mesh has a global roughness value',
        default=True
    )

    Scene.bake_smoothness_diffusepack = BoolProperty(
        name='Pack to diffuse alpha',
        description='Copies the smoothness map to the alpha channel of the diffuse map.\n' \
                    "Make sure to set Smoothness > Source to 'Albedo Alpha' in your Unity material",
        default=True
    )

    Scene.bake_pass_diffuse = BoolProperty(
        name='Diffuse (Color)',
        description='Bakes diffuse, un-lighted color. Usually you will want this.',
        default=True
    )

    Scene.bake_preserve_seams = BoolProperty(
        name="Preserve seams",
        description='Forces the Decimate operation to preserve vertices making up seams, preventing hard edges along seams.\n' \
                    'May result in less ideal geometry.\n' \
                    "Use if you notice ugly edges along your texture seams.",
        default=False
    )

    Scene.bake_pass_normal = BoolProperty(
        name='Normal (Bump)',
        description="Bakes a normal (bump) map. Allows you to keep the shading of a complex object with\n" \
                    "the geometry of a simple object. If you have selected 'Decimate', it will create a map\n" \
                    "that makes the low res output look like the high res input.\n" \
                    "Will not work well if you have self-intersecting islands",
        default=True
    )

    Scene.bake_normal_apply_trans = BoolProperty(
        name='Apply transforms',
        description="Applies offsets while baking normals. Neccesary if your model has many materials with different normal maps\n" \
                    "Turn this off if applying location causes problems with your model",
        default=True
    )

    Scene.bake_pass_ao = BoolProperty(
        name='Ambient Occlusion',
        description='Bakes Ambient Occlusion, non-projected shadows. Adds a significant amount of detail to your model.\n' \
                    'Reccomended for non-toon style avatars.\n' \
                    'Takes a fairly long time to bake',
        default=False
    )

    Scene.bake_pass_questdiffuse = BoolProperty(
        name='Quest Diffuse (Color+AO)',
        description='Blends the result of the Diffuse and AO bakes to make Quest-compatible shading.',
        default=True
    )

    Scene.bake_pass_emit = BoolProperty(
        name='Emit',
        description='Bakes Emit, glowyness',
        default=False
    )

    Scene.bake_show_advanced = BoolProperty(
        name='Advanced',
        description='Show advanced passes. These are not natively bakeable in Blender,\n' \
                    'so they may not work as well',
        default=False
    )

    Scene.bake_pass_alpha = BoolProperty(
        name='Transparency',
        description='Bakes transparency by connecting the last Principled BSDF Alpha input\n' \
                    'to the Base Color input and baking Diffuse',
        default=False
    )

    Scene.bake_alpha_diffusepack = BoolProperty(
        name='Pack to diffuse alpha',
        description='Copies the alpha map to the alpha channel of the diffuse map.\n' \
                    "This will override any existing alpha map",
        default=True
    )

    Scene.bake_pass_metallic = BoolProperty(
        name='Metallic',
        description='Bakes metallic by connecting the last Principled BSDF Metallic input\n' \
                    'to the Base Color input and baking Diffuse',
        default=False
    )

    Scene.bake_questdiffuse_opacity = FloatProperty(
        name="AO Opacity",
        description="The opacity of the shadows to blend onto the Diffuse map.\n" \
                    "This should match the unity slider for AO on the Desktop version.",
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
    #     description='Add this material to the atlas',
    #     default=False
    # )

    # Scene.material_list_index = IntProperty(
    #     default=0
    # )

    # Scene.material_list = CollectionProperty(
    #     type=Atlas.MaterialsGroup
    # )

    # Scene.clear_materials = BoolProperty(
    #     description='Clear materials checkbox',
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
        update=Common.toggle_mmd_tabs
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
    #     name='Disable VRChat Only Features',
    #     description='This will disable features which are solely used for VRChat.'
    #                 '\nThe following will be disabled:'
    #                 '\n- Eye Tracking'
    #                 '\n- Visemes',
    #     default=False,
    #     update=Settings.update_settings
    # )

    # Copy Protection - obsolete
    # Scene.protection_mode = EnumProperty(
    #     name="Randomization Level",
    #     description="Randomization Level",
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
