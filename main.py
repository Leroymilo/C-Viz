from cmath import *
from function import f

import pygame as pg

screen = pg.display.set_mode((500, 500), pg.RESIZABLE)

i = 1j

X, Y = 0, 0
W, H = screen.get_width(), screen.get_height()
M = 50   # zoom factor
X0, Y0 = X-W/(2*M), Y-H/(2*M)
K = 0.2

def resize() -> None:
    global W
    global H
    W, H = screen.get_width(), screen.get_height()

    global X0
    global Y0
    X0, Y0 = X-W/(2*M), Y-H/(2*M)

def map_xy2z(x: int, y: int) -> complex:
    return (X0 + x/M) + i * (Y0 + y/M)

def remap_lum(lum: float) -> float:
    # maps [0,+inf[ into [0, 1[
    return 1 - e**(-K * lum)

def hl_to_rgb( h:float, l:float ) -> pg.Color:
    c = 1 - abs(2*l - 1)
    h1 = h*6
    x = c * (1 - abs(h1%2 - 1))
    i = int(h1)%6

    if i==0: r, g, b = c, x, 0
    if i==1: r, g, b = x, c, 0
    if i==2: r, g, b = 0, c, x
    if i==3: r, g, b = 0, x, c
    if i==4: r, g, b = x, 0, c
    if i==5: r, g, b = c, 0, x

    m = l - c/2
    return pg.Color(*map(lambda v: int((v+m)*255), (r, g, b)))

def update():
    max_l = 0
    for x in range(W):
        for y in range(H):
            z = f(map_xy2z(x, y))
            if not z:
                color = pg.Color(0, 0, 0, 0)
            else:
                h = phase(z)/(2*pi) + 0.5
                l = remap_lum(abs(z))
                color = hl_to_rgb(h, l)
            screen.set_at((x, y), color)
    # print("max l :", max_l)
    print("finished frame")
    pg.display.flip()

if __name__ == "__main__":
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            elif event.type == pg.VIDEORESIZE:
                resize()
                update()

            elif event.type == pg.VIDEOEXPOSE:  # handles window minimising/maximising
                resize()
                update()
