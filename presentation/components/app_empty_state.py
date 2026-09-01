from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from presentation.components.app_button import AppButton


class AppEmptyState(QWidget):
    """Reusable friendly empty state with one clear next action."""

    action_clicked = Signal()

    def __init__(self, title: str = "", body: str = "", action_text: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 42, 36, 42)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.symbol_label = QLabel("＋")
        self.symbol_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.symbol_label.setProperty("role", "brand")
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setProperty("role", "sectionTitle")
        self.body_label = QLabel(body)
        self.body_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.body_label.setWordWrap(True)
        self.body_label.setProperty("role", "muted")
        self.action_btn = AppButton(action_text, AppButton.PRIMARY)
        self.action_btn.clicked.connect(self.action_clicked)

        layout.addWidget(self.symbol_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.body_label)
        layout.addSpacing(6)
        layout.addWidget(self.action_btn, 0, Qt.AlignmentFlag.AlignCenter)

    def set_content(self, title: str, body: str, action_text: str) -> None:
        self.title_label.setText(title)
        self.body_label.setText(body)
        self.action_btn.setText(action_text)
