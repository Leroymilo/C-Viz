# C-Viz - Complex Function Visualizer

## Required
 - [Python 3.10](https://www.python.org/downloads/)

## Setup
In your terminal :
 - Create python [virtual environment](https://docs.python.org/3/library/venv.html) `python -m venv env`
 - Activate virtual environment on linux : `source env/bin/activate`, on windows : `env\scripts\activate`
 - Update pip `pip install --upgrade pip`
 - Install required libraries `pip install -r requirements`

## Usage

 - Activate the virtual environment (see **Setup**).
 - Run `python main.py`.
 - Write the function you want to plot in `function.txt`, here are some pointers :
    - The case (UPPER or Lower) does not matter.
    - Exponentiation is noted with `^`.
    - You can use `z`, `x` as `Re(z)`, `y` as `Im(z)`, `r` as `|z|` and `t` as `arg(z)` as variables (instead of having to call functions of `z`).
    - You can use the constants `i`, `j`, `pi` and `e`.
    - Most usual complex functions are available : abs (modulus), arg, conj (conjugate), exp, log (natural logarithm), log10, sqrt, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh

### Controls :

 - Mouse wheel to zoom in and out.
 - Left click and drag to move the complex plane.
 - Space bar to reset zoom and position.
 - Return (new line key) to reload the function
 - Right click to cycle color maps (HSL, okHSL)

## Credits

Most of Pygame OpenGL from [here](https://www.youtube.com/watch?v=LFbePt8i0DI&t=643s) (source code in description).

Shader Code by myself.

Most of the parser code from [here](https://github.com/davidcallanan/py-simple-math-interpreter/tree/master).
I added support for constants, exponent, variables and functions.