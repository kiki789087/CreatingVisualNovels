from dataclasses import replace
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QFontMetrics, QPen

from models.frame import Frame
from models.text_style import TextStyle
from widgets.tools import Tool

class SceneView(QWidget):
    """
    Виджет сцены: рисует кадр с тремя слоями: фон, персонаж, текстовое поле
    """
    clicked = pyqtSignal()
    character_moved = pyqtSignal(float, float)
    text_box_moved = pyqtSignal(float, float)

    CHARACTER_HEIGHT_RATIO = 0.8
    REFERENCE_HEIGHT = 720
    PADDING = 16
    NAME_SIZE_FACTOR = 1.25
    TEXT_FLAGS = (int(Qt.AlignmentFlag.AlignLeft.value) | int(Qt.AlignmentFlag.AlignTop.value) | (int(Qt.TextFlag.TextWordWrap.value)))

    def __init__(self, parent=None):
        """
        Создает пустую сцену
        :param parent: виджет, внутри которого находится сцена
        """
        super().__init__(parent)
        self.setMinimumHeight(200)

        self._background = QPixmap()
        self._character = QPixmap()
        self._char_x = 0.5
        self._char_y = 1.0

        self._text = ""
        self._speaker = ""
        self._text_visible = False
        self._style = TextStyle()

        self._scene_rect = QRect()
        self._character_rect = QRect()
        self._text_rect = QRect()

        self._tool = Tool.NONE
        self._dragging = False
        self._grab_offset = (0.0, 0.0)

    def set_frame(self, frame: Frame):
        """
        Загружает данные кадра в сцену и перерисовывает ее
        :param frame: кадр, который нужно показать
        """
        self._background=QPixmap(frame.background_path) if frame.background_path else QPixmap()
        character = frame.character
        if character and character.image_path:
            self._character = QPixmap(character.image_path)
            self._char_x = character.x
            self._char_y = character.y
        else:
            self._character = QPixmap()
            self._char_x = 0.5
            self._char_y = 1.0

        self.set_text_data(frame)

    def set_text_data(self, frame: Frame):
        """
        Загружает в сцену только текст и оформление текстового поля и перерисовывает ее.
        :param frame: кадр, текст и оформление
        """
        self._text = frame.content
        self._speaker = frame.speaker
        self._text_visible = frame.text_visible
        self._style = replace(frame.text_style)
        self.update()

    def clear(self):
        """
        Очищает сцену
        """
        self._background = QPixmap()
        self._character = QPixmap()
        self._scene_rect = QRect()
        self._character_rect = QRect()
        self._text = ""
        self._speaker = ""
        self._text_visible = False
        self._text_rect = QRect()
        self.update()

    def set_tool(self, tool: Tool):
        """
        Выбирает активный инструмент мыши
        :param tool: режим работы мыши
        """
        self._tool = tool
        self.update()

    def paintEvent(self, event):
        """
        Рисует сцену слоями: нижний слой - фон, второй - персонаж, верхний - текстовое поле
        :param event:событие перерисовки
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        painter.fillRect(self.rect(), QColor("#1e1e1e"))

        self._scene_rect = self._draw_background(painter)
        self._draw_character(painter, self._scene_rect)
        self._draw_text_layer(painter, self._scene_rect)

    def _draw_background(self, painter: QPainter) -> QRect:
        """
        Рисует первый слой фона
        :param painter: объект, которым ведется рисование
        :return: прямоугольник, который занял фон
        """
        if self._background.isNull():
            painter.setPen(QColor("#888888"))
            painter.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter, "Фон не загружен")
            return self.rect()

        scaled = self._background.scaled(self.size(),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)

        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        return  QRect(x, y, scaled.width(), scaled.height())

    def _draw_character(self, painter: QPainter, scene_rect: QRect):
        """
        Рисует второй слой персонажа
        :param painter: объект, которым ведется рисование
        :param scene_rect:прямоугольник, который занял фон
        """
        self._character_rect = QRect()
        if self._character.isNull():
            return
        height = int(scene_rect.height() * self.CHARACTER_HEIGHT_RATIO)
        scaled = self._character.scaledToHeight( height, Qt.TransformationMode.SmoothTransformation)
        anchor_x = scene_rect.x() + self._char_x * scene_rect.width()
        anchor_y = scene_rect.y() + self._char_y * scene_rect.height()
        left = int(anchor_x - scaled.width() / 2)
        top = int(anchor_y - scaled.height())
        painter.drawPixmap(left,top,scaled)
        self._character_rect = QRect(left, top, scaled.width(), scaled.height())

    def _draw_text_layer(self, painter: QPainter, scene_rect: QRect):
        """
        Рисует третий слой сцены - текстовое поле.
        :param painter: объект QPainter, которым ведется отрисовка
        :param scene_rect: прямоугольник фона сцены
        """
        self._text_rect = QRect()
        if not self._text_visible:
            return

        style = self._style
        scale = scene_rect.height()/self.REFERENCE_HEIGHT

        box = QRect(int(scene_rect.x()+style.x*scene_rect.width()), int(scene_rect.y()+style.y*scene_rect.height()), int(style.width * scene_rect.width()), int(style.height * scene_rect.height()),)

        padding = int(self.PADDING * scale)
        text_px = max(1, int(style.font_size * scale))
        name_px = max(1, int(style.font_size * self.NAME_SIZE_FACTOR*scale))

        name_font = QFont(style.font_family)
        name_font.setPixelSize(name_px)
        name_font.setBold(True)

        text_font = QFont(style.font_family)
        text_font.setPixelSize(text_px)

        name_metric = QFontMetrics(name_font)
        name_height = name_metric.height()

        painter.save()

        background = QColor(style.bg_color)
        background.setAlphaF(style.bg_opacity)
        painter.fillRect(box,background)

        if self._speaker:
            name_metrics = QFontMetrics(name_font)
            name_height = name_metrics.height()
            name_width = name_metrics.horizontalAdvance(self._speaker)

            pad_x = int(style.name_box_padding_x * scale)
            pad_y = int(style.name_box_padding_y * scale)

            offset_x = int(style.name_box_offset_x * box.width())
            offset_y = int(style.name_box_offset_y * scale)

            name_rect = QRect(box.x() + padding + offset_x - pad_x,box.y() - name_height - (pad_y * 2) + offset_y, name_width + (pad_x * 2), name_height + (pad_y * 2))

            name_bg = QColor(style.bg_color)
            name_bg.setAlphaF(style.bg_opacity)

            painter.setBrush(name_bg)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(name_rect, 5 * scale, 5 * scale)

            painter.setFont(name_font)
            painter.setPen(QColor(style.name_color))
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter, self._speaker)

        if self._text:
            inner = box.adjusted(padding, padding, -padding, -padding)
            painter.setFont(text_font)
            painter.setPen(QColor(style.text_color))
            painter.drawText(inner, self.TEXT_FLAGS, self._text)

        painter.restore()

        if self._tool == Tool.MOVE_TEXT:
            painter.setPen(QPen(QColor("#4da3ff"),2, Qt.PenStyle.DashLine))
            painter.drawRect(box.adjusted(1,1,-1,-1))

        self._text_rect = box

    def mousePressEvent(self, event):
        """
        Превращает щелчок левой кнопкой мыши в сигнал clicked
        :param event: событие мыши
        """
        if event.button() != Qt.MouseButton.LeftButton:
            return
        point = event.position().toPoint()

        if self._tool == Tool.MOVE_TEXT and self._text_rect.contains(point):
            self._dragging = True
            left = self._scene_rect.x() + self._style.x * self._scene_rect.width()
            top = self._scene_rect.y() + self._style.y * self._scene_rect.height()
            self._grab_offset = (left - point.x(), top - point.y())

        elif self._tool == Tool.MOVE and self._character_rect.contains(point):
            self._dragging = True
            anchor_x = self._scene_rect.x() + self._char_x * self._scene_rect.width()
            anchor_y = self._scene_rect.y() + self._char_y * self._scene_rect.height()
            self._grab_offset = (anchor_x - point.x(), anchor_y-point.y())
        else:
            self.clicked.emit()

    def mouseMoveEvent(self, event):
        """
        Движение мыши с зажатой кнопкой. При перетаскивании переносит персонажа вслед за курсором и сообщает новую позицию сигналом
        :param event: информация о движении мыши
        """
        if not self._dragging:
            return
        width = self._scene_rect.width()
        height = self._scene_rect.height()
        if width<=0 or height<=0:
            return
        point = event.position().toPoint()
        px = point.x() + self._grab_offset[0]
        py = point.y() + self._grab_offset[1]

        x=(px-self._scene_rect.x())/width
        y=(py-self._scene_rect.y())/height

        if self._tool == Tool.MOVE_TEXT:
            x = max(0.0, min(1.0 - self._style.width, x))
            y = max(0.0, min(1.0 - self._style.height, y))
            self._style.x = x
            self._style.y = y
            self.update()
            self.text_box_moved.emit(x,y)
        elif self._tool == Tool.MOVE:
            x=max(0.0, min(1.0, x))
            y=max(0.0, min(1.0, y))
            self._char_x =x
            self._char_y =y
            self.update()
            self.character_moved.emit(x,y)

    def mouseReleaseEvent(self, event):
        """
        Отпускание кнопки мыши
        :param event: информация об отпускании
        """
        self._dragging = False