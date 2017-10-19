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
	WIN_STRIDE = (4, 4)
	PADDING = (16, 16)
	SCALE = 1.23
	RESIZE = (320, 240)

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
		import cv2
		if not self.initialized:
			self.initialize()

		img = context.data
		context.alert = False

		if img is not None:
			resized_img = cv2.resize(img, BodydetectorConsumer.RESIZE)
			grey_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
			found, w = self.hog.detectMultiScale(
				grey_img,
				winStride=BodydetectorConsumer.WIN_STRIDE,
				padding=BodydetectorConsumer.PADDING,
				scale=BodydetectorConsumer.SCALE)

			if len(found) > 0:
				BodydetectorConsumer.LOGGER.info('Body detected')
				context.alert = True
		else:
			BodydetectorConsumer.LOGGER.warning('No image')
			time.sleep(BodydetectorConsumer.TIMEOUT)

		return context

	def get_type(self):
		return Type.CAMERA
