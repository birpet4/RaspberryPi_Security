import logging
import time
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class FacedetectorConsumer(Consumer):
	"""
	Consumer class for detecting human body in an image
	"""
	LOGGER = logging.getLogger('FacedetectorConsumer')
	TIMEOUT = 1
	SCALE_FACTOR = 1.3
	MIN_NEIGHBORS = 5
	CASCADE_FILE = 'resource/haarcascade_frontalface_default.xml'

	def __init__(self):
		"""
		Constructor
		"""
		self.initialized = False
		self.face_cascade = None

	def get_name(self):
		return 'FacedetectorConsumer'

	def initialize(self):
		"""
		Initializes component
		"""
		import cv2
		FacedetectorConsumer.LOGGER.info('Initializing component')
		self.face_cascade = cv2.CascadeClassifier(FacedetectorConsumer.CASCADE_FILE)
		self.initialized = True

	def run(self, context: ConsumerContext):
		import cv2
		if not self.initialized:
			self.initialize()

		img = context.data
		context.alert = False

		if img is not None:
			grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			faces = self.face_cascade.detectMultiScale(
				image=grey_img,
				scaleFactor=FacedetectorConsumer.SCALE_FACTOR,
				minNeighbors=FacedetectorConsumer.MIN_NEIGHBORS)

			# Take one of the faces and process that
			if len(faces) > 0:
				FacedetectorConsumer.LOGGER.info('Face detected')
				(x, y, w, h) = faces[0]
				context.alert = True
				context.data = img[y:(y + h), x:(x + w)]
		else:
			FacedetectorConsumer.LOGGER.warning('No image')
			time.sleep(FacedetectorConsumer.TIMEOUT)

		return context

	def get_type(self):
		return Type.CAMERA
