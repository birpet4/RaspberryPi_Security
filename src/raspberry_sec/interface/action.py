class ActionMessage:
	"""
	Class for holding Action alert details
	"""
	def __init__(self, data):
		"""
		Constructor
		:param data: alert detail
		"""
		self.data = data


class Action:
	"""
	Base class for alerting
	"""
	def __init__(self, parameters: dict = dict()):
		"""
		Constructor
		:param parameters: configurations coming from the JSON file
		"""
		self.parameters = parameters

	def get_name(self):
		"""
		:return: name of the component
		"""
		pass

	def fire(self, msg: list):
		"""
		Alert functionality
		:param msg: list of ActionMessage instances
		"""
		pass

	def __eq__(self, other):
		"""
		:param other: other object
		:return: True or False depending on the name
		"""
		return self.get_name() == other.get_name()

	def __hash__(self):
		"""
		:return: hash code
		"""
		return hash(self.get_name())
