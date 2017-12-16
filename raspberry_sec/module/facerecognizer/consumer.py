import logging
import json
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

		self.eigen_recognizer.read(FacerecognizerConsumer.get_full_path(self.parameters['eigen_model']))
		self.fisher_recognizer.read(FacerecognizerConsumer.get_full_path(self.parameters['fisher_model']))
		self.lbph_recognizer.read(FacerecognizerConsumer.get_full_path(self.parameters['lbph_model']))

		try:
			label_map_path = FacerecognizerConsumer.get_full_path(self.parameters['label_map'])
			with open(label_map_path) as label_file:
				names_with_labels = json.load(label_file)
				self.label_to_name = {value: key for key, value in names_with_labels.items()}
		except Exception:
			FacerecognizerConsumer.LOGGER.warning('Cannot read the label file: ' + label_map_path)
			self.label_to_name = dict()

		self.initialized = True

	def run(self, context: ConsumerContext):
		import cv2
		if not self.initialized:
			self.initialize()

		# the data is expected to be the detected face
		face = context.data

		if face is not None:
			face = cv2.resize(face, (self.parameters['size'], self.parameters['size']))
			name = self.recognize(face)
			if name is None:
				context.alert = False
				context.alert_data = 'Cannot recognize face'
			else:
				context.alert = True
				context.alert_data = name
		else:
			context.alert = False
			FacerecognizerConsumer.LOGGER.warning('Face was not provided (is None)')

		return context

	def recognize(self, face):
		"""
		This method decides if the face is among those that are to be recognized.
		It uses 3 different recognition algorithms for this (Eigen, Fisher, LBPH).
		Though any of these can be disabled by the configuration.
		:param face: detected face
		:return: name if the face was successfully identified by at least 1 of the recognizers or None
		"""
		FacerecognizerConsumer.LOGGER.info('Starting recognition')
		# Get the recognition results
		names = {
			self.recognize_face(self.parameters['fisher_enabled'], 'FisherRecognizer', face, self.fisher_recognizer),
			self.recognize_face(self.parameters['eigen_enabled'], 'EigenRecognizer', face, self.eigen_recognizer),
			self.recognize_face(self.parameters['lbph_enabled'], 'LBPHRecognizer', face, self.lbph_recognizer)
		}

		# Filter out None-s
		names = {name for name in names if name is not None}

		# If there is onlyon name in the set, the result is unambiguous
		if len(names) == 1:
			return names.pop()
		else:
			return None

	def recognize_face(self, enabled: bool, name: str, face, recognizer):
		"""
		Conducts face recognition
		:param enabled: if False, None is returned
		:param name: of the technique used for recognition
		:param face: numpy object
		:param recognizer: method object
		:return: name of the recognized person, or None
		"""
		if enabled:
			label, c = recognizer.predict(face)
			if self.label_to_name.__contains__(label):
				recognized = self.label_to_name[label]
				FacerecognizerConsumer.LOGGER.info(name + ' identified ' + recognized + ' with ' + str(c))
				return recognized

		return None

	def get_type(self):
		return Type.CAMERA
