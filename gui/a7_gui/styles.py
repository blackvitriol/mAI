"""Shared Qt stylesheets."""

WINDOW_RADIUS = 16
WINDOW_CTRL_SIZE = 28
_FONT_FAMILY = "Segoe UI"


def configure_fonts(family: str) -> None:
    global _FONT_FAMILY
    global TITLE_LABEL, TITLE_DISPLAY, INDICATOR_LABEL
    global MUTED, PATH_LABEL, ERROR_LABEL, OK_LABEL, PANEL_TITLE
    global BTN_BASE, BTN_SMALL, WINDOW_BTN
    global PILL_RUNNING, PILL_STOPPED, PILL_BUSY, SERVICE_NAME, FIELD_LABEL
    global BTN_START, BTN_STOP, BTN_RESTART, BTN_INIT, ICON_BTN

    _FONT_FAMILY = family
    ff = f'font-family: "{family}";'

    TITLE_LABEL = (
        f"color: rgba(226, 232, 240, 0.75); {ff} font-size: 11px; "
        "font-style: normal; letter-spacing: 0.08em;"
    )
    TITLE_DISPLAY = (
        f"color: #f1f5f9; {ff} font-size: 22px; font-style: italic; letter-spacing: 0.06em;"
    )
    INDICATOR_LABEL = (
        f"color: rgba(148, 163, 184, 0.9); {ff} font-size: 9px; font-style: normal;"
    )
    MUTED = f"color: rgba(148, 163, 184, 0.95); {ff} font-size: 12px; font-style: normal;"
    PATH_LABEL = (
        f"color: rgba(100, 116, 139, 0.95); {ff} font-size: 10px; font-style: italic;"
    )
    ERROR_LABEL = f"color: #f87171; {ff} font-size: 12px; font-style: normal;"
    OK_LABEL = f"color: #86efac; {ff} font-size: 12px; font-style: normal;"
    PANEL_TITLE = (
        f"color: #e2e8f0; {ff} font-size: 14px; font-style: italic; margin-bottom: 4px;"
    )
    SERVICE_NAME = f"color: #e2e8f0; {ff} font-size: 12px; font-style: normal;"
    FIELD_LABEL = f"color: rgba(226, 232, 240, 0.85); {ff} font-size: 12px; font-style: italic;"

    BTN_BASE = f"""
QPushButton {{
    border-radius: 10px;
    padding: 8px 14px;
    {ff}
    font-size: 11px;
    font-style: normal;
    border: 1px solid rgba(255, 255, 255, 0.14);
    color: #f8fafc;
}}
QPushButton:disabled {{
    opacity: 0.45;
}}
"""

    BTN_SMALL = f"""
QPushButton {{
    border-radius: 8px;
    padding: 4px 8px;
    {ff}
    font-size: 11px;
    font-style: normal;
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #e2e8f0;
    background-color: rgba(30, 41, 59, 0.65);
}}
QPushButton:disabled {{ opacity: 0.4; }}
"""

    WINDOW_BTN = f"""
QPushButton {{
    min-width: {WINDOW_CTRL_SIZE}px;
    max-width: {WINDOW_CTRL_SIZE}px;
    min-height: {WINDOW_CTRL_SIZE}px;
    max-height: {WINDOW_CTRL_SIZE}px;
    width: {WINDOW_CTRL_SIZE}px;
    height: {WINDOW_CTRL_SIZE}px;
    padding: 0px;
    border-radius: 8px;
    {ff}
    font-size: 13px;
    font-style: normal;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background-color: rgba(15, 23, 42, 0.55);
    color: #f8fafc;
}}
QPushButton:hover {{ background-color: rgba(51, 65, 85, 0.75); }}
"""

    PILL_RUNNING = f"color: #86efac; {ff} font-size: 12px; font-style: italic;"
    PILL_STOPPED = f"color: #fca5a5; {ff} font-size: 12px; font-style: italic;"
    PILL_BUSY = f"color: #fcd34d; {ff} font-size: 12px; font-style: italic;"

    BTN_START = BTN_BASE + "QPushButton { background-color: rgba(34, 197, 94, 0.35); }"
    BTN_STOP = BTN_BASE + "QPushButton { background-color: rgba(239, 68, 68, 0.35); }"
    BTN_RESTART = BTN_BASE + "QPushButton { background-color: rgba(59, 130, 246, 0.35); }"
    BTN_INIT = BTN_BASE + "QPushButton { background-color: rgba(168, 85, 247, 0.35); }"
    ICON_BTN = WINDOW_BTN


