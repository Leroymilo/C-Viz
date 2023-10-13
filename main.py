#!/usr/bin/env python3
from __future__ import annotations

from enum import Enum
from array import array
import typing
from PyQt5 import QtCore

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QPointF, QSize, Qt
from PyQt5.QtWidgets import QWidget

import moderngl

from expression.main import parse_expression, simplify_tree

class ColorMap(Enum):
    HSL = 0
    OKLCh = 1


class SettingsWindow(QMainWindow):
    def __init__(self, render: RenderWindow) -> None:
        super().__init__()
        self.render_window = render
        self.openGL_widget = render.render_widget
        render.render_widget.settings_window = self

        main_layout = QVBoxLayout()

        # Formula line
        exp_layout = QHBoxLayout()

        exp_layout.addWidget(QLabel("Function expression : f(z) = "))

        self.expression_line = QLineEdit("z")
        exp_layout.addWidget(self.expression_line)

        self.reload_button = QPushButton("Reload")
        self.reload_button.setAutoDefault(True)
        exp_layout.addWidget(self.reload_button)

        self.expression_box = QWidget()
        self.expression_box.setLayout(exp_layout)
        main_layout.addWidget(self.expression_box)

        widget = QWidget()
        widget.setLayout(main_layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

        # binds
        self.reload_button.clicked.connect(self.reload_render)
        self.expression_line.returnPressed.connect(self.reload_render)

        print("settings initialized")
    
    def reload_render(self):
        self.openGL_widget.load_shader_code()
        self.openGL_widget.update()
    
    def closeEvent(self, event: QCloseEvent) -> None:
        self.render_window.close()
        return super().closeEvent(event)


class RenderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setBaseSize(QSize(800, 600))
        self.setMinimumSize(QSize(500, 500))
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        self.render_widget = RenderWidget()
        self.setCentralWidget(self.render_widget)
        self.render_widget.reset()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Return:
            self.render_widget.load_shader_code()
            self.render_widget.update()
        elif event.key() == Qt.Key.Key_Space:
            self.render_widget.reset()
            self.render_widget.update()
        return super().keyPressEvent(event)


class RenderWidget(QOpenGLWidget):
    def __init__(self) -> None:
        self.settings_window: SettingsWindow = None
        super().__init__()
    
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

        expression = self.settings_window.expression_line.text()
        try:
            tree = parse_expression(expression)
            glsl_expression = simplify_tree(tree, 1).glsl()
        except Exception as e:
            print(e)
            glsl_expression = "complex(1, 0)"

        print(glsl_expression)
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
        params["scale"] = self.get_scale()
        params["color_map"] = self.color_map.value
        for key, value in params.items():
            if key in self.program:
                self.program[key] = value
    
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)
        
    def wheelEvent(self, event: QWheelEvent):
        self.Z = (int(10*self.Z) + event.angleDelta().y()//120)/10
        # avoids float rounding errors
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & 1:
            self.move_start = event.localPos()
        if event.buttons() & 2:
            self.color_map = ColorMap((self.color_map.value + 1)%len(ColorMap))
            self.update()
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.move_start is not None:
            self.move(event.localPos())
            self.move_start = event.localPos()
        return super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == 1:
            if self.move_start is not None:
                self.move(event.localPos())
                self.move_start = None
        return super().mouseReleaseEvent(event)
    
    def move(self, pos: QPointF):
        scale = self.get_scale()
        delta: QPointF = (pos - self.move_start) / scale
        self.origin += delta - 2*QPointF(delta.x(), 0)
        # y is reversed in screen coordinates
        self.update()


if __name__ == '__main__':
    app = QApplication([])
    render = RenderWindow()
    settings = SettingsWindow(render)
    render.show()
    settings.show()
    app.exec_()