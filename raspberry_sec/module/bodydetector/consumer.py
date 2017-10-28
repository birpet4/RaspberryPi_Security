import logging
import time
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class BodydetectorConsumer(Consumer):
	"""
	Consumer class for detecting human body in an image
	"""
	LOGGER = logging.getLogger('BodydetectorConsumer')

	def __init__(self, parameters: dict):
		"""
		Constructor
		:param parameters: see Consumer constructor
		"""
		super().__init__(parameters)
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
			resized_img = cv2.resize(img, (self.parameters['resize_width'], self.parameters['resize_height']))
			grey_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
			found, w = self.hog.detectMultiScale(
				grey_img,
				winStride=(self.parameters['win_stride_x'], self.parameters['win_stride_y']),
				padding=(self.parameters['padding_x'], self.parameters['padding_y']),
				scale=self.parameters['scale'])

			if len(found) > 0:
				BodydetectorConsumer.LOGGER.info('Body detected')
				context.alert = True
		else:
			BodydetectorConsumer.LOGGER.warning('No image')
			time.sleep(self.parameters['timeout'])

		return context

	def get_type(self):
		return Type.CAMERA
