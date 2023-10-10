from cmath import *

FUNCS: dict[str,callable] = {
	"re": (lambda z: z.real),
    "im": (lambda z: z.imag),
    "arg": (lambda z: phase(z) + pi)    # result in [0, 2pi]
} | {
    # direct cmath functions :
    f.__name__: f
    for f in {
        abs, exp, log, log10, sqrt,
        cos, sin, tan, acos, asin, atan,
        cosh, sinh, tanh, acosh, asinh, atanh
    }
}