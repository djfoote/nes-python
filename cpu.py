import io_device
import instruction

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


class CPUFlags(object):
	def __init__(self):
		self.c = 0
		self.z = 0
		self.i = 1
		self.d = 0
		self.b = 1
		self.v = 0
		self.n = 0


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

		self.flags = CPUFlags()

		low_byte = self.read(PC_INIT_INDIRECT_ADDRESS)
		high_byte = self.read(PC_INIT_INDIRECT_ADDRESS + 1)
		self.pc = high_byte << 8 + low_byte

		self.instructions = instruction.initialize_instructions(self)

	def read(self, address):
		for device in self.external_io_devices:
			if device.chip_select(address):
				return device.read(address)
		return 0x00

	def write(self, address, data):
		for device in self.external_io_devices:
			if device.chip_select(address):
				device.write(address, data)
