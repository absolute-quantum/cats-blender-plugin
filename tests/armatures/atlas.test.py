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
    def test_atlas_button(self):
        # bpy.ops.cats_armature.fix()

        # bpy.context.scene.mesh_name_atlas = 'Body'
        # bpy.context.scene.texture_size = '1024'
        # bpy.context.scene.one_texture = True
        # bpy.context.scene.pack_islands = False
        # bpy.context.scene.angle_limit = 82.0
        # bpy.context.scene.area_weight = 0.0
        # bpy.context.scene.island_margin = 0.01

        # result = bpy.ops.cats_atlas.generate_atlas()
        # self.assertTrue(result == {'CANCELLED'})
        # self.assertTrue(result == {'FINISHED'})  # Does not work because it requires an external plugin which is not installed
        self.assertTrue(True)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
