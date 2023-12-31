from cmath import pi, exp

from expression_parser.constants import CONSTS
from expression_parser.variables import VARS
from expression_parser.tokens import Token, TokenType
from expression_parser.functions import FUNCS, DEF_FUNCS

WHITESPACE = " \n\t"
DIGITS = "0123456789"
CHARS = "abcdefghijklmnopqrstuvwxyz_ρθ"

SIMPLETOKENS = {
	'+': TokenType.PLUS,
	'-': TokenType.MINUS,
	'*': TokenType.MULTIPLY,
	'/': TokenType.DIVIDE,
	'^': TokenType.POWER,
	'(': TokenType.LPAREN,
	')': TokenType.RPAREN,
	',': TokenType.COMA
}

class Lexer:
	def __init__(self, text: str):
		self.text = iter(text.lower())
		self.advance()

	def advance(self):
		try:
			self.current_char = next(self.text)
		except StopIteration:
			self.current_char = None

	def generate_tokens(self):
		while self.current_char is not None:
			if self.current_char in WHITESPACE:
				self.advance()
			elif self.current_char == '.' or self.current_char in DIGITS:
				yield self.generate_number()
			elif self.current_char in CHARS:
				yield self.generate_str()
			else:
				for char, token_type in SIMPLETOKENS.items():
					if self.current_char == char:
						yield Token(token_type)
						self.advance()
						break
				else:
					raise Exception(f"Illegal character '{self.current_char}'")

	def generate_number(self):
		decimal_point_count = 0
		number_str = self.current_char
		self.advance()

		while self.current_char is not None and (self.current_char == '.' or self.current_char in DIGITS):
			if self.current_char == '.':
				decimal_point_count += 1
				if decimal_point_count > 1:
					break
			
			number_str += self.current_char
			self.advance()

		if number_str.startswith('.'):
			number_str = '0' + number_str
		if number_str.endswith('.'):
			number_str += '0'

		return Token(TokenType.NUMBER, float(number_str))

	def generate_str(self):
		# generates a function token or a variable token
		string = self.current_char
		self.advance()

		while self.current_char is not None and self.current_char in CHARS + DIGITS:
			string += self.current_char
			self.advance()

		if string in CONSTS.keys():
			return Token(TokenType.CONST, CONSTS[string])
		if string in VARS.keys():
			return Token(TokenType.VAR, VARS[string])
		if string in FUNCS.keys() | DEF_FUNCS.keys():
			return Token(TokenType.FUNC, string)
		raise Exception(f"Unknown function or constant: \"{string}\"")