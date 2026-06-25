from __future__ import annotations

from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .. import styles
from ..server_control import ContainerStatus, ServerStatus
from .effects import StatusLight, fade_in_widget, indicator_color

SERVICE_GRID_COLS = 2
STACK_BTN_SIZE = 36
ACTION_BTN_SIZE = 26

_ACTION_ICONS: dict[str, tuple[str, str]] = {
    "start": ("▶", "Start"),
    "stop": ("⏹", "Stop"),
    "restart": ("🔄", "Restart"),
}


def _icon_button(
    emoji: str,
    tooltip: str,
    *,
    style: str,
    size: int,
) -> QPushButton:
    btn = QPushButton(emoji)
    btn.setFixedSize(size, size)
    btn.setStyleSheet(style)
    btn.setToolTip(tooltip)
    return btn


class StackControlsPanel(QWidget):
    init_requested = pyqtSignal()
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    restart_requested = pyqtSignal()
    container_action_requested = pyqtSignal(str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("glassPanel")
        self.setStyleSheet(styles.GLASS_PANEL)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        title = QLabel("Server control")
        title.setStyleSheet(styles.PANEL_TITLE)
        root.addWidget(title)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addStretch()
        self._init_btn = _icon_button(
            "🛠", "Initialize stack", style=styles.BTN_INIT, size=STACK_BTN_SIZE
        )
        self._init_btn.clicked.connect(self.init_requested.emit)

        self._start_btn = _icon_button(
            "▶", "Start stack", style=styles.BTN_START, size=STACK_BTN_SIZE
        )
        self._start_btn.clicked.connect(self.start_requested.emit)

        self._stop_btn = _icon_button(
            "⏹", "Stop stack", style=styles.BTN_STOP, size=STACK_BTN_SIZE
        )
        self._stop_btn.clicked.connect(self.stop_requested.emit)

        self._restart_btn = _icon_button(
            "🔄", "Restart stack", style=styles.BTN_RESTART, size=STACK_BTN_SIZE
        )
        self._restart_btn.clicked.connect(self.restart_requested.emit)

        row.addWidget(self._init_btn)
        row.addWidget(self._start_btn)
        row.addWidget(self._stop_btn)
        row.addWidget(self._restart_btn)
        row.addStretch()
        root.addLayout(row)

        self._hint = QLabel("")
        self._hint.setStyleSheet(styles.MUTED)
        root.addWidget(self._hint)

        self._message = QLabel("")
        self._message.setStyleSheet(styles.OK_LABEL)
        self._message.setWordWrap(True)
        root.addWidget(self._message)

        self._error = QLabel("")
        self._error.setStyleSheet(styles.ERROR_LABEL)
        self._error.setWordWrap(True)
        root.addWidget(self._error)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        self._service_host = QWidget()
        self._service_layout = QGridLayout(self._service_host)
        self._service_layout.setContentsMargins(0, 0, 0, 0)
        self._service_layout.setHorizontalSpacing(8)
        self._service_layout.setVerticalSpacing(8)
        scroll.setWidget(self._service_host)
        root.addWidget(scroll, stretch=1)

        self._busy = False

    def fade_in_rows(self, start_delay_ms: int = 0) -> None:
        for i in range(self._service_layout.count()):
            item = self._service_layout.itemAt(i)
            widget = item.widget() if item is not None else None
            if widget is not None:
                fade_in_widget(widget, delay_ms=start_delay_ms + i * 70, duration_ms=420)

    def set_busy(self, busy: bool, label: str | None = None) -> None:
        self._busy = busy
        for btn in (self._init_btn, self._start_btn, self._stop_btn, self._restart_btn):
            btn.setDisabled(busy)
        if label:
            self._hint.setText(label)

    def set_feedback(self, message: str | None, error: str | None) -> None:
        self._message.setText(message or "")
        self._error.setText(error or "")
        if not self._busy:
            self._hint.setText("")

    def update_status(self, status: ServerStatus | None) -> None:
        if status is None:
            return

        docker_ok = status.docker_available
        initialized = status.initialized
        running = status.running

        self._init_btn.setEnabled(not self._busy and docker_ok and not initialized)
        self._start_btn.setEnabled(not self._busy and docker_ok and initialized and not running)
        self._stop_btn.setEnabled(not self._busy and docker_ok)
        self._restart_btn.setEnabled(not self._busy and docker_ok and initialized)

        if not docker_ok:
            self._hint.setText("Start Docker Desktop before controlling the stack.")

        self._rebuild_services(status.containers, docker_ok and initialized)

    def _rebuild_services(self, containers: list[ContainerStatus], enabled: bool) -> None:
        while self._service_layout.count():
            item = self._service_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for index, container in enumerate(containers):
            card = _ServiceCard(container, enabled and not self._busy, self)
            card.action_requested.connect(self.container_action_requested.emit)
            self._service_layout.addWidget(
                card,
                index // SERVICE_GRID_COLS,
                index % SERVICE_GRID_COLS,
            )


class _ServiceCard(QWidget):
    action_requested = pyqtSignal(str, str)

    def __init__(
        self,
        container: ContainerStatus,
        enabled: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("serviceCard")
        self.setStyleSheet(styles.SERVICE_CARD)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(6)
        light = StatusLight(self)
        light.set_color(indicator_color(container.state, container.health))
        header.addWidget(light, alignment=Qt.AlignmentFlag.AlignVCenter)

        title = QLabel(container.label)
        title.setStyleSheet(styles.SERVICE_NAME)
        title.setWordWrap(True)
        header.addWidget(title, stretch=1)
        root.addLayout(header)

        state = container.state
        if container.health:
            state = f"{state} ({container.health})"
        state_lbl = QLabel(state)
        state_lbl.setStyleSheet(styles.MUTED)
        state_lbl.setWordWrap(True)
        root.addWidget(state_lbl)

        actions = QHBoxLayout()
        actions.setSpacing(4)
        for action, (emoji, tooltip) in _ACTION_ICONS.items():
            btn = _icon_button(
                emoji,
                f"{tooltip} {container.label}",
                style=styles.ICON_BTN,
                size=ACTION_BTN_SIZE,
            )
            btn.setEnabled(enabled)
            btn.clicked.connect(
                lambda _checked=False, a=action, s=container.service: self.action_requested.emit(
                    s, a
                )
            )
            actions.addWidget(btn)

        if container.url:
            open_btn = _icon_button(
                "🔗",
                f"Open {container.label}",
                style=styles.ICON_BTN,
                size=ACTION_BTN_SIZE,
            )
            open_btn.clicked.connect(
                lambda: QDesktopServices.openUrl(QUrl(container.url))
            )
            actions.addWidget(open_btn)

        actions.addStretch()
        root.addLayout(actions)
