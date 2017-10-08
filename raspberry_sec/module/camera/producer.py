import logging
from raspberry_sec.interface.producer import Producer, ProducerDataManager, ProducerDataProxy, Type
from raspberry_sec.util import ProcessContext


class CameraProducerDataProxy(ProducerDataProxy):
	"""
	For storing shared camera data
	"""
	pass


class CameraProducer(Producer):
	"""
	Class for producing camera sample data
	"""
	LOGGER = logging.getLogger('CameraProducer')
	WAIT_KEY_INTERVAL = 100
	UNSUCCESSFUL_LIMIT = 50
	DEVICE = 0

	def __init__(self):
		pass

	def register_shared_data_proxy(self):
		ProducerDataManager.register('CameraProducerDataProxy', CameraProducerDataProxy)

	def create_shared_data_proxy(self, manager: ProducerDataManager):
		return manager.CameraProducerDataProxy()

	def produce_data_loop(self, context: ProcessContext):
		import cv2
		try:
			cam = cv2.VideoCapture(CameraProducer.DEVICE)
			if not cam.isOpened():
				CameraProducer.LOGGER.error('Cannot capture device: ' + str(CameraProducer.DEVICE))
				return

			unsuccessful_images = 0
			data_proxy = context.get_prop('shared_data_proxy')

			while not context.stop_event.is_set():
				ret_val, img = cam.read()
				if ret_val:
					data_proxy.set_data(img)
				else:
					unsuccessful_images += 1
					CameraProducer.LOGGER.warning('Could not capture image')
					# if too many errors happened we rather kill this process later
					if unsuccessful_images == CameraProducer.UNSUCCESSFUL_LIMIT:
						break

				cv2.waitKey(CameraProducer.WAIT_KEY_INTERVAL)
		finally:
			CameraProducer.LOGGER.debug('Stopping capturing images')
			cam.release()

	def get_data(self, data_proxy: ProducerDataProxy):
		CameraProducer.LOGGER.debug('Producer called')
		return data_proxy.get_data()

	def get_name(self):
		"""
		:return: name of the component
		"""
		return 'CameraProducer'

	def get_type(self):
		"""
		:return: Producer.Type of this component
		"""
		return Type.CAMERA
