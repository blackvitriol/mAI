from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from .fonts import font_italic
from .paths import asset_path


def build_app_icon() -> QIcon:
    icon_path = asset_path("tray.ico")
    if icon_path.is_file():
        return QIcon(str(icon_path))

    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#22c55e"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(6, 6, size - 12, size - 12)
    painter.setPen(QColor("#f8fafc"))
    painter.setFont(font_italic(22))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "A7")
    painter.end()
    return QIcon(pixmap)


class TrayController:
    def __init__(self, window) -> None:
        self._window = window
        self._icon = build_app_icon()
        QApplication.instance().setWindowIcon(self._icon)

        self._tray = QSystemTrayIcon(self._icon, window)
        self._tray.setToolTip("A7 Server")

        self._menu = QMenu()
        self._show_action = self._menu.addAction("Show")
        self._tray_action = self._menu.addAction("Minimize to tray")
        self._menu.addSeparator()
        self._quit_action = self._menu.addAction("Exit")

        self._show_action.triggered.connect(self.show_window)
        self._tray_action.triggered.connect(self.minimize_to_tray)
        self._quit_action.triggered.connect(self.quit_app)

        self._tray.setContextMenu(self._menu)
        self._tray.activated.connect(self._on_activated)
        self._tray.show()

    def show_window(self) -> None:
        self._window.showNormal()
        self._window.raise_()
        self._window.activateWindow()

    def minimize_to_tray(self) -> None:
        self._window.hide()
        self._tray.showMessage(
            "A7 Server",
            "Running in the system tray.",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )

    def quit_app(self) -> None:
        self._window.force_quit()

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
