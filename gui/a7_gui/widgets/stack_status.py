from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .. import styles
from ..server_control import ServerStatus


def _field_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(styles.FIELD_LABEL)
    return label


def _value_label(text: str = "…") -> QLabel:
    label = QLabel(text)
    label.setStyleSheet(styles.MUTED)
    return label


class StackStatusPanel(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("glassPanel")
        self.setStyleSheet(styles.GLASS_PANEL)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(8)

        row = QHBoxLayout()
        row.addWidget(_field_label("Stack"))
        self._pill = _value_label()
        row.addStretch()
        row.addWidget(self._pill)
        root.addLayout(row)

        row2 = QHBoxLayout()
        row2.addWidget(_field_label("Docker"))
        self._docker = _value_label()
        row2.addStretch()
        row2.addWidget(self._docker)
        root.addLayout(row2)

        self._init_row = QHBoxLayout()
        self._init_row.addWidget(_field_label("Initialized"))
        self._initialized = _value_label()
        self._init_row.addStretch()
        self._init_row.addWidget(self._initialized)
        root.addLayout(self._init_row)

        self._path = QLabel("")
        self._path.setStyleSheet(styles.PATH_LABEL)
        self._path.setWordWrap(True)
        root.addWidget(self._path)

        self._hint = QLabel("")
        self._hint.setStyleSheet(styles.MUTED)
        root.addWidget(self._hint)

        self._error = QLabel("")
        self._error.setStyleSheet(styles.ERROR_LABEL)
        self._error.setWordWrap(True)
        root.addWidget(self._error)

    def update_status(self, status: ServerStatus | None, loading: bool, error: str | None) -> None:
        if loading and status is None:
            self._hint.setText("Checking status…")
            return

        self._hint.setText("")
        self._error.setText(error or "")

        if status is None:
            return

        state = status.operation or ("running" if status.running else "stopped")
        pill_style = {
            "running": styles.PILL_RUNNING,
            "stopped": styles.PILL_STOPPED,
        }.get(state, styles.PILL_BUSY)
        self._pill.setText(state)
        self._pill.setStyleSheet(pill_style)

        self._docker.setText("ready" if status.docker_available else "unavailable")
        self._initialized.setText("yes" if status.initialized else "no")
        self._path.setText(status.server_root)
