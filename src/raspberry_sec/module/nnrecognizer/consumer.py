import logging
import os, base64
import cv2, numpy as np
from keras.models import load_model
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class NnrecognizerConsumer(Consumer):
	"""
	Consumer class for recognizing human face with a neural network
	"""
	LOGGER = logging.getLogger('NnrecognizerConsumer')

	def __init__(self, parameters: dict):
		"""
		Constructor
		:param parameters: see Consumer constructor
		"""
		super().__init__(parameters)
		self.model = None
		self.size = self.parameters['size']
		self.initialized = False

	def get_name(self):
		return 'NnrecognizerConsumer'

	def get_type(self):
		return Type.CAMERA

	@staticmethod
	def get_path(file: str):
		"""
		:param file: e.g. resources/model.h5py
		:return: the path for the file
		"""
		return os.sep.join([os.path.dirname(__file__), file])

	@staticmethod
	def img_to_str(img):
		"""
		Converts the numpy ndarray into a HTML compatible png src
		:param img: numpy array
		:return: HTML compatible img src
		"""
		resized = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
		png_encoded = cv2.imencode('.png', resized)[1]
		b64_encoded = base64.b64encode(png_encoded.tostring())
		final_format = b64_encoded.decode('utf-8')
		return '<img class="img-responsive center-block" src="data:image/png;base64,' + final_format + '">'

	def initialize(self):
		"""
		Initializes component
		"""
		NnrecognizerConsumer.LOGGER.info('Initializing component')
		try:
			model_path = NnrecognizerConsumer.get_path(self.parameters['model'])
			self.model = load_model(model_path)
			NnrecognizerConsumer.LOGGER.info('Loaded network model')
		except Exception as e:
			NnrecognizerConsumer.LOGGER.error('Cannot load model: ' + str(e))

		self.initialized = True

	def run(self, context: ConsumerContext):
		if not self.initialized:
			self.initialize()

		# the data is expected to be the detected face
		face = context.data
		context.alert = True

		if face is not None:
			NnrecognizerConsumer.LOGGER.info('Running face recognition...')
			if self.recognize(face):
				context.alert = False
				context.alert_data = 'Positive recognition'
				NnrecognizerConsumer.LOGGER.info(context.alert_data)
			else:
				context.alert_data = NnrecognizerConsumer.img_to_str(face)
				NnrecognizerConsumer.LOGGER.info('Negative recognition')
		else:
			NnrecognizerConsumer.LOGGER.warning('Face was not provided (is None)')
			context.alert_data = 'No face provided'

		return context

	def recognize(self, face: np.ndarray):
		"""
		Runs the face through the neural network
		:param face: detected face
		:return:
		"""
		# Resize
		face = cv2.resize(face, (self.size, self.size))

		# Normalize image
		face = np.asarray([face]).reshape(-1, self.size, self.size, 1).astype('float32') / 255

		# Run it through the network
		prediction = self.model.predict(face)
		prediction = np.argmax(np.round(prediction), axis=1)
		if prediction[0] == 1:
			return True
		else:
			return False
