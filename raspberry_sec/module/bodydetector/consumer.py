import logging
import time
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class BodydetectorConsumer(Consumer):
	"""
	Consumer class for detecting human body in an image
	"""
	LOGGER = logging.getLogger('BodydetectorConsumer')
	TIMEOUT = 1

	def __init__(self):
		"""
		Constructor
		"""
		self.initialized = False
		self.hog = None

	def get_name(self):
		return 'BodydetectorConsumer'

	def initialize(self):
		"""
		Initializes component
		"""
		import cv2
		BodydetectorConsumer.LOGGER.info('Initializing component')
		self.hog = cv2.HOGDescriptor()
		self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

		self.initialized = True

	def run(self, context: ConsumerContext):
		if not self.initialized:
			self.initialize()

		img = context.data
		if img is not None:
			found, w = self.hog.detectMultiScale(img, winStride=(8, 8), padding=(32, 32), scale=1.05)
			if len(found) > 0:
				BodydetectorConsumer.LOGGER.info('Body detected')
				context.alert = True
		else:
			BodydetectorConsumer.LOGGER.warning('No image')
			time.sleep(BodydetectorConsumer.TIMEOUT)

		return context

	def get_type(self):
		return Type.CAMERA
