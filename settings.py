import sys
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import *


# отлов ошибок
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("layouts/settings.ui", self)  # loading ui
        # todo setting stylesheet
        # with open("resources/scrollbar.txt") as file:
        #     self.setStyleSheet(file.read())




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SettingsWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
