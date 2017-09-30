from raspberry_sec.interface.producer import Producer, Type


class CameraProducer(Producer):
	"""
	Class for producing camera sample data
	"""
	def __init__(self):
		pass

	def get_name(self):
		"""
		:return: name of the component
		"""
		return 'CameraProducer'

	def get_data(self):
		"""
		:return: sample data
		"""
		pass

	def get_type(self):
		"""
		:return: Producer.Type of this component
		"""
		return Type.CAMERA