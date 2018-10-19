import logging
import time
import speech_recognition as sr
from raspberry_sec.interface.producer import Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext


class VoicerecognizerConsumer(Consumer):
	"""
	Base class for consuming sample data

	"""
	LOGGER = logging.getLogger('VoicerecognizerConsumer')
	def __init__(self, parameters: dict):
		"""
		Constructor
		:param parameters: configurations coming from the JSON file
		"""
		super().__init__(parameters)
		self.initialized = False

	def initialize(self):
		return True

	def get_name(self):
		return 'VoicerecognizerConsumer'

	def run(self, context: ConsumerContext):

		r = sr.Recognizer()
		audio = context.data
		context.alert = False
		print(audio)
		
		if audio:
			try:
			    # for testing purposes, we're just using the default API key
			    # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
			    # instead of `r.recognize_google(audio)`
				print("You said: " + r.recognize_google(audio))
			except sr.UnknownValueError:
				print("Google Speech Recognition could not understand audio")
			except sr.RequestError as e:
				print("Could not request results from Google Speech Recognition service; {0}".format(e))
				
		return context

	def get_type(self):
		return Type.MICROPHONE
