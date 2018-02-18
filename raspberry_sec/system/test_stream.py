import unittest
from raspberry_sec.system.stream import Stream, StreamController, StreamControllerMessage
from raspberry_sec.interface.producer import Producer, Type
from raspberry_sec.interface.consumer import Consumer


class TestStreamMethods(unittest.TestCase):

    def test_eq(self):
        # Given
        stream1 = Stream('STREAM1')
        stream2 = Stream('STREAM1')

        # When
        equal = stream1.__eq__(stream2)

        # Then
        self.assertTrue(equal)

    def test_hash(self):
        # Given
        stream1 = Stream('STREAM1')
        stream2 = Stream('STREAM1')

        # When
        hash1 = stream1.__eq__(stream1)
        hash2 = stream1.__eq__(stream2)

        # Then
        self.assertEqual(hash1, hash2)

    def test_validate_throws_exception_when_no_producer(self):
        # Given
        stream = Stream('STREAM')

        # Then
        self.assertRaises(AttributeError, stream.validate)

    def test_validate_throws_exception_when_wrong_consumer(self):
        # Given
        stream = Stream('STREAM')
        stream.producer = Producer()
        consumer = Consumer()
        stream.consumers = [consumer]

        # When
        consumer.get_type = lambda: 'SOUND'

        # Then
        self.assertRaises(AttributeError, stream.validate)

    def test_validate_returns_true(self):
        # Given
        stream = Stream('STREAM')
        stream.producer = Producer()
        stream.producer.get_type = lambda: Type.CAMERA
        consumer = Consumer()
        consumer.get_type = lambda: Type.CAMERA
        stream.consumers = [consumer]

        # When
        result = stream.validate()

        # Then
        self.assertTrue(result)


class TestStreamControllerMethods(unittest.TestCase):

    def test_evaluate_query_returns_correct_result(self):
        # Given
        expression1 = 'False or (False or True)'
        expression2 = 'False and (False or False)'

        # When
        result1 = StreamController.evaluate_query(expression1)
        result2 = StreamController.evaluate_query(expression2)

        # Then
        self.assertTrue(result1)
        self.assertFalse(result2)

    def test_evaluate_query_return_false_when_exception(self):
        # Given
        expression = 'hmmmm'

        # When
        result = StreamController.evaluate_query(expression)

        # Then
        self.assertFalse(result)

    def test_decide_alert_returns_true_and_two_action_messages(self):
        # Given
        controller = StreamController()
        controller.query = '@STREAM1@ and @STREAM2@'
        messages = [
            StreamControllerMessage(_alert=True, _msg='MSG', _sender='STREAM1'),
            StreamControllerMessage(_alert=True, _msg='MSG', _sender='STREAM2')
        ]

        # When
        result, action_msgs = controller.decide_alert(messages)

        # Then
        self.assertTrue(result)
        self.assertEqual(2, len(action_msgs))

    def test_decide_alert_returns_false_and_no_action_messages(self):
        # Given
        controller = StreamController()
        controller.query = '@STREAM1@ and @STREAM2@'
        messages = [
            StreamControllerMessage(_alert=False, _msg='MSG', _sender='STREAM1'),
            StreamControllerMessage(_alert=False, _msg='MSG', _sender='STREAM2')
        ]

        # When
        result, action_msgs = controller.decide_alert(messages)

        # Then
        self.assertFalse(result)
        self.assertEqual(0, len(action_msgs))


if __name__ == '__main__':
    unittest.main()
