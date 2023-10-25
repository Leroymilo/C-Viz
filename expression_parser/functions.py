from cmath import *
from json import load, dump
from typing import Callable, Sequence

from expression_parser.nodes import *

TYPES = {complex: 'z', float: 'x', int: 'n'}

@dataclass
class Function:
    name: str
    func: Callable
    arg_types: Sequence[type]
    ret_type: type
    desc: str

    def get_args(self) -> tuple[str]:
        if hasattr(self, "arg_names"):
            return self.arg_names
        
        CNT = {
            type_: self.arg_types.count(type_)
            for type_ in TYPES
        }

        i_t = {type_: 1 for type_ in TYPES}

        args = []

        for type_arg in self.arg_types:
            for type_, var in TYPES.items():
                if type_arg is not type_: continue
                if CNT[type_] > 1:
                    var += '_' + str(i_t[type_])
                    i_t[type_] += 1
                args.append(var)
                break
        
        self.arg_names = tuple(args)
        return self.arg_names

    def __repr__(self) -> str:
        return f"{self.name}({", ".join(self.get_args())}) -> {self.ret_type.__name__}"

    def eval(self, *args):
        return self.func(*args)
    
    def get_desc(self):
        return self.desc

@dataclass
class CustomFunction:
    name: str
    func: Node
    arg_types: Sequence[type]
    ret_types: type
    desc: str

def true_phase(z: complex) -> float:
    # result in [0, 2pi]
    p = phase(z)
    if p < 0:
        return p + 2 * pi
    return p

def real(z: complex) -> float:
    """Return the real part of z."""
    return z.real

def imag(z: complex) -> float:
    """Return the imaginary part of z."""
    return z.imag

def conj(z: complex) -> complex:
    """Return the conjugate of z (i.e. $Re(z) - i\\cdot Im(z)$)."""
    return z.conjugate()

def exp_(z: complex) -> complex:
    "Return the exponential value $e^z$."
    return exp(z)

true_phase.__doc__ = phase.__doc__ + " The result will be in $[0, 2π[$."

FUNCS: dict[str,callable] = {
	"re": real,
    "im": imag,
    "conj": conj,
    "arg": true_phase,
    "exp": exp_
} | {
    # direct cmath functions :
    f.__name__: f
    for f in {
        abs, log, log10, sqrt,
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