# GPL License

import unittest
import sys


class TestAddon(unittest.TestCase):
    def test_syntax_check(self):
        try:
            import cats
        except SyntaxError as e:
            return self.fail('SyntaxError in plugin found!')

    def test_bl_info(self):
        import cats
        self.assertIsNotNone(cats.bl_info)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
runner = unittest.TextTestRunner()
ret = not runner.run(suite).wasSuccessful()
sys.exit(ret)
