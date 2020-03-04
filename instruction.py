import instruction_data

A_REG = 'a'

opcode_dict = instruction_data.get_opcode_dict()


class Instruction(object):
	def __init__(self, cpu, opcode):
		self.cpu = cpu
		self.opcode = opcode

		instr_name, addr_mode, num_bytes, cycles_string = opcode_dict[opcode]

		self.operation = self.dispatch_operation(instr_name)
		self.addr_mode = addr_mode
		self.num_bytes = num_bytes
		self.cycles_string = cycles_string
		self.base_cycles = int(self.cycles_string[:-1])

		self.branched = False

	def execute(self):
		operand_address = self.get_operand_address()
		self.cpu.pc += self.num_bytes
		if operand_address is None:
			self.operation()
		else:
			self.operation(operand_address)
		return self.compute_cycles()

	def get_operand_address(self):
		# TODO: handle JMP bug when address is at page boundary
		if self.addr_mode == 'ACC':
			return A_REG
		elif self.addr_mode == 'ABS':
			return self.read_address()
		elif self.addr_mode == 'ABSX':
			return (self.read_address() + self.cpu.x) & 0xFFFF
		elif self.addr_mode == 'ABSY':
			return (self.read_address() + self.cpu.y) & 0xFFFF
		elif self.addr_mode == 'IMM':
			return (self.cpu.pc + 1) & 0xFFFF
		elif self.addr_mode == 'IMP':
			return None
		elif self.addr_mode == 'IND':
			return self.read_address(self.read_address())
		elif self.addr_mode == 'INDX':
			return self.read_address(self.read_byte() + self.cpu.x, mask=0xFF)
		elif self.addr_mode == 'INDY':
			return (self.read_address(self.read_byte(), mask=0xFF) +
			        self.cpu.y) & 0xFFFF
		elif self.addr_mode == 'REL':
			return self.cpu.pc + self.num_bytes + self.read_byte_signed()
		elif self.addr_mode == 'ZP':
			return self.read_byte()
		elif self.addr_mode == 'ZPX':
			return (self.read_byte() + self.cpu.x) & 0xFF
		elif self.addr_mode == 'ZPY':
			return (self.read_byte() + self.cpu.y) & 0xFF
		else:
			raise ValueError(f'Unknown addressing mode {self.addr_mode}')

	def read_operand_address(self, operand_address):
		if operand_address == A_REG:
			return self.cpu.a
		else:
			return self.cpu.read(operand_address)

	def read_address(self, address=None, mask=0xFFFF):
		if address is None:
			address = self.cpu.pc + 1
		return (self.cpu.read((address + 1) & mask) << 8 +
		        self.cpu.read(address & mask))

	def read_byte(self, address=None, mask=0xFFFF):
		if address is None:
			address = self.cpu.pc + 1
		return self.cpu.read(address & mask)

	def read_byte_signed(self, address=None):
		byte = self.read_byte(address)
		return -1 * (byte & 0x80) + (byte & 0x7F)

	def compute_cycles(self, operand_address):
		if '*' in self.cycles_string:
			if self.branched:
				current_page = self.cpu.pc >> 8
				branch_result_page = (
						(self.cpu.pc + operand_address) & 0x7FFF) >> 8
				different_page = branch_result_page != current_page
				return self.base_cycles + self.branched + different_page
			else:
				return self.base_cycles
		elif '+' in self.cycles_string:
			current_page = self.cpu.pc >> 8
			read_write_page = operand_address >> 8
			different_page = read_write_page != current_page
			return self.base_cycles + different_page
		else:
			return self.base_cycles

	def adc(self, operand_address):
		operand = self.read_operand_address(operand_address)
		self.cpu.a = self.cpu.a + operand + self.cpu.flags.c
		self.cpu.flags.c = self.cpu.a > 0xFF
		self.cpu.a &= 0xFF
		self.cpu.flags.z = self.cpu.a == 0
		self.cpu.flags.n = self.cpu.a >> 7

	def _placeholder(self, *args):
		pass

	def dispatch_operation(self, instr_name):
		return {
			'ADC': self.adc,
			'AND': self._placeholder,
			'ASL': self._placeholder,
			'BCC': self._placeholder,
			'BCS': self._placeholder,
			'BEQ': self._placeholder,
			'BMI': self._placeholder,
			'BNE': self._placeholder,
			'BPL': self._placeholder,
			'BVC': self._placeholder,
			'BVS': self._placeholder,
			'BIT': self._placeholder,
			'BRK': self._placeholder,
			'CLC': self._placeholder,
			'CLD': self._placeholder,
			'CLI': self._placeholder,
			'CLV': self._placeholder,
			'NOP': self._placeholder,
			'PHA': self._placeholder,
			'PLA': self._placeholder,
			'PHP': self._placeholder,
			'PLP': self._placeholder,
			'RTI': self._placeholder,
			'RTS': self._placeholder,
			'SEC': self._placeholder,
			'SED': self._placeholder,
			'SEI': self._placeholder,
			'TAX': self._placeholder,
			'TXA': self._placeholder,
			'TAY': self._placeholder,
			'TYA': self._placeholder,
			'TSX': self._placeholder,
			'TXS': self._placeholder,
			'CMP': self._placeholder,
			'CPX': self._placeholder,
			'CPY': self._placeholder,
			'DEC': self._placeholder,
			'DEX': self._placeholder,
			'DEY': self._placeholder,
			'INX': self._placeholder,
			'INY': self._placeholder,
			'EOR': self._placeholder,
			'INC': self._placeholder,
			'JMP': self._placeholder,
			'JSR': self._placeholder,
			'LDA': self._placeholder,
			'LDX': self._placeholder,
			'LDY': self._placeholder,
			'LSR': self._placeholder,
			'ORA': self._placeholder,
			'ROL': self._placeholder,
			'ROR': self._placeholder,
			'SBC': self._placeholder,
			'STA': self._placeholder,
			'STX': self._placeholder,
			'STY': self._placeholder,
		}[instr_name]


def initialize_instructions(cpu):
	return {opcode: Instruction(opcode) for opcode in opcode_dict}
