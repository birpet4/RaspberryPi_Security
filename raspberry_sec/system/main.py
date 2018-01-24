import logging
import multiprocessing as mp
from multiprocessing import Event, Queue
from threading import Thread
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from raspberry_sec.system.pca import PCASystemJSONDecoder
from raspberry_sec.system.util import LogQueueListener, ProcessContext, ProcessReady


class PCARuntime:
	"""
	Container class for the environment
	"""
	def __init__(self, pca_system):
		"""
		Constructor
		:param pca_system: PCASystem instance
		:param log_process: Process object of the logging process
		"""
		self.pca_system = pca_system
		self.pca_thread = None
		self.log_process = None
		self.log_queue = None
		self.stop_event = None

	@staticmethod
	def load_pca(config_path: str):
		"""
		Loads the PCASystem using the given config file
		:param config_path: file
		:return: PCASystem object
		"""
		abs_path = os.path.join(os.path.dirname(__file__), '../..', config_path)
		return PCASystemJSONDecoder.load_from_config(abs_path)

	@staticmethod
	def create_logging_process(ctx: ProcessContext, level: int):
		"""
		Creates the process that collects and outputs log-records
		:param ctx: context
		:param level: level of logging (e.g. logging.INFO)
		:return logging process
		"""
		log_listener = LogQueueListener(
			_format='[%(levelname)s]:[%(asctime)s]:[%(processName)s,%(threadName)s]:%(name)s - %(message)s',
			_level=level)
		return ProcessContext.create_process(target=log_listener.run, name='LogListener', args=(ctx,))

	def start(self, log_level: int):
		"""
		Starts the components
		:param log_level: LOGGING level
		"""
		self.log_queue = Queue()
		self.stop_event = Event()
		self.stop_event.clear()

		# Create logging process
		pca_context = ProcessContext(log_queue=self.log_queue, stop_event=self.stop_event)
		self.log_process = PCARuntime.create_logging_process(pca_context, log_level)

		# Setup logging for current process
		ProcessReady.setup_logging(self.log_queue)

		# PCA
		self.pca_thread = Thread(target=self.pca_system.run, name='PCA', args=(pca_context,))

		# START
		self.log_process.start()
		self.pca_thread.start()

	def stop(self):
		"""
		Stops the components
		"""
		# PCA
		self.stop_event.set()
		self.pca_thread.join()
		# Logging
		self.log_queue.put(None)
		self.log_process.join()


def run_pcasystem(env: str, logging_level: int):
	"""
	Sets up the logging facility and then
	it loads the PCASystem specified in the configuration
	:param env: test/prod
	:param logging_level: level of logging, e.g. INFO
	"""
	config_file = os.path.join('config', env, 'pca_system.json')
	pca_runtime = PCARuntime(PCARuntime.load_pca(config_file))
	pca_runtime.start(log_level=logging_level)

	input('Please press enter to exit...')
	pca_runtime.stop()


if __name__ == '__main__':
	mp.set_start_method('spawn')
	run_pcasystem('prod', logging.INFO)
