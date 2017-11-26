import unittest
import sys


class TestAddon(unittest.TestCase):
    try:
        import cats
    except Exception as e:
        print(str(e))

    def test_addon_enabled(self):
        self.assertIsNotNone(self.cats.bl_info)

def run():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
    runner = unittest.TextTestRunner()
    ret = not runner.run(suite).wasSuccessful()
    if not ret:
        raise Exception('Tests Failed')


try:
    run()
except Exception:
    sys.exit(1)
