import logging
import time
import cv2
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class MicrophoneConsumer(Consumer):
	"""
	Consumer class for showing camera images
	"""
	LOGGER = logging.getLogger('MicrophoneConsumer')

	def __init__(self, parameters: dict = dict()):
		"""
		Constructor
		:param parameters: see Consumer constructor
		"""
		super().__init__(parameters)

	def get_name(self):
		return 'MicrophoneConsumer'

	def run(self, context: ConsumerContext):

		return context

	def get_type(self):
		return Type.MICROPHONE
