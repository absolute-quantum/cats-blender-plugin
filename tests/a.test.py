import unittest

# import the already loaded addon
try:
    import cats
except Exception, e:
    print(str(e))
    exit(1)


class TestAddon(unittest.TestCase):
    def test_addon_enabled(self):
        self.assertIsNotNone(cats.bl_info)

    def test_syntax_error(self):
        self.assertRaises(SyntaxError, cats, "error_library")

# we have to manually invoke the test runner here, as we cannot use the CLI
suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestAddon)
unittest.TextTestRunner().run(suite)
