from PySide6.QtCore import QObject, QSettings, Signal

from presentation.theme.app_theme import AppTheme


class ThemeService(QObject):
    """Persists and applies the global light/dark Paper2Data appearance."""

    theme_changed = Signal(str)
    LIGHT = "light"
    DARK = "dark"

    def __init__(self, app):
        super().__init__()
        self._app = app
        self._settings = QSettings("Paper2Data", "Paper2Data")
        self._current_mode = self.LIGHT

    @property
    def current_mode(self) -> str:
        return self._current_mode

    @property
    def is_dark(self) -> bool:
        return self._current_mode == self.DARK

    def initialize(self) -> str:
        saved = str(self._settings.value("appearance", self.LIGHT)).lower()
        if saved not in {self.LIGHT, self.DARK}:
            saved = self.LIGHT
        self.apply(saved)
        return self._current_mode

    def apply(self, mode: str) -> None:
        normalized = self.DARK if mode == self.DARK else self.LIGHT
        self._current_mode = normalized
        self._settings.setValue("appearance", normalized)
        self._app.setStyleSheet(AppTheme.stylesheet(normalized))
        self.theme_changed.emit(normalized)

    def toggle(self) -> str:
        next_mode = self.LIGHT if self.is_dark else self.DARK
        self.apply(next_mode)
        return next_mode
