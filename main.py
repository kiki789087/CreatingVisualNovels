import sys
import traceback
from pathlib import Path
from models.frame import Frame

def show_error(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)

sys.excepthook = show_error

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLibraryInfo, QTranslator

from editor.editor_window import EditorWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = QTranslator()
    translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    if translator.load("qtbase_ru", translations_path):
        app.installTranslator(translator)
    else:
        print("Перевод Qt не найден:", translations_path)
    style_path = Path(__file__).parent / "resources" / "light.qss"
    if style_path.exists():
        app.setStyleSheet(style_path.read_text(encoding="utf-8"))
    window = EditorWindow()
    window.showMaximized()
    sys.exit(app.exec())