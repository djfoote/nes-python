import os

PRG_ROM_BANK_SIZE = 2**14  # 16kB
CHR_ROM_BANK_SIZE = 2**13  # 8kB
TRAINER_SIZE = 2**8  # 512B


# Lambda to delay execution since we want this at the top.
FILETYPES = {'.nes': lambda: load_nes_file}


def load_file(filepath):
	_, ext = os.path.splitext(filepath)
	return FILETYPES[ext]()(filepath)


def load_nes_file(filepath):
	with open(filepath, 'rb') as f:
		bytes_list = list(f.read())

	prg_rom_banks = bytes_list[4]
	chr_rom_banks = bytes_list[5]
	mirroring = 'vertical' if get_bit(bytes_list[6], 0) else 'horizontal'
	has_ram = get_bit(bytes_list[6], 1)
	has_trainer = get_bit(bytes_list[6], 2)
	mirroring = 'four_screen' if get_bit(bytes_list[6], 3) else mirroring
	vs_system = get_bit(bytes_list[7], 0)
	mapper_number = (bytes_list[6] & 0xF0) + (bytes_list[7] >> 4)
	ram_banks = max(bytes_list[8], 1)
	region = 'PAL' if get_bit(bytes_list[9], 0) else 'NTSC'

	data_start = 16
	if has_trainer:
		trainer = bytes_list[data_start : data_start + TRAINER_SIZE]
		data_start += TRAINER_SIZE
	else:
		trainer = []

	prg_rom = bytes_list[
			data_start : data_start + prg_rom_banks * PRG_ROM_BANK_SIZE]
	data_start += prg_rom_banks * PRG_ROM_BANK_SIZE
	chr_rom = bytes_list[
			data_start : data_start + chr_rom_banks * CHR_ROM_BANK_SIZE]

	return {
		'prg_rom_banks': prg_rom_banks,
		'chr_rom_banks': chr_rom_banks,
		'mirroring': mirroring,
		'has_ram': has_ram,
		'has_trainer': has_trainer,
		'mirroring': mirroring,
		'vs_system': vs_system,
		'mapper_number': mapper_number,
		'ram_banks': ram_banks,
		'region': region,
		'trainer': trainer,
		'prg_rom': prg_rom,
		'chr_rom': chr_rom,
	}


def get_bit(number, target_bit):
	return (number & 1 << target_bit) >> target_bit
