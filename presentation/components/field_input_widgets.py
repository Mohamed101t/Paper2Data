from typing import Iterable, Optional, Sequence, Tuple

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)


Choice = Tuple[str, str]


class RadioChoiceWidget(QWidget):
    """Visible single-choice input that stores stable option values."""

    def __init__(self, options: Sequence[Choice], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._buttons: list[tuple[QRadioButton, str]] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for label, value in options:
            button = QRadioButton(label)
            self._buttons.append((button, value))
            layout.addWidget(button)

    def value(self) -> str:
        for button, value in self._buttons:
            if button.isChecked():
                return value
        return ""

    def set_value(self, value: str) -> None:
        for button, option_value in self._buttons:
            button.setChecked(option_value == value or button.text() == value)

    def clear_value(self) -> None:
        for button, _value in self._buttons:
            button.setAutoExclusive(False)
            button.setChecked(False)
            button.setAutoExclusive(True)


class CheckboxChoiceWidget(QWidget):
    """Visible multiple-choice input that stores stable option values."""

    def __init__(self, options: Sequence[Choice], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._boxes: list[tuple[QCheckBox, str]] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        for label, value in options:
            box = QCheckBox(label)
            self._boxes.append((box, value))
            layout.addWidget(box)

    def values(self) -> list[str]:
        return [value for box, value in self._boxes if box.isChecked()]

    def set_values(self, values: Iterable[str]) -> None:
        selected = {value.strip() for value in values if value.strip()}
        for box, option_value in self._boxes:
            box.setChecked(option_value in selected or box.text() in selected)

    def clear_values(self) -> None:
        for box, _value in self._boxes:
            box.setChecked(False)


class FilePickerWidget(QWidget):
    """Reusable local-file picker. Stores only the selected local path."""

    MODE_FILE = "file"
    MODE_IMAGE = "image"
    MODE_SIGNATURE = "signature"

    def __init__(self, mode: str = MODE_FILE, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._mode = mode
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.path_input = QLineEdit()
        self.browse_btn = QPushButton()
        self.clear_btn = QPushButton()
        self.path_input.setReadOnly(True)

        layout.addWidget(self.path_input, 1)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.clear_btn)

        self.browse_btn.clicked.connect(self._browse)
        self.clear_btn.clicked.connect(self.clear_value)
        self.retranslate_ui()

    def value(self) -> str:
        return self.path_input.text().strip()

    def set_value(self, value: str) -> None:
        self.path_input.setText(value or "")

    def clear_value(self) -> None:
        self.path_input.clear()

    def retranslate_ui(self) -> None:
        self.browse_btn.setText(self.tr("Browse..."))
        self.clear_btn.setText(self.tr("Clear"))
        self.path_input.setPlaceholderText(self.tr("No file selected"))

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange and hasattr(self, "browse_btn"):
            self.retranslate_ui()
        super().changeEvent(event)

    def _browse(self) -> None:
        if self._mode in {self.MODE_IMAGE, self.MODE_SIGNATURE}:
            title = (
                self.tr("Select Image")
                if self._mode == self.MODE_IMAGE
                else self.tr("Select Signature Image")
            )
            file_filter = self.tr(
                "Image Files (*.png *.jpg *.jpeg *.bmp *.webp);;All Files (*.*)"
            )
        else:
            title = self.tr("Select File")
            file_filter = self.tr("All Files (*.*)")

        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            title,
            "",
            file_filter,
        )
        if file_path:
            self.set_value(file_path)
