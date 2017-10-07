import time
import logging
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class TestConsumer(Consumer):
	"""
	Consumer class for testing purposes
	"""
	LOGGER = logging.getLogger('TestConsumer')

	def get_name(self):
		return 'TestConsumer'

	def run(self, context: ConsumerContext):
		TestConsumer.LOGGER.info('Working...')
		time.sleep(5)
		TestConsumer.LOGGER.info('Done...')
		if 10 <= int(context.data):
			return ConsumerContext('DATA reached 10', True)
		else:
			return ConsumerContext('data', False)

	def get_type(self):
		return Type.CAMERA
