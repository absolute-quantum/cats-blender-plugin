# GPL License

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
