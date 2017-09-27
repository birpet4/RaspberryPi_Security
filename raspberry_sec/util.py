import importlib
import pkgutil
import logging
import json
from json import JSONEncoder
from json import JSONDecoder
from raspberry_sec.interface.producer import Producer
from raspberry_sec.interface.consumer import Consumer
from raspberry_sec.interface.action import Action
from raspberry_sec.system import PCASystem, StreamController, Stream


class Loader:

	def get_actions(self):
		pass

	def get_producers(self):
		pass

	def get_consumers(self):
		pass


class DynamicLoader:

	LOGGER = logging.getLogger('DynamicLoader')

	@staticmethod
	def load_class(full_class_name: str):
		class_name_parts = full_class_name.split('.')
		class_name = class_name_parts[-1]
		module_name = '.'.join(class_name_parts[:-1])

		_module = importlib.import_module(module_name)
		return getattr(_module, class_name)

	@staticmethod
	def list_modules(package_name: str):
		package = importlib.import_module(package_name)
		modules = []
		for (path, name, is_package) in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
			if not is_package:
				modules.append(name)
		return modules


class PCALoader(Loader):

	LOGGER = logging.getLogger('PCALoader')
	module_package = 'raspberry_sec.module'
	allowed_modules = set(['action', 'consumer','producer'])
	loaded_classes = {Action: {}, Consumer: {}, Producer: {}}

	def __init__(self):
		self.load()

	@staticmethod
	def filter_for_allowed_modules(modules: list):
		filtered_modules = []
		for _module in modules:
			module_name = _module.split('.')[-1]
			if module_name in PCALoader.allowed_modules:
				filtered_modules.append(_module)

		PCALoader.LOGGER.debug('These modules were filtered out: ' + str(set(modules) - set(filtered_modules)))
		return filtered_modules

	@staticmethod
	def generate_class_names(modules: list):
		class_names = []
		for _module in modules:
			_module_parts = _module.split('.')
			module_name = _module_parts[-1]
			package_name = _module_parts[-2]
			class_names.append('.'.join([_module, package_name.capitalize() + module_name.capitalize()]))
		return class_names

	def load(self):
		modules = DynamicLoader.list_modules(PCALoader.module_package)
		modules = PCALoader.filter_for_allowed_modules(modules)
		classes = PCALoader.generate_class_names(modules)

		for _class in classes:
			try:
				PCALoader.LOGGER.info('Loading: ' + _class)
				loaded_class = DynamicLoader.load_class(_class)
				for key in self.loaded_classes.keys():
					if issubclass(loaded_class, key):
						self.loaded_classes[key][loaded_class.__name__] = loaded_class
						break
			except ImportError:
				PCALoader.LOGGER.error(_class + ' - Cannot be imported')

	def get_actions(self):
		return self.loaded_classes[Action]

	def get_producers(self):
		return self.loaded_classes[Producer]

	def get_consumers(self):
		return self.loaded_classes[Consumer]


class PCASystemJSONEncoder(JSONEncoder):
	"""
	Encodes objects to JSON
	"""

	LOGGER = logging.getLogger('PCASystemJSONEncoder')
	TYPE = '__type__'

	@staticmethod
	def save_config(pca_system, config_path: str):
		if not config_path:
			config_path = 'config/pca_system.json'
			PCASystemJSONEncoder.LOGGER.info('Config-path was not set, defaults to ' + config_path)

		parsed = json.loads(json.dumps(pca_system, cls=PCASystemJSONEncoder))
		with open(config_path, 'w+') as configfile:
			json.dump(fp=configfile, obj=parsed, indent=4, sort_keys=True)

	def default(self, obj):
		if isinstance(obj, Stream):
			obj_dict = dict()
			obj_dict['producer'] = obj.producer.__name__
			obj_dict['consumers'] = [c.__name__ for c in obj.consumers]
			obj_dict['enabled'] = obj.enabled
			obj_dict['name'] = obj.name
			class_name = Stream.__name__
		elif isinstance(obj, PCASystem):
			obj_dict = dict()
			obj_dict['actions'] = list(obj.actions.keys())
			obj_dict['producers'] = list(obj.producers.keys())
			obj_dict['consumers'] = list(obj.consumers.keys())
			obj_dict['streams'] = list(obj.streams)
			obj_dict['stream_controller'] = obj.stream_controller
			class_name = PCASystem.__name__
		elif isinstance(obj, StreamController):
			obj_dict = dict()
			obj_dict['query'] = obj.query
			obj_dict['action'] = obj.action.__name__
			class_name = StreamController.__name__
		else:
			return json.JSONEncoder.default(self, obj)

		obj_dict.update({PCASystemJSONEncoder.TYPE: class_name})
		return obj_dict


