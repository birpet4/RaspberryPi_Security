import os
import sys
import logging
import multiprocessing as mp
from multiprocessing import Event, Queue
from threading import Thread
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from raspberry_sec.pca import PCASystemJSONDecoder
from raspberry_sec.util import LogQueueListener, ProcessContext, ProcessReady


def start_logging_process(ctx: ProcessContext, level: int):
	"""
	Starts the process that collects and outputs the log-records
	:param ctx: context
	:param level: level of logging (e.g. logging.INFO)
	:return logging process
	"""
	log_listener = LogQueueListener(
			_format='[%(levelname)s]:[%(asctime)s]:[%(processName)s,%(threadName)s]:%(name)s - %(message)s',
			_level=level)

	proc = ProcessContext.create_process(target=log_listener.run, name='LogListener', args=(ctx, ))
	proc.start()

	return proc


def run_pcasystem(env: str, logging_level: int):
	"""
	Sets up the logging facility and then
	it loads the PCASystem specified in the configuration
	:param env: test/prod
	:param logging_level: level of logging, e.g. INFO
	"""
	try:
		config_file = '../config/' + env + '/pca_system.json'
		logging_queue = Queue()
		event = Event()
		event.clear()
		process_context = ProcessContext(log_queue=logging_queue, stop_event=event)

		# Initiate logging process
		logging_process = start_logging_process(process_context, logging_level)

		# Setup logging for current process
		ProcessReady.setup_logging(logging_queue)

		pca_system = PCASystemJSONDecoder.load_from_config(config_file)
		pca_thread = Thread(target=pca_system.run, name='PCA', args=(process_context, ))
		pca_thread.start()

		input('Please press enter to exit...')
	finally:
		event.set()
		pca_thread.join()
		logging_process.terminate()


if __name__ == '__main__':
	mp.set_start_method('spawn')
	run_pcasystem('prod', logging.INFO)
