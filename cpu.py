import io_device

PRG_ROM_START = 0x8000


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
		self.a = 0x00
		self.x = 0x00
		self.y = 0x00
		self.sp = 0x00
		self.pc = PRG_ROM_START
		self.flags = 0x34

		self.ram = RAM()
		self.io_devices = [self.ram] + external_io_devices
