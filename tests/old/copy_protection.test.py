# GPL License

import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_copy_protection(self):
        bpy.ops.cats_armature.fix()
        bpy.ops.cats_copyprotection.enable()
        bpy.ops.cats_copyprotection.disable()


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
