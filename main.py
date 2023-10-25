from __future__ import annotations

from PyQt5.QtWidgets import QApplication

from settings_window import SettingsWindow

if __name__ == '__main__':
    app = QApplication([])
    settings = SettingsWindow()
    settings.show()
    app.exec_()