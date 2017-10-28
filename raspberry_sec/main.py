import os
import sys
import logging
import time
from multiprocessing import Process, Event, Queue
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from raspberry_sec.pca import PCASystemJSONEncoder, PCASystemJSONDecoder
from raspberry_sec.util import LogQueueListener, ProcessContext, ProcessReady


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
		log_listener = LogQueueListener(
			_format='[%(levelname)s]:[%(asctime)s]:[%(processName)s,%(threadName)s]:%(name)s - %(message)s',
			_level=logging_level)

		logging_process = Process(target=log_listener.run, args=(logging_queue,))
		logging_process.start()

		# Setup logging for current process
		ProcessReady.setup_logging(logging_queue)

		pca_system = PCASystemJSONDecoder.load_from_config(config_file)
		event = Event()
		event.clear()

		process_context = ProcessContext(log_queue=logging_queue, stop_event=event)
		pca_process = Process(target=pca_system.start, args=(process_context, ))
		pca_process.start()

		input('Please press enter to exit...')
	finally:
		event.set()
		time.sleep(4)
		pca_process.terminate()
		logging_process.terminate()

		# save config
		PCASystemJSONEncoder.save_config(pca_system, config_file)


def main():
	run_pcasystem('prod', logging.DEBUG)


if __name__ == '__main__':
	main()
