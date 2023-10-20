from dataclasses import dataclass
from cmath import pi, exp


@dataclass
class Constant:
    name: str
    eval_: complex
    glsl: str
    latex: str
    desc: str

    def __repr__(self) -> str:
        return self.name


CONSTS = {
    "i": Constant("i", 1j, "complex(0, 1)", "i",
        "$i$ is the imaginary number such that $i^2 = -1$."),
    "j": Constant("j", -0.5+1j*(3**0.5)/2, "complex(-0.5, sqrt(3)/2)", "j",
        "$j = e^{i \\frac{2 \\pi}{3}}$."),
    "pi": Constant("pi", pi, "complex(pi, 0)", "\\pi", "$\\pi$."),
    "e": Constant("e", exp(1), "complex(e, 0)", "e", "$e$.")
}