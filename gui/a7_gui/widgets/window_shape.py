from __future__ import annotations

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QPainterPath, QRegion
from PyQt6.QtWidgets import QWidget

from .. import styles


def apply_rounded_mask(widget: QWidget, radius: int | None = None) -> None:
    radius = radius if radius is not None else styles.WINDOW_RADIUS
    path = QPainterPath()
    path.addRoundedRect(
        QRectF(0, 0, widget.width(), widget.height()),
        radius,
        radius,
    )
    widget.setMask(QRegion(path.toFillPolygon().toPolygon()))
