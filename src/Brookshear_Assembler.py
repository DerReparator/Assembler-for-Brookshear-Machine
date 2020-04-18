'''Assembler for the Brookshear machine.

This is a module for assembling assembler code compatible to the Brookshear
Machine. http://joeledstrom.github.io/brookshear-emu/
'''
from enum import Enum
from typing import List, Tuple
import sys
	
class OpType(Enum):
	'''The type of the operand's parameter'''
	ZER = 0x0	# Zero (0)
	REG	= 0xF	# Register address
	NIB = 0xF	# Non-restricted Nibble (4 bit)
	ADR = 0xFF	# Address
	

class Op(Enum):
	'''All the available operands in this Brookshear machine model.
	
	Every element of the enumeration is a single operand in this Brookshear
	machine and consists of a tuple with the following elements:
	1. The OpCode in machine code
	2. The OpTypes of the input parameters
	3. The order of the output parameters.
	'''
#	Mnemonic	Opcode	Input-Types								output order
	LOAD 		= (1,	[OpType.REG, OpType.ADR],				[0, 1])
	LOADI 		= (2,	[OpType.REG, OpType.ADR],				[0, 1])
	STORE 		= (3,	[OpType.ADR, OpType.REG],				[1, 0])
	MOVE 		= (4,	[OpType.REG, OpType.REG], 				[OpType.ZER, 1, 0])
	ADD 		= (5,	[OpType.REG, OpType.REG, OpType.REG],	[0, 1, 2])
	ADD_FLOAT 	= (6,	[OpType.REG, OpType.REG, OpType.REG],	[0, 1, 2])
	OR 			= (7,	[OpType.REG, OpType.REG, OpType.REG],	[0, 1, 2])
	AND 		= (8,	[OpType.REG, OpType.REG, OpType.REG],	[0, 1, 2])
	XOR 		= (9,	[OpType.REG, OpType.REG, OpType.REG],	[0, 1, 2])
	ROTATE_RIGHT= (0xA,	[OpType.REG, OpType.NIB],				[0, OpType.ZER, 1])
	JUMP 		= (0xB,	[OpType.ADR, OpType.REG],				[1, 0])
	HALT 		= (0xC,	[],										[OpType.ZER, OpType.ZER, OpType.ZER])

class Assembler:
	'''Assembler for given Brookshear machine model.'''
	commentSymb = ";"
	delimSymb = ","
	
	def __init__(self, code: str):
		self.code = code
		self.output = None
		
	def get_last_translation(self) -> str:
		'''Return the most recently translated program.
		
		If no program was created yet, return null.
		'''
		return self.output
		
	def translate(self) -> str:
		'''Translates the Brookshear Assembly Code to Brookshear Machine code.'''
		self.output = ""
		for num, line in enumerate(self.code.split("\n"), 1):
			print(f"[DEBUG] Processing: #{line}#")
			line = self.__preprocess_line(line)
			# If the line is empty, skip further processing.
			if len(line) == 0:
				continue
			decoded_line = self.__decode_instr(line)
			if not decoded_line[0]:
				# There was an error decoding the instruction... Display error
				# and add notice to output
				print(f"[ERROR] ({num}): {decoded_line[1]}")
				self.output += "[ERR]"
			else:
				# The assembling of the instruction was successful. Add it to
				# the output.
				print(f"[DEBUG] {decoded_line[1]}")
				self.output += decoded_line[1]
				
		return self.output
				
	def __preprocess_line(self, line: str) -> str:
		'''Preprocess a line from the given input.
		
		Strip any leading/trailing whitespace, remove any comments and convert
		all characters to uppercase.
		'''
		return line.strip().split(Assembler.commentSymb)[0].upper()
		
	def __decode_instr(self, line: str) -> Tuple[bool,str]:
		'''Decode a single instruction.
		
		As a first step, a line from the source file is scanned for a known Op-
		Code and handled accordingly.
		Return a tuple whose first element is 'False' if any error occured.
		'''
		print(f"[DEBUG] Decode: #{line}#")
		# A String representation of all available Ops
		op_list = [name for name, member in Op.__members__.items()]
		# HALT Operation needs no space after it
		if line.startswith("HALT"):
			return self.__validate_instr(Op.HALT, line)
		elif len(line.split(" ")) <= 1\
		or line.split(" ")[0].replace("-","_") not in op_list:
			return (False, f"No valid instruction found! - "\
			f"len={len(line.split(' '))}, instr={line.split(' ')[0]}")
		else:
			op = line.split(" ")[0].replace("-","_")
			return self.__validate_instr(Op[op], line)
			
	def __validate_instr(self, op: Op, instr: str) -> Tuple[bool,str]:
		'''Validate a single decoded instruction.
		
		Return a tuple whose first element is 'False' if any error occured.
		'''
		print(f"[DEBUG] Validate: <{op}> #{instr}#")
		# Remove Assembler-OpCode and whitespace
		instr = instr[len(op.name) + 1:].strip()
		expected_no_of_ops = len(op.value[1])
		# Compare length of expected operand list and actual operand list
		if expected_no_of_ops > 0 and\
		expected_no_of_ops != len(instr.split(Assembler.delimSymb)):
			return (False, f"Invalid number of operands for Instr. {op.name}:"\
			f" Expected: {expected_no_of_ops}"\
			f" Got: {len(instr.split(Assembler.delimSymb))}")
		try:
			operands = None
			if expected_no_of_ops > 0:
				operands = [int(x.strip(), 16) for x in instr.split(",")]
			
				# Check if operands are in valid value range
				for limitation, operand in zip(op.value[1], operands):
					if operand > limitation.value:
						return (False, f"Invalid operand (value exceeds range): "\
						f"{operand}")
			# Every validation check was passed. Return successfully
			return (True, self.__encode_instr(op, operands))
		except ValueError as ve:
			return (False, f"Invalid argument value: {str(ve).split(': ')[-1]}")
	
	def __encode_instr(self, op: Op, operands: List[int]) -> str:
		'''Encode/Assemble a single validated instruction.
		
		Return a String consisting of the assembled instruction.
		'''
		print(f"[DEBUG] Encode: <{op}> #{operands}#")
		machine_code = format(op.value[0], "x")
		# Handle the output order of the assembler instructions
		for output in op.value[2]:
			if output == OpType.ZER:
				machine_code += "0"
			else:
				# add the operand with formatting based on its type
				if op.value[1][output] == OpType.ADR:
					machine_code += format(operands[output], "02x")
				else:
					machine_code += format(operands[output], "x")
		return machine_code

if __name__ == '__main__':
	source_file = None
	if len(sys.argv) <= 1:
		source_file = "../test/debug.bin"
	else:
		source_file = sys.argv[1]
	print(f"[INFO] I will assemble {source_file}")
	with open(source_file, "r") as f:
		ass = Assembler(f.read())
		print("Translate: " + ass.translate())
		print("URL:")
		print("http://joeledstrom.github.io/brookshear-emu/#" + ass.get_last_translation())
		#print("Get Translate: " + ass.get_last_translation())