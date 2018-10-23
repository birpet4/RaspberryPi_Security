import logging
import time
import importlib
import speech_recognition as sr
import builtins
from raspberry_sec.system import zonemanager
from raspberry_sec.system.pca import PCASystem
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
		:param parameters: see Consumer constructor
		"""
		super().__init__(parameters)
		self.initialized = False
		self.VoiceRecognizer = None

	def initialize(self):
		self.VoiceRecognizer = sr.Recognizer()
		self.initialized = True

	def get_name(self):
		return 'VoicerecognizerConsumer'

	def run(self, context: ConsumerContext):
		if not self.initialized:
			self.initialize()

		audio = None
		audio = context.data
		context.alert = False
		zones = zonemanager.get_zones()

		if audio:
			try:

				voice_recognition = self.VoiceRecognizer.recognize_google(audio)
				VoicerecognizerConsumer.LOGGER.info('You said: ' + voice_recognition)

				for key, value in zones.items():
					if key in voice_recognition:
						if 'off' in voice_recognition:
							if zones[key] == False:
								VoicerecognizerConsumer.LOGGER.info(key + ' is already inactive')
								break
							else:
								zonemanager.toggle_zone(key)
								break
						if 'on' in voice_recognition:
							if zones[key] == True:
								VoicerecognizerConsumer.LOGGER.info(key + ' is already active')
								break
							else:
								zonemanager.toggle_zone(key)
								break
	
			except sr.UnknownValueError: 
				VoicerecognizerConsumer.LOGGER.info('Voicerecognizer could not understand audio')
			except sr.RequestError as e:
				print("Could not request results from Speech Recognition service; {0}".format(e))
		time.sleep(3)
		return context

	def get_type(self):
		return Type.MICROPHONE
