from cmath import *

from lexer import Lexer
from parser_ import Parser
from functions import FUNCS
from nodes import *

def parse_expression(expression: str) -> Node:
    return Parser(Lexer(expression).generate_tokens()).parse()

def simplify_tree(tree: Node, strength: int = 0) -> Node:
    # If strength == 0: NumberNodes will be merged by operations and functions.
    # If strength == 1: ConstantNodes will be merged too.

    to_merge = NumberNode
    if strength == 1: to_merge = LiteralNode

    # no simplification
    if isinstance(tree, LiteralNode) or isinstance(tree, VariableNode):
        return tree
    
    # simplifying operations
    if isinstance(tree, OperationNode):
        tree.node_a = simplify_tree(tree.node_a, strength)
        tree.node_b = simplify_tree(tree.node_b, strength)
        if isinstance(tree.node_a, to_merge) and isinstance(tree.node_b, to_merge):
            return NumberNode(eval(str(tree)))
    
        return tree

    if isinstance(tree, FunctionNode):
        tree.node = simplify_tree(tree.node, strength)
        if isinstance(tree.node, to_merge):
            return NumberNode(FUNCS[tree.name](eval(str(tree.node))))


if __name__ == "__main__":
    while True:
        try:
            expression = input("f(z) = ")
            tokens = [token for token in Lexer(expression).generate_tokens()]
            # print(*tokens)
            tree = Parser(tokens).parse()
            print("Verify your expression in python :", tree)
            tree = simplify_tree(tree, 1)
            print("GLSL translation to use in shader :", tree.glsl())

        except Exception as e:
            print(e)
            continue
        break