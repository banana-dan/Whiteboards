from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class ElementText(QLineEdit):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteLater()
        super().keyPressEvent(event)
