from __future__ import annotations

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

from . import styles
from .paths import asset_path

FAMILY = "DS-Digital"
NORMAL_FONT_FILE = "DS-DIGI.TTF"
ITALIC_FONT_FILE = "DS-DIGII.TTF"


def init_fonts(app: QApplication) -> str:
    loaded = False
    for filename in (NORMAL_FONT_FILE, ITALIC_FONT_FILE):
        path = asset_path(filename)
        if path.is_file():
            QFontDatabase.addApplicationFont(str(path.resolve()))
            loaded = True

    family = FAMILY if loaded else app.font().family()
    if loaded:
        styles.configure_fonts(family)
        app.setFont(font_normal(11))

    return family


def font_normal(size: int = 11) -> QFont:
    return QFont(FAMILY, size)


def font_italic(size: int = 11) -> QFont:
    face = QFont(FAMILY, size)
    face.setItalic(True)
    return face
