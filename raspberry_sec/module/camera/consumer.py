import time
import logging
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class CameraConsumer(Consumer):
	"""
	Consumer class for showing camera images
	"""
	LOGGER = logging.getLogger('CameraConsumer')
	WAIT_KEY_TIMEOUT = 100

	def get_name(self):
		return 'CameraConsumer'

	def run(self, context: ConsumerContext):
		import cv2

		img = context.data
		if img is not None:
			cv2.imshow('Webcam', img)
		else:
			CameraConsumer.LOGGER.warning('No image')
		cv2.waitKey(CameraConsumer.WAIT_KEY_TIMEOUT)

		return context

	def get_type(self):
		return Type.CAMERA
