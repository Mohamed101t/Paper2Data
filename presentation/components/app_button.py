from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


class AppButton(QPushButton):
    """Design-system button. Use variants instead of one-off stylesheets."""

    PRIMARY = "primary"
    SOFT = "soft"
    GHOST = "ghost"
    DANGER = "danger"
    SUCCESS = "success"
    DEFAULT = "default"

    def __init__(self, text: str = "", variant: str = DEFAULT, parent=None):
        super().__init__(text, parent)
        self.setProperty("variant", variant)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
