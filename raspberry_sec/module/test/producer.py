import logging
import time
from multiprocessing import Event
from raspberry_sec.interface.producer import Producer, ProducerDataProxy, ProducerDataManager, Type


class TestDataProxy(ProducerDataProxy):
	"""
	ProducerDataProxy child for testing purposes
	"""
	pass


class TestProducer(Producer):
	"""
	Producer class for testing purposes
	"""
	LOGGER = logging.getLogger('TestProducer')
	SLEEP_INTERVAL = 1

	def register_shared_data_proxy(self):
		TestProducer.LOGGER.debug('Registered by shared data manager')
		ProducerDataManager.register('TestDataProxy', TestDataProxy)

	def create_shared_data_proxy(self, manager: ProducerDataManager):
		TestProducer.LOGGER.debug('Created shared data')
		return manager.TestDataProxy()

	def produce_data_loop(self, data_proxy: ProducerDataProxy, stop_event: Event):
		count = 1
		while not stop_event.is_set():
			TestProducer.LOGGER.debug('Producer Loop iteration')
			time.sleep(TestProducer.SLEEP_INTERVAL)
			data_proxy.set_data(str(count))
			count += 1
			if count == 15:
				break
		TestProducer.LOGGER.debug('Stopping')

	def get_data(self, data_proxy: ProducerDataProxy):
		TestProducer.LOGGER.debug('Producer called')
		time.sleep(1)
		data = data_proxy.get_data()
		TestProducer.LOGGER.debug(data)
		return data

	def get_name(self):
			return 'TestProducer'

	def get_type(self):
		return Type.CAMERA
