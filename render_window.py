from array import array
from traceback import format_exc

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import QSize, QTimer, QDateTime, Qt

import moderngl

from expression_parser.main import parse_expression, simplify_tree

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from settings_window import SettingsWindow


class RenderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Render")
        self.setMinimumSize(QSize(500, 500))
        # Prevents closing to pair the windows
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
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.start()
        self.timer.timeout.connect(self.update)

    def load_shader_code(self):
        with open("vertex_shader.glsl") as f:
            vertex_code = f.read()

        expression = self.settings.expression_line.text()
        try:
            tree = parse_expression(expression)
            glsl_expression = simplify_tree(tree).glsl()
        except Exception as e:
            self.settings.error_log.setText(str(e))
            print(format_exc())
            return 1
        
        self.settings.error_log.setText("All good!")

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
        
        # reset timer for consistency
        self.start = QDateTime.currentMSecsSinceEpoch()
        return 0

    def initializeGL(self):
        self.ctx = moderngl.create_context(require=450)
        self.quad_buffer = self.ctx.buffer(data=array('f', [
            # position (x, y), uv coords (x, y)
            -1.0, 1.0, -1.0, 1.0,   # topleft
            1.0, 1.0, 1.0, 1.0,     # topright
            -1.0, -1.0, -1.0, -1.0, # bottomleft
            1.0, -1.0, 1.0, -1.0,   # bottomright
        ]))

        exit_code = self.load_shader_code()
        if exit_code:
            raise Exception("Error while parsing expression or compiling shader code.")

    def paintGL(self):
        params = {}
        params["origin"] = self.settings.get_origin()
        params["size"] = (self.size().width(), self.size().height())
        params["scale"] = self.settings.get_scale()
        params["style"] = self.settings.get_style()
        params["K"] = self.settings.get_Ks()
        t = QDateTime.currentMSecsSinceEpoch() - self.start
        params["t_real"] = t % 4294967296 # modulo max uint
        for key, value in params.items():
            if key in self.program:
                self.program[key] = value
    
        self.render_object.render(mode=moderngl.TRIANGLE_STRIP)
        
    def wheelEvent(self, event: QWheelEvent):
        self.settings.change_scale(event.angleDelta().y()//120)

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