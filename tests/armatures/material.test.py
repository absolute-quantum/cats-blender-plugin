# GPL License

import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_material_combine(self):
        bpy.ops.cats_armature.fix()
        bpy.ops.cats_material.combine_mats()


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
