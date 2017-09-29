from enum import Enum


class Type(Enum):
	"""
	Producer types
	"""
	CAMERA=1


class Producer:
	"""
	Base class for producing sample data
	"""
	def get_name(self):
		"""
		:return: name of the component
		"""
		pass

	def get_data(self):
		"""
		:return: sample data
		"""
		pass

	def get_type(self):
		"""
		:return: Producer.Type
		"""
		pass

	def __eq__(self, other):
		"""
		:param other object
		:return: True or False depending on the name
		"""
		return self.get_name() == other.get_name()

	def __hash__(self):
		"""
		:return: hash code
		"""
		return hash(self.get_name())
