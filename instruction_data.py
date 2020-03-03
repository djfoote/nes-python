import csv

OPS_CSV_FILEPATH = 'utils/6502ops.csv'


def get_opcode_dict():
	return construct_dictionary(get_instruction_data())


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
	for opcode, name, addr_mode, instr_bytes, cycles in instruction_data:
		opcode_dict[int(opcode, 16)] = [name, addr_mode, int(instr_bytes), cycles]
	return opcode_dict
