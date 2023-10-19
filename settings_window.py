from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QPointF, Qt

from render_window import RenderWindow

from expression_parser.functions import read_defined_functions

COLORMAPS = [
    {"name": "HSL",   "desc": "Common Hue Saturation Luminosity colormap."},
    {"name": "OKHSL", "desc": "HSL colormap with a more consistent perceived lightness."}
]

STYLELINES = [
    {"name": "Re(f(z))",  "defK": 0,   "minK": -100, "maxK": 100, "map": lambda x: 10 ** (-x/10)},
    {"name": "Im(f(z))",  "defK": 0,   "minK": -100, "maxK": 100, "map": lambda x: 10 ** (-x/10)},
    {"name": "|f(z)|",    "defK": 0,   "minK": -100, "maxK": 100, "map": lambda x: 10 ** (-x/10)},
    {"name": "arg(f(z))", "defK": 179, "minK": 5,    "maxK": 180, "map": lambda x: 185 - x},
]

read_defined_functions()


class SettingsWindow(QMainWindow):

    # INITIALIZATION ================================================================================================

    def __init__(self, render: RenderWindow) -> None:
        super().__init__()
        self.render_window = render
        self.openGL_widget = render.render_widget
        render.render_widget.settings = self

        self.setWindowTitle("Settings")

        # Layout is built from top to bottom, from left to right

        main_layout = QVBoxLayout()

        self.expression(main_layout)
        self.zoom_pos(main_layout)
        self.style_(main_layout)

        main_layout.addStretch()

        main_layout.addWidget(QLabel("Press Escape to bring this window back to front."))
        
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.bind()
        self.refresh()
    
    def expression(self, parent_layout: QLayout):
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Function expression : f(z) = "))

        self.expression_line = QLineEdit("z^5-1")   # Unit 5th roots
        layout.addWidget(self.expression_line)

        self.reload_button = QPushButton("Reload")
        self.reload_button.setAutoDefault(True)
        layout.addWidget(self.reload_button)

        widget = QWidget()
        widget.setLayout(layout)
        parent_layout.addWidget(widget)
    
    def zoom_pos(self, parent_layout: QLayout):
        parent_layout.addWidget(QLabel("Zoom and Position"))
        
        layout = QVBoxLayout()

        self.position(layout)
        self.zoom(layout)

        self.zoom_pos_reset = QPushButton("Reset")
        layout.addWidget(self.zoom_pos_reset)

        widget = QGroupBox()
        widget.setLayout(layout)
        parent_layout.addWidget(widget)
    
    def position(self, parent_layout: QLayout):
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Centered on : "))

        self.pos_x = QLineEdit("{:.5e}".format(0))
        self.pos_x.setValidator(QDoubleValidator())
        self.pos_x.setFixedWidth(120)
        layout.addWidget(self.pos_x)

        layout.addWidget(QLabel(" + i"))

        self.pos_y = QLineEdit("{:.5e}".format(0))
        self.pos_y.setValidator(QDoubleValidator())
        self.pos_y.setFixedWidth(120)
        layout.addWidget(self.pos_y)

        layout.addStretch()

        widget = QWidget()
        widget.setLayout(layout)
        parent_layout.addWidget(widget)
    
    def zoom(self, parent_layout: QLayout):
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Scale (logarithmic) : "))

        self.scale = QSlider(Qt.Horizontal)
        self.scale.setMinimum(-170)
        self.scale.setMaximum(200)
        self.scale.setValue(22)    # good to see the unit circle on 500x500
        layout.addWidget(self.scale)

        self.scale_display = QLabel()
        self.scale_display.setFixedWidth(100)
        layout.addWidget(self.scale_display)

        widget = QWidget()
        widget.setLayout(layout)
        parent_layout.addWidget(widget)
    
    def style_(self, parent_layout: QLayout):
        parent_layout.addWidget(QLabel("Style"))
        layout = QVBoxLayout()

        self.colormap(layout)
        self.hue_lum(layout)    
        self.style_lines(layout)

        style_box = QGroupBox()
        style_box.setLayout(layout)
        parent_layout.addWidget(style_box)
    
    def colormap(self, parent_layout: QLayout):
        layout = QHBoxLayout()

        self.colormap_list = QComboBox()
        self.colormap_list.addItems([data["name"] for data in COLORMAPS])
        self.colormap_list.setFixedSize(self.colormap_list.minimumSizeHint())
        layout.addWidget(self.colormap_list)
        
        self.colormap_desc = QLabel()
        layout.addWidget(self.colormap_desc)

        widget = QWidget()
        widget.setLayout(layout)
        parent_layout.addWidget(widget)
    
    def hue_lum(self, parent_layout: QLayout):
        layout = QHBoxLayout()

        self.arg_hue = QCheckBox()
        self.arg_hue.setChecked(True)
        layout.addWidget(self.arg_hue)
        layout.addWidget(QLabel("arg(f(z)) as hue"))

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        layout.addWidget(sep)

        self.mod_lum = QCheckBox()
        self.mod_lum.setChecked(True)
        layout.addWidget(self.mod_lum)
        layout.addWidget(QLabel("|f(z)| as luminosity"))

        layout.addStretch()

        widget = QWidget()
        widget.setLayout(layout)
        parent_layout.addWidget(widget)
    
    def style_lines(self, parent_layout: QLayout):
        parent_layout.addWidget(QLabel("Style lines :"))

        layout = QGridLayout()

        layout.addWidget(QLabel("Along :"), 0, 0)
        layout.addWidget(QLabel("Line spacing (Re(f(z)), Im(f(z)) and |f(z)| are logarithmic)"), 0, 2)

        self.style_lines_checkboxes: list[QCheckBox] = []
        self.style_lines_sliders: list[QSlider] = []
        self.style_lines_resets: list[QPushButton] = []
        for i, data in enumerate(STYLELINES, start=1):
            layout.addWidget(QLabel(data["name"]), i, 0)

            checkbox = QCheckBox()
            layout.addWidget(checkbox, i, 1)
            self.style_lines_checkboxes.append(checkbox)

            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(data["minK"])
            slider.setMaximum(data["maxK"])
            slider.setValue(data["defK"])
            layout.addWidget(slider, i, 2)
            self.style_lines_sliders.append(slider)

            button = QPushButton("Reset")
            layout.addWidget(button, i, 3)
            self.style_lines_resets.append(button)

        widget = QGroupBox()
        widget.setLayout(layout)
        parent_layout.addWidget(widget)

    def bind(self):
        self.reload_button.clicked.connect(self.reload_expression)
        self.expression_line.returnPressed.connect(self.reload_expression)
        self.pos_x.returnPressed.connect(self.refresh)
        self.pos_y.returnPressed.connect(self.refresh)
        self.scale.valueChanged.connect(self.refresh)
        self.zoom_pos_reset.clicked.connect(self.reset)
        self.colormap_list.currentIndexChanged.connect(self.refresh)
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
    

    # RESETS ========================================================================================================

    def reset(self):
        self.pos_x.setText(str(0))
        self.pos_y.setText(str(0))
        self.scale.setValue(22)
        self.refresh()
    
    def reset_style_line(self, i: int):
        self.style_lines_sliders[i].setValue(STYLELINES[i]["defK"])
        self.refresh()
    

    # GETTERS =======================================================================================================
    
    def get_origin(self) -> tuple[float, float]:
        return tuple(map(float, (self.pos_x.text(), self.pos_y.text())))

    def get_scale(self) -> float:
        return 10 ** (self.scale.value()/10)
    
    def get_style(self) -> int:
        res = self.colormap_list.currentIndex()
        res |= 4 * self.arg_hue.isChecked()
        res |= 8 * self.mod_lum.isChecked()
        for i in range(4):
            res |= (1 << (4+i)) * self.style_lines_checkboxes[i].isChecked()
        return res
    
    def get_Ks(self) -> int:
        return (
            STYLELINES[i]["map"](self.style_lines_sliders[i].value())
            for i in range(4)
        )
    

    # SETTERS =======================================================================================================
    
    def move(self, pxl_delta: QPointF):
        delta: QPointF = pxl_delta / self.get_scale()
        X, Y = self.get_origin()
        self.pos_x.setText("{:.5e}".format(X - delta.x()))
        self.pos_y.setText("{:.5e}".format(Y + delta.y()))
        self.refresh()

    def change_scale(self, delta: int):
        self.scale.setValue(self.scale.value() + delta)


    # UPDATERS ======================================================================================================
    
    def update_scale_display(self):
        self.scale_display.setText("{:.3e}".format(self.get_scale()))
    
    def update_colormap_desc(self):
        self.colormap_desc.setText(COLORMAPS[self.colormap_list.currentIndex()]["desc"])

    def reload_expression(self):
        self.openGL_widget.load_shader_code()
        self.render_window.setWindowTitle(self.expression_line.text())
        self.refresh()
    
    def refresh(self):
        self.update_colormap_desc()
        self.update_scale_display()
        self.openGL_widget.update()


    # BUILTIN EVENTS ================================================================================================
    
    def closeEvent(self, event: QCloseEvent) -> None:
        # Closes both windows
        self.render_window.close()
        return super().closeEvent(event)