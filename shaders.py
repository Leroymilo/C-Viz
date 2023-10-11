import sys
from array import array

import pygame as pg
import pygame_gui as pgg
import moderngl


# Parameters (TODO : put all this in a class some day)

MINW, MINH = 500, 500
W, H = 500, 500
X, Y = 0, 0
Z = 1.7
K = 0.2


# Pygame Init

pg.init()
screen = pg.display.set_mode((W, H), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
gui_surf = pg.Surface((W, H), pg.RESIZABLE)
clock = pg.time.Clock()
manager = pgg.UIManager((W, H))
hello_button = pgg.elements.UIButton(
    relative_rect=pg.Rect((350, 275), (100, 50)),
    text='Say Hello',
    manager=manager)


# ModernGL Init

ctx = moderngl.create_context()
quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, -1.0, 1.0,   # topleft
    1.0, 1.0, 1.0, 1.0,     # topright
    -1.0, -1.0, -1.0, -1.0, # bottomleft
    1.0, -1.0, 1.0, -1.0,   # bottomright
]))


# Shader functions

def compile() -> tuple[moderngl.Program, moderngl.VertexArray]:
    with open("vertex_shader.glsl") as f:
        vert_shader = f.read()

    with open("fragment_shader.glsl") as f:
        frag_shader = f.read()

    program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
    render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])
    return program, render_object

def surf_to_texture(surf: pg.Surface):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

def render(program: moderngl.Program, render_object: moderngl.VertexArray):
    screen.fill((255, 255, 255))

    render_ui()
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


def render_ui():
    manager.draw_ui(screen)


# User Actions

def move(start, end):
    global X, Y
    scale = 10 ** Z
    dx, dy = (end[0] - start[0]) / scale, (end[1] - start[1]) / scale
    X, Y = X - dx, Y + dy
    # y is reversed in screen coordinates


def resize(new_w, new_h):
    global W, H
    global screen, render_surf, manager
    W = max(MINW, new_w)
    H = max(MINH, new_h)
    screen = pg.display.set_mode((W, H), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
    manager.set_window_resolution((W, H))


if __name__ == "__main__":

    program, render_object = compile()

    params = {}
    mv_start = None
    updated = True

    while True:
        time_delta = clock.tick(60)/1000.0
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
                
            elif event.type == pg.VIDEORESIZE:
                resize(event.w, event.h)
                updated = True
            
            elif event.type == pg.MOUSEWHEEL:
                Z += 0.1 * event.y
                updated = True
            
            elif event.type == pgg.UI_BUTTON_PRESSED:
                if event.ui_element == hello_button:
                    print('Hello World!')
            
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mv_start = event.pos
            
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                move(mv_start, event.pos)
                mv_start = None
                updated = True
            
            elif event.type == pg.MOUSEMOTION and mv_start is not None:
                move(mv_start, event.pos)
                mv_start = event.pos
                updated = True
            
            manager.process_events(event)
        
        manager.update(time_delta)


        if updated:
            render(program, render_object)
            updated = False