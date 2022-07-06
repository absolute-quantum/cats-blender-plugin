from .tools import common as Common
from .tools import atlas as Atlas
from .tools import eyetracking as Eyetracking
from .tools import rootbone as Rootbone
from .tools import settings as Settings
from .tools import importer as Importer
from .tools import translations as Translations
from .tools.translations import t

from bpy.types import Scene, Material, PropertyGroup
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, CollectionProperty, IntVectorProperty, StringProperty, FloatVectorProperty
from bpy.utils import register_class


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
        default=True
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

    # Manual
    Scene.use_google_only = BoolProperty(
        name=t('Scene.use_google_only.label'),
        description=t('Scene.use_google_only.desc'),
        default=False
    )

    Scene.keep_merged_bones = BoolProperty(
        name=t('keep_merged_bones'),
        description=t('select_this_to_keep_the_bones_after_merging_them_to_their_parents_or_to_the_active_bone'),
        default=False
    )

    Scene.merge_visible_meshes_only = BoolProperty(
        name=t('merge_visible_meshes_only'),
        description=t('select_this_to_only_merge_the_weights_of_the_visible_meshes'),
        default=False
    )

    Scene.show_more_options = BoolProperty(
        name=t('Scene.show_more_options.label'),
        description=t('Scene.show_more_options.desc'),
        default=False
    )

    # Custom Avatar Creation
    Scene.merge_mode = EnumProperty(
        name=t('Scene.merge_mode.label'),
        description=t('Scene.merge_mode.desc'),
        items=[
            ("ARMATURE", t('Scene.merge_mode.armature.label'), t('Scene.merge_mode.armature.desc')),
            ("MESH", t('Scene.merge_mode.mesh.label'), t('Scene.merge_mode.mesh.desc')),
            ("CLOTHES", "Fit Clothes", "Here you can attach un-rigged clothes to an already rigged body"),
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

    Scene.generate_twistbones_upper = BoolProperty(
        name=t("generate_upperhalf"),
        description=t("generate_the_twistbones_on_the_upper_half_of_the_bone_usually_used_for_upper_legs"),
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

    Scene.merge_armatures_cleanup_shape_keys = BoolProperty(
        name=t('Scene.merge_armatures_cleanup_shape_keys.label'),
        description=t('Scene.merge_armatures_cleanup_shape_keys.desc'),
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
        default=True
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

    Scene.decimation_animation_weighting_include_shapekeys = BoolProperty(
        name="Include Shapekeys",
        description="Factor shapekeys into animation weighting. Disable if your model has large body shapekeys.",
        default=False
    )

    # Bake
    Scene.bake_use_draft_quality = BoolProperty(
        name='Draft Quality',
        description='Reduce the number of samples and cap resolution at 1024, speeds up iteration',
        default=False
    )

    Scene.bake_animation_weighting = BoolProperty(
        name=t('Scene.decimation_animation_weighting.label'),
        description=t('Scene.decimation_animation_weighting.desc'),
        default=True
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

    Scene.bake_animation_weighting_include_shapekeys = BoolProperty(
        name="Include Shapekeys",
        description="Factor shapekeys into animation weighting. Disable if your model has large body shapekeys.",
        default=False
    )

    class BakePlatformPropertyGroup(PropertyGroup):
        name: StringProperty(name='name', default=t("New Platform"))
        use_decimation: BoolProperty(
            name=t('Scene.bake_use_decimation.label'),
            description=t('Scene.bake_use_decimation.desc'),
            default=True
        )
        max_tris: IntProperty(
            name=t('Scene.max_tris.label'),
            description=t('Scene.max_tris.desc'),
            default=7500,
            min=1,
            max=70000
        )
        use_lods: BoolProperty(
            name=t("generate_lods"),
            description=t("generate_courser_decimation_levels_for_efficient_rendering"),
            default=False
        )
        lods: FloatVectorProperty(
            name=t("lods"),
            description=t('lod_generation_levels_as_a_percent_of_the_max_tris'),
            #min=0.0,
            #max=1.0
        )
        use_physmodel: BoolProperty(
            name=t("generate_physics_model"),
            description=t("generate_an_additional_lod_used_for_simplified_physics_interactions"),
            default=False
        )
        physmodel_lod: FloatProperty(
            name=t("physmodel_percent"),
            default=0.1,
            min=0.0,
            max=1.0
        )
        remove_doubles: BoolProperty(
            name=t('Scene.decimation_remove_doubles.label'),
            description=t('Scene.decimation_remove_doubles.desc'),
            default=True
        )
        preserve_seams: BoolProperty(
            name=t('Scene.bake_preserve_seams.label'),
            description=t('Scene.bake_preserve_seams.desc'),
            default=False
        )
        optimize_static: BoolProperty(
            name=t("optimize_static_shapekeys"),
            description=t("seperate_vertices_unaffected_by_shape_keys_into_their_own_mesh_this_adds_a_drawcall_but_comes_with_a_significant_gpu_cost_savings_especially_on_mobile"),
            default=False
        )
        merge_twistbones: BoolProperty(
            name=t("merge_twist_bones"),
            description=t("merge_any_bone_with_twist_in_the_name_useful_as_quest_does_not_support_constraints"),
            default=False
        )
        metallic_alpha_pack: EnumProperty(
            name=t('Scene.bake_metallic_alpha_pack.label'),
            description=t('Scene.bake_metallic_alpha_pack.desc'),
            items=[
                ("NONE", t("Scene.bake_metallic_alpha_pack.none.label"), t("Scene.bake_metallic_alpha_pack.none.desc")),
                ("SMOOTHNESS", t("Scene.bake_metallic_alpha_pack.smoothness.label"), t("Scene.bake_metallic_alpha_pack.smoothness.desc"))
            ],
            default="NONE"
        )
        metallic_pack_ao: BoolProperty(
            name=t("pack_ao_to_metallic_green"),
            description=t("pack_ambient_occlusion_to_the_green_channel_saves_a_texture_as_unity_uses_g_for_ao_r_for_metallic"),
            default=True
        )
        diffuse_vertex_colors: BoolProperty(
            name=t("bake_to_vertex_colors"),
            description=t("rebake_to_vertex_colors_after_initial_bake_avoids_an_entire_extra_texture_if_your_colors_are_simple_enough_incorperates_ao"),
            default=False
        )
        diffuse_alpha_pack: EnumProperty(
            name=t('Scene.bake_diffuse_alpha_pack.label'),
            description=t('Scene.bake_diffuse_alpha_pack.desc'),
            items=[
                ("NONE", t("Scene.bake_diffuse_alpha_pack.none.label"), t("Scene.bake_diffuse_alpha_pack.none.desc")),
                ("TRANSPARENCY", t("Scene.bake_diffuse_alpha_pack.transparency.label"), t("Scene.bake_diffuse_alpha_pack.transparency.desc")),
                ("SMOOTHNESS", t("Scene.bake_diffuse_alpha_pack.smoothness.label"), t("Scene.bake_diffuse_alpha_pack.smoothness.desc")),
                ("EMITMASK", "Emit Mask", "A single-color emission mask, for use with preapplied emission")
            ],
            default="NONE"
        )
        normal_alpha_pack: EnumProperty(
            name=t("normal_alpha_pack"),
            description=t('Scene.bake_diffuse_alpha_pack.desc'),
            items=[
                ("NONE", t("Scene.bake_diffuse_alpha_pack.none.label"), t("Scene.bake_diffuse_alpha_pack.none.desc")),
                ("SPECULAR", "Specular", t("Scene.bake_diffuse_alpha_pack.none.desc")),
                ("SMOOTHNESS", "Smoothness", t("Scene.bake_diffuse_alpha_pack.none.desc")),
            ],
            default="NONE"
        )
        normal_invert_g: BoolProperty(
            name=t("invert_green_channel"),
            description=t("source_engine_uses_an_inverse_green_channel_this_fixes_that_on_export"),
            default=False
        )
        diffuse_premultiply_ao: BoolProperty(
            name=t("premultiply_diffuse_w_ao"),
            description=t('Scene.bake_pass_questdiffuse.desc'),
            default=False
        )
        diffuse_premultiply_opacity: FloatProperty(
            name=t('Scene.bake_questdiffuse_opacity.label'),
            description=t('Scene.bake_questdiffuse_opacity.desc'),
            default=1.0,
            min=0.0,
            max=1.0,
            step=0.05,
            precision=2,
            subtype='FACTOR'
        )
        smoothness_premultiply_ao: BoolProperty(
            name=t("premultiply_smoothness_w_ao"),
            description=t("while_not_technically_accurate_this_avoids_the_shine_effect_on_obscured_portions_of_your_model"),
            default=False
        )
        smoothness_premultiply_opacity: FloatProperty(
            name=t('Scene.bake_questdiffuse_opacity.label'),
            description=t('Scene.bake_questdiffuse_opacity.desc'),
            default=1.0,
            min=0.0,
            max=1.0,
            step=0.05,
            precision=2,
            subtype='FACTOR'
        )
        translate_bone_names: EnumProperty(
            name=t("translate_bone_names"),
            description=t("target_another_bone_naming_standard_when_exporting_requires_standard_bone_names"),
            items=[
                ("NONE", "None", "Don't translate any bones"),
                ("VALVE", "Valve", "Translate to Valve conventions when exporting, for use with Source Engine"),
                ("SECONDLIFE", "Second Life", "Translate to Second Life conventions when exporting, for use with Second Life")
            ],
            default="NONE"
        )
        export_format: EnumProperty(
            name=t('export_format'),
            description=t('model_format_to_use_when_exporting'),
            items=[
                ("FBX", "FBX", "FBX export format, for use with Unity"),
                ("DAE", "DAE", "Collada DAE, for use with Second Life and older engines"),
                ("GMOD", "GMOD", "Exports to gmod. Requires TGA image export enabled as well to work")
            ]
        )
        image_export_format: EnumProperty(
            name=t('image_export_format'),
            description=t('image_type_to_use_when_exporting'),
            items=[
                ("TGA", ".tga", "targa export format, for use with Gmod"),
                ("PNG", ".png", "png format, for use with most platforms.")
            ]
        )
        specular_setup: BoolProperty(
            name=t('specular_setup'),
            description=t("convert_diffuse_and_metallic_to_premultiplied_diffuse_and_specular_compatible_with_older_engines"),
            default=False
        )
        specular_alpha_pack: EnumProperty(
            name=t("specular_alpha_channel"),
            description=t("what_to_pack_to_the_alpha_channel_of_specularity"),
            items=[
                ("NONE", t("Scene.bake_metallic_alpha_pack.none.label"), t("Scene.bake_metallic_alpha_pack.none.desc")),
                ("SMOOTHNESS", t("Scene.bake_metallic_alpha_pack.smoothness.label"), "Smoothness, for use with Second Life")
            ],
            default="NONE"
        )
        phong_setup: BoolProperty(
            name=t('phong_setup_source'),
            description=t("for_source_engine_only_provides_diffuse_lighting_reflections_for_nonmetallic_objects"),
            default=False
        )
        diffuse_emit_overlay: BoolProperty(
            name=t('diffuse_emission_overlay'),
            description=t('blends_emission_into_the_diffuse_map_for_engines_without_a_seperate_emission_map'),
            default=False
        )
        specular_smoothness_overlay: BoolProperty(
            name=t('specular_smoothness_overlay'),
            description=t('merges_smoothness_into_the_specular_map_for_engines_without_a_seperate_smoothness_map'),
            default=False
        )
        gmod_model_name: StringProperty(name='Gmod Model Name', default="missing no")
        prop_bone_handling: EnumProperty(
            name="Prop objects",
            description="What to do with objects marked as Props",
            items=[
                ("NONE", "None", "Treat as ordinary objects and bake in"),
                ("GENERATE", "Generate Bones/Animations", "Generate prop bones and animations for toggling"),
                ("REMOVE", "Remove", "Remove completely, for platforms with no animation support"),
            ],
            default="GENERATE"
        )
        copy_only_handling: EnumProperty(
            name="Copy Only objects",
            description="What to do with objects marked as Copy Only",
            items=[
                ("COPY", "Copy", "Copy and export, but do not bake in"),
                ("REMOVE", "Remove", "Remove completely, for e.g. eye shells"),
            ],
            default="COPY"
        )

    register_class(BakePlatformPropertyGroup)

    Scene.bake_platforms = CollectionProperty(
        type=BakePlatformPropertyGroup
    )
    Scene.bake_platform_index = IntProperty(default=0)

    Scene.bake_cleanup_shapekeys = BoolProperty(
        name=t("cleanup_shapekeys"),
        description=t("remove_backup_shapekeys_in_the_final_result_eg_key__reverted_or_blinkold"),
        default=True
    )

    Scene.bake_resolution = IntProperty(
        name=t('Scene.bake_resolution.label'),
        description=t('Scene.bake_resolution.desc'),
        default=2048,
        min=256,
        max=4096
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
            ("MANUAL", "Manual", "Bake will take island information from any UVMap named 'Target' from your meshes, else it will default to the render-active one. Decimation works better when there's only one giant island per loose mesh!")
        ],
        default="UNMIRROR"
    )

    Scene.uvp_lock_islands = BoolProperty(
        name=t("keep_overlapping_islands_uvp"),
        description=t("experimental_try_to_keep_uvps_lock_overlapping_enabled"),
        default=False
    )

    Scene.bake_device = EnumProperty(
        name=t('bake_device'),
        description=t('device_to_bake_on_gpu_gives_a_significant_speedup_but_can_cause_issues_depending_on_your_graphics_drivers'),
        default='GPU',
        items=[
            ('CPU', 'CPU', 'Perform bakes on CPU (Safe)'),
            ('GPU', 'GPU', 'Perform bakes on GPU (Fast)')
        ]
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
        soft_min=0.5,
        soft_max=4.0,
        step=0.25,
        precision=2,
        subtype='FACTOR'
    )

    Scene.bake_sharpen = BoolProperty(
        name=t("sharpen_bakes"),
        description=t("sharpen_resampled_images_after_baking_diffusesmoothnessmetallic_reccomended_as_any_sampling_will_cause_blur"),
        default=True
    )

    Scene.bake_denoise = BoolProperty(
        name=t("denoise_renders"),
        description=t("denoise_the_resulting_image_after_emitao_reccomended_as_this_will_reduce_the_grainy_quality_of_inexpensive_rendering"),
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

    Scene.bake_pass_normal = BoolProperty(
        name=t('Scene.bake_pass_normal.label'),
        description=t('Scene.bake_pass_normal.desc'),
        default=True
    )

    Scene.bake_pass_displacement = BoolProperty(
        name=t('Scene.bake_pass_displacement.label'),
        description=t('Scene.bake_pass_displacement.desc'),
        default=True
    )

    Scene.bake_normal_apply_trans = BoolProperty(
        name=t('Scene.bake_normal_apply_trans.label'),
        description=t('Scene.bake_normal_apply_trans.desc'),
        default=True
    )

    Scene.bake_apply_keys = BoolProperty(
        name=t("apply_current_shapekey_mix"),
        description=t("when_selected_currently_active_shape_keys_will_be_applied_to_the_basis_this_is_extremely_beneficial_to_performance_if_your_avatar_is_intended_to_default_to_one_shapekey_mix_as_having_active_shapekeys_all_the_time_is_expensive_keys_ending_in_bake_are_always_applied_to_the_basis_and_removed_completely_regardless_of_this_option"),
        default=False
    )

    Scene.bake_ignore_hidden = BoolProperty(
        name=t("ignore_hidden_objects"),
        description=t("ignore_currently_hidden_objects_when_copying"),
        default=True
    )

    Scene.bake_show_advanced_general_options = BoolProperty(
        name=t("show_advanced_general_options"),
        description=t("will_show_extra_options_related_to_which_bake_passes_are_performed_and_how"),
        default=False
    )

    Scene.bake_show_advanced_platform_options = BoolProperty(
        name=t("show_advanced_platform_options"),
        description=t("will_show_extra_options_related_to_applicable_bones_and_texture_packing_setups"),
        default=False
    )

    Scene.bake_pass_ao = BoolProperty(
        name=t('Scene.bake_pass_ao.label'),
        description=t('Scene.bake_pass_ao.desc'),
        default=False
    )

    Scene.bake_pass_emit = BoolProperty(
        name=t('Scene.bake_pass_emit.label'),
        description=t('Scene.bake_pass_emit.desc'),
        default=False
    )

    Scene.bake_emit_indirect = BoolProperty(
        name=t("bake_projected_light"),
        description=t("bake_the_effect_of_emission_on_nearby_surfaces_results_in_much_more_realistic_lighting_effects_but_can_animate_less_well"),
        default=False
    )

    Scene.bake_emit_exclude_eyes = BoolProperty(
        name=t("exclude_eyes"),
        description=t("bakes_the_effect_of_any_eye_glow_onto_surrounding_objects_but_not_viceversa_improves_animation_when_eyes_are_moving_around"),
        default=True
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

    Scene.bake_optimize_solid_materials = BoolProperty(
        name=t("optimize_solid_materials"),
        description=t("optimizes_solid_materials_by_making_a_small_area_for_them_ao_pass_will_nullify"),
        default=True
    )

    Scene.bake_unwrap_angle = FloatProperty(
        name=t("unwrap_angle"),
        description=t("the_angle_reproject_uses_when_unwrapping_larger_angles_yield_less_islands_but_more_stretching_and_smaller_does_opposite"),
        default=66.0,
        min=0.1,
        max=89.9,
        step=0.1,
        precision=1
    )

    Scene.bake_steam_library = StringProperty(name='Steam Library', default="C:\\Program Files (x86)\\Steam\\")

    Scene.selection_mode = EnumProperty(
        name=t('Scene.selection_mode.label'),
        description=t('Scene.selection_mode.desc'),
        items=[
            ("SHAPES", t('Scene.selection_mode.shapekeys.label'), t('Scene.selection_mode.shapekeys.desc')),
            ("MESHES", t('Scene.selection_mode.meshes.label'), t('Scene.selection_mode.meshes.desc'))
        ]
    )

    Scene.bake_diffuse_indirect = BoolProperty(
        name="Bake indirect light",
        description="Bake reflected light as if the only light source is ambient light",
        default=False
    )

    Scene.bake_diffuse_indirect_opacity = FloatProperty(
        name="Opacity",
        description="How bright the indirect light will be on the diffuse layer",
        default=0.5,
        min=0.0,
        max=1.0,
        step=0.05,
        precision=2,
        subtype='FACTOR'
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
        max=500000
    )

    Scene.cats_is_unittest = BoolProperty(
        default=False
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
    Scene.show_avatar_2_tabs = BoolProperty(
        name=t('Scene.show_avatar_2_tabs.label'),
        description=t('Scene.show_avatar_2_tabs.desc'),
        default=False,
        update=Translations.update_ui
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
    Scene.ui_lang = EnumProperty(
        name=t('Scene.ui_lang.label'),
        description=t('Scene.ui_lang.desc'),
        items=Translations.get_languages_list,
        update=Translations.update_ui
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
