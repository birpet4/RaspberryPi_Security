import logging
import time
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class CameraConsumer(Consumer):
	"""
	Consumer class for showing camera images
	"""
	LOGGER = logging.getLogger('CameraConsumer')
	TIMEOUT = 1
	WAIT_KEY_TIMEOUT = 250

	def get_name(self):
		return 'CameraConsumer'

	def run(self, context: ConsumerContext):
		import cv2

		img = context.data
		if img is not None:
			cv2.imshow('Webcam', img)
			cv2.waitKey(CameraConsumer.WAIT_KEY_TIMEOUT)
		else:
			CameraConsumer.LOGGER.warning('No image')
			time.sleep(CameraConsumer.TIMEOUT)

		return context

	def get_type(self):
		return Type.CAMERA
