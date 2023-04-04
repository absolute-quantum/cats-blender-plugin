# GPL License

import unittest
import sys
import bpy

from bpy.types import Scene, Material, PropertyGroup
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, CollectionProperty, IntVectorProperty, StringProperty, FloatVectorProperty
from bpy.utils import register_class

class TestAddon(unittest.TestCase):
    def test_extensions(self):
        bpy.context.scene.debug_translations = True
        bpy.context.scene.use_custom_mmd_tools = True
        bpy.context.scene.embed_textures = True
        bpy.context.scene.show_mmd_tabs = True
        bpy.context.scene.disable_eye_blinking = True
        bpy.context.scene.disable_eye_movement = True
        bpy.context.scene.decimation_remove_doubles = True
        bpy.context.scene.decimate_hands = True
        bpy.context.scene.decimate_fingers = True
        bpy.context.scene.merge_armatures_cleanup_shape_keys = True
        bpy.context.scene.merge_armatures_remove_zero_weight_bones = True
        bpy.context.scene.merge_armatures_join_meshes = True
        bpy.context.scene.apply_transforms = True
        bpy.context.scene.merge_same_bones = True
        bpy.context.scene.show_more_options = True
        bpy.context.scene.merge_visible_meshes_only = True
        bpy.context.scene.keep_merged_bones = True
        bpy.context.scene.use_google_only = True
        bpy.context.scene.remove_rigidbodies_joints = True
        bpy.context.scene.fix_materials = True
        bpy.context.scene.connect_bones = True
        bpy.context.scene.join_meshes = True
        bpy.context.scene.fix_twist_bones = True
        bpy.context.scene.keep_twist_bones = True
        bpy.context.scene.keep_end_bones = True
        bpy.context.scene.remove_zero_weight = True
        bpy.context.scene.combine_mats = True
        bpy.context.scene.keep_upper_chest = True

        bpy.context.scene.debug_translations = False
        bpy.context.scene.use_custom_mmd_tools = False
        bpy.context.scene.embed_textures = False
        bpy.context.scene.show_mmd_tabs = False
        bpy.context.scene.disable_eye_blinking = False
        bpy.context.scene.disable_eye_movement = False
        bpy.context.scene.decimation_remove_doubles = False
        bpy.context.scene.decimate_hands = False
        bpy.context.scene.decimate_fingers = False
        bpy.context.scene.merge_armatures_cleanup_shape_keys = False
        bpy.context.scene.merge_armatures_remove_zero_weight_bones = False
        bpy.context.scene.merge_armatures_join_meshes = False
        bpy.context.scene.apply_transforms = False
        bpy.context.scene.merge_same_bones = False
        bpy.context.scene.show_more_options = False
        bpy.context.scene.merge_visible_meshes_only = False
        bpy.context.scene.keep_merged_bones = False
        bpy.context.scene.use_google_only = False
        bpy.context.scene.remove_rigidbodies_joints = False
        bpy.context.scene.fix_materials = False
        bpy.context.scene.connect_bones = False
        bpy.context.scene.join_meshes = False
        bpy.context.scene.fix_twist_bones = False
        bpy.context.scene.keep_twist_bones = False
        bpy.context.scene.keep_end_bones = False
        bpy.context.scene.remove_zero_weight = False
        bpy.context.scene.combine_mats = False
        bpy.context.scene.keep_upper_chest = False

        #result = bpy.ops.cats_atlas.generate_atlas()
        # self.assertTrue(result == {'CANCELLED'})
        # self.assertTrue(result == {'FINISHED'})  # Does not work because it requires an external plugin which is not installed
        self.assertTrue(True)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
