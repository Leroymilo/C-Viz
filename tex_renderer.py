from io import FileIO
import matplotlib.pyplot as plt

plt.rcParams["mathtext.fontset"] = "cm"
plt.axis("off")

def render_tex(expression: str, file: FileIO):
    plt.clf()

    plt.text(0.5, 0.5, f"${expression}$", size=50, ha="center", va="center")                                      
    plt.draw()

    plt.savefig(file, format="png", bbox_inches='tight', dpi=100)