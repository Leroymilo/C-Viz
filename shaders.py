import sys
from array import array

import pygame as pg
import moderngl

pg.init()

screen = pg.display.set_mode((800, 600), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
display = pg.Surface((800, 600))
ctx = moderngl.create_context()

clock = pg.time.Clock()

quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0,  # topleft
    1.0, 1.0, 1.0, 0.0,   # topright
    -1.0, -1.0, 0.0, 1.0, # bottomleft
    1.0, -1.0, 1.0, 1.0,  # bottomright
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

def resize():
    pass

def render():
    frame_tex = surf_to_texture(display)
    frame_tex.use(0)
    params["origin"] = (0, 0)
    params["size"] = screen.get_size()
    params["scale"] = 100
    params["lum_coef"] = 0.2
    for key, value in params.items():
        if key in program:
            program[key] = value
    render_object.render(mode=moderngl.TRIANGLE_STRIP)
    
    pg.display.flip()
    
    frame_tex.release()
    print("rendered")

params = {}

while True:
    display.fill((255, 255, 255))
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
            
        elif event.type == pg.VIDEORESIZE:
            resize()
            render()

        elif event.type == pg.VIDEOEXPOSE:  # handles window minimising/maximising
            resize()
            render()
    
    clock.tick(60)
    