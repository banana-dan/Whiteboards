import sys

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# константы
down_menu_height = 30
down_menu_left_and_right_margin = 30
down_menu_down_margin = 30
line_layout_height = 200
pen_layout_height = 200
eraser_layout_height = 100
figure_layout_height = 300
resolution_main_id = 3
screen_resolution_data = [(800, 400), (1600, 800), (3200, 1600), (6400, 3200), (9600, 4800),
                          (12800, 6400)]  # todo не получается сделать больше разрешение
tool_data = {"pen": 0, "eraser": 1, "line": 2, "figure": 3, "note": 6}


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
        # инициализируем флаги
        self.drawing = False
        self.moving = False
        self.erasing = False
        self.lining = False

        self.color = Qt.black
        self.brushSize = 10
        self.brushColor = Qt.black
        self.eraserSize = 10
        self.eraserColor = Qt.white

        self.lineSize = 10
        self.lineColor = Qt.black
        self.currLine = None
        self.LastPoint = None
        self.DefaultLastPoint = None
        self.defaultLineStartPoint = None
        self.lineStartPoint = None

        self.tool = tool_data["pen"]
        self.image = self.main_image.scaled(*screen_resolution_data[self.resolution_index])
        # находим отношения размеров холстов
        main_x, main_y = screen_resolution_data[resolution_main_id]
        curr_x, curr_y = screen_resolution_data[self.resolution_index]
        self.main_curr_x = main_x / curr_x
        self.main_curr_y = main_y / curr_y
        # todo без этих строки все плохо работает
        self.resize_canvas(-120, None)
        self.resize_canvas(120, None)

    def wheelEvent(self, event):
        if self.drawing or self.moving:
            return
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
        self.image = self.main_image.scaled(self.size())
        self.parent().setWindowTitle(str(screen_resolution_data[self.resolution_index]))
        # находим отношения размеров холстов
        main_x, main_y = screen_resolution_data[resolution_main_id]
        curr_x, curr_y = screen_resolution_data[self.resolution_index]
        self.main_curr_x = main_x / curr_x
        self.main_curr_y = main_y / curr_y

    def mousePressEvent(self, event):
        # карандаш
        if event.button() == Qt.LeftButton and self.tool == tool_data["pen"]:
            self.drawing = True  # устанавливаем флаг рисования
            self.paint_point(event.pos(), self.image, self.main_image, self.brushSize,
                             self.brushColor)  # рисуем точку
            self.LastPoint = event.pos()
        # ластик
        if event.button() == Qt.LeftButton and self.tool == tool_data["eraser"]:
            self.erasing = True
            self.paint_point(event.pos(), self.image, self.main_image, self.eraserSize,
                             self.eraserColor)  # рисуем точку
            self.LastPoint = event.pos()
        # прямая
        if event.button() == Qt.LeftButton and self.tool == tool_data["line"]:
            self.lining = True
            self.lineStartPoint = event.pos()
            self.LastPoint = event.pos()
            self.currLine = QLine(event.pos().x(), event.pos().y(), event.pos().x(), event.pos().y())
            self.update()
        if event.button() == Qt.RightButton:
            self.moving = True
            self.DefaultLastPoint = QPoint(QCursor.pos().x() - self.parent().x() - self.x(),
                                           QCursor.pos().y() - self.parent().y() - self.y())

    def mouseMoveEvent(self, event):
        # рисование карандашом
        if event.buttons() == Qt.LeftButton and self.drawing and self.tool == tool_data["pen"]:
            self.paint_line(self.LastPoint, event.pos(), self.image, self.main_image, self.brushSize,
                            self.brushColor)  # рисуем линию
            self.LastPoint = event.pos()
        # стирание ластиком
        if event.buttons() == Qt.LeftButton and self.erasing and self.tool == tool_data["eraser"]:
            self.paint_line(self.LastPoint, event.pos(), self.image, self.main_image,
                            self.eraserSize, self.eraserColor)  # рисуем линию
            self.LastPoint = event.pos()
            # прямая линия
        if event.buttons() == Qt.LeftButton and self.lining and self.tool == tool_data["line"]:
            self.currLine.setLine(self.lineStartPoint.x(), self.lineStartPoint.y(), event.pos().x(),
                                  event.pos().y())
            self.LastPoint = event.pos()
            self.update()
        if event.buttons() == Qt.RightButton and self.moving:
            x = (QCursor.pos().x() - self.parent().x()) - self.DefaultLastPoint.x()
            y = (QCursor.pos().y() - self.parent().y()) - self.DefaultLastPoint.y()
            self.move(x, y)

    def mouseReleaseEvent(self, event):
        if self.lining is True:
            print("jh")
            self.paint_line(self.lineStartPoint, self.LastPoint, self.image, self.main_image,
                            self.lineSize, self.lineColor)
        if event.buttons() == Qt.RightButton:
            self.DefaultLastPoint = QPoint(QCursor.pos().x() - self.parent().x(),
                                           QCursor.pos().y() - self.parent().y())
            self.LastPoint = event.pos()

        # обнуляем все флаги
        self.lining = False
        self.moving = False
        self.drawing = False
        self.erasing = False

    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())  # self.image.rect())
        if self.lining:
            self.show_line(self.lineStartPoint, self.LastPoint, self.lineSize, self.lineColor)

    def paint_line(self, begin, end, image1, main_image, size, color):
        # рисуем 1 картинку
        painter = QPainter(image1)
        painter.setPen(
            QPen(color,
                 size * screen_resolution_data[self.resolution_index][0] /
                 screen_resolution_data[resolution_main_id][0], Qt.SolidLine, Qt.RoundCap,
                 Qt.RoundJoin))
        painter.drawLine(begin, end)
        self.update()
        # изменяем основное изображение
        painter = QPainter(main_image)
        painter.setPen(
            QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawLine(QPoint(begin.x() * self.main_curr_x,
                                begin.y() * self.main_curr_y),
                         QPoint(end.x() * self.main_curr_x,
                                end.y() * self.main_curr_y))

    def paint_point(self, pos, image1, main_image, size, color):
        # рисуем 1 картинку
        painter = QPainter(image1)
        painter.setPen(
            QPen(color,
                 size * screen_resolution_data[self.resolution_index][0] /
                 screen_resolution_data[resolution_main_id][0], Qt.SolidLine, Qt.RoundCap,
                 Qt.RoundJoin))
        painter.drawPoint(pos)
        self.update()
        # изменяем основное изображение
        painter = QPainter(main_image)
        painter.setPen(
            QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPoint(QPoint(pos.x() * self.main_curr_x, pos.y() * self.main_curr_y))

    def show_line(self, begin, end, size, color):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(color, size))
        painter.setPen(QPen(color,
                            size * screen_resolution_data[self.resolution_index][0] /
                            screen_resolution_data[resolution_main_id][0], Qt.SolidLine, Qt.RoundCap,
                            Qt.RoundJoin))
        painter.drawLine(begin.x(), begin.y(), end.x(), end.y())
        painter.end()

    def set_tool(self, tool):
        self.tool = tool

    def set_eraser_size(self, size):
        self.eraserSize = size

    def set_pen_size(self, size):
        self.brushSize = size

    def set_pen_color(self, color):
        self.background = color

    def get_tool(self):
        return self.tool


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
        # настройки выскакивающих менюшек
        self.line_layout_is_expanded = False
        self.pen_layout_is_expanded = False
        self.eraser_layout_is_expanded = False
        self.figure_layout_is_expanded = False

        uic.loadUi('layouts/whiteboard.ui', self)  # Загружаем дизайн
        self.setup_handlers()

    def setup_handlers(self):
        self.penButton.clicked.connect(lambda x: self.set_canvas_tool(tool_data["pen"]))
        self.eraserButton.clicked.connect(lambda x: self.set_canvas_tool(tool_data["eraser"]))
        self.lineButton.clicked.connect(lambda x: self.set_canvas_tool(tool_data["line"]))
        self.figureButton.clicked.connect(lambda x: self.set_canvas_tool(tool_data["figure"]))
        self.applyPenButton.clicked.connect(
            lambda x: self.canvas.set_pen_size(self.choosePenSizeSpinBox.value()))
        self.applyEraserButton.clicked.connect(
            lambda x: self.canvas.set_eraser_size(self.chooseSizeEraserSpinBox.value()))

    def set_canvas_tool(self, tool):
        # карандаш
        if tool == tool_data["pen"]:
            if self.canvas.get_tool() == tool_data["pen"] and not self.pen_layout_is_expanded:
                self.pen_layout_is_expanded = True
                self.update()
                return
            if self.canvas.get_tool() == tool_data["pen"] and self.pen_layout_is_expanded:
                self.pen_layout_is_expanded = False
                self.update()
                return
            self.canvas.set_tool(tool_data["pen"], )
        # ластик
        if tool == tool_data["eraser"]:
            if self.canvas.get_tool() == tool_data["eraser"] and not self.eraser_layout_is_expanded:
                self.eraser_layout_is_expanded = True
                self.update()
                return
            if self.canvas.get_tool() == tool_data["eraser"] and self.eraser_layout_is_expanded:
                self.eraser_layout_is_expanded = False
                self.update()
                return
            self.canvas.set_tool(tool_data["eraser"])
        # линия
        if tool == tool_data["line"]:
            if self.canvas.get_tool() == tool_data["line"] and not self.line_layout_is_expanded:
                self.line_layout_is_expanded = True
                self.update()
                return
            if self.canvas.get_tool() == tool_data["line"] and self.line_layout_is_expanded:
                self.line_layout_is_expanded = False
                self.update()
                return
            self.canvas.set_tool(tool_data["line"])
        # фигура
        if tool == tool_data["figure"]:
            if self.canvas.get_tool() == tool_data["figure"] and not self.figure_layout_is_expanded:
                self.figure_layout_is_expanded = True
                self.update()
                return
            if self.canvas.get_tool() == tool_data["figure"] and self.figure_layout_is_expanded:
                self.figure_layout_is_expanded = False
                self.update()
                return
            self.canvas.set_tool(tool_data["figure"])
        self.reset_menu_expanded()

    def reset_menu_expanded(self):
        self.pen_layout_is_expanded = False
        self.eraser_layout_is_expanded = False
        self.line_layout_is_expanded = False
        self.figure_layout_is_expanded = False

    def paintEvent(self, event):
        # настройка нижнего меню
        height = down_menu_height
        x = down_menu_left_and_right_margin
        width = self.width() - 2 * x
        y = self.height() - height - down_menu_down_margin
        self.downMenu.setGeometry(QRect(x, y, width, height))
        # настройка фона
        self.background_image_label.setGeometry(-1, -1, self.width(), self.height())
        # настройка дополнительных меню

        # линия
        if self.line_layout_is_expanded:
            self.lineLayout.setFixedHeight(line_layout_height)
            self.lineLayout.setFixedWidth(self.lineButton.width())
            self.lineLayout.move(self.lineButton.x() + self.downMenu.x(),
                                 self.downMenu.y() - line_layout_height)
        if not self.line_layout_is_expanded:
            self.lineLayout.setFixedHeight(0)
            self.lineLayout.setFixedWidth(self.lineButton.width())
            self.lineLayout.move(self.lineButton.x() + self.downMenu.x(),
                                 self.downMenu.y() - line_layout_height)
        # карандаш
        if not self.pen_layout_is_expanded:
            self.penLayout.setFixedHeight(0)
            self.penLayout.setFixedWidth(self.penButton.width())
            self.penLayout.move(self.penButton.x() + self.downMenu.x(),
                                self.downMenu.y() - pen_layout_height)
        if self.pen_layout_is_expanded:
            self.penLayout.setFixedHeight(pen_layout_height)
            self.penLayout.setFixedWidth(self.penButton.width())
            self.penLayout.move(self.penButton.x() + self.downMenu.x(),
                                self.downMenu.y() - pen_layout_height)
        # ластик
        if not self.eraser_layout_is_expanded:
            self.eraserLayout.setFixedHeight(0)
            self.eraserLayout.setFixedWidth(self.eraserButton.width())
            self.eraserLayout.move(self.eraserButton.x() + self.downMenu.x(),
                                   self.downMenu.y() - eraser_layout_height)
        if self.eraser_layout_is_expanded:
            self.eraserLayout.setFixedHeight(eraser_layout_height)
            self.eraserLayout.setFixedWidth(self.eraserButton.width())
            self.eraserLayout.move(self.eraserButton.x() + self.downMenu.x(),
                                   self.downMenu.y() - eraser_layout_height)
        # фигура
        if not self.figure_layout_is_expanded:
            self.figureLayout.setFixedHeight(0)
            self.figureLayout.setFixedWidth(self.eraserButton.width())
            self.figureLayout.move(self.figureButton.x() + self.downMenu.x(),
                                   self.downMenu.y() - figure_layout_height)
        if self.figure_layout_is_expanded:
            self.figureLayout.setFixedHeight(figure_layout_height)
            self.figureLayout.setFixedWidth(self.figureButton.width())
            self.figureLayout.move(self.figureButton.x() + self.downMenu.x(),
                                   self.downMenu.y() - figure_layout_height)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WhiteboardWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
