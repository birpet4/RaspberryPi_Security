import time
import logging
import re
from itertools import groupby
from multiprocessing import Process, Queue, Event
from threading import Event
from concurrent.futures import ThreadPoolExecutor
from raspberry_sec.interface.consumer import ConsumerContext
from raspberry_sec.interface.producer import ProducerDataProxy, ProducerDataManager


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
		This method validates whether the stream is properly configured.
		Raises exception if not.
		"""
		if self.producer is None:
			Stream.LOGGER.error('No producer set for stream: ' + self.name)
			raise

		prod_type = self.producer().get_type()
		for consumer in self.consumers:
			if consumer().get_type() is not prod_type:
				Stream.LOGGER.error('Wrong consumer type in stream: ' + self.name)
				raise

	def run(self, queue: Queue, producer_data_proxy: ProducerDataProxy):
		"""
		This method runs the stream.
		:param queue: for sending alert messages
		:param producer_data_proxy: for sharing data between producers
		"""
		self.validate()

		# instantiating classes
		producer = self.producer()
		consumers = [consumer() for consumer in self.consumers]

		# stream main loop
		while True:
			try:
				Stream.LOGGER.debug(self.name + ' calling producer')
				data = producer.get_data(producer_data_proxy)

				context = ConsumerContext(data, True)
				for consumer in consumers:
					Stream.LOGGER.debug(self.name + ' calling consumer: ' + consumer.get_name())
					context = consumer.run(context)

				Stream.LOGGER.debug(self.name + ' enqueueing controller message')
				queue.put(StreamControllerMessage(_alert=context.alert, _msg=context.data, _sender=self.name))
			except:
				Stream.LOGGER.error('Something really bad happened')


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
		This method polls the queue for new messages
		and takes care of the action firing mechanism.
		:param queue: for inter-process communication (receives messages)
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
	TIMEOUT = 1
	POLLING_INTERVAL = 2

	def __init__(self):
		"""
		Constructor
		"""
		self.producers = dict()
		self.consumers = dict()
		self.actions = dict()
		self.streams = set()
		self.stream_controller = None

	def validate(self):
		"""
		Validates the system by checking its sub-components.
		Raises exception if something is wrong.
		"""
		if not self.stream_controller:
			PCASystem.LOGGER.error('StreamController was not set')
			raise

		if not self.streams:
			PCASystem.LOGGER.warning('There are no streams configured')

	def start_stream_controller(self, queue: Queue):
		"""
		Starts the stream controller in a separate process
		:param queue: for communication between streams and the controller
		:return: newly created process
		"""
		sc_message_limit = len(self.streams) * 2
		PCASystem.LOGGER.info('Starting stream-controller')
		sc_process = Process(target=self.stream_controller.run, name='SC process', args=(queue, sc_message_limit,))
		sc_process.start()
		return sc_process

	@staticmethod
	def prepare_shared_manager(producers: set):
		"""
		Prepares the shared data manager for use
		:param producers: set of Producer instances
		:return: manager
		"""

		PCASystem.LOGGER.info('Number of different producers: ' + str(len(producers)))
		for producer in producers:
			producer.register_shared_data_proxy()

		manager = ProducerDataManager()
		manager.start()
		PCASystem.LOGGER.info('ProducerDataManager started')

		return manager

	@staticmethod
	def resurrect_producers(prod_to_proc: dict, prod_to_proxy: dict, stop_event: Event):
		"""
		Restarts processes that are not running
		:param prod_to_proc: producer to process mapping
		:param prod_to_proxy: producer to shared data proxy object mapping
		:param stop_event: Event object for notification
		"""
		PCASystem.LOGGER.debug('Checking producer processes')
		for prod, proc in prod_to_proc.items():
			if not proc.is_alive():
				PCASystem.LOGGER.info(prod.get_name() + ' process will be resurrected')
				new_proc = Process(
					target=prod.produce_data_loop,
					name=prod.get_name(),
					args=(prod_to_proxy[prod], stop_event, ))
				prod_to_proc[prod] = new_proc
				new_proc.start()

	def run(self, stop_event: Event):
		"""
		This method starts the components in separate processes
		and then waits for the stop event. Then it terminates the processes if necessary.
		:param stop_event: Event object for notification
		"""
		self.validate()
		stream_processes = []
		prod_to_proc = {}
		prod_to_proxy = {}
		producer_set = set([s.producer() for s in self.streams])
		queue = Queue()

		# shared data manager
		manager = PCASystem.prepare_shared_manager(producer_set)

		# producers
		for producer in producer_set:
			prod_name = producer.get_name()
			proxy = producer.create_shared_data_proxy(manager)

			PCASystem.LOGGER.info('Starting producer: ' + prod_name)
			proc = Process(target=producer.produce_data_loop, name=prod_name, args=(proxy, stop_event, ))

			prod_to_proc[producer] = proc
			prod_to_proxy[producer] = proxy

			proc.start()

		# stream controller
		sc_process = self.start_stream_controller(queue)

		# streams
		for stream in self.streams:
			PCASystem.LOGGER.info('Starting stream: ' + stream.name)
			process = Process(
				target=stream.run,
				name=stream.name,
				args=(queue, prod_to_proxy[stream.producer()], ))

			stream_processes.append(process)
			process.start()

		# wait for the stop event and periodically check the producers
		while not stop_event.is_set():
			stop_event.wait(timeout=PCASystem.POLLING_INTERVAL)
			PCASystem.resurrect_producers(prod_to_proc, prod_to_proxy, stop_event)

		PCASystem.LOGGER.debug('Stop event arrived')

		PCASystem.LOGGER.debug('Number of stream processes to be stopped: ' + str(len(stream_processes)))
		for process in stream_processes:
			process.terminate()

		PCASystem.LOGGER.debug('Stopping stream controller')
		sc_process.terminate()

		PCASystem.LOGGER.debug('Waiting for producers')
		time.sleep(PCASystem.TIMEOUT)
		for prod, proc in prod_to_proc.items():
			proc.terminate()

		PCASystem.LOGGER.info('Finished')
