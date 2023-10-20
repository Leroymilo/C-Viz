from cmath import *
from json import load, dump

from expression_parser.nodes import *

def true_phase(z: complex) -> float:
    # result in [0, 2pi]
    p = phase(z)
    if p < 0:
        return p + 2 * pi
    return p

FUNCS: dict[str,callable] = {
	"re": (lambda z: z.real),
    "im": (lambda z: z.imag),
    "conj": (lambda z: z.real - 1j * z.imag),
    "arg": (lambda z: true_phase(z))
} | {
    # direct cmath functions :
    f.__name__: f
    for f in {
        abs, exp, log, log10, sqrt,
        sin, cos, tan, asin, acos, atan,
        sinh, cosh, tanh, asinh, acosh, atanh
    }
}

DEF_FUNCS: dict[str, Node] = {}

def parse_tree(root_dict: dict) -> Node:
    node_type = root_dict["type"]

    kwargs = {
        key: parse_tree(val) if isinstance(val, dict) else val
        for key, val in root_dict.items()
        if key != "type"
    }

    return eval(node_type)(**kwargs)

def dump_function(func_tree: Node):return {
        "type": func_tree.__class__.__name__
    } | {
        key: dump_function(value) if isinstance(value, Node) else value
        for key, value in func_tree.__dict__.items()
    }

def read_defined_functions():
    with open("functions.json", 'r') as f:
        functions: dict[str, dict] = load(f)
    
    for name, data in functions.items():
        base_node: dict[str, str | int | dict] = data["tree"]
        DEF_FUNCS[name] = parse_tree(base_node)

def save_function(func_name: str, func_tree: Node):
    with open("functions.json", 'rw') as f:
        functions: dict[str, dict] = load(f)
        functions[func_name] = dump_function(func_tree)
        dump(function, f)

def remove_function(function_name: str):
    with open("functions.json", 'rw') as f:
        functions: dict[str, dict] = load(f)
        functions.pop(function_name)
        dump(function, f)

def replace_var(func_tree: Node, param_tree: Node):

    kwargs = {}
    for key, value in func_tree.__dict__.items():
        if isinstance(value, VariableNode) and value.value == 'z':
            kwargs[key] = param_tree
        elif isinstance(value, Node):
            kwargs[key] = replace_var(value, param_tree)
        else:
            kwargs[key] = value
    
    return func_tree.__class__(**kwargs)