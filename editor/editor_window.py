from  pathlib import Path
from pydoc import text

from PyQt6 import uic
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QVBoxLayout, QButtonGroup, QColorDialog

from models.project import Project
from widgets.scene_view import SceneView
from player.player_window import PlayerWindow
from models.character import Character
from widgets.tools import Tool
from models.text_style import TextStyle

UI_PATH = Path(__file__).parent / "editor_window.ui"
IMAGE_FILTER = "Изображения (*.jpg *.jpeg *.png *bmp *.gif *.jpe)"

class EditorWindow(QMainWindow):
    """
    Главное окно редактора. Связывает интерфейс с данными
    """
    def __init__(self):
        """
        Загружает интерфейс из .ui-файла, создает проект и сцену, подключает сигналы и показывает пустое состояние редактора, когда нет ни одного кадра.
        """
        super().__init__()
        uic.loadUi(UI_PATH, self)
        self.setWindowTitle("Программная система для создания визуальных новелл")
        self.resize(1000, 650)

        self.project = Project()
        self.current_index = -1
        self._player = None

        self.scene_view = SceneView()
        container_layout = QVBoxLayout(self.scene_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.scene_view)

        font = self.title_edit.font()
        font.setBold(True)
        font.setPointSize(13)
        self.title_edit.setFont(font)

        self.splitter.setStretchFactor(0,1)
        self.splitter.setStretchFactor(1,4)

        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)
        self.tool_group.addButton(self.move_tool_button, Tool.MOVE.value)
        self.tool_group.addButton(self.move_text_button, Tool.MOVE_TEXT.value)

        self._connect_signals()
        self._refresh_list()
        self.show_frame(-1)

    def _connect_signals(self):
        """
        Связывает действия пользователя с методами-обработчиками
        """
        self.frame_list.currentRowChanged.connect(self.show_frame)

        self.add_button.clicked.connect(self.on_add_clicked)
        self.del_button.clicked.connect(self.on_delete_clicked)
        self.prev_button.clicked.connect(lambda : self.show_frame(self.current_index - 1))
        self.next_button.clicked.connect(lambda : self.show_frame(self.current_index + 1))
        self.play_button.clicked.connect(self.on_play_clicked)

        self.title_edit.textEdited.connect(self.on_title_edited)
        self.title_edit.editingFinished.connect(self.on_title_finished)
        self.speaker_edit.textEdited.connect(self.on_speaker_edited)
        self.text_edit.textChanged.connect(self.on_text_changed)

        self.load_bg_button.clicked.connect(self.on_load_background)
        self.clear_bg_button.clicked.connect(self.on_clear_background)
        self.load_char_button.clicked.connect(self.on_load_character)
        self.clear_char_button.clicked.connect(self.on_clear_character)

        self.font_combo.currentFontChanged.connect(self.on_style_edited)
        self.font_size_spin.valueChanged.connect(self.on_style_edited)
        self.box_width_spin.valueChanged.connect(self.on_style_edited)
        self.box_height_spin.valueChanged.connect(self.on_style_edited)
        self.bg_opacity_spin.valueChanged.connect(self.on_style_edited)
        self.text_color_button.clicked.connect(lambda : self.on_pick_color("text_color", "Цыет текста"))
        self.name_color_button.clicked.connect(lambda : self.on_pick_color("name_color", "Цвет имени персонажа"))
        self.bg_color_button.clicked.connect(lambda : self.on_pick_color("bg_color", "Цвет фона поля"))

        self.add_text_button.clicked.connect(self.on_add_text_clicked)
        self.remove_text_button.clicked.connect(self.on_remove_text_clicked)

        self.tool_group.idToggled.connect(self.on_tool_toggled)
        self.scene_view.character_moved.connect(self.on_character_moved)
        self.scene_view.text_box_moved.connect(self.on_text_box_moved)
        self.move_tool_button.setChecked(True)

    def _refresh_list(self):
        """
        Перерисовывает список кадров слева по данным проекта и выделяет в нем текущий кадр
        """
        self.frame_list.blockSignals(True)
        self.frame_list.clear()
        for frame in self.project.frames:
            self.frame_list.addItem(frame.title)
        if 0 <= self.current_index < len(self.project):
            self.frame_list.setCurrentRow(self.current_index)
        self.frame_list.blockSignals(False)

    def show_frame(self, index:int):
        """
        Делает кадр текущим и показывает его в редакторе
        :param index: номер кадра, который нужно показать
        """
        if not 0 <= index < len(self.project):
            self.current_index = -1
            self._set_editors("","","")
        else:
            self.current_index = index
            frame = self.project[index]
            self._set_editors(frame.title,frame.content, frame.speaker)
            self._set_style_controls(frame)
            if self.frame_list.currentRow() != index:
                self.frame_list.blockSignals(True)
                self.frame_list.setCurrentRow(index)
                self.frame_list.blockSignals(False)
        self._refresh_scene()
        self._update_ui_state()

    def _refresh_scene(self):
        """
        Перерисовывает сцену по текущему кадру
        """
        if self.current_index < 0:
            self.scene_view.clear()
        else:
            self.scene_view.set_frame(self.project[self.current_index])

    def _set_editors(self, title:str, content:str, speaker:str):
        """
        Записывает название и текст кадра и имя говорящего в поле ввода
        :param title:  название кадра
        :param content: текст сцены
        :param speaker: имя говорящего
        """
        widgets = (self.text_edit, self.title_edit, self.speaker_edit)
        for widget in widgets:
            widget.blockSignals(True)
        self.title_edit.setText(title)
        self.text_edit.setPlainText(content)
        self.speaker_edit.setText(speaker)
        for widget in widgets:
            widget.blockSignals(False)

    def on_add_clicked(self):
        """
        Добавляет в проект новый кадр и делает его текущим
        """
        self.current_index = self.project.add_frame()
        self._refresh_list()
        self.show_frame(self.current_index)
        self.title_edit.setFocus()
        self.title_edit.selectAll()

    def on_delete_clicked(self):
        """
        Удаляет текущий кадр после подтверждения пользователя.
        """
        if self.current_index < 0:
            return
        title = self.project[self.current_index].title
        answer = QMessageBox.question(self, "Удаление кадра", f"Удалить «{title}»?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.project.remove_frame(self.current_index)
        new_index = min(self.current_index, len(self.project) - 1)
        self.current_index = new_index
        self._refresh_list()
        self.show_frame(new_index)

    def on_title_edited(self,text:str):
        """
        Сохраняет название кадра при каждом изменении поля и сразу обновляет его в списке кадров.
        :param text: текущий текст в поле названия
        """
        if self.current_index < 0:
            return
        self.project.rename_frame(self.current_index, text)
        item = self.frame_list.item(self.current_index)
        if item is not None:
            item.setText(self.project[self.current_index].title)

    def on_title_finished(self):
        """
        Вызывается, когда пользователь закончил ввод названия. Подставляет в поле фактическое название кадра.
        """
        if self.current_index < 0:
            return
        self.title_edit.blockSignals(True)
        self.title_edit.setText(self.project[self.current_index].title)
        self.title_edit.blockSignals(False)

    def on_speaker_edited(self, text:str):
        """
        Сохраняет имя говорящего и сразу показывает его на сцене
        :return: текущий текст в поле имени
        """
        if self.current_index < 0:
            return
        frame = self.project[self.current_index]
        frame.speaker = text
        if frame.content or frame.speaker:
            frame.text_visible = True
        self.scene_view.set_text_data(frame)

    def on_text_changed(self):
        """
        Сохраняет текст сцены в текущем кадре и сразу показывает ее на сцене
        """
        if self.current_index < 0:
            return
        frame = self.project[self.current_index]
        frame.content = self.text_edit.toPlainText()
        if frame.content or frame.speaker:
            frame.text_visible = True
        self.scene_view.set_text_data(frame)

    def _set_style_controls(self, frame):
        """
        Показывает в элементах управления настройки кадра
        :param frame: кадр или None
        """
        style = frame.text_style if frame is not None else TextStyle()
        widgets = (self.font_combo, self.font_size_spin, self.box_width_spin, self.box_height_spin, self.bg_opacity_spin)
        for widget in widgets:
            widget.blockSignals(True)
        self.font_combo.setCurrentFont(QFont(style.font_family))
        self.font_size_spin.setValue(style.font_size)
        self.box_width_spin.setValue(round(style.width * 100))
        self.box_height_spin.setValue(round(style.height * 100))
        self.bg_opacity_spin.setValue(round(style.bg_opacity * 100))
        for widget in widgets:
            widget.blockSignals(False)
        self._paint_color_buttons(style)

    def _paint_color_buttons(self, style: TextStyle):
        """
        Показывает текущие цвета на кнопках
        :param style: оформление цвета
        :return:
        """
        for button, color in ((self.text_color_button, style.text_color), (self.name_color_button, style.name_color),(self.bg_color_button, style.bg_color)):
            button.setStyleSheet(f"border-bottom: 4px solid {color};")

    def on_style_edited(self, *_):
            """
            Переносит значения из полей оформления в стиль текущего кадра и перерисовывает текстовое поле.
            """
            if self.current_index < 0:
                return
            frame = self.project[self.current_index]
            style = frame.text_style
            style.font_family = self.font_combo.currentFont().family()
            style.font_size = self.font_size_spin.value()
            style.width = self.box_width_spin.value()/100
            style.height = self.box_height_spin.value()/100
            style.bg_opacity = self.bg_opacity_spin.value()/100
            style.fit_inside()
            self.scene_view.set_text_data(frame)

    def on_pick_color(self, field: str, title: str):
        """
        Открывает диалог выбора цвета и записывает результат в стиль кадра
        :param field: поле стиля: "text_color", "name_color" или "bg_color"
        :param title: заголовок диалога
        """
        if self.current_index < 0:
            return
        frame = self.project[self.current_index]
        current = QColor(getattr(frame.text_style, field))
        color = QColorDialog.getColor(current, self, title)
        if not color.isValid():
            return
        setattr(frame.text_style, field, color.name())
        self._paint_color_buttons(frame.text_style)
        self.scene_view.set_text_data(frame)

    def on_add_text_clicked(self):
        """
        Показывает текстовое поле в текущем кадре
        """
        if self.current_index < 0:
            return
        frame = self.project[self.current_index]
        frame.text_visible = True
        self.scene_view.set_text_data(frame)
        self.text_edit.setFocus()

    def on_remove_text_clicked(self):
        """
        Скрывает текстовое поле в текущем кадре
        :return:
        """
        if self.current_index < 0:
            return
        frame = self.project[self.current_index]
        frame.text_visible = False
        self.scene_view.set_text_data(frame)

    def _choose_image(self, caption: str)-> str:
        """
        Открывает диалог выбора файла изображение.
        :param caption: заголовок диалога
        :return: путь к выбранному файлы
        """
        path, _ = QFileDialog.getOpenFileName(self, caption, "", IMAGE_FILTER)
        return path

    def on_load_background(self):
        """
        Загружает фон в текущий кадр
        """
        if self.current_index < 0:
            return
        path = self._choose_image("Выберите фон")
        if not path:
            return
        self.project[self.current_index].background_path = path
        self._refresh_scene()

    def on_clear_background(self):
        """
        Удаляет фон у текущего кадра
        """
        if self.current_index < 0:
            return
        self.project[self.current_index].background_path = ""
        self._refresh_scene()

    def on_load_character(self):
        """
        Загружает изображение персонажа в текущий кадр
        """
        if self.current_index < 0:
            return
        path = self._choose_image("Выберите персонажа")
        if not path:
            return
        frame = self.project[self.current_index]
        if frame.character is None:
            frame.character = Character(image_path=path)
        else:
            frame.character.image_path = path
        self._refresh_scene()

    def on_clear_character(self):
        """
        Удаляет персонажа из текущего кадра
        """
        if self.current_index < 0:
            return
        self.project[self.current_index].character = None
        self._refresh_scene()

    def on_tool_toggled(self, tool_id: int, checked: bool):
        """
        Включает выбанный инструмент на сцене.
        :param tool_id: числовое значение инструмента
        :param checked: True, если кнопка включена
        """
        if checked:
            self.scene_view.set_tool(Tool(tool_id))

    def on_character_moved(self, x:float, y:float):
        """
        Сохраняет новую позицию персонажа
        :param x: положение по горизонтали
        :param y: положение по вертикали
        """
        if self.current_index < 0:
            return
        character = self.project[self.current_index].character
        if character is None:
            return
        character.x = x
        character.y = y

    def on_text_box_moved(self, x:float, y:float):
        """
        Сохраняет позицию текстового поля
        :param x: положение левого края
        :param y: положение верхнего края
        """
        if self.current_index < 0:
            return
        style = self.project[self.current_index].text_style
        style.x = x
        style.y = y

    def on_play_clicked(self):
        """
        Запускает проект
        """
        if len(self.project) == 0:
            QMessageBox.information(self, "Запуск", "Необходимо добавить один кадр.")
            return
        self._player = PlayerWindow(self.project.frames, self)
        self._player.showFullScreen()

    def _update_ui_state(self):
        """
        Включает и отключает элементы управления
        """
        has_current = self.current_index >= 0
        for widget in (self.title_edit, self.speaker_edit, self.text_edit, self.del_button, self.load_bg_button, self.clear_bg_button, self.load_char_button, self.clear_char_button, self.move_tool_button, self.move_text_button, self.font_combo, self.font_size_spin, self.box_width_spin, self.box_height_spin, self.bg_opacity_spin, self.text_color_button, self.bg_color_button, self.add_text_button, self.remove_text_button):
            widget.setEnabled(has_current)

        self.prev_button.setEnabled(has_current and self.current_index > 0)
        self.next_button.setEnabled(has_current and self.current_index < len(self.project) - 1)
        self.play_button.setEnabled(len(self.project) > 0)
