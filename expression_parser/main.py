from cmath import *

from expression_parser.lexer import Lexer
from expression_parser.parser_ import Parser
from expression_parser.functions import FUNCS
from expression_parser.nodes import *

def parse_expression(expression: str) -> Node:
    return Parser(Lexer(expression).generate_tokens()).parse()

def simplify_tree(tree: Node) -> Node:
    # If strength == 0: NumberNodes will be merged by operations and functions.
    # If strength == 1: ConstantNodes will be merged too.

    to_merge = LiteralNode

    # no simplification
    if isinstance(tree, LiteralNode) or isinstance(tree, VariableNode):
        return tree
    
    # simplifying operations
    if isinstance(tree, OperationNode):
        a = simplify_tree(tree.node_a)
        b = simplify_tree(tree.node_b)
        new_tree = tree.__class__(a, b)
        if isinstance(a, to_merge) and isinstance(b, to_merge):
            return NumberNode(eval(str(new_tree)))
    
        return new_tree

    # simplifying functions
    if isinstance(tree, FunctionNode):
        a = simplify_tree(tree.node)
        new_tree = tree.__class__(tree.name, a)
        if isinstance(a, to_merge):
            return NumberNode(FUNCS[new_tree.name](eval(str(new_tree.node))))
        
        return new_tree
    
    return tree


if __name__ == "__main__":
    while True:
        try:
            expression = input("f(z) = ")
            tokens = [token for token in Lexer(expression).generate_tokens()]
            # print(*tokens)
            tree = Parser(tokens).parse()
            print("Verify your expression in python :", tree)
            tree = simplify_tree(tree)
            print("GLSL translation to use in shader :", tree.glsl())

        except Exception as e:
            print(e)
            continue
        break