import sys

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# константы
down_menu_height = 30
down_menu_left_and_right_margin = 30
down_menu_down_margin = 30
resolution_main_id = -1
# screen_resolution_data = [(480, 270), (960, 540), (1920, 1080), (3840, 2160)]
screen_resolution_data = [(800, 400), (1600, 800), (3200, 1600)] # todo не получается сделать больше разрешение
# screen_resolution_data = [()(8000, 4000)]

# отлов ошибок
def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class WhiteboardCanvas(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setGeometry(0, 0, 1980, 1280)
        self.background = Qt.white
        self.main_image = QImage(QSize(screen_resolution_data[resolution_main_id][0],
                                       screen_resolution_data[resolution_main_id][1]),
                                 QImage.Format_RGB32)
        self.main_image.fill(self.background)

        self.resolution_index = 0  # переменная, отвечающая за приближение и отдаление
        self.drawing = False
        self.moving = False
        self.color = Qt.black
        self.defaultBrushSize = 2
        self.brushSize = 10
        self.brushColor = Qt.black
        self.LastPoint = None
        self.LastPoint = None
        # находим отношения размеров холстов
        main_x, main_y = screen_resolution_data[resolution_main_id]
        curr_x, curr_y = screen_resolution_data[self.resolution_index]
        self.main_curr_x = main_x / curr_x
        self.main_curr_y = main_y / curr_y
        # todo без этих строки все плохо работает
        self.resize_canvas(-120, None)
        self.resize_canvas(120, None)

    def wheelEvent(self, event):
        self.resize_canvas(event.angleDelta().y(), event)

    def resize_canvas(self, angle, event):
        # определяем куда вращает колесико пользователь
        if angle > 0:

            self.resolution_index = self.resolution_index + 1
            if self.resolution_index >= len(screen_resolution_data):
                self.resolution_index = len(screen_resolution_data) - 1
            else:
                # изменяем размер холста
                self.resize(*screen_resolution_data[self.resolution_index])
                if event is not None:
                    # двигаем холст
                    prev_x, prev_y = screen_resolution_data[self.resolution_index - 1]
                    curr_x, curr_y = screen_resolution_data[self.resolution_index]
                    x = self.geometry().x() + (event.pos().x() - event.pos().x() * curr_x / prev_x)
                    y = self.geometry().y() + (event.pos().y() - event.pos().y() * curr_y / prev_y)
                    self.move(x, y)
        if angle < 0:
            # изменяем размер холста
            self.resolution_index = self.resolution_index - 1
            if self.resolution_index < 0:
                self.resolution_index = 0
            else:
                self.resize(*screen_resolution_data[self.resolution_index])
                if event is not None:
                    # двигаем холст
                    prev_x, prev_y = screen_resolution_data[self.resolution_index + 1]
                    curr_x, curr_y = screen_resolution_data[self.resolution_index]
                    x = self.geometry().x() + (event.pos().x() - event.pos().x() * curr_x / prev_x)
                    y = self.geometry().y() + (event.pos().y() - event.pos().y() * curr_y / prev_y)
                    self.move(x, y)
        # изменяем размер изображения
        # self.image = self.image.scaled(self.size())
        self.parent().setWindowTitle(str(screen_resolution_data[self.resolution_index]))
        # находим отношения размеров холстов
        main_x, main_y = screen_resolution_data[resolution_main_id]
        curr_x, curr_y = screen_resolution_data[self.resolution_index]
        self.main_curr_x = main_x / curr_x
        self.main_curr_y = main_y / curr_y

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.LastPoint = QPoint(event.pos().x() * self.main_curr_x,
                                    event.pos().y() * self.main_curr_y)
        if event.button() == Qt.RightButton:
            self.moving = True
            self.LastPoint = QPoint(QCursor.pos().x() - self.parent().x() - self.x(),
                                    QCursor.pos().y() - self.parent().y() - self.y())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drawing:
            painter = QPainter(self.main_image)
            main_x, main_y = screen_resolution_data[resolution_main_id]
            curr_x, curr_y = screen_resolution_data[self.resolution_index]
            painter.setPen(
                QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.LastPoint, QPoint(event.pos().x() * main_x // curr_x,
                                                    event.pos().y() * main_y // curr_y))
            self.LastPoint = QPoint(event.pos().x() * main_x / curr_x,
                                    event.pos().y() * main_y / curr_y)
            self.update()
        if event.buttons() == Qt.RightButton and self.moving:
            x = (QCursor.pos().x() - self.parent().x()) - self.LastPoint.x()
            y = (QCursor.pos().y() - self.parent().y()) - self.LastPoint.y()
            self.move(x, y)

    def mouseReleaseEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.drawing = False
        if event.buttons() == Qt.RightButton:
            self.moving = False
            self.LastPoint = QPoint(QCursor.pos().x() - self.parent().x(),
                                    QCursor.pos().y() - self.parent().y())

    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.main_image.scaled(
            *screen_resolution_data[self.resolution_index]), self.main_image.scaled(
            *screen_resolution_data[self.resolution_index]).rect())  # self.image.rect())


class WhiteboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.background_image_label = QLabel(self)
        self.background_image_label.setPixmap(QPixmap("resources/flowers.png"))
        # настраиваем виджет
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        # создаем холст
        self.canvas = WhiteboardCanvas(self)
        self.canvas.setObjectName("canvas")
        self.canvas.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.canvas.show()
        # создаем кнопку назад
        self.button_back = QPushButton(self)
        self.button_back.setText("Назад")
        rect = QRect(10, 10, 100, 30)
        self.button_back.setGeometry(rect)

        uic.loadUi('layouts/whiteboard.ui', self)  # Загружаем дизайн

    def paintEvent(self, event):
        # настройка нижнего меню
        height = down_menu_height
        x = down_menu_left_and_right_margin
        width = self.width() - 2 * x
        y = self.height() - height - down_menu_down_margin
        self.downMenu.setGeometry(QRect(x, y, width, height))
        # настройка фона
        self.background_image_label.setGeometry(-1, -1, self.width(), self.height())
        # # настройка холста
        # x = (self.width() - self.canvas.width()) // 2
        # y = (self.height() - self.canvas.height()) // 2
        # self.canvas.setGeometry(x, y, self.canvas.width(), self.canvas.height())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WhiteboardWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
