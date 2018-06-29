import time
import logging
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class TestConsumer(Consumer):
	"""
	Consumer class for testing purposes
	"""
	LOGGER = logging.getLogger('TestConsumer')

	def __init__(self, parameters: dict):
		"""
		Constructor
		:param parameters: see Consumer constructor
		"""
		super().__init__(parameters)

	def get_name(self):
		return 'TestConsumer'

	def run(self, context: ConsumerContext):
		TestConsumer.LOGGER.info('Working...')
		time.sleep(5)
		TestConsumer.LOGGER.info('Done...')
		if 10 <= int(context.data):
			return ConsumerContext(_alert_data='DATA reached 10', _alert=True)
		else:
			return ConsumerContext(_data='data', _alert=False)

	def get_type(self):
		return Type.CAMERA
