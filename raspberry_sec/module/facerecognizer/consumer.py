import logging
import json
import os
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class FacerecognizerConsumer(Consumer):
	"""
	Consumer class for recognizing human face
	"""
	LOGGER = logging.getLogger('FacerecognizerConsumer')
	TIMEOUT = 1
	RESOURCE = 'resources'
	EIGEN_MODEL = os.sep.join([RESOURCE, 'eigen.yml'])
	FISHER_MODEL = os.sep.join([RESOURCE, 'fisher.yml'])
	LBPH_MODEL = os.sep.join([RESOURCE, 'lbph.yml'])
	LABEL_MAP = os.sep.join([RESOURCE, 'labels.json'])
	SIZE = 150
	EIGEN_COMPONENTS = 10
	EIGEN_THRESHOLD = 4000.0
	FISHER_COMPONENTS = 5
	FISHER_THRESHOLD = 600.0
	LBPH_RADIUS = 3
	LBPH_NEIGHBORS = 9
	LBPH_WIDTH = 7
	LBPH_HEIGHT = 7
	LBPH_THRESHOLD = 80.0

	def __init__(self):
		"""
		Constructor
		"""
		self.initialized = False
		self.eigen_recognizer = None
		self.fisher_recognizer = None
		self.lbph_recognizer = None
		self.label_to_name = None

	def get_name(self):
		return 'FacerecognizerConsumer'

	def initialize(self):
		"""
		Initializes component
		"""
		import cv2
		FacerecognizerConsumer.LOGGER.info('Initializing component')

		self.eigen_recognizer = cv2.face.EigenFaceRecognizer_create(
			num_components=FacerecognizerConsumer.EIGEN_COMPONENTS,
			threshold=FacerecognizerConsumer.EIGEN_THRESHOLD)

		self.fisher_recognizer = cv2.face.FisherFaceRecognizer_create(
			num_components=FacerecognizerConsumer.FISHER_COMPONENTS,
			threshold=FacerecognizerConsumer.FISHER_THRESHOLD)

		self.lbph_recognizer = cv2.face.LBPHFaceRecognizer_create(
			radius=FacerecognizerConsumer.LBPH_RADIUS,
			neighbors=FacerecognizerConsumer.LBPH_NEIGHBORS,
			grid_x=FacerecognizerConsumer.LBPH_WIDTH,
			grid_y=FacerecognizerConsumer.LBPH_HEIGHT,
			threshold=FacerecognizerConsumer.LBPH_THRESHOLD)

		self.eigen_recognizer.load(FacerecognizerConsumer.EIGEN_MODEL)
		self.fisher_recognizer.load(FacerecognizerConsumer.FISHER_MODEL)
		self.lbph_recognizer.load(FacerecognizerConsumer.LBPH_MODEL)

		try:
			with open(FacerecognizerConsumer.LABEL_MAP) as label_file:
				self.label_to_name = json.load(label_file)
		except Exception:
			FacerecognizerConsumer.LOGGER.error('Cannot read the label file: ' + FacerecognizerConsumer.LABEL_MAP)
			self.label_to_name = dict()

		self.initialized = True

	def run(self, context: ConsumerContext):
		import cv2
		if not self.initialized:
			self.initialize()

		# the data is expected to be the detected face
		face = context.data
		context.alert = False

		if face is not None:
			face = cv2.resize(face, (FacerecognizerConsumer.SIZE, FacerecognizerConsumer.SIZE))
			name = self.recognize(face)
			if name is not None:
				context.alert = True
				context.data = 'Recognized face: ' + name
				FacerecognizerConsumer.LOGGER.info(context.data)

		return context

	def recognize(self, face):
		"""
		This method decides if the face is among those that are to be recognized.
		It uses 3 different recognition algorithms for this (Eigen, Fisher, LBPH).
		:param face: detected face
		:return: name if the face was successfully identified by at least 1 of the recognizers or None
		"""
		f_label, _ = self.fisher_recognizer.predict(face)
		e_label, _ = self.eigen_recognizer.predict(face)
		l_label, _ = self.lbph_recognizer.predict(face)

		if self.label_to_name.__contains__(f_label):
			return self.label_to_name[f_label]
		elif self.label_to_name.__contains__(e_label):
			return self.label_to_name[e_label]
		elif self.label_to_name.__contains__(l_label):
			return self.label_to_name[l_label]
		else:
			return None

	def get_type(self):
		return Type.CAMERA
