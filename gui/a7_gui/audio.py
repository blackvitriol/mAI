from __future__ import annotations

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from .paths import asset_path


class BackgroundMusic:
    def __init__(self, parent=None) -> None:
        self._muted = False
        self._available = False
        self._player = QMediaPlayer(parent)
        self._audio = QAudioOutput(parent)
        self._player.setAudioOutput(self._audio)
        self._audio.setVolume(0.45)

        track = asset_path("pixel_breakout.mp3")
        if track.is_file():
            self._player.setSource(QUrl.fromLocalFile(str(track.resolve())))
            self._player.mediaStatusChanged.connect(self._loop_on_end)
            self._available = True

    def start(self) -> None:
        if self._available and not self._muted:
            self._player.play()

    def stop(self) -> None:
        if self._available:
            self._player.stop()

    def set_muted(self, muted: bool) -> None:
        self._muted = muted
        self._audio.setMuted(muted)
        if not muted and self._available:
            if self._player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
                self._player.play()

    def is_muted(self) -> bool:
        return self._muted

    def _loop_on_end(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia and not self._muted:
            self._player.setPosition(0)
            self._player.play()
