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
    'bake.eyetest.blend': {
        'SCRIPT_diffuse.png': {
            # For some reason Blender 2.93 ends up with values off-by-one (but not alpha)
            #(64,64): (0,255,255,255),
            # (178,55): (255,0,255,255),
            # (32,222): (0,0,255,255),
            #(178,200): (5,255,0,255)
        }
    },
    'bake.bakematerialtest.blend': {
        'SCRIPT_diffuse.png': {
            (0,0): (128,128,128,255),
            (215,40): (255,0,0,255),
            (215,7): (0,0,255,255),
            (215,24): (0,255,0,255),
            (200,40): (231,0,231,255),
            (232,40): (231,231,231,255),
            (215,56): (0,0,0,255),
            (96,32): (188,188,188,255),
            (96,96): (188,188,188,255),
            (96,160): (188,188,188,255),
            (96,220): (188,188,188,255),
        },
        'SCRIPT_emission.png': {
            (0,0): (0,0,0,255),
            (215,48): (252,252,252,255),
            (215,63): (55,55,55,255),
        },
        'SCRIPT_metallic.png': {
            (0,0): (0,0,0,255),
            (215,32): (215,215,215,255)
        },
        'SCRIPT_smoothness.png': {
            (0,0): (0,0,0,255),
            (215,24): (122,122,122,255),
            (215,17): (234,234,234,255)
        },
        'SCRIPT_alpha.png': {
            (0,0): (255,255,255,255),
            (216,0): (36,36,36,255)
        },
        'VRChat Desktop metallic.png': {
            (215,17): (0,0,0,234),
            (96,220): (0,0,0,127),
            (216,0): (0,0,0,127),
            (215,32): (215,0,0,127),
            (96,32): (0,0,0,127),
            (96,96): (0,0,0,127),
            (96,160): (0,0,0,127),
            (215,24): (0,0,0,122),
            (232,40): (0,0,0,127),
            (200,40): (0,0,0,127),
            (215,56): (0,0,0,127),
            (215,7): (0,0,0,127),
            (0,0): (0,0,0,0),
            (215,48): (0,0,0,127),
            (215,63): (0,0,0,127),
            (215,40): (64,0,0,127),
        },
        'VRChat Desktop diffuse.png': {
            (215,17): (0,255,0,255),
            (96,220): (188,188,188,255),
            (216,0): (0,0,255,36),
            (215,32): (255,0,0,255),
            (96,32): (188,188,188,255),
            (96,96): (188,188,188,255),
            (96,160): (188,188,188,255),
            (215,24): (0,255,0,255),
            (232,40): (231,231,231,255),
            (200,40): (231,0,231,255),
            (215,56): (0,0,0,255),
            (215,7): (0,0,255,180),
            (0,0): (128,128,128,255),
            (215,48): (0,0,0,255),
            (215,63): (0,0,0,255),
            (215,40): (255,0,0,255),
        },
        'VRChat Desktop normal.png': {
            (215,17): (128,128,255,255),
            (96,220): (127,127,255,255),
            (98,32): (127,127,255,255),
            (96,96): (128,127,255,255),
            (96,160): (127,127,255,255),
            (215,24): (128,128,255,255),
            (232,40): (127,127,255,255),
            (200,40): (191,64,218,255),
            (215,56): (128,127,255,255),
            (215,7): (128,128,255,255),
            (0,0): (128,128,255,255),
            (215,48): (128,127,255,255),
            (215,63): (128,127,255,255),
            (215,40): (128,127,255,255),
        },
        'VRChat Quest Excellent metallic.png': {
            (215,17): (0,0,0,234),
            (96,220): (0,0,0,127),
            (216,0): (0,0,0,127),
            (215,32): (215,0,0,127),
            (96,32): (0,0,0,127),
            (96,96): (0,0,0,127),
            (96,160): (0,0,0,127),
            (215,24): (0,0,0,122),
            (232,40): (0,0,0,127),
            (200,40): (0,0,0,127),
            (215,56): (0,0,0,127),
            (215,7): (0,0,0,127),
            (0,0): (0,0,0,0),
            (215,48): (0,0,0,127),
            (215,63): (0,0,0,127),
            (215,40): (64,0,0,127),
        },
        'VRChat Quest Excellent alpha.png': {
            (215,17): (255,255,255,255),
            (96,220): (255,255,255,255),
            (216,0): (36,36,36,255),
            (215,32): (255,255,255,255),
            (96,32): (255,255,255,255),
            (96,96): (255,255,255,255),
            (96,160): (255,255,255,255),
            (215,24): (255,255,255,255),
            (232,40): (255,255,255,255),
            (200,40): (255,255,255,255),
            (215,56): (255,255,255,255),
            (215,7): (180,180,180,255),
            (0,0): (255,255,255,255),
            (215,48): (255,255,255,255),
            (215,63): (255,255,255,255),
            (215,40): (255,255,255,255),
        },
        'VRChat Quest Excellent smoothness.png': {
            (215,17): (234,234,234,255),
            (96,220): (127,127,127,255),
            (216,0): (127,127,127,255),
            (215,32): (127,127,127,255),
            (96,32): (127,127,127,255),
            (96,96): (127,127,127,255),
            (96,160): (127,127,127,255),
            (215,24): (122,122,122,255),
            (232,40): (127,127,127,255),
            (200,40): (127,127,127,255),
            (215,56): (127,127,127,255),
            (215,7): (127,127,127,255),
            (0,0): (0,0,0,255),
            (215,48): (127,127,127,255),
            (215,63): (127,127,127,255),
            (215,40): (127,127,127,255),
        },
        'VRChat Quest Excellent diffuse.png': {
            (215,17): (0,255,0,255),
            (96,220): (188,188,188,255),
            (216,0): (0,0,255,255),
            (215,32): (255,0,0,255),
            (96,32): (188,188,188,255),
            (96,96): (188,188,188,255),
            (96,160): (188,188,188,255),
            (215,24): (0,255,0,255),
            (232,40): (231,231,231,255),
            (200,40): (231,0,231,255),
            (215,56): (0,0,0,255),
            (215,7): (0,0,255,255),
            (0,0): (128,128,128,255),
            (215,48): (0,0,0,255),
            (215,63): (0,0,0,255),
            (215,40): (255,0,0,255),
        },
        'VRChat Quest Excellent normal.png': {
            (215,17): (128,128,255,255),
            (96,220): (127,127,255,255),
            (96,32): (128,128,255,255),
            (96,96): (128,127,255,255),
            (96,160): (127,127,255,255),
            (215,24): (128,128,255,255),
            (232,40): (127,127,255,255),
            (200,40): (191,64,218,255),
            (215,56): (128,127,255,255),
            (215,7): (128,128,255,255),
            (0,0): (128,128,255,255),
            (215,48): (128,127,255,255),
            (215,63): (128,127,255,255),
            (215,40): (128,127,255,255),
        },
        'VRChat Quest Good metallic.png': {
            (215,17): (0,0,0,234),
            (96,220): (0,0,0,127),
            (216,0): (0,0,0,127),
            (215,32): (215,0,0,127),
            (96,32): (0,0,0,127),
            (96,96): (0,0,0,127),
            (96,160): (0,0,0,127),
            (215,24): (0,0,0,122),
            (232,40): (0,0,0,127),
            (200,40): (0,0,0,127),
            (215,56): (0,0,0,127),
            (215,7): (0,0,0,127),
            (0,0): (0,0,0,0),
            (215,48): (0,0,0,127),
            (215,63): (0,0,0,127),
            (215,40): (64,0,0,127),
        },
        'VRChat Quest Good alpha.png': {
            (215,17): (255,255,255,255),
            (96,220): (255,255,255,255),
            (216,0): (36,36,36,255),
            (215,32): (255,255,255,255),
            (96,32): (255,255,255,255),
            (96,96): (255,255,255,255),
            (96,160): (255,255,255,255),
            (215,24): (255,255,255,255),
            (232,40): (255,255,255,255),
            (200,40): (255,255,255,255),
            (215,56): (255,255,255,255),
            (215,7): (180,180,180,255),
            (0,0): (255,255,255,255),
            (215,48): (255,255,255,255),
            (215,63): (255,255,255,255),
            (215,40): (255,255,255,255),
        },
        'VRChat Quest Good smoothness.png': {
            (215,17): (234,234,234,255),
            (96,220): (127,127,127,255),
            (216,0): (127,127,127,255),
            (215,32): (127,127,127,255),
            (96,32): (127,127,127,255),
            (96,96): (127,127,127,255),
            (96,160): (127,127,127,255),
            (215,24): (122,122,122,255),
            (232,40): (127,127,127,255),
            (200,40): (127,127,127,255),
            (215,56): (127,127,127,255),
            (215,7): (127,127,127,255),
            (0,0): (0,0,0,255),
            (215,48): (127,127,127,255),
            (215,63): (127,127,127,255),
            (215,40): (127,127,127,255),
        },
        'VRChat Quest Good diffuse.png': {
            (215,17): (0,255,0,255),
            (96,220): (188,188,188,255),
            (216,0): (0,0,255,255),
            (215,32): (255,0,0,255),
            (96,32): (188,188,188,255),
            (96,96): (188,188,188,255),
            (96,160): (188,188,188,255),
            (215,24): (0,255,0,255),
            (232,40): (231,231,231,255),
            (200,40): (231,0,231,255),
            (215,56): (0,0,0,255),
            (215,7): (0,0,255,255),
            (0,0): (128,128,128,255),
            (215,48): (0,0,0,255),
            (215,63): (0,0,0,255),
            (215,40): (255,0,0,255),
        },
        'VRChat Quest Good normal.png': {
            (215,17): (128,128,255,255),
            (96,220): (127,127,255,255),
            (96,32): (128,128,255,255),
            (96,96): (128,127,255,255),
            (96,160): (127,127,255,255),
            (215,24): (128,128,255,255),
            (232,40): (127,127,255,255),
            (200,40): (191,64,218,255),
            (215,56): (128,127,255,255),
            (215,7): (128,128,255,255),
            (0,0): (128,128,255,255),
            (215,48): (128,127,255,255),
            (215,63): (128,127,255,255),
            (215,40): (128,127,255,255),
        },
        'Second Life metallic.png': {
            (215,17): (0,0,0,255),
            (96,220): (0,0,0,255),
            (216,0): (0,0,0,255),
            (215,32): (215,0,0,255),
            (96,32): (0,0,0,255),
            (96,96): (0,0,0,255),
            (96,160): (0,0,0,255),
            (215,24): (0,0,0,255),
            (232,40): (0,0,0,255),
            (200,40): (0,0,0,255),
            (215,56): (0,0,0,255),
            (215,7): (0,0,0,255),
            (0,0): (0,0,0,255),
            (215,48): (0,0,0,255),
            (215,63): (0,0,0,255),
            (215,40): (64,0,0,255),
        },
        'Second Life alpha.png': {
            (215,17): (255,255,255,255),
            (96,220): (255,255,255,255),
            (216,0): (36,36,36,255),
            (215,32): (255,255,255,255),
            (96,32): (255,255,255,255),
            (96,96): (255,255,255,255),
            (96,160): (255,255,255,255),
            (215,24): (255,255,255,255),
            (232,40): (255,255,255,255),
            (200,40): (255,255,255,255),
            (215,56): (255,255,255,255),
            (215,7): (180,180,180,255),
            (0,0): (255,255,255,255),
            (215,48): (255,255,255,255),
            (215,63): (255,255,255,255),
            (215,40): (255,255,255,255),
        },
        'Second Life smoothness.png': {
            (215,17): (234,234,234,255),
            (96,220): (127,127,127,255),
            (216,0): (127,127,127,255),
            (215,32): (127,127,127,255),
            (96,32): (127,127,127,255),
            (96,96): (127,127,127,255),
            (96,160): (127,127,127,255),
            (215,24): (122,122,122,255),
            (232,40): (127,127,127,255),
            (200,40): (127,127,127,255),
            (215,56): (127,127,127,255),
            (215,7): (127,127,127,255),
            (0,0): (0,0,0,255),
            (215,48): (127,127,127,255),
            (215,63): (127,127,127,255),
            (215,40): (127,127,127,255),
        },
        'Second Life diffuse.png': {
            (215,17): (0,255,0,0),
            (96,220): (188,188,188,0),
            (216,0): (0,0,255,0),
            (215,32): (40,0,0,0),
            (96,32): (188,188,188,0),
            (96,96): (188,188,188,0),
            (96,160): (188,188,188,0),
            (215,24): (0,255,0,0),
            (232,40): (231,231,231,0),
            (200,40): (231,0,231,0),
            (215,7): (0,0,255,0),
            (0,0): (128,128,128,0),
            (215,48): (252,252,252,252),
            (215,63): (55,55,55,55),
            (215,40): (191,0,0,0),
        },
        'Second Life normal.png': {
            (215,17): (128,128,255,255),
            (96,220): (127,127,255,255),
            (96,32): (128,128,255,255),
            (96,96): (128,127,255,255),
            (96,160): (127,127,255,255),
            (215,24): (128,128,255,255),
            (232,40): (127,127,255,255),
            (200,40): (191,64,218,255),
            (215,56): (128,127,255,255),
            (215,7): (128,128,255,255),
            (0,0): (128,128,255,255),
            (215,48): (128,127,255,255),
            (215,63): (128,127,255,255),
            (215,40): (128,127,255,255),
        },
    }
}

