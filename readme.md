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
 - Write the function you want to plot in function.py, the [cmath](https://docs.python.org/3/library/cmath.html) package is imported for access to functions.</br>
 Maths errors should be handled but you should return None when f(z) is not defined to avoid errors.
 - Activate the virtual environment (see **Setup**)
 - Run `python main.py`
