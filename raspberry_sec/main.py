import os
import sys
import logging
import time
from threading import Thread
from multiprocessing import Process, Event, Queue
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from raspberry_sec.pca import PCASystemJSONDecoder
from raspberry_sec.util import LogQueueListener, ProcessContext


def run_pcasystem():
	"""
	Sets up the logging facility and then
	it loads the PCASystem specified in the configuration
	"""
	try:
		logging_queue = Queue()
		log_listener = LogQueueListener(
			_format='[%(asctime)s]:[%(processName)s,%(threadName)s]:%(name)s:%(levelname)s - %(message)s',
			_level=logging.DEBUG)

		logging_process = Process(target=log_listener.run, args=(logging_queue,))
		logging_process.start()

		pca_system = PCASystemJSONDecoder.load_from_config('../config/pca_system.json')
		event = Event()
		event.clear()

		process_context = ProcessContext(log_queue=logging_queue, stop_event=event)
		Thread(target=pca_system.start, args=(process_context, )).start()

		time.sleep(30)
	finally:
		event.set()
		time.sleep(0.5)
		logging_process.terminate()


def main():
	run_pcasystem()


if __name__ == '__main__':
	main()
