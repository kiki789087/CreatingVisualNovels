from dataclasses import dataclass
@dataclass
class Character:
    """
    Модель данных персонажа. Хранит имя, путь к файлу с персонажем, координаты( относительно размера фона)
    """
    name: str = ""
    image_path: str = ""
    x: float = 0.5
    y: float = 1.0