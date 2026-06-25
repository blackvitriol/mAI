from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsOpacityEffect,
    QMainWindow,
    QMenu,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from .server_control import ServerController, ServerStatus
from .audio import BackgroundMusic
from .fonts import init_fonts
from .tray import TrayController
from .widgets.background import BackgroundWidget, window_size_for_background
from .widgets.chrome import TitleBar, WindowControls
from .widgets.drag_bar import DragBar
from .widgets.effects import fade_in_widget
from .widgets.stack_controls import StackControlsPanel
from .widgets.stack_status import StackStatusPanel
from .widgets.window_shape import apply_rounded_mask

POLL_MS = 3000
WINDOW_FADE_MS = 3000


class _ActionWorker(QThread):
    finished_ok = pyqtSignal(str)
    finished_err = pyqtSignal(str)

    def __init__(self, fn, parent=None) -> None:
        super().__init__(parent)
        self._fn = fn

    def run(self) -> None:
        try:
            message = self._fn()
            self.finished_ok.emit(message)
        except Exception as exc:  # noqa: BLE001
            self.finished_err.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._controller = ServerController()
        self._worker: _ActionWorker | None = None
        self._last_status: ServerStatus | None = None
        self._status_error: str | None = None
        self._intro_played = False
        self._force_quit = False
        self._tray: TrayController | None = None
        self._music = BackgroundMusic(self)
        self._music_started = False
        self._window_fade_anim: QPropertyAnimation | None = None

        self.setWindowTitle("A7 Server")
        window_size = window_size_for_background()
        self.setFixedSize(window_size)
        self._base_window_flags = (
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        )
        self.setWindowFlags(self._base_window_flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        central = QWidget()
        central.setObjectName("appShell")
        central.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCentralWidget(central)

        self._background = BackgroundWidget(central)
        overlay = QWidget(central)
        overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._drag_bar = DragBar(overlay)
        self._title = TitleBar(overlay)

        self._window_controls = WindowControls(overlay)
        self._window_controls.minimize_requested.connect(self.minimize_to_tray)
        self._window_controls.close_requested.connect(self.minimize_to_tray)
        self._window_controls.backdrop_toggled.connect(self._background.set_backdrop_dark)
        self._window_controls.pin_toggled.connect(self._set_always_on_top)
        self._window_controls.mute_toggled.connect(self._music.set_muted)

        self._status_panel = StackStatusPanel(overlay)
        self._controls_panel = StackControlsPanel(overlay)
        self._controls_panel.init_requested.connect(lambda: self._run_action("init"))
        self._controls_panel.start_requested.connect(lambda: self._run_action("start"))
        self._controls_panel.stop_requested.connect(lambda: self._run_action("stop"))
        self._controls_panel.restart_requested.connect(lambda: self._run_action("restart"))
        self._controls_panel.container_action_requested.connect(self._run_container_action)

        layout = QVBoxLayout(overlay)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(10)
        layout.addWidget(self._drag_bar)
        layout.addWidget(self._title)
        layout.addWidget(self._status_panel)
        layout.addWidget(self._controls_panel, stretch=1)

        self._context_menu = QMenu(self)
        self._context_show = QAction("Show", self)
        self._context_tray = QAction("Minimize to tray", self)
        self._context_exit = QAction("Exit", self)
        self._context_menu.addAction(self._context_show)
        self._context_menu.addAction(self._context_tray)
        self._context_menu.addSeparator()
        self._context_menu.addAction(self._context_exit)
        self._context_show.triggered.connect(self.show_window)
        self._context_tray.triggered.connect(self.minimize_to_tray)
        self._context_exit.triggered.connect(self.force_quit)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh_status)
        self._timer.start(POLL_MS)

        for panel in (self._status_panel, self._controls_panel):
            effect = QGraphicsOpacityEffect(panel)
            panel.setGraphicsEffect(effect)
            effect.setOpacity(0.0)

        self.refresh_status()
        self.setWindowOpacity(0.0)

    def _fade_in_window(self) -> None:
        self._window_fade_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._window_fade_anim.setDuration(WINDOW_FADE_MS)
        self._window_fade_anim.setStartValue(0.0)
        self._window_fade_anim.setEndValue(1.0)
        self._window_fade_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._window_fade_anim.start()

    def attach_tray(self, tray: TrayController) -> None:
        self._tray = tray

    def _set_always_on_top(self, pinned: bool) -> None:
        flags = self._base_window_flags
        if pinned:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self._sync_layout()

    def show_window(self) -> None:
        self.setWindowOpacity(1.0)
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def minimize_to_tray(self) -> None:
        if self._tray is not None:
            self._tray.minimize_to_tray()
        else:
            self.hide()

    def force_quit(self) -> None:
        self._force_quit = True
        self._music.stop()
        QApplication.instance().quit()

    def contextMenuEvent(self, event) -> None:  # noqa: N802
        self._context_menu.exec(event.globalPos())

    def changeEvent(self, event) -> None:  # noqa: N802
        if event.type() == QEvent.Type.WindowStateChange and self.isMinimized():
            QTimer.singleShot(0, self.minimize_to_tray)
        super().changeEvent(event)

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._force_quit:
            event.accept()
            return
        event.ignore()
        self.minimize_to_tray()

    def _sync_layout(self) -> None:
        central = self.centralWidget()
        if central is not None:
            self._background.setGeometry(central.rect())
            overlay = self._status_panel.parentWidget()
            if overlay is not None:
                overlay.setGeometry(central.rect())
            self._window_controls.move(
                self.width() - self._window_controls.width() - 8, 6
            )
        apply_rounded_mask(self)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._sync_layout()
        if not self._intro_played:
            self._intro_played = True
            self._fade_in_window()
            self._play_intro()
        if not self._music_started:
            self._music_started = True
            self._music.start()

    def _play_intro(self) -> None:
        self._title.start_typewriter()
        fade_in_widget(self._status_panel, delay_ms=280, duration_ms=520)
        fade_in_widget(self._controls_panel, delay_ms=460, duration_ms=540)
        QTimer.singleShot(640, lambda: self._controls_panel.fade_in_rows(0))

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._sync_layout()

    def refresh_status(self) -> None:
        try:
            self._last_status = self._controller.get_status()
            self._status_error = None
        except Exception as exc:  # noqa: BLE001
            self._status_error = str(exc)
        self._status_panel.update_status(self._last_status, False, self._status_error)
        self._controls_panel.update_status(self._last_status)

    def _run_action(self, action: str) -> None:
        if self._worker is not None and self._worker.isRunning():
            return

        labels = {
            "init": "Initializing…",
            "start": "Starting…",
            "stop": "Stopping…",
            "restart": "Restarting…",
        }
        fns = {
            "init": self._controller.run_init,
            "start": self._controller.start_server,
            "stop": self._controller.stop_server,
            "restart": self._controller.restart_server,
        }

        self._controls_panel.set_busy(True, labels[action])
        self._controls_panel.set_feedback(None, None)
        self._worker = _ActionWorker(fns[action], self)
        self._worker.finished_ok.connect(self._on_action_ok)
        self._worker.finished_err.connect(self._on_action_err)
        self._worker.finished.connect(self._on_action_done)
        self._worker.start()

    def _run_container_action(self, service: str, action: str) -> None:
        if self._worker is not None and self._worker.isRunning():
            return

        self._controls_panel.set_busy(True, f"{service} {action}…")
        self._controls_panel.set_feedback(None, None)
        self._worker = _ActionWorker(
            lambda: self._controller.control_container(service, action),
            self,
        )
        self._worker.finished_ok.connect(self._on_action_ok)
        self._worker.finished_err.connect(self._on_action_err)
        self._worker.finished.connect(self._on_action_done)
        self._worker.start()

    def _on_action_ok(self, message: str) -> None:
        self._controls_panel.set_feedback(message, None)

    def _on_action_err(self, message: str) -> None:
        self._controls_panel.set_feedback(None, message)

    def _on_action_done(self) -> None:
        self._controls_panel.set_busy(False)
        self.refresh_status()


def run_app() -> None:
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    init_fonts(app)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("[WARN] System tray is not available on this platform.")

    window = MainWindow()
    if QSystemTrayIcon.isSystemTrayAvailable():
        tray = TrayController(window)
        window.attach_tray(tray)

    window.show()
    app.exec()
