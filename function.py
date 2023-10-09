from cmath import *

def f(z: complex) -> complex:
    try:
        # your code here
        # return None when undefined (will show white)
        return z*z
    except ZeroDivisionError | ValueError:
        # Handles division by 0 and log(0)
        return None