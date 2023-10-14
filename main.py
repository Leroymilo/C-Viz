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
    {"name": "HSL",   "desc": "Common Hue Saturation Luminosity colormap."},
    {"name": "OKHSL", "desc": "HSL colormap with a more consistent perceived lightness."}
]

style_lines = [
    {"name": "Re(f(z))",  "defK": 0,   "minK": -100, "maxK": 100, "map": lambda x: 10 ** (-x/10)},
    {"name": "Im(f(z))",  "defK": 0,   "minK": -100, "maxK": 100, "map": lambda x: 10 ** (-x/10)},
    {"name": "|f(z)|",    "defK": 0,   "minK": -100, "maxK": 100, "map": lambda x: 10 ** (-x/10)},
    {"name": "arg(f(z))", "defK": 179, "minK": 5,    "maxK": 180, "map": lambda x: 185 - x},
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

        # Zoom and position

        main_layout.addWidget(QLabel("Zoom and Position"))
        zoom_pos_layout = QVBoxLayout()

        ## Center position line
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
        zoom_pos_layout.addWidget(position_box)

        ## Scale line
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
        zoom_pos_layout.addWidget(scale_box)


        self.zoom_pos_reset = QPushButton("Reset")
        zoom_pos_layout.addWidget(self.zoom_pos_reset)

        zoom_pos_box = QGroupBox()
        zoom_pos_box.setLayout(zoom_pos_layout)
        main_layout.addWidget(zoom_pos_box)

        # Style

        main_layout.addWidget(QLabel("Style"))
        style_layout = QVBoxLayout()

        ## Colormap line
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
        style_layout.addWidget(colormap_box)

        ## General style line
        gen_style_layout = QHBoxLayout()

        self.arg_hue = QCheckBox()
        self.arg_hue.setChecked(True)
        gen_style_layout.addWidget(self.arg_hue)
        gen_style_layout.addWidget(QLabel("arg(f(z)) as hue"))

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        gen_style_layout.addWidget(sep)

        self.mod_lum = QCheckBox()
        self.mod_lum.setChecked(True)
        gen_style_layout.addWidget(self.mod_lum)
        gen_style_layout.addWidget(QLabel("|f(z)| as luminosity"))

        gen_style_layout.addStretch()
        gen_style_box = QWidget()
        gen_style_box.setLayout(gen_style_layout)
        style_layout.addWidget(gen_style_box)

        ## Style lines box
        style_layout.addWidget(QLabel("Style lines :"))

        style_lines_layout = QGridLayout()

        style_lines_layout.addWidget(QLabel("Along :"), 0, 0)
        style_lines_layout.addWidget(QLabel("Line spacing (Re(f(z)), Im(f(z)) and |f(z)| are logarithmic)"), 0, 2)

        self.style_lines_checkboxes: list[QCheckBox] = []
        self.style_lines_sliders: list[QSlider] = []
        self.style_lines_resets: list[QPushButton] = []
        for i, data in enumerate(style_lines, start=1):
            style_lines_layout.addWidget(QLabel(data["name"]), i, 0)

            cb = QCheckBox()
            style_lines_layout.addWidget(cb, i, 1)
            self.style_lines_checkboxes.append(cb)

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(data["minK"])
            slider.setMaximum(data["maxK"])
            slider.setValue(data["defK"])
            style_lines_layout.addWidget(slider, i, 2)
            self.style_lines_sliders.append(slider)

            button = QPushButton("Reset")
            style_lines_layout.addWidget(button, i, 3)
            self.style_lines_resets.append(button)

        style_lines_box = QGroupBox()
        style_lines_box.setLayout(style_lines_layout)
        style_layout.addWidget(style_lines_box)


        style_box = QGroupBox()
        style_box.setLayout(style_layout)
        main_layout.addWidget(style_box)

        # Set the central widget of the Window.
        main_layout.addStretch()
        main_layout.addWidget(QLabel("Press Escape to bring this window back to front."))
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        # binds
        self.reload_button.clicked.connect(self.reload_expression)
        self.expression_line.returnPressed.connect(self.reload_expression)
        self.pos_x.returnPressed.connect(self.refresh)
        self.pos_y.returnPressed.connect(self.refresh)
        self.scale.valueChanged.connect(self.refresh)
        self.zoom_pos_reset.clicked.connect(self.reset)
        self.colormap.currentIndexChanged.connect(self.refresh)
        self.arg_hue.stateChanged.connect(self.refresh)
        self.mod_lum.stateChanged.connect(self.refresh)
        for i in range(4):
            self.style_lines_checkboxes[i].stateChanged.connect(self.refresh)
            self.style_lines_sliders[i].valueChanged.connect(self.refresh)
        # The loop put every call to self.reset_style_line(3) for some reason
        self.style_lines_resets[0].clicked.connect(lambda : self.reset_style_line(0))
        self.style_lines_resets[1].clicked.connect(lambda : self.reset_style_line(1))
        self.style_lines_resets[2].clicked.connect(lambda : self.reset_style_line(2))
        self.style_lines_resets[3].clicked.connect(lambda : self.reset_style_line(3))
    
    def reset(self):
        self.pos_x.setText(str(0))
        self.pos_y.setText(str(0))
        self.scale.setValue(22)
        self.refresh()
    
    def reset_style_line(self, i: int):
        self.style_lines_sliders[i].setValue(style_lines[i]["defK"])
        self.refresh()
    
    def get_origin(self) -> tuple[float, float]:
        return tuple(map(float, (self.pos_x.text(), self.pos_y.text())))

    def get_scale(self) -> float:
        return 10 ** (self.scale.value()/10)
    
    def get_style(self) -> int:
        res = self.colormap.currentIndex()
        res |= 4 * self.arg_hue.isChecked()
        res |= 8 * self.mod_lum.isChecked()
        for i in range(4):
            res |= (1 << (4+i)) * self.style_lines_checkboxes[i].isChecked()
        return res
    
    def get_Ks(self) -> int:
        return (
            style_lines[i]["map"](self.style_lines_sliders[i].value())
            for i in range(4)
        )
    
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
        if event.key() == Qt.Key.Key_Escape:
            window = self.render_widget.settings
            window.setWindowState(window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
            window.activateWindow()

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
        params["K"] = self.settings.get_Ks()
        for key, value in params.items():
            if key in self.program:
                self.program[key] = value
    
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)
        
    def wheelEvent(self, event: QWheelEvent):
        self.settings.update_scale(event.angleDelta().y()//120)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.buttons() & 1:
            self.move_start = event.localPos()
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