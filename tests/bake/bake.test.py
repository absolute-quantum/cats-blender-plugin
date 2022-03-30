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

class TestAddon(unittest.TestCase):
    def test_bake_button(self):
        bpy.ops.cats_bake.preset_all()

        bpy.context.scene.bake_resolution = 128
        result = bpy.ops.cats_bake.bake(is_unittest=True)

        # TODO: take a random sampling of each image result, confirm it's +- 1/128 of expectations

        # TODO: test each of:
        # Scene.bake_platforms = CollectionProperty(
        # Scene.bake_platform_index = IntProperty(default=0)
        # Scene.bake_cleanup_shapekeys = BoolProperty(
        # Scene.bake_steam_library = StringProperty(name='Steam Library', default="C:\\Program Files (x86)\\Steam\\")
        # Scene.bake_unwrap_angle = FloatProperty(
        # Scene.bake_optimize_solid_materials = BoolProperty(
        # Scene.bake_pass_metallic = BoolProperty(
        # Scene.bake_pass_alpha = BoolProperty(
        # Scene.bake_emit_exclude_eyes = BoolProperty(
        # Scene.bake_emit_indirect = BoolProperty(
        # Scene.bake_pass_emit = BoolProperty(
        # Scene.bake_pass_ao = BoolProperty(
        # Scene.bake_show_advanced_platform_options = BoolProperty(
        # Scene.bake_show_advanced_general_options = BoolProperty(
        # Scene.bake_ignore_hidden = BoolProperty(
        # Scene.bake_apply_keys = BoolProperty(
        # Scene.bake_normal_apply_trans = BoolProperty(
        # Scene.bake_pass_normal = BoolProperty(
        # Scene.bake_pass_diffuse = BoolProperty(
        # Scene.bake_pass_smoothness = BoolProperty(
        # Scene.bake_illuminate_eyes = BoolProperty(
        # Scene.bake_denoise = BoolProperty(
        # Scene.bake_sharpen = BoolProperty(
        # Scene.bake_face_scale = FloatProperty(
        # Scene.bake_prioritize_face = BoolProperty(
        #         ("REPROJECT", t("Scene.bake_uv_overlap_correction.reproject.label"), t("Scene.bake_uv_overlap_correction.reproject.desc")),
        #         ("UNMIRROR", t("Scene.bake_uv_overlap_correction.unmirror.label"), t("Scene.bake_uv_overlap_correction.unmirror.desc")),
        #         ("NONE", t("Scene.bake_uv_overlap_correction.none.label"), t("Scene.bake_uv_overlap_correction.none.desc")),
        # Scene.bake_uv_overlap_correction = EnumProperty(
        # Scene.bake_generate_uvmap = BoolProperty(

        self.assertTrue(result == {'FINISHED'})

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
