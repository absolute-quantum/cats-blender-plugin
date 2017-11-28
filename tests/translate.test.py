import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_translate_shapekeys(self):
        result = bpy.ops.translate.shapekeys()
        self.assertEqual(result == {'FINISHED'}, True)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
