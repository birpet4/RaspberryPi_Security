import os
import sys
import logging
import time
from threading import Thread, Event
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from raspberry_sec.util import PCASystemJSONDecoder


LOGGER = logging.getLogger('main')


def setup_logging():
	logging.basicConfig(
		format='[%(asctime)s]:[%(processName)s,%(threadName)s]:%(name)s:%(levelname)s - %(message)s',
		level=logging.DEBUG)


def main():
	setup_logging()
	LOGGER.info('Starting up service')

	pca_system = PCASystemJSONDecoder.load_from_config('../config/pca_system.json')
	event = Event()
	event.clear()
	pca_thread = Thread(name='PCASystem Thread', target=pca_system.run, args=(event,))
	pca_thread.start()

	time.sleep(15)
	LOGGER.info('Stopping service')
	pca_system.enabled = False
	event.set()


if __name__ == '__main__':
	main()
