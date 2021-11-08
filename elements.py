from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

element_types_data = {"text": 0, "check_box": 1}


class ElementText(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.element_type = element_types_data["text"]
        self.main_begin = None
        self.main_end = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteLater()
            self.element_type = None
        super().keyPressEvent(event)

    def editingFinished(self):
        if self.text().strip() == "":
            self.deleteLater()

    def get_type(self):
        return self.element_type

    def set_main_geometry(self, begin, end):
        self.main_begin = begin
        self.main_end = end

    def get_main_geometry(self):
        return self.main_begin, self.main_end


class ElementCheckBox(QCheckBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.element_type = element_types_data["check_box"]
        self.main_begin = None
        self.main_end = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteLater()
        super().keyPressEvent(event)
        # todo перенести информацию из списка сюда

    def get_type(self):
        return self.element_type

    def set_main_geometry(self, begin, end):
        self.main_begin = begin
        self.main_end = end

    def get_main_geometry(self):
        return self.main_begin, self.main_end
