import sys
from note import NoteWindow
from whiteboard import WhiteboardWindow
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


# отлов ошибок
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.widget_data = []
        self.note = NoteWindow()
        self.whiteboard = WhiteboardWindow()
        uic.loadUi("layouts/main.ui", self)  # loading ui
        # setting stylesheet
        with open("resources/scrollbar.txt") as file:
            self.setStyleSheet(file.read())
        self.setup_handlers()  # setup buttons handlers

    def setup_handlers(self):
        self.newElementButton.clicked.connect(self.create_new_element)

    def create_new_element(self):
        # узнаем у пользователя тип элемента
        element_type, ok_pressed = QInputDialog.getItem(
            self, "Выбор типа нового элемента", "Выбери тип элемента",
            ("белая доска", "заметка", "папка"), 0, False)

        # если пользователь нажал ок, то создаем элемент
        if ok_pressed:
            # создаем элемент
            item = QWidget()
            uic.loadUi("layouts/element.ui", item)
            item.setStyleSheet(
                """QWidget{
                background-color: rgb(255, 255, 255); 
                }
                QPushButton{
                    background-color: rgba(255, 255, 255, 0);
                }
                """)
            # Задаем размер
            item.setFixedWidth(200)
            item.setFixedHeight(150)
            element_data = None
            # костомизация элемента в зависимости от типа
            if element_type == "белая доска":
                item.lineEdit.setText("Доска " + str(len(self.widget_data) + 1))
                item.imageLabel.mousePressEvent = self.go_to_whiteboard_window

            if element_type == "заметка":
                item.lineEdit.setText("Заметка " + str(len(self.widget_data) + 1))
                item.imageLabel.mousePressEvent = self.go_to_note_window

            if element_type == "папка":
                item.lineEdit.setText("Папка " + str(len(self.widget_data) + 1))
                item.imageLabel.setPixmap(QPixmap("resources/folder32.png"))

            # сохраняем элемент
            # формат: элемент, тип, данные об элементе
            self.widget_data.append([item, element_type, element_data])
            # добавляем элемент на экран
            row = (len(self.widget_data) - 1) % 5
            col = (len(self.widget_data) - 1) // 5
            self.gridLayout.addWidget(item, col, row)

    def go_to_note_window(self, event):
        self.hide()
        self.note.show()
        self.note.hideEvent = self.go_to_main_window

    def go_to_main_window(self, event):
        self.show()

    def go_to_whiteboard_window(self, event):
        self.hide()
        self.whiteboard.show()
        self.whiteboard.hideEvent = self.go_to_main_window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
