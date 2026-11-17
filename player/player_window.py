from PyQt6.QtWidgets import QWidget,QVBoxLayout
from PyQt6.QtCore import Qt

from widgets.scene_view import SceneView

class PlayerWindow(QWidget):
    """
    Окно запуска проекта.
    Получает список кадров, показывает первый и по щелчку мыши переходит к следующему.
    После последнего кадра щелчок закрывает окно.
    """
    def __init__(self, frames, parent=None):
        """
        Создает окно, размещает в нем сцену, подключает щелчок мыши к смене кадра и показывает первый кадр.
        :param frames: список кадров проекта
        :param parent: окно редактора
        """
        super().__init__(parent, Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self._frames = frames
        self._index = 0

        self.scene_view = SceneView(self)
        self.scene_view.clicked.connect(self.next_frame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.scene_view)

        self._show_current()

    def _show_current(self):
        """
        Показывает на сцене текущий кадр.
        """
        self.scene_view.set_frame(self._frames[self._index])

    def next_frame(self):
        """
        Переходит к следующему кадру. Если кадр последний, то закрывается окно просмотра
        """
        if self._index < len(self._frames) - 1:
            self._index += 1
            self._show_current()
        else:
            self.close()

    def keyPressEvent(self, event):
        """
        Обрабатывает нажатие клавиш: Esc закрывает окно, пробел и стрелка впрво переходят к следующему кадру.
        :param event: информация о нажатой клавише
        """
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Right):
            self.next_frame()