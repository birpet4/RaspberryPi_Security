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

	LOGGER = logging.getLogger('Stream')

	def __init__(self, _name: str):
		self.name = _name
		self.producer = None
		self.consumers = []

	def get_name(self):
		return self.name

	def __eq__(self, other):
		return self.get_name() == other.get_name()

	def __hash__(self):
		return hash(self.get_name())

	def validate_components(self):
		if self.producer is None:
			Stream.LOGGER.error('No producer set for stream: ' + self.name)
			raise

		prod_type = self.producer().get_type()
		for consumer in self.consumers:
			if consumer().get_type() is not prod_type:
				Stream.LOGGER.error('Wrong consumer type in stream: ' + self.name)
				raise

	def run(self, queue: Queue):
		self.validate_components()

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

	def __init__(self, _alert: bool, _msg: str, _sender: str):
		self.alert = _alert
		self.msg = _msg
		self.sender = _sender


class StreamController:

	LOGGER = logging.getLogger('StreamController')
	PLACEHOLDER_PATTERN = '@.*?@'

	def __init__(self):
		self.action = None
		self.query = 'False'

	def decide_alert(self, messages: list()):
		query = self.query
		alert_data_list = []

		# iterating through every alert message
		for sender, msg_iter in groupby(messages, lambda m: m.sender):
			alert_messages = [m for m in list(msg_iter) if m.alert]
			if alert_messages:
				StreamController.LOGGER.debug(sender + ' reported ' + str(len(alert_messages)) + ' alert messages')
				query = query.replace('@' + sender.upper() + '@', 'True')
				alert_data_list = alert_data_list + [am.msg for am in alert_messages]
			else:
				query = query.replace('@' + sender.upper() + '@', 'False')

		# making sure no placeholder remains in query
		query = re.sub(pattern=StreamController.PLACEHOLDER_PATTERN, repl='False', string=query)

		StreamController.LOGGER.debug('Evaluating query: ' + query)
		return eval(query), '; '.join(alert_data_list)

	def run(self, queue: Queue, limit: int):
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

				time.sleep(1)


class PCASystem:

	LOGGER = logging.getLogger('PCASystem')

	def __init__(self):
		self.producers = dict()
		self.consumers = dict()
		self.actions = dict()
		self.streams = set()
		self.enabled = True
		self.stream_controller = None

	def run(self, event: Event):
		processes = []
		queue = Queue()
		if not self.stream_controller:
			PCASystem.LOGGER.error('StreamController was not set')
			raise

		# starting StreamController process
		sc_process = Process(target=self.stream_controller.run, args=(queue, len(self.streams)*2,))
		processes.append(sc_process)
		sc_process.start()

		# starting Stream processes
		for stream in self.streams:
			PCASystem.LOGGER.info('Starting stream: ' + stream.name)
			process = Process(target=stream.run, args=(queue,))
			processes.append(process)
			process.start()

		while self.enabled:
			# wait for an event
			event.wait()

			if not self.enabled:
				PCASystem.LOGGER.debug('Number of processes to be stopped: ' + str(len(processes)))
				for process in processes:
					process.terminate()
			PCASystem.LOGGER.info('Finished')
