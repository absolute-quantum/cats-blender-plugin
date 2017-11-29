import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_viseme_button(self):
        # first fix armature
        bpy.ops.armature.fix()

        # Then translate shapekeys
        bpy.ops.translate.shapekeys()

        bpy.context.scene.mesh_name_viseme = 'Body'

        result = bpy.ops.auto.viseme()
        self.assertEqual(result == {'FINISHED'}, True)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
