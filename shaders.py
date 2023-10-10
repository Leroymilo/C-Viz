import sys
from array import array

import pygame as pg
import moderngl

pg.init()

W, H = 500, 500
X, Y = 0, 0
Z = 1.7
K = 0.2

screen = pg.display.set_mode((W, H), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
ctx = moderngl.create_context()

clock = pg.time.Clock()

quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, -1.0, 1.0,  # topleft
    1.0, 1.0, 1.0, 1.0,   # topright
    -1.0, -1.0, -1.0, -1.0, # bottomleft
    1.0, -1.0, 1.0, -1.0,  # bottomright
]))

with open("vertex_shader.glsl") as f:
    vert_shader = f.read()

with open("fragment_shader.glsl") as f:
    frag_shader = f.read()

program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

def surf_to_texture(surf: pg.Surface):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

def render():
    frame_tex = surf_to_texture(screen)
    frame_tex.use(0)
    params["origin"] = (X, Y)
    params["size"] = (W, H)
    params["scale"] = 10 ** Z
    params["lum_coef"] = K
    for key, value in params.items():
        if key in program:
            program[key] = value
    render_object.render(mode=moderngl.TRIANGLE_STRIP)
    
    pg.display.flip()
    
    frame_tex.release()

def move(start, end):
    global X, Y
    dx, dy = end[0] - start[0], end[1] - start[1]
    X, Y = X - dx, Y + dy
    # y is reversed in screen coordinates

params = {}
mv_start = None

render()

while True:
    screen.fill((255, 255, 255))
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
            
        elif event.type == pg.VIDEORESIZE:
            W, H = event.w, event.h
            render()
        
        elif event.type == pg.MOUSEWHEEL:
            Z += 0.1 * event.y
            render()
        
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mv_start = event.pos
        
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            move(mv_start, event.pos)
            mv_start = None
            render()
        
        elif event.type == pg.MOUSEMOTION and mv_start is not None:
            move(mv_start, event.pos)
            mv_start = event.pos
            render()
    
    clock.tick(60)
    