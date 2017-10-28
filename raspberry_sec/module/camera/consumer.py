import logging
import time
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class CameraConsumer(Consumer):
	"""
	Consumer class for showing camera images
	"""
	LOGGER = logging.getLogger('CameraConsumer')

	def __init__(self, parameters: dict):
		"""
		Constructor
		:param parameters: see Consumer constructor
		"""
		super().__init__(parameters)

	def get_name(self):
		return 'CameraConsumer'

	def run(self, context: ConsumerContext):
		import cv2

		img = context.data
		if img is not None:
			cv2.imshow('Webcam', img)
			cv2.waitKey(self.parameters['wait_key_timeout'])
		else:
			CameraConsumer.LOGGER.warning('No image')
			time.sleep(self.parameters['timeout'])

		return context

	def get_type(self):
		return Type.CAMERA
