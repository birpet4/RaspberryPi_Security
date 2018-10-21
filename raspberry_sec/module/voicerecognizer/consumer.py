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
		:param parameters: configurations coming from the JSON file
		"""
		super().__init__(parameters)
		self.initialized = False

	def initialize(self):
		self.initialized = True

	def get_name(self):
		return 'VoicerecognizerConsumer'

	def run(self, context: ConsumerContext):
		if not self.initialized:
			self.initialize()
		r = sr.Recognizer()
		audio = context.data
		context.alert = False
		zones = zonemanager.get_zones()
		if audio:
			try:

				you_said = r.recognize_google(audio)
				print("You said: " + you_said)
				for key, value in zones.items():
					if key in you_said:
						print('yours ubstring was found')
						if 'off' or 'on' in you_said:
							print('onoff was found')
							zonemanager.toggle_zone(key)
							print(zonemanager.get_zones())
							return
			except sr.UnknownValueError:
				print("Google Speech Recognition could not understand audio")
			except sr.RequestError as e:
				print("Could not request results from Google Speech Recognition service; {0}".format(e))
				
		return context

	def get_type(self):
		return Type.MICROPHONE
