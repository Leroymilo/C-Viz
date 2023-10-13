from enum import Enum
from dataclasses import dataclass

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
	value: str | complex = None

	def __repr__(self):
		return self.type.name + (f":{self.value}" if self.value != None else "")
