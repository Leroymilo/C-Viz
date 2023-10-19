from __future__ import annotations

from PyQt5.QtWidgets import QApplication

from settings_window import SettingsWindow
from render_window import RenderWindow

if __name__ == '__main__':
    app = QApplication([])
    render = RenderWindow()
    settings = SettingsWindow(render)
    render.showMaximized()
    settings.show()
    app.exec_()