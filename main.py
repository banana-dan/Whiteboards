import sys
from note import NoteWindow
from main_window import MainWindow
from settings import SettingsWindow
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import *


# отлов ошибок
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # multi window work realisation
    settings_window = SettingsWindow()


    def main_window_to_settings_window():
        settings_window.show()


    main_window = MainWindow()
    main_window.show()
    main_window.settingsButton.clicked.connect(main_window_to_settings_window)
    sys.excepthook = except_hook
    sys.exit(app.exec_())
