import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_atlas_button(self):
        bpy.ops.armature.fix()

        bpy.context.scene.mesh_name_atlas = 'Body'
        bpy.context.scene.texture_size = '1024'
        bpy.context.scene.one_texture = True
        bpy.context.scene.pack_islands = False
        bpy.context.scene.angle_limit = 82.0
        bpy.context.scene.area_weight = 0.0
        bpy.context.scene.island_margin = 0.01

        result = bpy.ops.auto.atlas()
        self.assertEqual(result == {'FINISHED'}, True)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
