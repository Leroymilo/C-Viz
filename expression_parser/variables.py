from dataclasses import dataclass

from expression_parser.nodes import Node, VariableNode, FunctionNode


@dataclass
class Variable:
    name: str
    latex: str
    subtree: Node
    desc: str

    def __repr__(self) -> str:
        return self.name


VARS = {
    "z": Variable(
        "z", "$z$",
        VariableNode("z"),
        "The main variable of the function."
    ),
    "t": Variable(
        "t", "$t$",
        VariableNode("t"),
        "A time variable constantly increasing with time (in seconds)."
    ),
    "x": Variable(
        "x", "$x$",
        FunctionNode("re", VariableNode("z")),
        "The real part of z ($z = x + i y$)."
    ),
    "y": Variable(
        "y", "$y$",
        FunctionNode("im", VariableNode("z")),
        "The imaginary part of z ($z = x + i y$)."
    ),
    "ρ": Variable(
        "ρ", "$\\rho$",
        FunctionNode("abs", VariableNode("z")),
        "The modulus, or absolute value of z ($z = \\rho e^{i \\theta}$)."
    ),
    "θ": Variable(
        "θ", "$\\theta$",
        FunctionNode("arg", VariableNode("z")),
        "The argument of z ($z = \\rho e^{i \\theta}$)."
    )
}