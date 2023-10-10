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

 - Write the function you want to plot in `function.py`, the [cmath](https://docs.python.org/3/library/cmath.html) package is imported for access to functions.</br>
 Maths errors should be handled but you should return None when f(z) is not defined to avoid errors.
 - Activate the virtual environment (see **Setup**).
 - Run `python main.py`

### GLSL

 - Write the function you want to plot in `vertex_shader.glsl`, be careful : all operations need to be redefined from scratch, a few are already done (mult, add, div), but anything else needs to be remade.</br>
 Values with undefined result should show white on the resulting image.
 - Activate the virtual environment (see **Setup**).
 - Run `python shaders.py`

This version has zoom (with mouse wheel) and pan (click and drag) support!

## Credits

Most of Pygame OpenGL from [here](https://www.youtube.com/watch?v=LFbePt8i0DI&t=643s) (source code in description).

Shader Code by myself.

Most of the parser code from [here](https://github.com/davidcallanan/py-simple-math-interpreter/tree/master).
I added support for constants, exponent, variables and functions.