import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_viseme_button(self):
        # TODO: set correct parameters
        # bpy.context.scene.remove_constraints = True
        # bpy.context.scene.remove_zero_weight = True
        # Cannot select these values, this might be a limitation of blender scripting api :(
        # bpy.context.scene.mesh_name_eye = 'Head'
        # bpy.context.scene.head = 'Head'
        # bpy.context.scene.eye_left = 'EyeReturn_L'
        # bpy.context.scene.eye_left = 'EyeReturn_R'
        # bpy.ops.armature.fix()
        # bpy.ops.create.eyes()
        pass


def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
    runner = unittest.TextTestRunner()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)


try:
    run()
except Exception:
    sys.exit(1)
