import json
import logging
from json import JSONEncoder
from json import JSONDecoder
from multiprocessing import Queue, Process
from raspberry_sec.util import Loader, DynamicLoader, ProcessContext, ProcessReady
from raspberry_sec.stream import StreamController, Stream
from raspberry_sec.interface.producer import Producer, ProducerDataManager, ProducerDataProxy
from raspberry_sec.interface.consumer import Consumer
from raspberry_sec.interface.action import Action


class PCASystem(ProcessReady):
	"""
	Class for hosting the components. Serves as a container/coordinator.
	"""
	LOGGER = logging.getLogger('PCASystem')
	TIMEOUT = 2
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

	def create_stream_controller_process(self, context: ProcessContext, queue: Queue):
		"""
		Starts the stream controller in a separate process
		:param context: Process context
		:param queue: for communication between streams and the controller
		:return: newly created process
		"""
		sc_context = ProcessContext(
			log_queue=context.logging_queue,
			stop_event=context.stop_event,
			message_limit=len(self.streams) * 2,
			message_queue=queue

		)
		return Process(
			target=self.stream_controller.start,
			name='SC process',
			args=(sc_context, )
		)

	@staticmethod
	def create_stream_process(context: ProcessContext, stream: Stream, proxy: ProducerDataProxy, sc_queue: Queue):
		"""
		Creates stream process
		:param context: Process context
		:param stream: Stream object
		:param proxy: shared data proxy
		:param sc_queue:  StreamController message queue
		:return: newly created process
		"""
		s_context = ProcessContext(
			log_queue=context.logging_queue,
			stop_event=context.stop_event,
			shared_data_proxy=proxy,
			sc_queue=sc_queue
		)
		return Process(
			target=stream.start,
			name=stream.name,
			args=(s_context,)
		)

	@staticmethod
	def create_producer_process(context: ProcessContext, prod: Producer, proxy: ProducerDataProxy):
		"""
		Creates a new Producer process
		:param context: Process context
		:param prod: Producer instance
		:param proxy: shared data
		:return: newly created process
		"""
		new_context = ProcessContext(
			stop_event=context.stop_event,
			log_queue=context.logging_queue,
			shared_data_proxy=proxy
		)
		return Process(
			target=prod.start,
			name=prod.get_name(),
			args=(new_context,)
		)

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
	def resurrect_producers(context: ProcessContext, prod_to_proc: dict, prod_to_proxy: dict):
		"""
		Restarts processes that are not running
		:param context: Process context
		:param prod_to_proc: producer to process mapping
		:param prod_to_proxy: producer to shared data proxy object mapping
		"""
		PCASystem.LOGGER.debug('Checking producer processes')
		for prod, proc in prod_to_proc.items():
			if not proc.is_alive():
				PCASystem.LOGGER.info(prod.get_name() + ' process will be resurrected')
				new_proc = PCASystem.create_producer_process(context, prod, prod_to_proxy[prod])
				prod_to_proc[prod] = new_proc
				new_proc.start()

	def run(self, context: ProcessContext):
		"""
		This method starts the components in separate processes
		and then waits for the stop event. It then terminates the processes if necessary.
		:param context: contains tools needed for 'running alone'
		"""
		self.validate()

		producer_set = set([s.producer() for s in self.streams])
		sc_queue = Queue()
		stream_processes = []
		# producer-to-process mapping
		prod_to_proc = {}
		# producer-to-shared data proxy mapping
		prod_to_proxy = {}

		# shared data manager
		manager = PCASystem.prepare_shared_manager(producer_set)

		# start producer processes
		for producer in producer_set:
			proxy = producer.create_shared_data_proxy(manager)
			proc = PCASystem.create_producer_process(context, producer, proxy)

			prod_to_proc[producer] = proc
			prod_to_proxy[producer] = proxy

			PCASystem.LOGGER.info('Starting producer: ' + producer.get_name())
			proc.start()

		# start stream controller process
		sc_process = self.create_stream_controller_process(context, sc_queue)
		PCASystem.LOGGER.info('Stream-controller started')
		sc_process.start()

		# start stream processes
		for stream in self.streams:
			s_process = PCASystem.create_stream_process(context, stream, prod_to_proxy[stream.producer()], sc_queue)
			stream_processes.append(s_process)
			PCASystem.LOGGER.info('Starting stream: ' + stream.name)
			s_process.start()

		# wait for the stop event and periodically check the producers
		while not context.stop_event.is_set():
			context.stop_event.wait(timeout=PCASystem.POLLING_INTERVAL)
			PCASystem.resurrect_producers(context, prod_to_proc, prod_to_proxy)

		PCASystem.LOGGER.debug('Stop event arrived')

		PCASystem.LOGGER.debug('Number of stream processes to be stopped: ' + str(len(stream_processes)))
		for process in stream_processes:
			process.terminate()

		PCASystem.LOGGER.debug('Stopping stream controller')
		sc_process.terminate()

		PCASystem.LOGGER.debug('Waiting for producers')
		for prod, proc in prod_to_proc.items():
			proc.join()

		PCASystem.LOGGER.info('Finished')


