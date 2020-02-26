import csv
import sys

import file_opener

PRG_ROM_START = 0x8000

OPS_CSV_FILEPATH = 'utils/6502ops.csv'


def get_instruction_data():
	instruction_data = []
	with open(OPS_CSV_FILEPATH, newline='') as csvfile:
		reader = csv.reader(csvfile)
		for i, line in enumerate(reader):
			if i and line:  # Throw away first line and empty lines.
				instruction_data.append(line)
	return instruction_data


def construct_dictionary(instruction_data):
	opcode_dict = {}
	for opcode, name, addr_mode, instr_bytes, cycles, flags in instruction_data:
		opcode_dict[int(opcode, 16)] = [name, addr_mode, int(instr_bytes)]
	return opcode_dict


def disassemble_program(prg_rom, opcode_dict):
	byte_offset = 0
	while byte_offset < len(prg_rom):
		memory_address = format(PRG_ROM_START + byte_offset, '04X')
		opcode = prg_rom[byte_offset]
		opcode_string = format(opcode, '02X')

		if opcode not in opcode_dict:
			print(f'{memory_address} {opcode_string}       ??? ')
			byte_offset += 1
			continue

		name, addr_mode, instr_bytes = opcode_dict[opcode]
		if byte_offset + instr_bytes > len(prg_rom):
			print(f'{memory_address} {opcode_string}       ??? ')
			byte_offset += 1
			continue

		extra_bytes = prg_rom[byte_offset + 1 : byte_offset + instr_bytes]
		byte2_string = format(extra_bytes[0], '02X') if instr_bytes >= 2 else '  '
		byte3_string = format(extra_bytes[1], '02X') if instr_bytes >= 3 else '  '
		address_string = get_address_string(addr_mode, extra_bytes)
		line_string = (
				f'{memory_address} {opcode_string} {byte2_string} {byte3_string} '
				f'{name} {address_string}')
		print(line_string)
		byte_offset += instr_bytes


def get_address_string(addr_mode, extra_bytes):
	number_string = '$'
	for byte in extra_bytes[::-1]:  # 6502 CPU is little-endian.
		number_string += format(byte, '02X')

	if addr_mode == 'ACC':
		return 'A'
	elif addr_mode == 'ABS':
		return number_string
	elif addr_mode == 'ABSX':
		return f'{number_string},X'
	elif addr_mode == 'ABSY':
		return f'{number_string},Y'
	elif addr_mode == 'IMM':
		return f'#{number_string}'
	elif addr_mode == 'IMP':
		return ''
	elif addr_mode == 'IND':
		return f'({number_string})'
	elif addr_mode == 'INDX':
		return f'({number_string},X)'
	elif addr_mode == 'INDY':
		return f'({number_string}),Y'
	elif addr_mode == 'REL':
		return number_string
	elif addr_mode == 'ZP':
		return number_string
	elif addr_mode == 'ZPX':
		return f'{number_string},X'
	elif addr_mode == 'ZPY':
		return f'{number_string},Y'
	else:
		raise ValueError(f'Unknown addressing mode {addr_mode}')


def main():
	opcode_dict = construct_dictionary(get_instruction_data())

	filepath = sys.argv[1]
	loaded_rom = file_opener.load_file(filepath)
	disassemble_program(loaded_rom['prg_rom'], opcode_dict)


if __name__ == '__main__':
	main()
