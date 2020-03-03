import io_device
from utils import file_opener

PRG_ROM_START = 0x8000

PRG_ROM_BANK_SIZE = 2**14  # 16kB
CHR_ROM_BANK_SIZE = 2**13  # 8kB


class ROMWriteException(Exception):
	pass


class NESCartridge(io_device.IODevice):
	def __init__(self, rom_filepath):
		loaded_file = file_opener.load_file(rom_filepath)
		self.prg_rom = loaded_file['prg_rom']
		self.chr_rom = loaded_file['chr_rom']
		self.mapper = get_mapper(loaded_file['mapper_number'])(self)

	def chip_select(self, address):
		return self.mapper.chip_select(address)

	def read(self, address):
		return self.mapper.read_prg_rom(address)

	def write(self, address, data):
		self.mapper.write_prg_rom(address, data)

	def read_chr_rom(self, address):
		return self.mapper.read_chr_rom()


class MemoryMapper(object):
	def __init__(self, cartridge):
		self.cartridge = cartridge

		if len(self.cartridge.prg_rom) % PRG_ROM_BANK_SIZE != 0:
			raise ValueError(f'PRG-ROM size ({len(self.cartridge.prg_rom)}) not '
			                 f'a multiple of bank size ({PRG_ROM_BANK_SIZE})')
		self.num_prg_rom_banks = len(self.cartridge.prg_rom) // PRG_ROM_BANK_SIZE

		if len(self.cartridge.chr_rom) % CHR_ROM_BANK_SIZE != 0:
			raise ValueError(f'CHR-ROM size ({len(self.cartridge.chr_rom)}) not '
			                 f'a multiple of bank size ({CHR_ROM_BANK_SIZE})')
		self.num_chr_rom_banks = len(self.cartridge.chr_rom) // CHR_ROM_BANK_SIZE

		if self.num_prg_rom_banks == 0:
			raise ValueError('Loaded ROM has no PRG-ROM data')

		self.initialize_prg_rom()
		self.initialize_chr_rom()

	def initialize_prg_rom(self):
		self.loaded_prg_rom_banks = self.cartridge.prg_rom[:PRG_ROM_BANK_SIZE * 2]

	def initialize_chr_rom(self):
		self.loaded_chr_rom_banks = self.cartridge.chr_rom[:CHR_ROM_BANK_SIZE]

	def chip_select(self, address):
		raise NotImplementedError()

	def read_prg_rom(self, address):
		raise NotImplementedError()

	def write_prg_rom(self, address, data):
		raise ROMWriteException('Cannot write to PRG-ROM region')

	def read_chr_rom(self, address):
		raise NotImplementedError()


class NROM(MemoryMapper):
	def __init__(self, prg_rom):
		super().__init__(prg_rom)
		if self.num_prg_rom_banks > 2:
			raise ValueError(f'Too much PRG-ROM data ({self.prg_rom_banks} '
			                 f'banks) to fit on an NROM-mapped cartridge')

	def chip_select(self, address):
		return address >= PRG_ROM_START

	def read_prg_rom(self, address):
		relative_address = address - PRG_ROM_START
		if self.num_prg_rom_banks == 1:  # First bank is mirrored
			relative_address &= 0x3FFF
		return self.loaded_prg_rom_banks[relative_address]

	def read_chr_rom(self, address):
		return self.loaded_chr_rom_banks[address]


def get_mapper(mapper_number):
	mappers = {
		0: NROM,
	}
	if mapper_number in mappers:
		return mappers[mapper_number]
	else:
		raise NotImplementedError(
				f'Mapper number {mapper_number} not implemented')
