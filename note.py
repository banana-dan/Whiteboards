import sys
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import *


# отлов ошибок
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class NoteWindow(QWidget):
    def __init__(self, file_path=None, element_name=None):
        self.file_path = file_path
        super().__init__()
        uic.loadUi("layouts/note.ui", self)  # loading ui
        self.setup_handlers()

    def setup_handlers(self):
        self.saveButton.clicked.connect(self.save)
        self.saveAsButton.clicked.connect(self.save_as)
        self.backButton.clicked.connect(self.exit)

    def save(self):
        if self.file_path is None:
            self.save_as()
        else:
            text = self.textEdit.toPlainText()  # текст из textEdit
            with open(self.file_path, 'w') as out_file:
                out_file.write(text)

    def save_as(self):
        # Спрашиваем, куда сохранить файл
        name, is_ok_pressed = QFileDialog.getSaveFileName(self, "Куда сохранить файл?")
        # todo написать название элемента, когда сохраняем файл
        # если пользователь вышел, то ничего не сохраняем
        if not is_ok_pressed:
            return

        text = self.textEdit.toPlainText()  # текст из textEdit
        # сохраняем
        # print(".".join(name.split(".")[:-1]))
        # todo спросить про то надо ли делать проверку на правильность написания файла
        with open(name, 'w', encoding="utf-8") as out_file:
            out_file.write(text)
        self.file_path = name

    def exit(self):
        self.hide()

    def set_file_path(self, file_path):
        self.file_path = file_path

    def get_file_path(self):
        return self.file_path


# todo сохранить настройки, куда в прошлый раз сохраняли файл
# todo Автоатически вбивать имя элемента в имя файла
# todo в главном окне при изменении имени элемента должно изменяться и имя файла


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NoteWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
