# C-Viz - Complex Function Visualizer

## Use

### Install

Download the executable corresponding to your operating system from the latest release on [this page](https://github.com/Leroymilo/C-Viz/releases).

### Settings

When starting the app, you should have two windows : `Settings` and `Render`.</br>
In the settings window, there's a text field where you can put any complex function, here are some restrictions:
- The case (UPPER or lower) does not matter.
- Exponentiation is noted with `^`.
- You can use `z`, `x` as `Re(z)`, `y` as `Im(z)`, `r` as `|z|` and `t` as `arg(z)` as variables (instead of having to call functions of `z`).
- You can use the constants `i`, `pi` and `e`.
- Most usual complex functions are available: abs (modulus), arg, conj (conjugate), exp, log (natural logarithm), log10, sqrt, sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, asinh, acosh, atanh.

**If there's a mistake in your formula, the function will be treated as f(z) = 1** (error display is WIP)

Below this is the Zoom and position panel.</br>
The position is where you can set the point on which the render will be centered.
This value can also be modified by left-clicking and dragging on the render.</br>
The zoom slider allows to zoom in and out of the center point.
This can also be done by scrolling the mousewheel on the render.</br>
The default zoom and position (where it resets) is on 0, large enough to see the unit circle. 

The style panel allows to change how f(z) is represented :
- The unfolding list allows to change the colormap. This is mostly for aesthetics, but graphic programmers care a lot about okHSL.
- The 2 checkboxes allow to toggle the representation of arg(f(z)) as hue and |f(z)| as luminosity (A color reference is WIP). If arg(f(z)) as hue is disabled, the render will be a grayscale image. It is recommended to disable |f(z)| as luminosity before enabling the style lines described after this.
- The style lines enable a step function on the luminosity depending on different components of f(z). In practice it shows lines on the graph : either the image of the cartesian grid or the image of the polar representation of the plane (lines for constant |z| and constant arg(z)).
- The sliders will change the space between the rendered lines.
 **Note that the image of the unit circle will always be displayed as long as the style lines for |f(z)| are enabled.**


### Controls

 - Mouse wheel to zoom in and out.
 - Left click and drag to move the complex plane.
 - Escape to bring the settings window to front.

## Build

### Required
 - Python 3.10

### Setup
In your terminal:
 - Create python [virtual environment](https://docs.python.org/3/library/venv.html) `python -m venv env`.
 - Activate virtual environment on linux: `source env/bin/activate`, on windows: `env\scripts\activate`.
 - Update pip `pip install --upgrade pip`.
 - Install required libraries `pip install -r requirements`.

### Run

 - Activate the virtual environment (see **Setup**).
 - Run `python main.py`.

### "Build"
In your terminal, with virtual environment activated:
 - Install pyinstaller `pip install pyinstaller`.
 - Run pyinstaller `pyinstaller main.py --onefile --hidden-import glcontext`.

The executable should be in the newly created `dist` folder.</br>
This is not a proper build since python is a scripting language,
but pyinstaller allows for packaging a script with its libraries
and the python interpreter for use without installing python.</br>
Once built, the executable needs to be run in the parent directory of `vertex_shader.glsl` and of the whole folder `fragment_shader` to work properly. like this</br>
```
parent_folder
\  main (or main.exe)
 | vertex_shader.glsl
 | fragment_shader
 | \ ...
```

## Credits

Qt GUI by myself.

Most of the parser code from [here](https://github.com/davidcallanan/py-simple-math-interpreter/tree/master).
I added support for constants, exponent, variables and functions as well as adapting it to print both python and complex glsl formulas (see `fragment_shader/complex.glsl` for details on complex operators and functions).

Most of the colorspace converter code from [here](https://bottosson.github.io/posts/colorpicker/) (thanks Björn).
I had to port from C to glsl.

Shader Code by myself, including redefining complex functions.
