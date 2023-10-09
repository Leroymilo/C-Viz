from cmath import *
from function import f

import pygame as pg

screen = pg.display.set_mode((500, 500), pg.RESIZABLE)

i = 1j

X, Y = 0, 0
W, H = screen.get_width(), screen.get_height()
M = 5   # zoom factor
X0, Y0 = X-W/(2*M), Y-H/(2*M)

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
    return 1 - e**(-lum)

def hl_to_rgb( h:float, l:float ) -> pg.Color:
    if h == 1.0: h = 0.0
    i = int(h*6.0)
    f = h*6.0 - i
    
    w = 0
    q = int(255 * l * (1.0 - f))
    t = int(255 * l * (1.0 - (1.0 - f)))
    l = int(255 * l)

    if i==0: return pg.Color(l, t, w)
    if i==1: return pg.Color(q, l, w)
    if i==2: return pg.Color(w, l, t)
    if i==3: return pg.Color(w, q, l)
    if i==4: return pg.Color(t, w, l)
    if i==5: return pg.Color(l, w, q)

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
                max_l = max(max_l, l)
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
