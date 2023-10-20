from enum import Enum
from dataclasses import dataclass

from expression_parser.constants import Constant
from expression_parser.variables import Variable

class TokenType(Enum):
	NUMBER    	= 0
	CONST		= 1
	VAR			= 2
	PLUS      	= 3
	MINUS     	= 4
	MULTIPLY  	= 5
	DIVIDE    	= 6
	POWER		= 7
	LPAREN    	= 8
	RPAREN    	= 9
	FUNC		= 10

@dataclass
class Token:
	type: TokenType
	value: str | complex | Constant | Variable = None

	def __repr__(self):
		return self.type.name + (f":{self.value}" if self.value != None else "")
