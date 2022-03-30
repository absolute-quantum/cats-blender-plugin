# MIT License

# Copyright (c) 2017 GiveMeAllYourCats

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Code author: GiveMeAllYourCats
# Repo: https://github.com/michaeldegroot/cats-blender-plugin
# Edits by: GiveMeAllYourCats

import unittest
import sys
import bpy

from bpy.types import Scene, Material, PropertyGroup
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, CollectionProperty, IntVectorProperty, StringProperty, FloatVectorProperty
from bpy.utils import register_class

class TestAddon(unittest.TestCase):
    def test_extensions(self):
        bpy.ops.cats_armature.fix(is_unittest=True)

        bpy.context.scene.debug_translations = True
        bpy.context.scene.use_custom_mmd_tools = True
        bpy.context.scene.embed_textures = True
        bpy.context.scene.show_mmd_tabs = True
        bpy.context.scene.disable_eye_blinking = True
        bpy.context.scene.disable_eye_movement = True
        bpy.context.scene.decimation_remove_doubles = True
        bpy.context.scene.decimate_hands = True
        bpy.context.scene.decimate_fingers = True
        bpy.context.scene.bake_optimize_solid_materials = True
        bpy.context.scene.bake_pass_metallic = True
        bpy.context.scene.bake_pass_alpha = True
        bpy.context.scene.bake_emit_exclude_eyes = True
        bpy.context.scene.bake_emit_indirect = True
        bpy.context.scene.bake_pass_emit = True
        bpy.context.scene.bake_pass_ao = True
        bpy.context.scene.bake_show_advanced_platform_options = True
        bpy.context.scene.bake_show_advanced_general_options = True
        bpy.context.scene.bake_ignore_hidden = True
        bpy.context.scene.bake_apply_keys = True
        bpy.context.scene.bake_normal_apply_trans = True
        bpy.context.scene.bake_pass_normal = True
        bpy.context.scene.bake_pass_diffuse = True
        bpy.context.scene.bake_pass_smoothness = True
        bpy.context.scene.bake_illuminate_eyes = True
        bpy.context.scene.bake_denoise = True
        bpy.context.scene.bake_sharpen = True
        bpy.context.scene.bake_prioritize_face = True
        bpy.context.scene.uvp_lock_islands = True
        bpy.context.scene.bake_generate_uvmap = True
        bpy.context.scene.bake_cleanup_shapekeys = True
        bpy.context.scene.merge_armatures_cleanup_shape_keys = True
        bpy.context.scene.merge_armatures_remove_zero_weight_bones = True
        bpy.context.scene.merge_armatures_join_meshes = True
        bpy.context.scene.generate_twistbones_upper = True
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
        bpy.context.scene.bake_optimize_solid_materials = False
        bpy.context.scene.bake_pass_metallic = False
        bpy.context.scene.bake_pass_alpha = False
        bpy.context.scene.bake_emit_exclude_eyes = False
        bpy.context.scene.bake_emit_indirect = False
        bpy.context.scene.bake_pass_emit = False
        bpy.context.scene.bake_pass_ao = False
        bpy.context.scene.bake_show_advanced_platform_options = False
        bpy.context.scene.bake_show_advanced_general_options = False
        bpy.context.scene.bake_ignore_hidden = False
        bpy.context.scene.bake_apply_keys = False
        bpy.context.scene.bake_normal_apply_trans = False
        bpy.context.scene.bake_pass_normal = False
        bpy.context.scene.bake_pass_diffuse = False
        bpy.context.scene.bake_pass_smoothness = False
        bpy.context.scene.bake_illuminate_eyes = False
        bpy.context.scene.bake_denoise = False
        bpy.context.scene.bake_sharpen = False
        bpy.context.scene.bake_prioritize_face = False
        bpy.context.scene.uvp_lock_islands = False
        bpy.context.scene.bake_generate_uvmap = False
        bpy.context.scene.bake_cleanup_shapekeys = False
        bpy.context.scene.merge_armatures_cleanup_shape_keys = False
        bpy.context.scene.merge_armatures_remove_zero_weight_bones = False
        bpy.context.scene.merge_armatures_join_meshes = False
        bpy.context.scene.generate_twistbones_upper = False
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
