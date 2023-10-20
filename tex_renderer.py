from matplotlib import use
import matplotlib.pyplot as plt

use("tkagg")    # avoids Segfault on Fedora for some reason

plt.rcParams["mathtext.fontset"] = "cm" # Chooses a nice font for the rendered text
fig = plt.figure()
r = fig.canvas.get_renderer()

def render_tex(expression: str, file_name: str, size: int = 12):
    # expression is a string containing any text to allow mixed renders (text and LateX),
    # to render LateX make sure to put it in-between 2 `$` characters.

    fig.clf()
    plt.axis("off")

    # change parameters here for centering and text size
    text = fig.text(0.5, 0.5, f"{expression}", size=size, ha="center", va="center")

    # Crops the render to fit text
    bb = text.get_window_extent(renderer=r)
    q = 110
    fig.set_size_inches(bb.width/q, bb.height/q)

    plt.draw()

    plt.savefig(file_name, format="png", bbox_inches='tight', dpi=100)
    # did not manage to save to BytesIO, Pillow wants a path