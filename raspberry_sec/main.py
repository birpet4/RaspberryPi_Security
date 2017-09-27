import os
import sys
import logging
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


LOGGER = logging.getLogger('main')


def setup_logging():
	logging.basicConfig(
		format='[%(asctime)s]:%(name)s:%(levelname)s - %(message)s',
		level=logging.DEBUG)


def main():
	setup_logging()
	LOGGER.info('Starting up service')
	from raspberry_sec.system import PCASystem, Stream, StreamController
	from raspberry_sec.util import PCALoader, PCASystemJSONEncoder, PCASystemJSONDecoder
	import json

	pca_loader = PCALoader()

	stream1 = Stream('stream1')
	stream1.producer = pca_loader.get_producers().get('TestProducer')
	stream1.consumers = [pca_loader.get_consumers().get('TestConsumer')]

	stream2 = Stream('stream2')
	stream2.producer = pca_loader.get_producers().get('TestProducer')
	stream2.consumers = [pca_loader.get_consumers().get('TestConsumer')]

	pca_system = PCASystem()
	pca_system.producers = pca_loader.get_producers()
	pca_system.consumers = pca_loader.get_consumers()
	pca_system.actions = pca_loader.get_actions()
	pca_system.streams = set([stream1, stream2])
	pca_system.stream_controller = StreamController()
	pca_system.stream_controller.action = pca_loader.get_actions().get('TestAction')

	PCASystemJSONEncoder.save_config(pca_system, '../config/pca_system.json')

	pca_system = PCASystemJSONDecoder.load_from_config('../config/pca_system.json')
	print(json.dumps(pca_system, cls=PCASystemJSONEncoder))


if __name__ == '__main__':
	main()
