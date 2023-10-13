#!/usr/bin/env python3
from __future__ import annotations
from array import array

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QPointF, QSize, Qt
from PyQt5.QtWidgets import QWidget

import moderngl

from expression_parser.main import parse_expression, simplify_tree

COLORMAPS = [
    {"name": "HSL", "desc": "Common Hue Saturation Luminosity colormap."},
    {"name": "OKHSL", "desc": "HSL colormap with a more consistent perceived lightness."}
]


class SettingsWindow(QMainWindow):
    def __init__(self, render: RenderWindow) -> None:
        super().__init__()
        self.render_window = render
        self.openGL_widget = render.render_widget
        render.render_widget.settings = self

        main_layout = QVBoxLayout()

        # Formula line
        exp_layout = QHBoxLayout()

        exp_layout.addWidget(QLabel("Function expression : f(z) = "))

        self.expression_line = QLineEdit("z^5-1")   # Unit 5th roots
        exp_layout.addWidget(self.expression_line)

        self.reload_button = QPushButton("Reload")
        self.reload_button.setAutoDefault(True)
        exp_layout.addWidget(self.reload_button)

        expression_box = QWidget()
        expression_box.setLayout(exp_layout)
        main_layout.addWidget(expression_box)

        # Center position line
        position_layout = QHBoxLayout()

        position_layout.addWidget(QLabel("Centered on : "))

        self.pos_x = QLineEdit("{:.5e}".format(0))
        self.pos_x.setValidator(QDoubleValidator())
        self.pos_x.setFixedWidth(120)
        position_layout.addWidget(self.pos_x)

        position_layout.addWidget(QLabel(" + i"))

        self.pos_y = QLineEdit("{:.5e}".format(0))
        self.pos_y.setValidator(QDoubleValidator())
        self.pos_y.setFixedWidth(120)
        position_layout.addWidget(self.pos_y)

        position_layout.addStretch()
        position_box = QWidget()
        position_box.setLayout(position_layout)
        main_layout.addWidget(position_box)

        # Scale line
        scale_layout = QHBoxLayout()

        scale_layout.addWidget(QLabel("Scale (logarithmic) : "))

        self.scale = QSlider(Qt.Horizontal)
        self.scale.setMinimum(-170)
        self.scale.setMaximum(200)
        self.scale.setValue(22)    # tested with (z*z-2)/(z*z)
        scale_layout.addWidget(self.scale)

        self.scale_display = QLabel()
        self.scale_display.setFixedWidth(100)
        self.update_scale_display()
        scale_layout.addWidget(self.scale_display)

        scale_box = QWidget()
        scale_box.setLayout(scale_layout)
        main_layout.addWidget(scale_box)

        # Colormap line
        colormap_layout = QHBoxLayout()

        self.colormap = QComboBox()
        self.colormap.addItems([data["name"] for data in COLORMAPS])
        self.colormap.setFixedSize(self.colormap.minimumSizeHint())
        colormap_layout.addWidget(self.colormap)
        
        self.colormap_desc = QLabel()
        self.update_colormap_desc()
        colormap_layout.addWidget(self.colormap_desc)

        colormap_box = QWidget()
        colormap_box.setLayout(colormap_layout)
        main_layout.addWidget(colormap_box)

        # General style line
        style_layout = QHBoxLayout()

        style_layout.addWidget(QLabel("Style :"))

        self.arg_hue = QCheckBox("arg(f(z)) as hue")
        self.arg_hue.setChecked(True)
        style_layout.addWidget(self.arg_hue)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        style_layout.addWidget(sep)

        self.mod_lum = QCheckBox("|f(z)| as luminosity")
        self.mod_lum.setChecked(True)
        style_layout.addWidget(self.mod_lum)

        style_layout.addStretch()
        style_box = QWidget()
        style_box.setLayout(style_layout)
        main_layout.addWidget(style_box)

        # # Style lines box
        # main_layout.addWidget(QLabel("Style lines :"))

        # style_lines_layout = QVBoxLayout()
        # style_lines_layout.addWidget(QLabel("Test"))
        # style_lines_layout.addWidget(QLabel("Test2"))

        # style_lines_box = QGroupBox()
        # style_lines_box.setLayout(style_lines_layout)
        # main_layout.addWidget(style_lines_box)

        # Set the central widget of the Window.
        main_layout.addStretch()
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # binds
        self.reload_button.clicked.connect(self.reload_expression)
        self.expression_line.returnPressed.connect(self.reload_expression)
        self.pos_x.returnPressed.connect(self.refresh)
        self.pos_y.returnPressed.connect(self.refresh)
        self.scale.valueChanged.connect(self.refresh)
        self.colormap.currentIndexChanged.connect(self.refresh)
        self.arg_hue.stateChanged.connect(self.refresh)
        self.mod_lum.stateChanged.connect(self.refresh)
    
    def reset(self):
        self.pos_x.setText(str(0))
        self.pos_y.setText(str(0))
        self.scale.setValue(22)
        self.refresh()
    
    def get_origin(self) -> tuple[float, float]:
        return tuple(map(float, (self.pos_x.text(), self.pos_y.text())))

    def get_scale(self) -> float:
        return 10 ** (self.scale.value()/10)
    
    def get_style(self) -> int:
        res = self.colormap.currentIndex()
        res |= 4 * self.arg_hue.isChecked()
        res |= 8 * self.mod_lum.isChecked()
        return res
    
    def move(self, pxl_delta: QPointF):
        delta: QPointF = pxl_delta / self.get_scale()
        X, Y = self.get_origin()
        self.pos_x.setText("{:.5e}".format(X - delta.x()))
        self.pos_y.setText("{:.5e}".format(Y + delta.y()))
        self.refresh()

    def update_scale(self, delta: int):
        self.scale.setValue(self.scale.value() + delta)
    
    def update_scale_display(self):
        self.scale_display.setText("{:.3e}".format(self.get_scale()))
    
    def cycle_colormap(self):
        self.colormap.setCurrentIndex((self.colormap.currentIndex() + 1)%len(COLORMAPS))
    
    def update_colormap_desc(self):
        self.colormap_desc.setText(COLORMAPS[self.colormap.currentIndex()]["desc"])

    def reload_expression(self):
        self.openGL_widget.load_shader_code()
        self.refresh()
    
    def refresh(self):
        self.update_colormap_desc()
        self.update_scale_display()
        self.openGL_widget.update()
    
    def closeEvent(self, event: QCloseEvent) -> None:
        self.render_window.close()
        return super().closeEvent(event)


class RenderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(500, 500))
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        self.render_widget = RenderWidget()
        self.setCentralWidget(self.render_widget)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Return:
            self.render_widget.settings.reload_expression()
        elif event.key() == Qt.Key.Key_Space:
            self.render_widget.settings.reset()
        return super().keyPressEvent(event)


class RenderWidget(QOpenGLWidget):
    def __init__(self) -> None:
        self.move_start = None
        self.settings: SettingsWindow = None
        super().__init__()

    def load_shader_code(self):
        with open("vertex_shader.glsl") as f:
            vertex_code = f.read()

        expression = self.settings.expression_line.text()
        try:
            tree = parse_expression(expression)
            glsl_expression = simplify_tree(tree, 1).glsl()
        except Exception as e:
            print(e)
            glsl_expression = "complex(1, 0)"

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
        params["origin"] = self.settings.get_origin()
        params["size"] = (self.size().width(), self.size().height())
        params["scale"] = self.settings.get_scale()
        params["style"] = self.settings.get_style()
        params["K"] = (1, 1, 5, 15)
        for key, value in params.items():
            if key in self.program:
                self.program[key] = value
    
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)
        
    def wheelEvent(self, event: QWheelEvent):
        self.settings.update_scale(event.angleDelta().y()//120)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & 1:
            self.move_start = event.localPos()
        if event.buttons() & 2:
            self.settings.cycle_colormap()
            self.update()
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.move_start is not None:
            self.settings.move(event.localPos() - self.move_start)
            self.move_start = event.localPos()
        return super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == 1:
            if self.move_start is not None:
                self.settings.move(event.localPos() - self.move_start)
                self.move_start = None
        return super().mouseReleaseEvent(event)

if __name__ == '__main__':
    app = QApplication([])
    render = RenderWindow()
    settings = SettingsWindow(render)
    render.showMaximized()
    settings.show()
    app.exec_()