class PCASystemJSONDecoder(JSONDecoder):
	"""
	Decodes JSON to objects
	"""

	LOGGER = logging.getLogger('PCASystemJSONDecoder')

	def __init__(self, *args, **kwargs):
		self.pca_loader = PCALoader()
		json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

	@staticmethod
	def load_from_config(config_path: str):
		if config_path:
			with open(config_path, 'r') as configfile:
				return json.load(fp=configfile, cls=PCASystemJSONDecoder)
		else:
			PCASystemJSONDecoder.LOGGER.warning('Config-path was not given, returning empty object')
			return PCASystem()

	def object_hook(self, obj_dict):
		loaded_producers = self.pca_loader.get_producers()
		loaded_consumers = self.pca_loader.get_consumers()
		loaded_actions = self.pca_loader.get_actions()

		# Unfamiliar object
		if PCASystemJSONEncoder.TYPE not in obj_dict:
			return obj_dict

		# Stream object
		elif obj_dict[PCASystemJSONEncoder.TYPE] == Stream.__name__:
			try:
				new_stream = Stream(_name=obj_dict['name'])
				new_stream.enabled = obj_dict['enabled']
				new_stream.producer = loaded_producers[obj_dict['producer']]
				new_stream.consumers = [loaded_consumers[cons] for cons in obj_dict['consumers']]
				return new_stream
			except KeyError:
				PCASystemJSONDecoder.LOGGER.error('Cannot load Stream-s in JSON')
				raise

		# PCASystem object
		elif obj_dict[PCASystemJSONEncoder.TYPE] == PCASystem.__name__:
			try:
				pca_system = PCASystem()
				try:
					for name in obj_dict['actions']:
						pca_system.actions[name] = loaded_actions[name]
				except KeyError:
					PCASystemJSONDecoder.LOGGER.error('Cannot find Action-s in JSON')

				try:
					for name in obj_dict['producers']:
						pca_system.producers[name] = loaded_producers[name]
				except KeyError:
					PCASystemJSONDecoder.LOGGER.error('Cannot find Producer-s in JSON')

				try:
					for name in obj_dict['consumers']:
						pca_system.consumers[name] = loaded_consumers[name]
				except KeyError:
					PCASystemJSONDecoder.LOGGER.error('Cannot find Consumer-s in JSON')

				pca_system.stream_controller = obj_dict['stream_controller']
				pca_system.streams = obj_dict['streams']

				return pca_system
			except KeyError:
				PCASystemJSONDecoder.LOGGER.error('Cannot load PCASystem in JSON')
				raise

		# StreamController object
		elif obj_dict[PCASystemJSONEncoder.TYPE] == StreamController.__name__:
			try:
				stream_controller = StreamController()
				stream_controller.query = obj_dict['query']
				stream_controller.action = loaded_actions[obj_dict['action']]
				return stream_controller
			except KeyError:
				PCASystemJSONDecoder.LOGGER.error('Cannot load StreamController in JSON')
				raise

		# Default
		else:
			return {}


		# iterate through Actions
