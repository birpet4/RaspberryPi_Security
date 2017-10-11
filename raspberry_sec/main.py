import os
import sys
import logging
import time
from multiprocessing import Process, Event, Queue
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from raspberry_sec.pca import PCASystemJSONEncoder, PCASystemJSONDecoder
from raspberry_sec.util import LogQueueListener, ProcessContext, ProcessReady


def run_pcasystem():
	"""
	Sets up the logging facility and then
	it loads the PCASystem specified in the configuration
	"""
	try:
		logging_queue = Queue()
		log_listener = LogQueueListener(
			_format='[%(levelname)s]:[%(asctime)s]:[%(processName)s,%(threadName)s]:%(name)s - %(message)s',
			_level=logging.INFO)

		logging_process = Process(target=log_listener.run, args=(logging_queue,))
		logging_process.start()

		# Setup logging for current process
		ProcessReady.setup_logging(logging_queue)

		pca_system = PCASystemJSONDecoder.load_from_config('../config/pca_system.json')
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
		PCASystemJSONEncoder.save_config(pca_system, '../config/pca_system.json')


def main():
	run_pcasystem()


if __name__ == '__main__':
	main()
