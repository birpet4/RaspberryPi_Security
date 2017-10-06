import time
import logging
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class CameraConsumer(Consumer):
	"""
	Consumer class for saving camera images
	"""
	LOGGER = logging.getLogger('CameraConsumer')

	def get_name(self):
		return 'CameraConsumer'

	def run(self, context: ConsumerContext):
		CameraConsumer.LOGGER.info('Sleeping now')
		time.sleep(5)
		return ConsumerContext('data', False)

	def get_type(self):
		return Type.CAMERA
