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
# Edits by:

import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    filename = bpy.path.basename(bpy.context.blend_data.filepath)

    def test_experimental_eye_fix(self):
        # first fix armature
        bpy.ops.armature.fix()

        # Try with experimental eye fix
        if self.filename == 'armature.mmd1.blend':
            bpy.context.scene.eye_left = 'EyeReturn_L'
            bpy.context.scene.eye_right = 'EyeReturn_R'
            bpy.context.scene.experimental_eye_fix = True

        result = bpy.ops.create.eyes()
        self.assertEqual(result == {'FINISHED'}, True)

    def test_eye_tracking(self):
        # Try without experimental eye fix
        if self.filename == 'armature.mmd1.blend':
            bpy.context.scene.eye_left = 'EyeReturn_L'
            bpy.context.scene.eye_right = 'EyeReturn_R'
            bpy.context.scene.experimental_eye_fix = False

        result = bpy.ops.create.eyes()
        self.assertEqual(result == {'FINISHED'}, True)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
