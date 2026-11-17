from dataclasses import replace
from models.frame import Frame

class Project:
    """
    Модель данных,хранит список кадров и отвечает за все операции над ними: добавление, удаление, переименование и автоматическую нумерацию.
    """
    def __init__(self):
        """
         Создает пустой список
        """
        self.frames: list[Frame] = []

    def __len__(self) -> int:
        """
        Возвращает количество кадров
        :return: число кадров len(self.frames)
        """
        return len(self.frames)

    def __getitem__(self, index:int) -> Frame:
        """
        Возвращает кадр по номеру
        :param index: номер кадра в проекте
        :return: объект Frame с этим номером
        """
        return self.frames[index]

    def add_frame(self) -> int:
        """
        Добавляет пустой кадр в конец списка и присваивает ему название "Кадр N"
        Если уже есть кадры, фон и текстовое поле нового кадра копируется с последнего
        :return: индекс добавленного кадра len(self.frames) - 1
        """
        new_frame = Frame()
        if self.frames:
            previous_frame = self.frames[-1]
            new_frame.background_path = previous_frame.background_path
            new_frame.text_style = replace(previous_frame.text_style)
        self.frames.append(new_frame)
        self._renumber()
        return len(self.frames) - 1

    def remove_frame(self, index:int):
        """
        Удаляет кадр и перенумеровывает кадры с автоматическими названиями
        :param index: номер удаляемого кадра
        """
        del self.frames[index]
        self._renumber()

    def rename_frame(self, index: int, text:str):
        """
        Задает кадру название, которое ввел пользователь
        :param index: номер кадра
        :param text: новое название
        """
        frame = self.frames[index]
        text = text.strip()
        if text:
            frame.title = text
            frame.auto_title = False
        else:
            frame.auto_title = True
            self._renumber()

    def _renumber(self):
        """
        Присваивает название "Кадр N" всем кадрам автоматически
        """
        for number, frame in enumerate(self.frames, start=1):
            if frame.auto_title:
                frame.title = f"Кадр {number}"
