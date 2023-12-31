from expression_parser.tokens import Token, TokenType
from expression_parser.nodes import *
from expression_parser.functions import FUNCS, DEF_FUNCS, replace_var

class Parser:
	def __init__(self, tokens):
		self.tokens = iter(tokens)
		self.current_token: Token
		self.advance()

	def raise_error(self):
		raise Exception("Invalid syntax")
	
	def advance(self):
		try:
			self.current_token = next(self.tokens)
		except StopIteration:
			self.current_token = None

	def parse(self):
		if self.current_token == None:
			return None

		try:
			result = self.expr()
		except Exception as e:
			self.raise_error()

		if self.current_token != None:
			self.raise_error()

		return result

	def expr(self):
		result = self.exponent()

		while self.current_token != None and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
			if self.current_token.type == TokenType.PLUS:
				self.advance()
				result = AddNode(result, self.exponent())
			elif self.current_token.type == TokenType.MINUS:
				self.advance()
				result = SubtractNode(result, self.exponent())

		return result

	def exponent(self):
		result = self.term()

		while self.current_token != None and self.current_token.type in {TokenType.MULTIPLY, TokenType.DIVIDE}:
			if self.current_token.type == TokenType.MULTIPLY:
				self.advance()
				result = MultiplyNode(result, self.term())
			elif self.current_token.type == TokenType.DIVIDE:
				self.advance()
				result = DivideNode(result, self.term())
				
		return result

	def term(self):
		result = self.factor()

		while self.current_token != None and self.current_token.type == TokenType.POWER:
			self.advance()
			result = PowerNode(result, self.factor())
				
		return result

	def factor(self):
		token: Token = self.current_token

		if token.type == TokenType.FUNC:
			self.advance()

			args = []

			if self.current_token.type != TokenType.LPAREN:
				self.raise_error()
			self.advance()

			while self.current_token.type != TokenType.RPAREN:
				args.append(self.expr())
				
				if self.current_token.type not in {TokenType.RPAREN, TokenType.COMA}:
					self.raise_error()

				if self.current_token.type == TokenType.COMA:
					self.advance()
			self.advance()

			# TODO : handle multiple variable functions

			if token.value not in FUNCS.keys():
				# custom defined function, replace var with result node
				return replace_var(DEF_FUNCS[token.value], args[0])
			
			# built in function
			return FunctionNode(token.value, args[0])

		if token.type == TokenType.LPAREN:
			self.advance()
			result = self.expr()

			if self.current_token.type != TokenType.RPAREN:
				self.raise_error()
			
			self.advance()
			return result
		
		if token.type == TokenType.CONST:
			self.advance()
			return ConstantNode(token.value)

		if token.type == TokenType.NUMBER:
			self.advance()
			return NumberNode(token.value)
		
		if token.type == TokenType.VAR:
			self.advance()
			return VariableNode(token.value)

		if token.type == TokenType.PLUS:
			self.advance()
			return self.factor()
		
		if token.type == TokenType.MINUS:
			self.advance()
			return MultiplyNode(NumberNode(-1), self.factor())
		
		self.raise_error()
