import time
import logging
from raspberry_sec.interface.producer import Producer, Type
from raspberry_sec.interface.consumer import Consumer, ConsumerContext
from raspberry_sec.interface.action import Action


class Stream:

	LOGGER = logging.getLogger('Stream')

	def __init__(self, _name: str):
		self.name = _name
		self.enabled = True
		self.producer = None
		self.consumers = []

	def run(self):
		while self.enabled:
			data = self.producer.get_data()

			context = ConsumerContext(data, True)
			for consumer in self.consumers:
				context = consumer.run(context)

	def get_name(self):
		return self.name

	def __eq__(self, other):
		return self.get_name() == other.get_name()

	def __hash__(self):
		return hash(self.get_name())


class StreamControllerMessage:

	def __init__(self, _alert: bool, _msg: str, _sender: str):
		self.alert = _alert
		self.msg = _msg
		self.sender = _sender


class StreamController:

	LOGGER = logging.getLogger('StreamController')

	def __init__(self):
		self.action = None
		self.query = 'False'
		self.enabled = True

	def run(self):
		while self.enabled:
			self.LOGGER.info('ALERT !!!')


class PCASystem:

	LOGGER = logging.getLogger('PCASystem')

	def __init__(self):
		self.producers = dict()
		self.consumers = dict()
		self.actions = dict()
		self.streams = set()
		self.stream_controller = None

	def run(self):
		stream_count = len(self.streams)
		processes = []
