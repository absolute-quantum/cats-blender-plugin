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
