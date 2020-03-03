class IODevice(object):
	def chip_select(self, address):
		return False

	def read(self, address):
		raise NotImplementedError()

	def write(self, address, data):
		raise NotImplementedError()
