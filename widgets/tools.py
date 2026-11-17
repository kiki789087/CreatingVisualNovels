from enum import Enum

class Tool(Enum):
    """
    Режим работы мыши на сцене.
    NONE мышь на сцене ничего не меняет
    MOVE персонажа можно перетаскивать
    """
    NONE = 0
    MOVE = 1
    MOVE_TEXT = 2