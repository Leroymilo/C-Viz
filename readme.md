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

There are 2 ways to use this tool : in python (slow but easier to write function), or in glsl (verry fast but all complex functions have to be redefined).

### Python

 - Activate the virtual environment (see **Setup**).
 - Write the function you want to plot in `function.py`, the [cmath](https://docs.python.org/3/library/cmath.html) package is imported for access to functions.</br>
 Maths errors should be handled but you should return None when f(z) is not defined to avoid errors.
 - Run `python main.py`

### GLSL

 - Activate the virtual environment (see **Setup**).
 - Write the function you want to plot in `vertex_shader.glsl`, be careful : all operations are replaced with a function (`c_add` for addition, `c_mult` for multiplication, ...) and all usual functions have not been completed (inverse trigonometric functions and hyperbolic functions are wip).</br>
 Values with undefined result should show white on the resulting image.</br>
 There is a tool to convert your expression in glsl shader code :
    - Run `python expression/main.py`
    - Write your expression in the terminal (complete `f(z) = `) (exponentiation is noted with `^` instead of the pythonic `**`).
    - You can use `z`, `x` as `Re(z)`, `y` as `Im(z)`, `r` as `|z|` and `t` as `arg(z)` as variables (instead of having to call functions of `z`).
    - You can use the constants `pi` and `e`.
 - Run `python shaders.py`

This version has zoom (with mouse wheel) and pan (click and drag) support!

## Credits

Most of Pygame OpenGL from [here](https://www.youtube.com/watch?v=LFbePt8i0DI&t=643s) (source code in description).

Shader Code by myself.

Most of the parser code from [here](https://github.com/davidcallanan/py-simple-math-interpreter/tree/master).
I added support for constants, exponent, variables and functions.