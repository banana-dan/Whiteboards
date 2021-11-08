import sys

from PyQt5 import uic  # Импортируем uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from elements import ElementText

# константы
down_menu_height = 30
down_menu_left_and_right_margin = 30
down_menu_down_margin = 30
line_layout_height = 200
pen_layout_height = 200
eraser_layout_height = 100
figure_layout_height = 300
other_layout_height = 200
add_layout_height = 200
resolution_main_id = 3
screen_resolution_data = [(800, 400), (1600, 800), (3200, 1600), (6400, 3200), (9600, 4800),
                          (12800, 6400)]  # todo не получается сделать больше разрешение
tool_data = {"pen": 0, "eraser": 1, "line": 2, "figure_square": 3, "figure_circle": 4,
             "other_text": 5, "other_checkbox": 7, "add_note": 6, "add_image": 8, "add_csv": 9}
element_types_data = {"text": 0, "check_box": 1}


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
        self.drawing_square = False
        self.drawing_circle = False
        self.selection = False
        self.check_box_selection = False

        self.color = Qt.black
        self.brushSize = 10
        self.brushColor = Qt.black
        self.eraserSize = 10
        self.eraserColor = Qt.white
        self.figure_color = Qt.black
        self.figure_size = 10
        self.lineSize = 10
        self.lineColor = Qt.black
        self.currCircleRect = None
        self.currSquare = None
        self.currLine = None
        self.LastPoint = None
        self.DefaultLastPoint = None
        self.defaultLineStartPoint = None
        self.StartPoint = None

        self.elements = []  # список всех элементов на холсте

        self.tool = tool_data["pen"]
        self.image = self.main_image.scaled(*screen_resolution_data[self.resolution_index])
        # находим отношения размеров холстов
        main_x, main_y = screen_resolution_data[resolution_main_id]
        curr_x, curr_y = screen_resolution_data[self.resolution_index]
        self.main_curr_x = main_x / curr_x
        self.main_curr_y = main_y / curr_y

        # todo без этих строк все плохо работает
        self.resize_canvas(-120, None)
        self.resize_canvas(120, None)

    def wheelEvent(self, event):
        if self.drawing or self.moving:
            return
        if event.angleDelta().y() != 0:
            self.resize_canvas(event.angleDelta().y(), event)
            self.resize_elements()

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

    def resize_elements(self):
        for el_type, el, begin, end in self.elements:
            if el_type == element_types_data["text"]:
                el.move(begin.x() / self.main_curr_x, begin.y() / self.main_curr_y)
                el.setFixedWidth(end.x() / self.main_curr_x - begin.x() / self.main_curr_x)
                el.setFixedHeight(end.y() / self.main_curr_y - begin.y() / self.main_curr_y)
                font = QFont()
                font.setPixelSize(el.height())
                el.setFont(font)
                el.setText(el.text())
                el.setTextMargins(0,0,0,0)

    def mousePressEvent(self, event):
        # карандаш
        if event.button() == Qt.LeftButton and self.tool == tool_data["pen"]:
            self.set_pen_size(self.parent().choosePenSizeSpinBox.value())
            self.drawing = True  # устанавливаем флаг рисования
            self.paint_point(event.pos(), self.image, self.main_image, self.brushSize,
                             self.brushColor)  # рисуем точку
            self.LastPoint = event.pos()
        # ластик
        if event.button() == Qt.LeftButton and self.tool == tool_data["eraser"]:
            self.set_eraser_size(self.parent().chooseSizeEraserSpinBox.value())
            self.erasing = True
            self.paint_point(event.pos(), self.image, self.main_image, self.eraserSize,
                             self.eraserColor)  # рисуем точку
            self.LastPoint = event.pos()
        # прямая
        if event.button() == Qt.LeftButton and self.tool == tool_data["line"]:
            self.set_line_size(self.parent().chooseLineSizeSpinBox.value())
            self.lining = True
            self.StartPoint = event.pos()
            self.LastPoint = event.pos()
            self.currLine = QLine(event.pos().x(), event.pos().y(), event.pos().x(), event.pos().y())
            self.update()
        # квадрат
        if event.button() == Qt.LeftButton and self.tool == tool_data["figure_square"]:
            self.set_figure_size(self.parent().chooseLineSizeSpinBox.value())
            self.drawing_square = True
            self.StartPoint = event.pos()
            self.LastPoint = event.pos()
            self.currSquare = QRect(self.StartPoint, self.LastPoint)
            self.update()
        # круг
        if event.button() == Qt.LeftButton and self.tool == tool_data["figure_circle"]:
            self.set_figure_size(self.parent().chooseLineSizeSpinBox.value())
            self.drawing_circle = True
            self.StartPoint = event.pos()
            self.LastPoint = event.pos()
            self.currCircleRect = QRect(self.StartPoint, self.LastPoint)
            self.update()
        # текст
        if event.button() == Qt.LeftButton and self.tool == tool_data["other_text"]:
            self.selection = True
            self.StartPoint = event.pos()
            self.LastPoint = event.pos()
            self.update()
        # чек бокс
        if event.button() == Qt.LeftButton and self.tool == tool_data["other_checkbox"]:
            self.check_box_selection = True
            self.StartPoint = event.pos()
            self.LastPoint = event.pos()
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
        # прямая линия
        if event.buttons() == Qt.LeftButton and self.lining and self.tool == tool_data["line"]:
            self.currLine.setLine(self.StartPoint.x(), self.StartPoint.y(), event.pos().x(),
                                  event.pos().y())
            self.LastPoint = event.pos()
            self.update()
        # квадрат
        if event.buttons() == Qt.LeftButton and self.drawing_square and \
                self.tool == tool_data["figure_square"]:
            self.set_figure_size(self.parent().chooseFigureSizeSpinBox.value())
            self.currSquare.setCoords(self.StartPoint.x(), self.StartPoint.y(), event.pos().x(),
                                      event.pos().y())
            self.LastPoint = event.pos()
            self.update()
        # круг
        if event.buttons() == Qt.LeftButton and self.drawing_circle and \
                self.tool == tool_data["figure_circle"]:
            self.set_figure_size(self.parent().chooseFigureSizeSpinBox.value())
            self.currCircleRect.setCoords(self.StartPoint.x(), self.StartPoint.y(), event.pos().x(),
                                          event.pos().y())
            self.LastPoint = event.pos()
            self.update()
        # текст
        if event.buttons() == Qt.LeftButton and self.selection and \
                self.tool == tool_data["other_text"]:
            self.LastPoint = event.pos()
            self.update()
        # чек бокс
        if event.buttons() == Qt.LeftButton and self.check_box_selection and \
                self.tool == tool_data["other_checkbox"]:
            self.LastPoint = event.pos()
            self.update()

        if event.buttons() == Qt.RightButton and self.moving:
            x = (QCursor.pos().x() - self.parent().x()) - self.DefaultLastPoint.x()
            y = (QCursor.pos().y() - self.parent().y()) - self.DefaultLastPoint.y()
            self.move(x, y)

    def mouseReleaseEvent(self, event):
        if self.lining is True:
            self.paint_line(self.StartPoint, self.LastPoint, self.image, self.main_image,
                            self.lineSize, self.lineColor)
        if self.drawing_square:
            self.paint_rect(self.StartPoint, self.LastPoint, self.image, self.main_image,
                            self.figure_size, self.figure_color)
        if event.buttons() == Qt.RightButton:
            self.DefaultLastPoint = QPoint(QCursor.pos().x() - self.parent().x(),
                                           QCursor.pos().y() - self.parent().y())
            self.LastPoint = event.pos()
        if self.drawing_circle:
            self.paint_circle(self.StartPoint, self.LastPoint, self.image, self.main_image,
                              self.figure_size, self.figure_color)

        if self.selection:
            self.add_text(self.StartPoint, self.LastPoint)

        if self.check_box_selection:
            self.add_check_box(self.StartPoint, self.LastPoint)

        # обнуляем все флаги
        self.drawing_square = False
        self.selection = False
        self.check_box_selection = False
        self.drawing_circle = False
        self.lining = False
        self.moving = False
        self.drawing = False
        self.erasing = False
        self.update()

    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())  # self.image.rect())
        if self.lining:
            self.show_line(self.StartPoint, self.LastPoint, self.lineSize, self.lineColor)
        if self.drawing_square:
            self.show_rect(self.StartPoint, self.LastPoint, self.figure_size, self.figure_color)
        if self.drawing_circle:
            self.show_circle(self.StartPoint, self.LastPoint, self.figure_size, self.figure_color)
        if self.selection:
            self.show_selection(self.StartPoint, self.LastPoint)
        if self.check_box_selection:
            self.show_square_selection(self.StartPoint, self.LastPoint)

    def delete_element(self, event, id):
        if event.key() == Qt.Key_Delete:
            element = self.elements.pop(id)
            element.deleteLater()
            self.update()

    # методы рисования
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

    def paint_rect(self, begin, end, image1, main_image, size, color):
        painter = QPainter(image1)
        painter.setPen(
            QPen(color,
                 size * screen_resolution_data[self.resolution_index][0] /
                 screen_resolution_data[resolution_main_id][0]))

        painter.drawLine(begin, QPoint(end.x(), begin.y()))
        painter.drawLine(QPoint(end.x(), begin.y()), end)
        painter.drawLine(end, QPoint(begin.x(), end.y()))
        painter.drawLine(begin, QPoint(begin.x(), end.y()))
        self.update()
        # изменяем основное изображение
        painter = QPainter(main_image)
        painter.setPen(
            QPen(color, size))
        # сдесь я решил отказаться от использования drawRect так как у него закругляются края
        # painter.drawRect(begin.x() * self.main_curr_x,
        #                  begin.y() * self.main_curr_y,
        #                  end.x() * self.main_curr_x - begin.x() * self.main_curr_x,
        #                  end.y() * self.main_curr_y - begin.y() * self.main_curr_y)
        up_left = QPoint(begin.x() * self.main_curr_x, begin.y() * self.main_curr_y)
        up_right = QPoint(end.x() * self.main_curr_x, begin.y() * self.main_curr_y)
        down_right = QPoint(end.x() * self.main_curr_x, end.y() * self.main_curr_y)
        down_left = QPoint(begin.x() * self.main_curr_x, end.y() * self.main_curr_y)
        painter.drawLine(up_left, up_right)
        painter.drawLine(up_right, down_right)
        painter.drawLine(down_right, down_left)
        painter.drawLine(down_left, up_left)

    def paint_circle(self, begin, end, image1, main_image, size, color):
        painter = QPainter(image1)
        painter.setPen(
            QPen(color,
                 size * screen_resolution_data[self.resolution_index][0] /
                 screen_resolution_data[resolution_main_id][0]))

        painter.drawEllipse(begin.x(), begin.y(), end.x() - begin.x(), end.y() - begin.y())
        self.update()
        # изменяем основное изображение
        painter = QPainter(main_image)
        painter.setPen(
            QPen(color, size))
        up_left = QPoint(begin.x() * self.main_curr_x, begin.y() * self.main_curr_y)
        down_right = QPoint(end.x() * self.main_curr_x, end.y() * self.main_curr_y)
        painter.drawEllipse(up_left.x(), up_left.y(), down_right.x() - up_left.x(),
                            down_right.y() - up_left.y())

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

    def show_rect(self, begin, end, size, color):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(color, size))
        painter.setPen(QPen(color,
                            size * screen_resolution_data[self.resolution_index][0] /
                            screen_resolution_data[resolution_main_id][0]))
        # почему-то когда я рисую квадрат у меня появляются полоски, по этому буду рисовать линии
        # painter.drawRect(begin.x(), begin.y(), end.x() - begin.x(), end.y() - begin.y())
        # painter.drawRect(self.currSquare)
        # painter.drawPolygon(begin, QPoint(end.x(), begin.y()), end, QPoint(begin.x(), end.y()))
        painter.drawLine(begin, QPoint(end.x(), begin.y()))
        painter.drawLine(QPoint(end.x(), begin.y()), end)
        painter.drawLine(end, QPoint(begin.x(), end.y()))
        painter.drawLine(begin, QPoint(begin.x(), end.y()))
        painter.end()

    def show_circle(self, begin, end, size, color):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(QPen(color,
                            size * screen_resolution_data[self.resolution_index][0] /
                            screen_resolution_data[resolution_main_id][0]))
        painter.drawEllipse(begin.x(), begin.y(), end.x() - begin.x(), end.y() - begin.y())
        painter.end()

    def show_selection(self, begin, end):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(Qt.black, 10))
        pen = QPen(Qt.black,
                   10 * screen_resolution_data[self.resolution_index][0] /
                   screen_resolution_data[resolution_main_id][0])
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(begin, QPoint(end.x(), begin.y()))
        painter.drawLine(QPoint(end.x(), begin.y()), end)
        painter.drawLine(end, QPoint(begin.x(), end.y()))
        painter.drawLine(begin, QPoint(begin.x(), end.y()))
        painter.end()

    def show_square_selection(self, begin, end):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(Qt.black, 10))
        pen = QPen(Qt.black,
                   10 * screen_resolution_data[self.resolution_index][0] /
                   screen_resolution_data[resolution_main_id][0])
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(begin, QPoint(begin.x(), end.y()))
        painter.drawLine(QPoint(begin.x(), end.y()), QPoint(end.y() - begin.y() + begin.x(), end.y()))
        painter.drawLine(QPoint(end.y() - begin.y() + begin.x(), end.y()), QPoint(end.y() - begin.y() + begin.x(), begin.y()))
        painter.drawLine(QPoint(end.y() - begin.y() + begin.x(), begin.y()), begin)
        painter.end()

    def add_text(self, begin, end):
        text = ElementText(self)
        text.setText("...")
        text.setTextMargins(0, 0, 0, 0)
        # with open("resources/line_edit.txt") as file:
        #     text.setStyleSheet(file.read())

        max_x = max(begin.x(), end.x())
        max_y = max(begin.y(), end.y())
        min_x = min(begin.x(), end.x())
        min_y = min(begin.y(), end.y())
        font = QFont()
        font.setPixelSize(max_y - min_y)
        text.setFont(font)
        text.setGeometry(min_x, min_y, max_x - min_x, max_y - min_y)
        text.show()
        self.elements.append((element_types_data["text"], text,
                              QPoint(min_x * self.main_curr_x, min_y * self.main_curr_y),
                              QPoint(max_x * self.main_curr_x, max_y * self.main_curr_y)))

    def add_check_box(self, begin, end):
        # todo
        text = ElementText(self)
        text.setText("...")
        text.setTextMargins(0, 0, 0, 0)
        # with open("resources/line_edit.txt") as file:
        #     text.setStyleSheet(file.read())

        max_x = max(begin.x(), end.x())
        max_y = max(begin.y(), end.y())
        min_x = min(begin.x(), end.x())
        min_y = min(begin.y(), end.y())
        font = QFont()
        font.setPixelSize(max_y - min_y)
        text.setFont(font)
        text.setGeometry(min_x, min_y, max_x - min_x, max_y - min_y)
        text.show()
        self.elements.append((element_types_data["text"], text,
                              QPoint(min_x * self.main_curr_x, min_y * self.main_curr_y),
                              QPoint(max_x * self.main_curr_x, max_y * self.main_curr_y)))

    # геттеры и сеттеры
    def set_tool(self, tool):
        self.tool = tool

    def set_eraser_size(self, size):
        self.eraserSize = size

    def set_pen_size(self, size):
        self.brushSize = size

    def set_pen_color(self, color):
        self.brushColor = color

    def set_line_color(self, color):
        self.lineColor = color

    def set_line_size(self, size):
        self.lineSize = size

    def set_figure_size(self, size):
        self.figure_size = size

    def set_figure_color(self, color):
        self.figure_color = color

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
        self.other_layout_is_expanded = False
        self.add_layout_is_expanded = False

        self.curr_figure = tool_data["figure_square"]

        uic.loadUi('layouts/whiteboard.ui', self)  # Загружаем дизайн
        self.setup_handlers()

    def setup_handlers(self):
        # назначаем команды на кнопки
        # выбор элементов
        self.penButton.clicked.connect(self.set_canvas_tool_pen)
        self.lineButton.clicked.connect(self.set_canvas_tool_line)
        self.figureButton.clicked.connect(self.set_canvas_tool_figure)
        self.eraserButton.clicked.connect(self.set_canvas_tool_eraser)
        self.otherButton.clicked.connect(self.set_canvas_tool_other)
        self.addButton.clicked.connect(self.set_canvas_tool_add)
        self.circleChooseButton.clicked.connect(self.set_canvas_tool_figure_circle)
        self.chooseSquareButton.clicked.connect(self.set_canvas_tool_figure_square)
        self.addTextButton.clicked.connect(self.set_canvas_tool_other_text)
        self.addCheckBoxButton.clicked.connect(self.set_canvas_tool_other_check_box)
        self.addNoteButton.clicked.connect(self.set_canvas_tool_add_note)
        self.addImageButton.clicked.connect(self.set_canvas_tool_add_image)
        self.addCsvButton.clicked.connect(self.set_canvas_tool_add_csv)
        self.button_back.clicked.connect(self.hide)
        # изменение свойств
        self.choosePenColorButton.clicked.connect(
            lambda: self.canvas.set_pen_color(QColorDialog.getColor()))
        self.selectBlackPenColorButton.clicked.connect(lambda: self.canvas.set_pen_color(Qt.black))
        self.selectRedPenColorButton.clicked.connect(lambda: self.canvas.set_pen_color(Qt.red))
        self.selectBluePenColorButton.clicked.connect(lambda: self.canvas.set_pen_color(Qt.blue))
        self.selectGreenPenColorButton.clicked.connect(lambda: self.canvas.set_pen_color(Qt.green))
        self.chooseFigureColorButton.clicked.connect(
            lambda: self.canvas.set_figure_color(QColorDialog.getColor()))
        self.chooseLineColorButton.clicked.connect(
            lambda: self.canvas.set_line_color(QColorDialog.getColor()))

    # команды на кнопки
    def set_canvas_tool_pen(self):
        if self.canvas.get_tool() == tool_data["pen"]:
            self.pen_layout_is_expanded = not self.pen_layout_is_expanded
            self.update()
            return
        self.canvas.set_tool(tool_data["pen"])
        self.reset_menu_expanded()
        self.update()

    def set_canvas_tool_line(self):
        if self.canvas.get_tool() == tool_data["line"]:
            self.line_layout_is_expanded = not self.line_layout_is_expanded
            self.update()
            return
        self.canvas.set_tool(tool_data["line"])
        self.reset_menu_expanded()
        self.update()

    def set_canvas_tool_figure(self):
        if self.canvas.get_tool() in (tool_data["figure_square"], tool_data["figure_circle"]):
            self.figure_layout_is_expanded = not self.figure_layout_is_expanded
            self.update()
            return
        self.canvas.set_tool(self.curr_figure)
        self.reset_menu_expanded()
        self.update()

    def set_canvas_tool_eraser(self):
        if self.canvas.get_tool() == tool_data["eraser"]:
            self.eraser_layout_is_expanded = not self.eraser_layout_is_expanded
            self.update()
            return
        self.canvas.set_tool(tool_data["eraser"])
        self.reset_menu_expanded()
        self.update()

    def set_canvas_tool_figure_circle(self):
        self.curr_figure = tool_data["figure_circle"]
        self.canvas.set_tool(self.curr_figure)

    def set_canvas_tool_figure_square(self):
        self.curr_figure = tool_data["figure_square"]
        self.canvas.set_tool(self.curr_figure)

    def set_canvas_tool_other(self):
        self.reset_menu_expanded()
        self.other_layout_is_expanded = True
        self.update()

    def set_canvas_tool_add(self):
        self.reset_menu_expanded()
        self.add_layout_is_expanded = True
        self.update()

    def set_canvas_tool_other_text(self):
        self.canvas.set_tool(tool_data["other_text"])
        self.reset_menu_expanded()
        self.update()

    def set_canvas_tool_other_check_box(self):
        self.canvas.set_tool(tool_data["other_checkbox"])
        self.reset_menu_expanded()
        self.update()

    def set_canvas_tool_add_image(self):
        self.canvas.set_tool(tool_data["add_image"])
        self.reset_menu_expanded()
        self.update()

    def set_canvas_tool_add_csv(self):
        self.canvas.set_tool(tool_data["add_csv"])
        self.reset_menu_expanded()
        self.update()

    def set_canvas_tool_add_note(self):
        self.canvas.set_tool(tool_data["add_note"])
        self.reset_menu_expanded()
        self.update()

    def reset_menu_expanded(self):
        self.pen_layout_is_expanded = False
        self.eraser_layout_is_expanded = False
        self.line_layout_is_expanded = False
        self.figure_layout_is_expanded = False
        self.other_layout_is_expanded = False
        self.add_layout_is_expanded = False

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
        self.set_menu_geometry(self.lineLayout, self.line_layout_is_expanded, self.lineButton,
                               line_layout_height)
        # карандаш
        self.set_menu_geometry(self.penLayout, self.pen_layout_is_expanded, self.penButton,
                               pen_layout_height)
        # ластик
        self.set_menu_geometry(self.eraserLayout, self.eraser_layout_is_expanded, self.eraserButton,
                               eraser_layout_height)
        # фигура
        self.set_menu_geometry(self.figureLayout, self.figure_layout_is_expanded, self.figureButton,
                               figure_layout_height)
        # другое
        self.set_menu_geometry(self.otherLayout, self.other_layout_is_expanded, self.otherButton,
                               other_layout_height)
        # добавить
        self.set_menu_geometry(self.addLayout, self.add_layout_is_expanded, self.addButton,
                               add_layout_height)

    def set_menu_geometry(self, layout, is_expanded, button_reference, height):

        if not is_expanded:
            layout.setFixedHeight(0)
            layout.setFixedWidth(button_reference.width())
            layout.move(button_reference.x() + self.downMenu.x(),
                        self.downMenu.y() - height)
        if is_expanded:
            layout.setFixedHeight(height)
            layout.setFixedWidth(button_reference.width())
            layout.move(button_reference.x() + self.downMenu.x(),
                        self.downMenu.y() - height)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Insert or event.key() == Qt.Key_Return:
            self.reset_menu_expanded()
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WhiteboardWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
