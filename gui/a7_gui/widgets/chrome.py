from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from .. import styles
from .effects import TypewriterLabel


def _window_ctrl_button(text: str, *, checkable: bool = False) -> QPushButton:
    btn = QPushButton(text)
    if checkable:
        btn.setCheckable(True)
    btn.setFixedSize(styles.WINDOW_CTRL_SIZE, styles.WINDOW_CTRL_SIZE)
    btn.setStyleSheet(styles.WINDOW_BTN)
    return btn


class TitleBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(44)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 4)
        self._title = TypewriterLabel("A7 Server", parent=self)
        layout.addStretch()
        layout.addWidget(self._title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def start_typewriter(self) -> None:
        self._title.start()


class WindowControls(QWidget):
    minimize_requested = pyqtSignal()
    close_requested = pyqtSignal()
    backdrop_toggled = pyqtSignal(bool)
    pin_toggled = pyqtSignal(bool)
    mute_toggled = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._backdrop_btn = _window_ctrl_button("🌓", checkable=True)
        self._backdrop_btn.setToolTip("Full dark backdrop")
        self._backdrop_btn.toggled.connect(self._on_backdrop_toggled)

        self._pin_btn = _window_ctrl_button("📍", checkable=True)
        self._pin_btn.setToolTip("Pin on top")
        self._pin_btn.toggled.connect(self._on_pin_toggled)

        self._mute_btn = _window_ctrl_button("🔊", checkable=True)
        self._mute_btn.setToolTip("Mute music")
        self._mute_btn.toggled.connect(self._on_mute_toggled)

        min_btn = _window_ctrl_button("—")
        min_btn.clicked.connect(self.minimize_requested.emit)
        close_btn = _window_ctrl_button("×")
        close_btn.clicked.connect(self.close_requested.emit)

        layout.addWidget(self._backdrop_btn)
        layout.addWidget(self._pin_btn)
        layout.addWidget(self._mute_btn)
        layout.addWidget(min_btn)
        layout.addWidget(close_btn)

    def _on_backdrop_toggled(self, dark: bool) -> None:
        self._backdrop_btn.setText("🌑" if dark else "🌓")
        self._backdrop_btn.setToolTip("30% backdrop" if dark else "Full dark backdrop")
        self.backdrop_toggled.emit(dark)

    def _on_pin_toggled(self, pinned: bool) -> None:
        self._pin_btn.setText("📌" if pinned else "📍")
        self._pin_btn.setToolTip("Unpin" if pinned else "Pin on top")
        self.pin_toggled.emit(pinned)

    def _on_mute_toggled(self, muted: bool) -> None:
        self._mute_btn.setText("🔇" if muted else "🔊")
        self._mute_btn.setToolTip("Unmute music" if muted else "Mute music")
        self.mute_toggled.emit(muted)
