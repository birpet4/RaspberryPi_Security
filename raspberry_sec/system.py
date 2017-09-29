import time
import logging
import re
from itertools import groupby
from multiprocessing import Process
from multiprocessing import Queue
from threading import Event
from concurrent.futures import ThreadPoolExecutor
from raspberry_sec.interface.consumer import ConsumerContext


class Stream:
	"""
	Class for storing stream components.
	"""
	LOGGER = logging.getLogger('Stream')

	def __init__(self, _name: str):
		"""
		Constructor
		:param _name: uniquely identifies the Stream instance
		"""
		self.name = _name
		self.producer = None
		self.consumers = []

	def get_name(self):
		"""
		:return: the name of this stream
		"""
		return self.name

	def __eq__(self, other):
		"""
		Decides equality
		:param other: Stream instance
		:return: True or False
		"""
		return self.get_name() == other.get_name()

	def __hash__(self):
		"""
		:return: hash of the instance
		"""
		return hash(self.get_name())

	def validate(self):
		"""

		:return:
		"""
		if self.producer is None:
			Stream.LOGGER.error('No producer set for stream: ' + self.name)
			raise

		prod_type = self.producer().get_type()
		for consumer in self.consumers:
			if consumer().get_type() is not prod_type:
				Stream.LOGGER.error('Wrong consumer type in stream: ' + self.name)
				raise

	def run(self, queue: Queue):
		"""
		
		:param queue:
		:return:
		"""
		self.validate()

		while True:
			# instantiating classes
			producer = self.producer()
			consumers = [consumer() for consumer in self.consumers]

			Stream.LOGGER.debug(self.name + ' calling producer')
			data = producer.get_data()

			context = ConsumerContext(data, True)
			for consumer in consumers:
				Stream.LOGGER.debug(self.name + ' calling consumer: ' + consumer.get_name())
				context = consumer.run(context)

			Stream.LOGGER.debug(self.name + ' enqueueing controller message')
			queue.put(StreamControllerMessage(_alert=context.alert, _msg=context.data, _sender=self.name))


class StreamControllerMessage:
	"""
	Class for managing notifications in case of alerts.
	@see raspberry_sec.interface.action.Action
	"""
	def __init__(self, _alert: bool, _msg: str, _sender: str):
		"""
		Constructor
		:param _alert: True or False
		:param _msg: textual content of the alert
		:param _sender: name of the stream that sent this message
		"""
		self.alert = _alert
		self.msg = _msg
		self.sender = _sender


class StreamController:
	"""
	Class for handling StreamControllerMessage-s
	"""
	LOGGER = logging.getLogger('StreamController')
	PLACEHOLDER_PATTERN = '@.*?@'
	POLLING_INTERVAL = 1

	def __init__(self):
		"""
		Constructor
		"""
		self.action = None
		self.query = 'False'

	@staticmethod
	def evaluate_query(query: str):
		"""
		Evaluates the query and returns a logical value as a response
		:param query: logical expression
		:return: True or False
		"""
		try:
			StreamController.LOGGER.debug('Evaluating query: ' + query)
			return eval(query)
		except Exception:
			StreamController.LOGGER.error('Could not evaluate the query: ' + query)
			return False

	def decide_alert(self, messages: list()):
		"""
		This method decides based on a list of messages
		whether to alert or not. For that it puts together a logical
		expression that it also evaluates afterwards.
		:param messages: list of StreamControllerMessage-s
		:return: decision (True/False) and alert data
		"""
		query = self.query
		alert_data_list = []

		# iterating through every alert message
		for sender, msg_iter in groupby(messages, lambda m: m.sender):
			msg_list = list(msg_iter)
			StreamController.LOGGER.debug(sender + ' sent ' + str(len(msg_list)) + ' messages')

			alert_messages = [msg for msg in msg_list if msg.alert]
			if alert_messages:
				StreamController.LOGGER.debug(sender + ' reported ' + str(len(alert_messages)) + ' alerts')
				alert_data_list = alert_data_list + [am.msg for am in alert_messages]
				query = query.replace('@' + sender.upper() + '@', 'True')
			else:
				query = query.replace('@' + sender.upper() + '@', 'False')

		# making sure no placeholder remains in query
		query = re.sub(pattern=StreamController.PLACEHOLDER_PATTERN, repl='False', string=query)
		alert_data = '; '.join(alert_data_list)

		return StreamController.evaluate_query(query), alert_data

	def run(self, queue: Queue, limit: int):
		"""
		This method in an infinite loop polls the queue for new messages
		and takes care of the action firing mechanism.
		:param queue: for inter-process communication
		:param limit: max number of messages to handle at once
		"""
		# instantiating action
		action = self.action()

		# iterate through messages in queue
		with ThreadPoolExecutor(max_workers=4) as executor:
			while True:
				StreamController.LOGGER.debug('Checking message queue')
				messages = []
				count = 0

				# fetch messages
				while not queue.empty() and count <= limit:
					messages.append(queue.get(block=False))
					count += 1

				# process messages
				alert, data = self.decide_alert(messages)

				# alert
				if alert:
					executor.submit(action.fire, data)

				time.sleep(StreamController.POLLING_INTERVAL)


class PCASystem:
	"""
	Class for hosting the components. Serves as a container.
	"""
	LOGGER = logging.getLogger('PCASystem')

	def __init__(self):
		"""
		Constructor
		"""
		self.producers = dict()
		self.consumers = dict()
		self.actions = dict()
		self.streams = set()
		self.enabled = True
		self.stream_controller = None

	def validate(self):
		"""
		Validates the system by checking its sub-components
		"""
		if not self.stream_controller:
			PCASystem.LOGGER.error('StreamController was not set')
			raise

		if not self.streams:
			PCASystem.LOGGER.warning('There are no streams configured')

	def run(self, event: Event):
		"""
		This method starts the components in separate processes
		and then waits for events. Terminate the processes if necessary.
		:param event: Event object for notification
		"""
		processes = []
		queue = Queue()

		self.validate()

		# starting StreamController process
		sc_message_limit = len(self.streams)*2
		PCASystem.LOGGER.info('Starting stream-controller')
		sc_process = Process(target=self.stream_controller.run, name='SC process', args=(queue, sc_message_limit,))
		processes.append(sc_process)
		sc_process.start()

		# starting Stream processes
		for stream in self.streams:
			PCASystem.LOGGER.info('Starting stream: ' + stream.name)
			process = Process(target=stream.run, name=stream.name, args=(queue,))
			processes.append(process)
			process.start()

		while self.enabled:
			# wait for an event
			event.wait()
			PCASystem.LOGGER.debug('Event arrived')

			if not self.enabled:
				PCASystem.LOGGER.debug('Number of processes to be stopped: ' + str(len(processes)))
				for process in processes:
					process.terminate()
				PCASystem.LOGGER.info('Finished')
