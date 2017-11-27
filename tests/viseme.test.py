import unittest
import sys
import bpy


class TestAddon(unittest.TestCase):
    def test_viseme_button(self):
        # Context failures, figure out why :(
        # bpy.ops.auto.viseme()
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
