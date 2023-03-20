# GPL License

import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_armature(self):
        bpy.context.scene.remove_zero_weight = True
        result = bpy.ops.cats_armature.fix()
        self.assertTrue(result == {'FINISHED'})

    def test_armature_with_zero_weights_off(self):
        bpy.context.scene.remove_zero_weight = False
        result = bpy.ops.cats_armature.fix()
        self.assertTrue(result == {'FINISHED'})


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
