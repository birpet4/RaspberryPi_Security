import os
import sys
import logging
import time
from threading import Thread
from multiprocessing import Process, Event
from multiprocessing.managers import BaseManager
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


class ProducerDataManager(BaseManager): 
	pass


class ProducerDataProxy(object):

	def __init__(self):
		self.data = None

	def set_data(self, new):
		self.data = new

	def get_data(self):
		return self.data


class Producer:

	@staticmethod
	def register_shared_data():
		ProducerDataManager.register('ProducerDataProxy', ProducerDataProxy)

	@staticmethod
	def get_shared_data(manager: ProducerDataManager):
		return manager.ProducerDataProxy()

	def show_cam(self, data_proxy: ProducerDataProxy, f: int):
		import cv2
		print('Show Cam')
		while True:
			img = data_proxy.get_data()
			if img is not None:
				cv2.imshow('Webcam', img)
			else:
				print('None')
			cv2.waitKey(f)

	def produce_img(self, data_proxy: ProducerDataProxy):
		import cv2
		cam = cv2.VideoCapture(0)
		if not cam.isOpened():
			print('Cannot capture image')
			cam.release()
			return

		print('Got it')
		while True:
			ret_val, img = cam.read()
			if ret_val:
				data_proxy.set_data(img)
			else:
				print('bad')
			cv2.waitKey(100)


def multi():
	Producer.register_shared_data()
	manager = ProducerDataManager()
	manager.start()
	proxy = Producer.get_shared_data(manager)

	producer1 = Producer()
	producer2 = Producer()
	producer3 = Producer()

	process1 = Process(target=producer1.show_cam, args=(proxy, 250, ))
	process2 = Process(target=producer2.show_cam, args=(proxy, 450, ))
	process3 = Process(target=producer3.produce_img, args=(proxy, ))

	process3.start()
	process1.start()
	process2.start()

	time.sleep(5)

	if not process3.is_alive():
		process3 = Process(target=producer3.produce_img, args=(proxy, ))
		process3.start()

	time.sleep(10)

	process1.terminate()
	process2.terminate()
	process3.terminate()
	manager.shutdown()


def main():
	setup_logging()
	run_pcasystem()


if __name__ == '__main__':
	main()