class PCALoader(Loader):
	"""
	Implementation of Loader, that is capable of loading a PCASystem from the package system.
	"""
	LOGGER = logging.getLogger('PCALoader')
	module_package = 'raspberry_sec.module'
	allowed_modules = {'action', 'consumer','producer'}
	loaded_classes = {Action: {}, Consumer: {}, Producer: {}}

	def __init__(self):
		"""
		Constructor
		"""
		self.load()

	@staticmethod
	def filter_for_allowed_modules(modules: list):
		"""
		This method filters the input based on preconfigured settings.
		Only Action, Producer, Consumer classes can be loaded from specific modules.
		:param modules: modules to be used by the system
		:return: filtered list
		"""
		filtered_modules = []
		for _module in modules:
			module_name = _module.split('.')[-1]
			if module_name in PCALoader.allowed_modules:
				filtered_modules.append(_module)

		PCALoader.LOGGER.debug('These modules were filtered out: ' + str(set(modules) - set(filtered_modules)))
		return filtered_modules

	@staticmethod
	def generate_class_names(modules: list):
		"""
		Based on predefined rules it generates class names to be loaded.
		E.g. xxx.yyy.test.consumer --> xxx.yyy.test.consumer.TestConsumer
		:param modules: list of modules
		:return: list of class names generated from the input
		"""
		class_names = []
		for _module in modules:
			_module_parts = _module.split('.')
			module_name = _module_parts[-1]
			package_name = _module_parts[-2]
			class_names.append('.'.join([_module, package_name.capitalize() + module_name.capitalize()]))
		return class_names

	def load(self):
		"""
		Loads and stores the newly loaded class objects
		"""
		modules = DynamicLoader.list_modules(PCALoader.module_package)
		modules = PCALoader.filter_for_allowed_modules(modules)
		classes = PCALoader.generate_class_names(modules)

		for _class in classes:
			try:
				loaded_class = DynamicLoader.load_class(_class)
				PCALoader.LOGGER.info('Loaded: ' + _class)
				for key in self.loaded_classes.keys():
					if issubclass(loaded_class, key):
						self.loaded_classes[key][loaded_class.__name__] = loaded_class
						break
			except ImportError:
				PCALoader.LOGGER.error(_class + ' - Cannot be imported')

	def get_actions(self):
		"""
		:return: Action class dictionary
		"""
		return self.loaded_classes[Action]

	def get_producers(self):
		"""
		:return: Producer class dictionary
		"""
		return self.loaded_classes[Producer]

	def get_consumers(self):
		"""
		:return: Consumer class dictionary
		"""
		return self.loaded_classes[Consumer]


class PCASystemJSONEncoder(JSONEncoder):
	"""
	Encodes objects to JSON
	"""
	LOGGER = logging.getLogger('PCASystemJSONEncoder')
	TYPE = '__type__'

	@staticmethod
	def save_config(pca_system: PCASystem, config_path: str):
		"""
		Using JSON serialization this method saves the system into a file
		:param pca_system: to be serialized
		:param config_path: file path to save it to
		"""
		if not config_path:
			config_path = 'config/pca_system.json'
			PCASystemJSONEncoder.LOGGER.info('Config-path was not set, defaults to ' + config_path)

		parsed = json.loads(json.dumps(pca_system, cls=PCASystemJSONEncoder))
		with open(config_path, 'w+') as configfile:
			json.dump(fp=configfile, obj=parsed, indent=4, sort_keys=True)

	@staticmethod
	def stream_to_dict(obj: Stream):
		"""
		:param obj: Stream object
		:return: dict version of the input
		"""
		obj_dict = dict()
		obj_dict['producer'] = obj.producer.__name__
		obj_dict['consumers'] = [c.__name__ for c in obj.consumers]
		obj_dict['name'] = obj.name
		obj_dict[PCASystemJSONEncoder.TYPE] = Stream.__name__
		return obj_dict

	@staticmethod
	def pcasystem_to_dict(obj: PCASystem):
		"""
		:param obj: PCASystem object
		:return: dict version of the input
		"""
		obj_dict = dict()
		obj_dict['streams'] = list(obj.streams)
		obj_dict['stream_controller'] = obj.stream_controller
		obj_dict[PCASystemJSONEncoder.TYPE] = PCASystem.__name__
		return obj_dict

	@staticmethod
	def streamcontroller_to_dict(obj: StreamController):
		"""
		:param obj: StreamController object
		:return: dict version of the input
		"""
		obj_dict = dict()
		obj_dict['query'] = obj.query
		obj_dict['action'] = obj.action.__name__
		obj_dict[PCASystemJSONEncoder.TYPE] = StreamController.__name__
		return obj_dict

	def default(self, obj):
		"""
		:param obj: to be serialized
		:return: dictionary
		"""
		if isinstance(obj, Stream):
			return PCASystemJSONEncoder.stream_to_dict(obj)
		elif isinstance(obj, PCASystem):
			return PCASystemJSONEncoder.pcasystem_to_dict(obj)
		elif isinstance(obj, StreamController):
			return PCASystemJSONEncoder.streamcontroller_to_dict(obj)
		else:
			return json.JSONEncoder.default(self, obj)


