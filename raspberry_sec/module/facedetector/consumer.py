import logging
import time
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class FacedetectorConsumer(Consumer):
	"""
	Consumer class for detecting human body in an image
	"""
	LOGGER = logging.getLogger('FacedetectorConsumer')

	def __init__(self, parameters: dict):
		"""
		Constructor
		:param parameters: see Consumer constructor
		"""
		super().__init__(parameters)
		self.initialized = False
		self.face_cascade = None

	def get_name(self):
		return 'FacedetectorConsumer'

	@staticmethod
	def get_full_path(file: str):
		"""
		:param file: e.g. Cascade.xml
		:return: the absolute path for the file
		"""
		import os
		return os.sep.join([os.path.dirname(__file__), file])

	def initialize(self):
		"""
		Initializes component
		"""
		import cv2
		FacedetectorConsumer.LOGGER.info('Initializing component')
		self.face_cascade = cv2.CascadeClassifier(FacedetectorConsumer.get_full_path(self.parameters['cascade_file']))
		self.initialized = True

	def run(self, context: ConsumerContext):
		import cv2
		if not self.initialized:
			self.initialize()

		img = context.data
		context.alert = False

		if img is not None:
			img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			faces = self.face_cascade.detectMultiScale(
				image=img,
				scaleFactor=self.parameters['scale_factor'],
				minNeighbors=self.parameters['min_neighbors'])

			# Take one of the faces and process that
			if len(faces) > 0:
				(x, y, w, h) = faces[0]
				context.alert = True
				context.alert_data = 'Face detected'
				context.data = img[y:(y + h), x:(x + w)]
				FacedetectorConsumer.LOGGER.info(context.alert_data)
			else:
				FacedetectorConsumer.LOGGER.debug('Could not detect any faces')
		else:
			FacedetectorConsumer.LOGGER.warning('No image')
			time.sleep(self.parameters['timeout'])

		return context

	def get_type(self):
		return Type.CAMERA
