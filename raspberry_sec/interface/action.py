class Action:
	"""
	Base class for alerting
	"""
	def get_name(self):
		"""
		:return: name of the component
		"""
		pass

	def fire(self, msg: str):
		"""
		Alert functionality
		:param msg: textual content
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
