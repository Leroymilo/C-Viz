from dataclasses import dataclass
from abc import ABC, abstractclassmethod

@dataclass
class Node(ABC):
	@abstractclassmethod
	def glsl(self) -> str:
		pass

	@abstractclassmethod
	def __repr__(self) -> str:
		pass

@dataclass
class VariableNode(Node):
	def glsl(self) -> str:
		return 'z'
	
	def __repr__(self) -> str:
		return 'z'

@dataclass
class LiteralNode(Node):
	value: complex | str

@dataclass
class NumberNode(LiteralNode):
	value: complex

	def glsl(self) -> str:
		return f"complex({self.value.real}, {self.value.imag})"
	
	def __repr__(self) -> str:
		return f"{self.value}"

@dataclass
class ConstantNode(LiteralNode):
	value: str

	def glsl(self) -> str:
		return self.value

	def __repr__(self) -> str:
		return self.value

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
	
	def __repr__(self) -> str:
		return f"({self.node_a} + {self.node_b})"

@dataclass
class SubtractNode(OperationNode):
	node_a: Node
	node_b: Node

	def glsl(self) -> str:
		return f"c_sub({self.node_a.glsl()}, {self.node_b.glsl()})"
	
	def __repr__(self) -> str:
		return f"({self.node_a} - {self.node_b})"

@dataclass
class MultiplyNode(OperationNode):
	node_a: Node
	node_b: Node

	def glsl(self) -> str:
		return f"c_mult({self.node_a.glsl()}, {self.node_b.glsl()})"
	
	def __repr__(self) -> str:
		return f"({self.node_a} * {self.node_b})"

@dataclass
class DivideNode(OperationNode):
	node_a: Node
	node_b: Node

	def glsl(self) -> str:
		return f"c_div({self.node_a.glsl()}, {self.node_b.glsl()})"
	
	def __repr__(self) -> str:
		return f"({self.node_a} / {self.node_b})"

@dataclass
class PowerNode(OperationNode):
	node_a: Node
	node_b: Node

	def glsl(self) -> str:
		return f"c_pow({self.node_a.glsl()}, {self.node_b.glsl()})"
	
	def __repr__(self) -> str:
		return f"({self.node_a} ** {self.node_b})"

@dataclass
class FunctionNode:
	name: str
	node: Node
	
	def glsl(self) -> str:
		return f"c_{self.name}({self.node.glsl()})"
	
	def __repr__(self) -> str:
		return f"{self.name}({self.node})"
