import os
import sys
import logging
import time
from threading import Thread
from multiprocessing import Event
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from raspberry_sec.util import PCASystemJSONDecoder


def setup_logging():
	"""
	Sets up the global logging facility
	"""
	logging.basicConfig(
		format='[%(asctime)s]:[%(processName)s,%(threadName)s]:%(name)s:%(levelname)s - %(message)s',
		level=logging.DEBUG)


def run_pcasystem():
	"""
	Runs the configuration and starts-up the PCASystem
	"""
	try:
		pca_system = PCASystemJSONDecoder.load_from_config('../config/pca_system.json')
		event = Event()
		event.clear()
		pca_thread = Thread(target=pca_system.run, args=(event,))
		pca_thread.start()

		time.sleep(30)
	finally:
		event.set()


def main():
	setup_logging()
	run_pcasystem()


if __name__ == '__main__':
	main()
