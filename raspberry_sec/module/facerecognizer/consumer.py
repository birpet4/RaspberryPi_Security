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

	def __init__(self, parameters: dict):
		"""
		Constructor
		:param parameters: see Consumer constructor
		"""
		super().__init__(parameters)
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
			num_components=self.parameters['eigen_components'],
			threshold=self.parameters['eigen_threshold'])

		self.fisher_recognizer = cv2.face.FisherFaceRecognizer_create(
			num_components=self.parameters['fisher_components'],
			threshold=self.parameters['fisher_threshold'])

		self.lbph_recognizer = cv2.face.LBPHFaceRecognizer_create(
			radius=self.parameters['lbph_radius'],
			neighbors=self.parameters['lbph_neighbors'],
			grid_x=self.parameters['lbph_width'],
			grid_y=self.parameters['lbph_height'],
			threshold=self.parameters['lbph_threshold'])

		self.eigen_recognizer.read(self.parameters['eigen_model'])
		self.fisher_recognizer.read(self.parameters['fisher_model'])
		self.lbph_recognizer.read(self.parameters['lbph_model'])

		try:
			with open(self.parameters['label_map']) as label_file:
				names_with_labels = json.load(label_file)
				self.label_to_name = {value: key for key, value in names_with_labels.items()}
		except Exception:
			FacerecognizerConsumer.LOGGER.error('Cannot read the label file: ' + self.parameters['label_map'])
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
			face = cv2.resize(face, (self.parameters['size'], self.parameters['size']))
			name = self.recognize(face)
			if name is None:
				context.alert = True
				context.data = 'Cannot recognize face'
				FacerecognizerConsumer.LOGGER.info(context.data)
			else:
				context.data = name
				FacerecognizerConsumer.LOGGER.info('Recognized: ' + name)

		return context

	def recognize(self, face):
		"""
		This method decides if the face is among those that are to be recognized.
		It uses 3 different recognition algorithms for this (Eigen, Fisher, LBPH).
		Though these can be disabled by the configuration.
		:param face: detected face
		:return: name if the face was successfully identified by at least 1 of the recognizers or None
		"""
		if self.parameters['fisher_enabled']:
			label, _ = self.fisher_recognizer.predict(face)
			if self.label_to_name.__contains__(label):
				return self.label_to_name[label]

		if self.parameters['eigen_enabled']:
			label, _ = self.eigen_recognizer.predict(face)
			if self.label_to_name.__contains__(label):
				return self.label_to_name[label]

		if self.parameters['lbph_enabled']:
			label, _ = self.lbph_recognizer.predict(face)
			if self.label_to_name.__contains__(label):
				return self.label_to_name[label]

		return None

	def get_type(self):
		return Type.CAMERA
