import os
import sys
import time
import cv2
from multiprocessing import Process, Event
from threading import Thread
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from raspberry_sec.module.camera.producer import CameraProducer
from raspberry_sec.module.camera.consumer import CameraConsumer, ConsumerContext
from raspberry_sec.system.util import ProcessContext
from raspberry_sec.interface.producer import ProducerDataProxy, ProducerDataManager


def set_producer_parameters():
	parameters = dict()
	parameters['device'] = 0
	parameters['unsuccessful_limit'] = 50
	parameters['wait_key_interval'] = 50
	return parameters


def set_consumer_parameters():
	parameters = dict()
	parameters['timeout'] = 1
	parameters['wait_key_timeout'] = 250
	return parameters


def setup_context(proxy: ProducerDataProxy, event: Event):
	return ProcessContext(
		log_queue=None,
		stop_event=event,
		shared_data_proxy=proxy
	)


def show_image(context: ProcessContext):
	data_proxy = context.get_prop('shared_data_proxy')
	consumer = CameraConsumer(set_consumer_parameters())
	consumer_context = ConsumerContext(None, False)
	try:
		while not context.stop_event.is_set():
			consumer_context.data = data_proxy.get_data()
			consumer.run(consumer_context)
	finally:
		cv2.destroyAllWindows()


def finish(stop_event: Event):
	input('Please press enter to exit...')
	stop_event.set()
	time.sleep(1)


def integration_test():
	# Given
	parameters = set_producer_parameters()

	producer = CameraProducer(parameters)
	producer.register_shared_data_proxy()

	manager = ProducerDataManager()
	manager.start()

	proxy = producer.create_shared_data_proxy(manager)
	stop_event = Event()
	stop_event.clear()

	producer_context = setup_context(proxy, stop_event)
	consumer_context = setup_context(proxy, stop_event)

	# When
	Process(target=producer.run, args=(producer_context,)).start()
	Thread(target=finish, args=(stop_event,)).start()

	# Then
	show_image(consumer_context)


if __name__ == '__main__':
	integration_test()
