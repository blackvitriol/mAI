from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QImageReader, QMovie
from PyQt6.QtWidgets import QLabel, QSizePolicy, QWidget

from .. import styles
from ..paths import asset_path

DEFAULT_WINDOW_SIZE = QSize(520, 720)


def background_gif_size() -> QSize | None:
    gif = asset_path("background.gif")
    if not gif.is_file():
        return None
    reader = QImageReader(str(gif))
    if not reader.canRead():
        return None
    size = reader.size()
    if size.isValid() and size.width() > 0 and size.height() > 0:
        return size
    return None


def window_size_for_background() -> QSize:
    return background_gif_size() or DEFAULT_WINDOW_SIZE


class BackgroundWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._backdrop = QWidget(self)
        self._backdrop.setObjectName("backdropFill")
        self._backdrop.setStyleSheet(styles.BACKDROP_FILL)

        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._movie: QMovie | None = None
        self._native_size: QSize | None = None
        self._load_background()

    def native_size(self) -> QSize | None:
        return self._native_size

    def _load_background(self) -> None:
        gif = asset_path("background.gif")
        if gif.is_file():
            reader = QImageReader(str(gif))
            if reader.canRead():
                size = reader.size()
                if size.isValid():
                    self._native_size = size

            self._movie = QMovie(str(gif))
            self._label.setMovie(self._movie)
            if self._native_size is not None:
                self._movie.setScaledSize(self._native_size)
            self._movie.start()
            return

        self._label.setStyleSheet(
            "background: qlineargradient("
            "x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #0f172a, stop:0.55 #1e293b, stop:1 #0b1220);"
        )

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._backdrop.setGeometry(self.rect())
        self._label.setGeometry(self.rect())
        self._backdrop.lower()
        self._label.raise_()
        if self._movie is not None and self._native_size is not None:
            self._movie.setScaledSize(self._native_size)

    def set_backdrop_dark(self, dark: bool) -> None:
        self._backdrop.setStyleSheet(
            styles.BACKDROP_FILL_DARK if dark else styles.BACKDROP_FILL
        )
