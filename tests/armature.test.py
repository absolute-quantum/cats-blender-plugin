import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_armature_button(self):
        bpy.context.scene.remove_constraints = True
        bpy.context.scene.remove_zero_weight = True
        bpy.ops.armature.fix()


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
    runner = unittest.TextTestRunner()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)


try:
    run()
except Exception:
    sys.exit(1)