class TestAddon(unittest.TestCase):

    def reset_stage(self):
        for colname in ['VRChat Desktop', 'VRChat Quest Excellent', 'VRChat Quest Good',
                        'Second Life']:
            bpy.data.collections.remove(bpy.data.collections["CATS Bake " + colname],
                                        do_unlink=True)

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

    def test_bake_button(self):
        bpy.context.scene.cats_is_unittest = True
        bpy.ops.cats_bake.preset_all()
        bpy.context.scene.bake_pass_displacement = False

        bpy.context.scene.bake_resolution = 256
        if 'bake.eyetest.blend' == bpy.path.basename(bpy.context.blend_data.filepath):
            bpy.context.scene.bake_uv_overlap_correction = 'NONE'
        # TODO: presently, all filter_image passes save to disk as an intermediate step, which
        # can introduce an error of +/- 1 value. We should save to a better intermediate format
        for filter_img in [False, True]:
            bpy.context.scene.bake_denoise = filter_img
            bpy.context.scene.bake_sharpen = filter_img
            result = bpy.ops.cats_bake.bake()

            # take a random sampling of each image result, confirm it's what we expect
            self.assertTrue(bpy.path.basename(bpy.context.blend_data.filepath) in sampling_lookup)
            for (bakename, cases) in sampling_lookup[bpy.path.basename(bpy.context.blend_data.filepath)].items():
                self.assertTrue(bakename in bpy.data.images, bakename)
                for (coordinate, color) in cases.items():
                    pxoffset = (coordinate[0] + (coordinate[1] * 256 )) * 4
                    foundcolor = tuple(round(px*255) for px in bpy.data.images[bakename].pixels[pxoffset:pxoffset+4])
                    foundraw = tuple(px for px in bpy.data.images[bakename].pixels[pxoffset:pxoffset+4])
                    if not filter_img:
                        for i in range(4):
                            self.assertTrue(color[i] - 2 <= foundcolor[i] <= color[i] + 2,
                                         "{}@({}, {}): {} != {} ({})".format(bakename,
                                                                             coordinate[0],
                                                                             coordinate[1],
                                                                             color, foundcolor,
                                                                             foundraw))
                    else:
                        for i in range(4):
                            # Wide margins, since sharpening actually does change it (on purpose)
                            self.assertTrue(color[i] - 40 <= foundcolor[i] <= color[i] + 40,
                                            "{} != {} ({})".format(color, foundcolor, foundraw))
            self.reset_stage()
        # TODO: test each of:
        # Scene.bake_cleanup_shapekeys = BoolProperty(
        # Scene.bake_unwrap_angle = FloatProperty(
        # Scene.bake_optimize_solid_materials = BoolProperty(
        # Scene.bake_ignore_hidden = BoolProperty(
        # Scene.bake_apply_keys = BoolProperty(
        # Scene.bake_normal_apply_trans = BoolProperty(
        # Scene.bake_uv_overlap_correction = EnumProperty(
        # Scene.bake_generate_uvmap = BoolProperty(

        # TODO: custom normal tests
        self.assertTrue(result == {'FINISHED'})

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
