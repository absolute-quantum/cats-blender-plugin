import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_armature(self):
        bpy.context.scene.remove_zero_weight = True
        bpy.context.scene.remove_constraints = True
        result = bpy.ops.armature.fix()
        self.assertEqual(result == {'FINISHED'}, True)

    def test_armature_with_zero_weights_off(self):
        bpy.context.scene.remove_zero_weight = False
        bpy.context.scene.remove_constraints = True
        result = bpy.ops.armature.fix()
        self.assertEqual(result == {'FINISHED'}, True)

    def test_armature_with_constraints_off(self):
        bpy.context.scene.remove_zero_weight = True
        bpy.context.scene.remove_constraints = False
        result = bpy.ops.armature.fix()
        self.assertEqual(result == {'FINISHED'}, True)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
