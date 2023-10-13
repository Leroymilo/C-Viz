from cmath import *

FUNCS: dict[str,callable] = {
	"re": (lambda z: z.real),
    "im": (lambda z: z.imag),
    "conj": (lambda z: z.real - 1j * z.imag),
    "arg": (lambda z: phase(z) + pi)    # result in [0, 2pi]
} | {
    # direct cmath functions :
    f.__name__: f
    for f in {
        abs, exp, log, log10, sqrt,
        sin, cos, tan, asin, acos, atan,
        sinh, cosh, tanh, asinh, acosh, atanh
    }
}