import sys
from array import array

import pygame as pg
import moderngl

from expression.main import parse_expression, simplify_tree

# Parameters (TODO : put all this in a class some day)

MINW, MINH = 500, 500
W, H = 800, 500
X, Y = 0, 0
Z = 1.7


# Pygame Init

pg.init()
screen = pg.display.set_mode((W, H), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
clock = pg.time.Clock()


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

    with open("function.txt") as f:
        expression = f.read().lower()
    
    tree = parse_expression(expression)
    glsl_expression = simplify_tree(tree, 1).glsl()
    with open("fragment_shader.glsl") as f:
        frag_shader = f.read().replace("FUNCTION", glsl_expression)

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
    # frame_tex = surf_to_texture(gui_surf)
    # frame_tex.use(0)
    
    params["origin"] = (X, Y)
    params["size"] = (W, H)
    params["scale"] = 10 ** Z
    for key, value in params.items():
        if key in program:
            program[key] = value
    
    render_object.render(mode=moderngl.TRIANGLE_STRIP)
    pg.display.flip()
    # frame_tex.release()


# User Actions

def move(start, end):
    global X, Y
    scale = 10 ** Z
    dx, dy = (end[0] - start[0]) / scale, (end[1] - start[1]) / scale
    X, Y = X - dx, Y + dy
    # y is reversed in screen coordinates


def resize(new_w, new_h):
    global W, H
    global screen
    # Cannot limit resize for some reason : pg.display.set_mode janks out
    # W = max(MINW, new_w)
    # H = max(MINH, new_h)
    # screen = pg.display.set_mode((W, H), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE
    W, H = new_w, new_h


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
                resize(*event.size)
                updated = True
            
            elif event.type == pg.MOUSEWHEEL:
                Z += 0.1 * event.y
                updated = True
            
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
            
            elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                program, render_object = compile()
                updated = True
            
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                X, Y = 0, 0
                Z = 1.7
                updated = True

        if updated:
            render(program, render_object)
            updated = False