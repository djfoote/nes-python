import io_device

PC_INIT_INDIRECT_ADDRESS = 0xFFFC


class RAM(io_device.IODevice):
	def __init__(self):
		self.memory = [0x00] * 0x800

	def chip_select(self, address):
		return address < 0x2000

	def read(self, address):
		return self.memory[address & 0x7FF]

	def write(self, address, data):
		self.memory[address & 0x7FF] = data


class CPU(object):
	def __init__(self, external_io_devices):		
		self.initialize_registers()

		self.ram = RAM()
		self.io_devices = [self.ram] + external_io_devices

	def initialize_registers(self):
		self.a = 0x00
		self.x = 0x00
		self.y = 0x00
		self.sp = 0xFF
		self.flags = 0x34

		low_byte = self.read(PC_INIT_INDIRECT_ADDRESS)
		high_byte = self.read(PC_INIT_INDIRECT_ADDRESS + 1)
		self.pc = high_byte << 8 + low_byte

	def read(self, address):
		for device in self.external_io_devices:
			if device.chip_select(address):
				return device.read(address)
		return 0x00

	def write(self, address, data):
		for device in self.external_io_devices:
			if device.chip_select(address):
				device.write(address, data)