class PCASystemJSONDecoder(JSONDecoder):
	"""
	Decodes JSON to objects
	"""
	LOGGER = logging.getLogger('PCASystemJSONDecoder')

	def __init__(self, *args, **kwargs):
		"""
		Constructor
		:param args:
		:param kwargs:
		"""
		pca_loader = PCALoader()
		self.loaded_producers = pca_loader.get_producers()
		self.loaded_consumers = pca_loader.get_consumers()
		self.loaded_actions = pca_loader.get_actions()

		json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

	@staticmethod
	def load_from_config(config_path: str):
		"""
		This method loads a PCASystem from a JSON file
		:param config_path: file path
		:return: read system object
		"""
		if config_path:
			with open(config_path, 'r') as configfile:
				return json.load(fp=configfile, cls=PCASystemJSONDecoder)
		else:
			PCASystemJSONDecoder.LOGGER.warning('Config-path was not given, returning empty system')
			return PCASystem()

	def stream_from_dict(self, obj_dict: dict):
		"""
		:param obj_dict: JSON structure
		:return: Stream object
		"""
		try:
			new_stream = Stream(_name=obj_dict['name'])
			new_stream.producer = self.loaded_producers[obj_dict['producer']]
			new_stream.consumers = [self.loaded_consumers[cons] for cons in obj_dict['consumers']]
			return new_stream
		except KeyError:
			PCASystemJSONDecoder.LOGGER.error('Cannot load Stream-s from JSON')
			raise

	def streamcontroller_from_dict(self, obj_dict: dict):
		"""
		:param obj_dict: JSON structure
		:return: StreamController object
		"""
		try:
			stream_controller = StreamController()
			stream_controller.query = obj_dict['query']
			stream_controller.action = self.loaded_actions[obj_dict['action']]
			return stream_controller
		except KeyError:
			PCASystemJSONDecoder.LOGGER.error('Cannot load StreamController from JSON')
			raise

	def pcasystem_from_dict(self, obj_dict: dict):
		"""
		:param obj_dict: JSON structure
		:return: PCASystem object
		"""
		try:
			pca_system = PCASystem()
			pca_system.actions = {a: a for a in self.loaded_actions}
			pca_system.producers = {p: p for p in self.loaded_producers}
			pca_system.consumers = {c: c for c in self.loaded_consumers}

			pca_system.stream_controller = obj_dict['stream_controller']
			pca_system.streams = obj_dict['streams']
			return pca_system
		except KeyError:
			PCASystemJSONDecoder.LOGGER.error('Cannot load PCASystem from JSON')
			raise

	def object_hook(self, obj_dict):
		"""
		:param obj_dict: JSON structure
		:return: object equivalent
		"""
		# Unfamiliar object
		if PCASystemJSONEncoder.TYPE not in obj_dict:
			return obj_dict
		# Stream object
		elif obj_dict[PCASystemJSONEncoder.TYPE] == Stream.__name__:
			return self.stream_from_dict(obj_dict)
		# PCASystem object
		elif obj_dict[PCASystemJSONEncoder.TYPE] == PCASystem.__name__:
			return self.pcasystem_from_dict(obj_dict)
		# StreamController object
		elif obj_dict[PCASystemJSONEncoder.TYPE] == StreamController.__name__:
			return self.streamcontroller_from_dict(obj_dict)
		# Default
		else:
			return {}
