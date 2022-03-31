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

# Lookup table of expected samples. Bear in mind that these are linear colorspace!
sampling_lookup = {
    'SCRIPT_diffuse.png': {
        (0,0): (128,128,128,255),
        (64,113): (255,0,0,255),
        (64,17): (0,0,255,255),
        (64,64): (0,255,0,255),
        (19,113): (231,0,231,255),
        (94,113): (231,231,231,255),
        (64,144): (0,0,0,255),
        (192,17): (188,188,188,255),
        (192,64): (188,188,188,255),
        (192,113): (188,188,188,255),
        (192,144): (188,188,188,255),
    },
    'SCRIPT_emission.png': {
        (0,0): (0,0,0,255),
        (64,128): (253,253,253,255),
        (64,166): (84,84,84,255),
    },
    'SCRIPT_metallic.png': {
        (0,0): (0,0,0,255),
        (64,87): (190,190,190,255)
    },
    'SCRIPT_smoothness.png': {
        (0,0): (0,0,0,255),
        (64,17): (127,127,127,255),
        (64,43): (250,250,250,255)
    },
}

class TestAddon(unittest.TestCase):

    def reset_stage(self):
        for colname in ['VRChat Desktop', 'VRChat Quest Excellent', 'VRChat Quest Good',
                        'Second Life']:
            bpy.data.collections.remove(bpy.data.collections["CATS Bake " + colname],
                                        do_unlink=True)

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

    def test_bake_button(self):
        bpy.ops.cats_bake.preset_all()

        bpy.context.scene.bake_resolution = 256
        # TODO: presently, all filter_image passes save to disk as an intermediate step, which
        # can introduce an error of +/- 1 value. We should save to a better intermediate format
        for filter_img in [False, True]: # TODO: this doesn't like python parameterized test cases yet
            bpy.context.scene.bake_denoise = filter_img
            bpy.context.scene.bake_sharpen = filter_img
            result = bpy.ops.cats_bake.bake(is_unittest=True)

            self.assertTrue("SCRIPT_diffuse.png" in bpy.data.images)
            self.assertTrue("SCRIPT_smoothness.png" in bpy.data.images)
            self.assertTrue("SCRIPT_world.png" in bpy.data.images)
            self.assertTrue("SCRIPT_metallic.png" in bpy.data.images)
            # take a random sampling of each image result, confirm it's what we expect
            for (bakename, cases) in sampling_lookup.items():
                for (coordinate, color) in cases.items():
                    pxoffset = (coordinate[0] + (coordinate[1] * 256 )) * 4
                    foundcolor = tuple(round(px*255) for px in bpy.data.images[bakename].pixels[pxoffset:pxoffset+4])
                    print(color)
                    print(foundcolor)
                    if not filter_img:
                        self.assertEqual(foundcolor, color)
                    else:
                        for i in range(4):
                            # Wide margins, since sharpening actually does change it (on purpose)
                            self.assertTrue(color[i] - 10 <= foundcolor[i] <= color[i] + 10)
            self.reset_stage()

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
