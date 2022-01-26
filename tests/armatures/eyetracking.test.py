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
    filename = bpy.path.basename(bpy.context.blend_data.filepath)

    def test_eye_tracking(self):
        return
        bpy.ops.cats_armature.fix()
        if self.filename == 'armature.mmd1.blend':
            bpy.context.scene.eye_left = 'Eye_L'
            bpy.context.scene.eye_right = 'Eye_R'

        if self.filename == 'armature.bonetranslationerror.blend':
            bpy.context.scene.eye_left = 'Eye_L'
            bpy.context.scene.eye_right = 'Eye_R'

        bpy.context.scene.disable_eye_movement = False
        bpy.context.scene.disable_eye_blinking = False

        result = bpy.ops.cats_eyes.create.create_eye_tracking()
        self.assertTrue(result == {'FINISHED'})

    def test_eye_tracking_no_movement(self):
        return
        if self.filename == 'armature.bonetranslationerror.blend':
            bpy.context.scene.eye_left = 'Eye_L'
            bpy.context.scene.eye_right = 'Eye_R'

        bpy.context.scene.disable_eye_movement = True
        bpy.context.scene.disable_eye_blinking = False

        result = bpy.ops.cats_eyes.create.create_eye_tracking()
        self.assertTrue(result == {'FINISHED'})

    def test_eye_tracking_no_blinking(self):
        return
        if self.filename == 'armature.bonetranslationerror.blend':
            bpy.context.scene.eye_left = 'Eye_L'
            bpy.context.scene.eye_right = 'Eye_R'

        bpy.context.scene.disable_eye_movement = False
        bpy.context.scene.disable_eye_blinking = True

        result = bpy.ops.cats_eyes.create.create_eye_tracking()
        self.assertTrue(result == {'FINISHED'})


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
