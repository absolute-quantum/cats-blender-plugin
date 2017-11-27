import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_translate_bones(self):
        bpy.ops.translate.bones()

    def test_translate_textures(self):
        bpy.ops.translate.textures()

    def test_translate_materials(self):
        bpy.ops.translate.materials()

    def test_translate_shapekeys(self):
        bpy.ops.translate.shapekeys()

    def test_translate_meshes(self):
        bpy.ops.translate.meshes()


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
    runner = unittest.TextTestRunner()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)


try:
    run()
except Exception:
    sys.exit(1)
