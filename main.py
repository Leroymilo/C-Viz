#!/usr/bin/env python3

from enum import Enum
from array import array

import PyQt5.QtGui as QtGui
from PyQt5.QtCore import QPointF, QSize, Qt
from PyQt5.QtWidgets import QApplication

import moderngl

from expression.main import parse_expression, simplify_tree

class ColorMap(Enum):
    HSL = 0
    OKLCh = 1


class MinimalGLWidget(QtGui.QOpenGLWindow):
    def __init__(self):
        super().__init__()
        self.setWidth(800)
        self.setWidth(600)
        self.setMinimumSize(QSize(500, 500))
        self.reset()
    
    def reset(self):
        self.origin = QPointF(0, 0)
        self.Z = 1.7    # Zoom exponent
        self.color_map = ColorMap.HSL
        self.move_start: QPointF = None
    
    def get_scale(self):
        return 10 ** self.Z

    def load_shader_code(self):
        with open("vertex_shader.glsl") as f:
            vertex_code = f.read()

        with open("function.txt") as f:
            expression = f.read().lower()
        tree = parse_expression(expression)
        glsl_expression = simplify_tree(tree, 1).glsl()

        fragment_code = ""
        dir_ = "fragment_shader/"
        with open(dir_+"header.glsl") as f:
            fragment_code += f.read()
        with open(dir_+"colormap.glsl") as f:
            fragment_code += f.read()
        with open(dir_+"complex.glsl") as f:
            fragment_code += f.read()
        with open(dir_+"shader.glsl") as f:
            fragment_code += f.read().replace("FUNCTION", glsl_expression)

        self.program = self.ctx.program(vertex_shader=vertex_code, fragment_shader=fragment_code)
        self.render_object = self.ctx.vertex_array(self.program, [(self.quad_buffer, '2f 2f', 'vert', 'texcoord')])

    def initializeGL(self):
        # ModernGL Init

        self.ctx = moderngl.create_context()
        self.quad_buffer = self.ctx.buffer(data=array('f', [
            # position (x, y), uv coords (x, y)
            -1.0, 1.0, -1.0, 1.0,   # topleft
            1.0, 1.0, 1.0, 1.0,     # topright
            -1.0, -1.0, -1.0, -1.0, # bottomleft
            1.0, -1.0, 1.0, -1.0,   # bottomright
        ]))

        self.load_shader_code()

    def paintGL(self):
        params = {}
        params["origin"] = self.origin.x(), self.origin.y()
        params["size"] = (self.size().width(), self.size().height())
        params["scale"] = 10 ** self.Z
        params["color_map"] = self.color_map.value
        for key, value in params.items():
            if key in self.program:
                self.program[key] = value
    
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)
        
    def wheelEvent(self, event: QtGui.QWheelEvent):
        self.Z = (int(10*self.Z) + event.angleDelta().y()//120)/10
        # avoids float rounding errors
        self.update()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() & 1:
            self.move_start = event.localPos()
        if event.buttons() & 2:
            self.color_map = ColorMap((self.color_map.value + 1)%len(ColorMap))
            self.update()
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.move_start is not None:
            self.move(event.localPos())
            self.move_start = event.localPos()
        return super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == 1:
            if self.move_start is not None:
                self.move(event.localPos())
                self.move_start = None
        return super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        print(event.key())
        if event.key() == Qt.Key.Key_Return:
            self.load_shader_code()
            self.update()
        elif event.key() == Qt.Key.Key_Space:
            self.reset()
            self.update()
        return super().keyPressEvent(event)
    
    def move(self, pos: QPointF):
        scale = 10 ** self.Z
        delta: QPointF = (pos - self.move_start) / scale
        self.origin += delta - 2*QPointF(delta.x(), 0)
        # y is reversed in screen coordinates
        self.update()


if __name__ == '__main__':
    app = QApplication([])
    widget = MinimalGLWidget()
    widget.show()
    app.exec_()