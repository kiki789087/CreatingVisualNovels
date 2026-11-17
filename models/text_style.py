from dataclasses import dataclass
@dataclass
class TextStyle:
    """
    Оформление текстового поля кадра.
    """
    x: float = 0.1
    y: float = 0.72
    width: float = 0.8
    height: float = 0.25
    font_family: str = "Segoe UI"
    font_size: int = 26
    text_color: str = "#ffffff"
    name_color: str = "#b6ffb6"
    bg_color: str = "#000000"
    bg_opacity: float = 0.7

    name_box_padding_x: int = 15
    name_box_padding_y: int = 5
    name_box_offset_y: int = -5
    name_box_offset_x: float = 0.0

    def fit_inside(self):
        """
        Приводит размер и положение к допустимым значениям.
        """
        self.width = max(0.1, min(1.0, self.width))
        self.height = max(0.05, min(1.0, self.height))
        self.x = max(0.0, min(1.0 - self.width, self.x))
        self.y = max(0.0, min(1.0 - self.height, self.y))