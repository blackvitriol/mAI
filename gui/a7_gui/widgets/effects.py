from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QLabel, QWidget

from .. import styles


class TypewriterLabel(QLabel):
    def __init__(
        self,
        text: str = "",
        *,
        interval_ms: int = 70,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._full_text = text
        self._index = 0
        self._cursor_visible = True
        self._done = False
        self.setStyleSheet(styles.TITLE_DISPLAY)
        self.setText("")

        self._type_timer = QTimer(self)
        self._type_timer.setInterval(interval_ms)
        self._type_timer.timeout.connect(self._type_tick)

        self._cursor_timer = QTimer(self)
        self._cursor_timer.setInterval(480)
        self._cursor_timer.timeout.connect(self._blink_cursor)

    def start(self) -> None:
        self._index = 0
        self._done = False
        self._type_timer.start()
        self._cursor_timer.start()
        self._render()

    def _type_tick(self) -> None:
        if self._index < len(self._full_text):
            self._index += 1
            self._render()
            return
        self._type_timer.stop()
        self._done = True

    def _blink_cursor(self) -> None:
        if not self._done:
            return
        self._cursor_visible = not self._cursor_visible
        self._render()

    def _render(self) -> None:
        shown = self._full_text[: self._index]
        if not self._done or self._cursor_visible:
            shown += "▌"
        self.setText(shown)


def fade_in_widget(
    widget: QWidget,
    *,
    delay_ms: int = 0,
    duration_ms: int = 520,
) -> QPropertyAnimation:
    """Fade a widget in (top-to-bottom stagger via delay_ms)."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    effect.setOpacity(0.0)

    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setDuration(duration_ms)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    if delay_ms > 0:
        QTimer.singleShot(delay_ms, anim.start)
    else:
        anim.start()

    return anim


class StatusLight(QLabel):
    """Green / yellow / red microservice indicator."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(11, 11)
        self.set_color("red")

    def set_color(self, color: str) -> None:
        styles_map = {
            "green": styles.LIGHT_GREEN,
            "yellow": styles.LIGHT_YELLOW,
            "red": styles.LIGHT_RED,
            "off": styles.LIGHT_OFF,
        }
        self.setStyleSheet(styles_map.get(color, styles.LIGHT_OFF))


def indicator_color(state: str, health: str | None) -> str:
    state_l = state.lower()
    health_l = (health or "").lower()

    if state_l in {"missing", "exited", "dead", "stopped"}:
        return "red"
    if state_l in {"created", "paused", "restarting", "starting", "removing"}:
        return "yellow"
    if state_l == "running":
        if health_l in {"unhealthy", "starting"}:
            return "yellow"
        return "green"
    return "yellow"
