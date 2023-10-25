from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QPointF, Qt, QSize

from render_window import RenderWindow

print("Setting up LateX renderer...")
from tex_renderer import render_tex
print("LateX renderer ready!")

from expression_parser.lexer import VARS, CONSTS, FUNCS, DEF_FUNCS
from expression_parser.main import parse_expression

print("Importing saved functions...")
from expression_parser.functions import read_defined_functions
read_defined_functions()
print("Saved functions imported!")

COLORMAPS = [
    {"name": "HSL",   "desc": "Common Hue Saturation Luminosity colormap."},
    {"name": "OKHSL", "desc": "HSL colormap with a more consistent perceived lightness."}
]

STYLELINES = [
    {"name": "Re(f(z))",  "defK": 0,   "minK": -100, "maxK": 100, "map": lambda x: 10 ** (x/10)},
    {"name": "Im(f(z))",  "defK": 0,   "minK": -100, "maxK": 100, "map": lambda x: 10 ** (x/10)},
    {"name": "|f(z)|",    "defK": 0,   "minK": -100, "maxK": 100, "map": lambda x: 10 ** (-x/10)},
    {"name": "arg(f(z))", "defK": 179, "minK": 5,    "maxK": 180, "map": lambda x: 185 - x},
]


class SettingsWindow(QMainWindow):

    # INITIALIZATION ================================================================================================

    def __init__(self) -> None:
        super().__init__()
        self.render_window = RenderWindow()
        self.openGL_widget = self.render_window.render_widget
        self.openGL_widget.settings = self

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
        self.update_insert_cb()
        self.update_exp_tex_render()
    
    def expression(self, parent_layout: QLayout):
        parent_layout.addWidget(QLabel("Function expression"))

        layout = QVBoxLayout()

        self.exp_line(layout)
        self.exp_insert(layout)

        self.reload_button = QPushButton("Reload")
        self.reload_button.setAutoDefault(True)
        layout.addWidget(self.reload_button)

        self.error_log = QLineEdit("This is where error show up.")
        self.error_log.setReadOnly(True)
        layout.addWidget(self.error_log)

        widget = QGroupBox()
        widget.setLayout(layout)
        parent_layout.addWidget(widget)
    
    def exp_line(self, parent_layout: QLayout):
        layout = QHBoxLayout()

        layout.addWidget(QLabel("f(z) = "))

        self.expression_line = QLineEdit("z^5 + (2*oscil01(1)-1)")   # Unit 5th roots
        layout.addWidget(self.expression_line)

        self.tex_label = QLabel()
        self.tex_label.setStyleSheet("border: 1px solid black;") 
        layout.addWidget(self.tex_label)

        widget = QWidget()
        widget.setLayout(layout)
        parent_layout.addWidget(widget)
    
    def exp_insert(self, parent_layout: QLayout):
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Insert : "))

        self.insert_type = QComboBox()
        self.insert_type.addItems(
            ["Variable", "Constant", "Built-in Function", "Custom Function"]
        )
        layout.addWidget(self.insert_type)

        self.insert_name = QComboBox()
        self.insert_name.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy(QComboBox.AdjustToContents)
        )
        layout.addWidget(self.insert_name)

        # Displaying a raw icon (for tooltip):
        label = QLabel()
        icon = self.style().standardIcon(QStyle.SP_MessageBoxInformation)
        label.setPixmap(icon.pixmap(QSize(16, 16)))
        label.setToolTip("<img src=\"tooltip.png\">")
        layout.addWidget(label)

        layout.addStretch()

        self.insert = QPushButton("Insert")
        layout.addWidget(self.insert)

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
        self.expression_line.textChanged.connect(self.update_exp_tex_render)
        self.expression_line.returnPressed.connect(self.reload_expression)
        self.insert_type.currentIndexChanged.connect(self.update_insert_cb)
        self.insert_name.currentTextChanged.connect(self.update_insert_desc)
        self.insert.clicked.connect(self.apply_insert)
        self.reload_button.clicked.connect(self.reload_expression)
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

    def update_exp_tex_render(self):
        text = self.expression_line.text()
        try:
            tree = parse_expression(text)
        except Exception as e:
            return
        
        if tree is None: return
        
        name = "fz.png"
        render_tex(f"${tree.tex()}$", name, size=20)
        pixmap = QPixmap(name)
        self.tex_label.setPixmap(pixmap)

    def update_insert_cb(self):
        self.insert_name.clear()
        
        match (self.insert_type.currentText()):
            case "Variable":
                self.insert_name.addItems(VARS.keys())
            case "Constant":
                self.insert_name.addItems(CONSTS.keys())
            case "Built-in Function":
                self.insert_name.addItems(sorted(FUNCS.keys()))
            case "Custom Function":
                self.insert_name.addItems(sorted(DEF_FUNCS.keys()))
        
        self.insert_name.adjustSize()
    
    def update_insert_desc(self):
        desc = "None"
        name = self.insert_name.currentText()
        if name :

            match (self.insert_type.currentText()):
                case "Variable":
                    desc = VARS[name].desc
                case "Constant":
                    desc = CONSTS[name].desc
                case "Built-in Function":
                    desc = FUNCS[name].__doc__
                case "Custom Function":
                    desc = f"${name}(z) = {DEF_FUNCS[name].tex()}$"
        
        render_tex(desc, "tooltip.png")
    
    def apply_insert(self):

        pos = self.expression_line.cursorPosition()
        exp = self.expression_line.text()

        match (self.insert_type.currentText()):
            case "Variable" | "Constant":
                text = self.insert_name.currentText()
            case "Built-in Function" | "Custom Function":
                text = self.insert_name.currentText() + "()"

        self.expression_line.setText(exp[:pos] + text + exp[pos:])
        self.expression_line.setFocus()
    
    def update_scale_display(self):
        self.scale_display.setText("{:.3e}".format(self.get_scale()))
    
    def update_colormap_desc(self):
        self.colormap_desc.setText(COLORMAPS[self.colormap_list.currentIndex()]["desc"])

    def reload_expression(self):
        self.openGL_widget.load_shader_code()
        self.refresh()
    
    def refresh(self):
        self.update_colormap_desc()
        self.update_scale_display()
        self.openGL_widget.update()


    # BUILTIN EVENTS ================================================================================================
    
    def show(self) -> None:
        # Opens both windows
        self.render_window.showMaximized()
        return super().show()
    
    def closeEvent(self, event: QCloseEvent) -> None:
        # Closes both windows
        self.render_window.close()
        return super().closeEvent(event)