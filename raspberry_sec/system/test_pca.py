import unittest
from raspberry_sec.system.pca import PCASystem, PCALoader
from raspberry_sec.system.stream import Stream, StreamController


class TestPCALoaderMethods(unittest.TestCase):

    def test_filter_for_allowed_modules(self):
        # Give
        package = PCALoader.module_package
        modules = [
            package + '.test1.consumer',
            package + '.test1.producer',
            package + '.test1.test',
            package + '.test2.consumer',
            package + '.test3.producer',
            package + '.test4.action',
            package + '.test5.util'
        ]

        # When
        filtered_list = PCALoader.filter_for_allowed_modules(modules)

        # Then
        self.assertEqual(5, len(filtered_list))

    def test_generate_class_names(self):
        # Given
        package = PCALoader.module_package
        modules = [
            package + '.test1.consumer',
            package + '.test1.producer',
            package + '.test2.consumer',
            package + '.test3.producer',
            package + '.test4.action'
        ]

        # When
        modules = PCALoader.generate_class_names(modules)

        # Then
        self.assertEqual(5, len(modules))
        self.assertTrue(modules.__contains__(package + '.test1.consumer.Test1Consumer'))
        self.assertTrue(modules.__contains__(package + '.test1.producer.Test1Producer'))
        self.assertTrue(modules.__contains__(package + '.test3.producer.Test3Producer'))
        self.assertTrue(modules.__contains__(package + '.test4.action.Test4Action'))


class TestPCASystemMethods(unittest.TestCase):

    def test_validate_throws_exception(self):
        # Given
        pca = PCASystem()

        # Then
        self.assertRaises(AttributeError, pca.validate)

    def test_validate_returns_false(self):
        # Given
        pca = PCASystem()
        pca.stream_controller = StreamController()

        # When
        result = pca.validate()

        # Then
        self.assertFalse(result)

    def test_validate_returns_true(self):
        # Given
        pca = PCASystem()
        pca.stream_controller = StreamController()
        pca.streams = [Stream('STREAM1')]

        # When
        result = pca.validate()

        # Then
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
