import unittest
import sys


class TestAddon(unittest.TestCase):
    try:
        import cats
    except Exception as e:
        print(str(e))

    def test_addon_enabled(self):
        self.assertIsNotNone(self.cats.bl_info)

# we have to manually invoke the test runner here, as we cannot use the CLI
suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