# Defaults before configure_fonts() — overridden when assets load.
TITLE_LABEL = "color: rgba(226, 232, 240, 0.75); font-size: 11px; letter-spacing: 0.08em;"
TITLE_DISPLAY = "color: #f1f5f9; font-size: 22px; font-style: italic; letter-spacing: 0.06em;"
INDICATOR_LABEL = "color: rgba(148, 163, 184, 0.9); font-size: 9px;"
MUTED = "color: rgba(148, 163, 184, 0.95); font-size: 12px;"
PATH_LABEL = "color: rgba(100, 116, 139, 0.95); font-size: 10px; font-style: italic;"
ERROR_LABEL = "color: #f87171; font-size: 12px;"
OK_LABEL = "color: #86efac; font-size: 12px;"
PANEL_TITLE = "color: #e2e8f0; font-size: 14px; font-style: italic; margin-bottom: 4px;"
SERVICE_NAME = "color: #e2e8f0; font-size: 12px;"
FIELD_LABEL = "color: rgba(226, 232, 240, 0.85); font-size: 12px; font-style: italic;"

BTN_BASE = """
QPushButton {
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 11px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    color: #f8fafc;
}
QPushButton:disabled { opacity: 0.45; }
"""

BTN_START = BTN_BASE + "QPushButton { background-color: rgba(34, 197, 94, 0.35); }"
BTN_STOP = BTN_BASE + "QPushButton { background-color: rgba(239, 68, 68, 0.35); }"
BTN_RESTART = BTN_BASE + "QPushButton { background-color: rgba(59, 130, 246, 0.35); }"
BTN_INIT = BTN_BASE + "QPushButton { background-color: rgba(168, 85, 247, 0.35); }"

SERVICE_CARD = """
QWidget#serviceCard {
    background-color: rgba(30, 41, 59, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
}
"""

BTN_SMALL = """
QPushButton {
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 11px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #e2e8f0;
    background-color: rgba(30, 41, 59, 0.65);
}
QPushButton:disabled { opacity: 0.4; }
"""

WINDOW_BTN = f"""
QPushButton {{
    min-width: {WINDOW_CTRL_SIZE}px;
    max-width: {WINDOW_CTRL_SIZE}px;
    min-height: {WINDOW_CTRL_SIZE}px;
    max-height: {WINDOW_CTRL_SIZE}px;
    width: {WINDOW_CTRL_SIZE}px;
    height: {WINDOW_CTRL_SIZE}px;
    padding: 0px;
    border-radius: 8px;
    font-size: 13px;
    border: 1px solid rgba(255, 255, 255, 0.14);
    background-color: rgba(15, 23, 42, 0.55);
    color: #f8fafc;
}}
QPushButton:hover {{ background-color: rgba(51, 65, 85, 0.75); }}
"""

ICON_BTN = WINDOW_BTN

PILL_RUNNING = "color: #86efac; font-size: 12px; font-style: italic;"
PILL_STOPPED = "color: #fca5a5; font-size: 12px; font-style: italic;"
PILL_BUSY = "color: #fcd34d; font-size: 12px; font-style: italic;"

BACKDROP_COLOR = "15, 23, 42"
BACKDROP_ALPHA_DIM = 77  # 30%
BACKDROP_ALPHA_DARK = 255


def backdrop_fill(alpha: int) -> str:
    return f"""
QWidget#backdropFill {{
    background-color: rgba({BACKDROP_COLOR}, {alpha});
    border-radius: {WINDOW_RADIUS}px;
}}
"""


BACKDROP_FILL = backdrop_fill(BACKDROP_ALPHA_DIM)
BACKDROP_FILL_DARK = backdrop_fill(BACKDROP_ALPHA_DARK)

DRAG_BAR = """
QWidget#dragBar {
    background-color: rgba(15, 23, 42, 0.45);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
"""

GLASS_PANEL = """
QWidget#glassPanel {
    background-color: rgba(15, 23, 42, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
}
"""

_LIGHT_BASE = (
    "border-radius: 6px; min-width: 11px; max-width: 11px; min-height: 11px; max-height: 11px;"
)
LIGHT_GREEN = _LIGHT_BASE + " background-color: #22c55e; border: 1px solid #86efac;"
LIGHT_YELLOW = _LIGHT_BASE + " background-color: #eab308; border: 1px solid #fde047;"
LIGHT_RED = _LIGHT_BASE + " background-color: #ef4444; border: 1px solid #fca5a5;"
LIGHT_OFF = _LIGHT_BASE + " background-color: #475569; border: 1px solid #64748b;"
