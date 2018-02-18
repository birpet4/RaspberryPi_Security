import unittest
from raspberry_sec.system.util import DynamicLoader


class TestDynamicLoaderMethods(unittest.TestCase):

    def test_list_modules(self):
        # Given
        package_name = 'raspberry_sec.system'

        # When
        modules = DynamicLoader.list_modules(package_name)

        # Then
        self.assertTrue(modules.__contains__('raspberry_sec.system.test_util'))
        self.assertTrue(modules.__contains__('raspberry_sec.system.util'))

    def test_load_class(self):
        # Given
        to_be_loaded = 'raspberry_sec.system.util.DynamicLoader'

        # When
        loaded_class = DynamicLoader.load_class(to_be_loaded)

        # Then
        self.assertTrue(loaded_class.__name__ == DynamicLoader.__name__)


if __name__ == '__main__':
    unittest.main()
