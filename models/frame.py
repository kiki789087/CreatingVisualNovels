from dataclasses import dataclass, field
from models.character import Character
from models.text_style import TextStyle

@dataclass
class Frame:
    """
    Модель данных одного кадра.
    Хранит: название кадра, текст сцены, имя говорящего, путь к фону, персонажа, оформление текстового поля и автоназвание кадра
    """
    title: str = ""
    content: str = ""
    speaker: str = ""
    text_visible: bool = False
    background_path: str = ""
    character: Character | None = None
    text_style: TextStyle = field(default_factory=TextStyle)
    auto_title: bool = True