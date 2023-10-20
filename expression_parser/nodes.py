from dataclasses import dataclass
from abc import ABC, abstractmethod

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
# 	from expression_parser.variables import Variable
from expression_parser.constants import Constant

@dataclass
class Node(ABC):
	@abstractmethod
	def glsl(self) -> str:
		pass

	@abstractmethod
	def tex(self) -> str:
		pass

	@abstractmethod
	def __repr__(self) -> str:
		pass

@dataclass
class VariableNode(Node):
	value: str # | Variable

	def glsl(self) -> str:
		if isinstance(self.value, str):
			return self.value
		return self.value.subtree.glsl()
	
	def tex(self) -> str:
		if isinstance(self.value, str):
			return self.value
		return self.value.latex
	
	def __repr__(self) -> str:
		return self.value.name

@dataclass
class LiteralNode(Node):
	value: complex | Constant
	
	def __repr__(self) -> str:
		return str(self.value)

@dataclass
class NumberNode(LiteralNode):
	value: complex

	def glsl(self) -> str:
		return f"complex({self.value.real}, {self.value.imag})"
	
	def tex(self) -> str:
		if self.value == 0:
			return '0'
	
		real, imag = self.value.real, self.value.imag
		if imag == 0:
			return str(real)
		if imag == 1:
			imag = 'i'
		else:
			imag = f"{imag}i"
		return f"{real} + {imag}"

	def __repr__(self) -> str:
		return super().__repr__()

@dataclass
class ConstantNode(LiteralNode):
	value: Constant

	def glsl(self):
		return self.value.glsl
	
	def tex(self):
		return self.value.latex

	def __repr__(self) -> str:
		return super().__repr__()

@dataclass
class OperationNode(Node):
	node_a: Node
	node_b: Node

@dataclass
class AddNode(OperationNode):
	node_a: Node
	node_b: Node

	def glsl(self) -> str:
		return f"c_add({self.node_a.glsl()}, {self.node_b.glsl()})"
	
	def tex(self) -> str:
		return f"({self.node_a.tex()} + {self.node_b.tex()})"
	
	def __repr__(self) -> str:
		return f"({self.node_a} + {self.node_b})"

@dataclass
class SubtractNode(OperationNode):
	node_a: Node
	node_b: Node

	def glsl(self) -> str:
		return f"c_sub({self.node_a.glsl()}, {self.node_b.glsl()})"
	
	def tex(self) -> str:
		return f"({self.node_a.tex()} - {self.node_b.tex()})"
	
	def __repr__(self) -> str:
		return f"({self.node_a} - {self.node_b})"

@dataclass
class MultiplyNode(OperationNode):
	node_a: Node
	node_b: Node

	def glsl(self) -> str:
		return f"c_mult({self.node_a.glsl()}, {self.node_b.glsl()})"
	
	def tex(self) -> str:
		return f"{{{self.node_a.tex()}}} \\cdot {{{self.node_b.tex()}}}"
	
	def __repr__(self) -> str:
		return f"({self.node_a} * {self.node_b})"

@dataclass
class DivideNode(OperationNode):
	node_a: Node
	node_b: Node

	def glsl(self) -> str:
		return f"c_div({self.node_a.glsl()}, {self.node_b.glsl()})"
	
	def tex(self) -> str:
		return f"\\frac{{{self.node_a.tex()}}} {{{self.node_b.tex()}}}"
	
	def __repr__(self) -> str:
		return f"({self.node_a} / {self.node_b})"

@dataclass
class PowerNode(OperationNode):
	node_a: Node
	node_b: Node

	def glsl(self) -> str:
		return f"c_pow({self.node_a.glsl()}, {self.node_b.glsl()})"
	
	def tex(self) -> str:
		return f"{{{self.node_a.tex()}}}^{{{self.node_b.tex()}}}"
	
	def __repr__(self) -> str:
		return f"({self.node_a} ** {self.node_b})"

@dataclass
class FunctionNode(Node):
	name: str
	node: Node
	
	def glsl(self) -> str:
		return f"c_{self.name}({self.node.glsl()})"
	
	def tex(self) -> str:
		return f"{self.name}({{{self.node.tex()}}})"
	
	def __repr__(self) -> str:
		return f"{self.name}({self.node})"
