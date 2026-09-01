from typing import Any, Dict, List, Optional

from PySide6.QtCore import QDate, QDateTime, QEvent, QTimer, Qt, QTime
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QScrollArea,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.record import Record
from presentation.components.app_button import AppButton
from presentation.components.field_input_widgets import (
    CheckboxChoiceWidget,
    FilePickerWidget,
    RadioChoiceWidget,
)
from presentation.theme.app_theme import AppTheme
from presentation.viewmodels.record_viewmodel import RecordViewModel


class DataEntryView(QWidget):
    YES_VALUE = "yes"
    NO_VALUE = "no"
    LTR_FIELD_TYPES = {
        FieldType.INTEGER,
        FieldType.DECIMAL,
        FieldType.CURRENCY,
        FieldType.PERCENTAGE,
        FieldType.DATE,
        FieldType.TIME,
        FieldType.DATE_TIME,
        FieldType.DURATION,
        FieldType.PHONE_NUMBER,
        FieldType.EMAIL,
        FieldType.URL,
        FieldType.IDENTIFIER,
        FieldType.NATIONAL_ID,
        FieldType.CODE,
        FieldType.POSTAL_CODE,
        FieldType.COORDINATES,
        FieldType.MEASUREMENT,
        FieldType.WEIGHT,
        FieldType.LENGTH_HEIGHT,
        FieldType.TEMPERATURE,
        FieldType.BARCODE,
        FieldType.QR_CODE,
        FieldType.AUTO_NUMBER,
    }

    def __init__(
        self,
        viewmodel: RecordViewModel,
        project_id: int,
        project_name: str,
        fields: List[Field],
        existing_record: Optional[Record] = None,
    ):
        super().__init__()
        self.viewmodel = viewmodel
        self.project_id = project_id
        self.project_name = project_name
        self.fields = fields
        self.existing_record = existing_record
        self.input_widgets: Dict[int, QWidget] = {}
        self.field_frames: Dict[int, QFrame] = {}
        self.error_labels: Dict[int, QLabel] = {}

        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()
        self.setup_keyboard_navigation()
        if existing_record:
            self._fill_from_record(existing_record)

    def setup_ui(self):
        self.setObjectName("AppRoot")
        self.resize(760, 780)
        self.setMinimumSize(620, 620)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 24, 30, 26)
        main_layout.setSpacing(16)

        head = QVBoxLayout()
        head.setSpacing(3)
        self.title_label = QLabel()
        self.title_label.setProperty("role", "pageTitle")
        self.subtitle_label = QLabel()
        self.subtitle_label.setProperty("role", "muted")
        head.addWidget(self.title_label)
        head.addWidget(self.subtitle_label)
        main_layout.addLayout(head)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        container = QWidget()
        self.form_layout = QVBoxLayout(container)
        self.form_layout.setContentsMargins(2, 4, 8, 4)
        self.form_layout.setSpacing(12)

        for field in self.fields:
            frame = QFrame()
            frame.setProperty("card", True)
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(16, 13, 16, 14)
            frame_layout.setSpacing(7)

            label = QLabel(f"{field.name} " + ("*" if field.is_required else ""))
            label.setProperty("role", "body")
            frame_layout.addWidget(label)

            widget = self._create_widget_for_field(field)
            self._apply_field_direction(field, widget)
            self.input_widgets[field.id] = widget
            self.field_frames[field.id] = frame
            frame_layout.addWidget(widget)

            error_label = QLabel()
            error_label.setProperty("role", "error")
            error_label.setWordWrap(True)
            error_label.hide()
            self.error_labels[field.id] = error_label
            frame_layout.addWidget(error_label)

            self.form_layout.addWidget(frame)

        self.form_layout.addStretch()
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area, 1)

        footer = QFrame()
        footer.setProperty("softCard", True)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(14, 10, 14, 10)
        self.status_label = QLabel()
        self.status_label.setProperty("role", "success")
        footer_layout.addWidget(self.status_label, 1)
        self.save_btn = AppButton(variant=AppButton.SOFT)
        self.save_and_next_btn = AppButton(variant=AppButton.PRIMARY)
        self.save_and_next_btn.setMinimumWidth(220)
        if self.existing_record is not None:
            self.save_and_next_btn.hide()
        footer_layout.addWidget(self.save_btn)
        footer_layout.addWidget(self.save_and_next_btn)
        main_layout.addWidget(footer)

        self.retranslate_ui()

    def _create_widget_for_field(self, field: Field):
        field_type = FieldType.normalize(field.field_type)

        if field_type in {FieldType.LONG_TEXT, FieldType.ADDRESS}:
            widget = QTextEdit()
            widget.setMinimumHeight(92)
            return widget
        if field_type == FieldType.DATE:
            widget = QDateEdit()
            widget.setCalendarPopup(True)
            widget.setDisplayFormat("yyyy-MM-dd")
            widget.setDate(QDate.currentDate())
            widget.setDateRange(QDate(1900, 1, 1), QDate(2100, 12, 31))
            return widget
        if field_type == FieldType.TIME:
            widget = QTimeEdit()
            widget.setDisplayFormat("HH:mm")
            widget.setTime(QTime.currentTime())
            return widget
        if field_type == FieldType.DATE_TIME:
            widget = QDateTimeEdit()
            widget.setCalendarPopup(True)
            widget.setDisplayFormat("yyyy-MM-dd HH:mm")
            widget.setDateTime(QDateTime.currentDateTime())
            widget.setDateRange(QDate(1900, 1, 1), QDate(2100, 12, 31))
            return widget
        if field_type in {FieldType.SINGLE_CHOICE, FieldType.DROPDOWN}:
            widget = QComboBox()
            widget.addItem(self.tr("-- Select --"), "")
            for option in field.options:
                widget.addItem(option.label, option.value)
            return widget
        if field_type == FieldType.MULTIPLE_CHOICE:
            widget = QListWidget()
            widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
            widget.setMaximumHeight(150)
            for option in field.options:
                item = QListWidgetItem(option.label)
                item.setData(99, option.value)
                widget.addItem(item)
            return widget
        if field_type == FieldType.RADIO_BUTTONS:
            return RadioChoiceWidget([(option.label, option.value) for option in field.options])
        if field_type == FieldType.CHECKBOXES:
            return CheckboxChoiceWidget([(option.label, option.value) for option in field.options])
        if field_type == FieldType.YES_NO:
            widget = QComboBox()
            widget.addItem(self.tr("-- Select --"), "")
            widget.addItem(self.tr("Yes"), self.YES_VALUE)
            widget.addItem(self.tr("No"), self.NO_VALUE)
            return widget
        if field_type == FieldType.RATING:
            widget = QComboBox()
            widget.addItem(self.tr("-- Select --"), "")
            for value in range(1, 6):
                widget.addItem("★" * value, str(value))
            return widget
        if field_type == FieldType.SCALE:
            widget = QComboBox()
            widget.addItem(self.tr("-- Select --"), "")
            for value in range(0, 11):
                widget.addItem(str(value), str(value))
            return widget
        if field_type in FieldType.FILE_TYPES:
            mode = FilePickerWidget.MODE_FILE
            if field_type == FieldType.IMAGE:
                mode = FilePickerWidget.MODE_IMAGE
            elif field_type == FieldType.SIGNATURE:
                mode = FilePickerWidget.MODE_SIGNATURE
            return FilePickerWidget(mode)

        widget = QLineEdit()
        if field_type in FieldType.VIRTUAL_TYPES:
            widget.setReadOnly(True)
        return widget

    def _apply_field_direction(self, field: Field, widget: QWidget) -> None:
        field_type = FieldType.normalize(field.field_type)
        if field_type not in self.LTR_FIELD_TYPES:
            return
        widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        if isinstance(widget, QLineEdit):
            widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def setup_connections(self):
        self.save_btn.clicked.connect(lambda: self.on_save(close_on_success=True))
        self.save_and_next_btn.clicked.connect(lambda: self.on_save(close_on_success=False))
        self.viewmodel.error_occurred.connect(self.show_error)
        self.viewmodel.operation_success.connect(self.show_success)
        if hasattr(self.viewmodel, "validation_failed"):
            self.viewmodel.validation_failed.connect(self.show_field_error)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+S"), self, lambda: self.on_save(True))
        QShortcut(QKeySequence("Ctrl+Return"), self, lambda: self.on_save(False))

    def setup_keyboard_navigation(self):
        self._keyboard_widgets = []
        supported = (QLineEdit, QComboBox, QDateEdit, QTimeEdit, QDateTimeEdit)
        for field in self.fields:
            widget = self.input_widgets.get(field.id)
            if not isinstance(widget, supported):
                continue
            if isinstance(widget, QLineEdit) and widget.isReadOnly():
                continue
            widget.installEventFilter(self)
            self._keyboard_widgets.append(widget)
        for current, next_widget in zip(self._keyboard_widgets, self._keyboard_widgets[1:]):
            QWidget.setTabOrder(current, next_widget)
        if self._keyboard_widgets:
            self._keyboard_widgets[0].setFocus()

    def eventFilter(self, watched, event):
        if (
            event.type() == QEvent.Type.KeyPress
            and event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}
            and event.modifiers() == Qt.KeyboardModifier.NoModifier
            and watched in getattr(self, "_keyboard_widgets", [])
        ):
            index = self._keyboard_widgets.index(watched)
            if index < len(self._keyboard_widgets) - 1:
                self._keyboard_widgets[index + 1].setFocus()
            else:
                self.on_save(close_on_success=self.existing_record is not None)
            return True
        return super().eventFilter(watched, event)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Paper2Data - Data Entry: {name}").format(name=self.project_name))
        title = self.tr("Edit Record - {name}") if self.existing_record is not None else self.tr("New Record - {name}")
        self.title_label.setText(title.format(name=self.project_name))
        self.subtitle_label.setText(
            self.tr("Move through the fields with Enter. Paper2Data validates the record before saving.")
        )
        self.save_btn.setText(self.tr("Save"))
        self.save_btn.setToolTip(self.tr("Ctrl+S"))
        self.save_and_next_btn.setText(self.tr("Save & Next →"))
        self.save_and_next_btn.setToolTip(self.tr("Ctrl+Enter"))
        for field in self.fields:
            widget = self.input_widgets.get(field.id)
            if widget is not None:
                self._retranslate_field_widget(field, widget)

    def _retranslate_field_widget(self, field: Field, widget: QWidget) -> None:
        field_type = FieldType.normalize(field.field_type)
        if isinstance(widget, (QLineEdit, QTextEdit)):
            placeholders = {
                FieldType.INTEGER: self.tr("Enter an integer..."),
                FieldType.DECIMAL: self.tr("Enter a decimal number..."),
                FieldType.CURRENCY: self.tr("Enter an amount..."),
                FieldType.PERCENTAGE: self.tr("Enter percentage (0-100)..."),
                FieldType.DURATION: self.tr("Enter duration as HH:MM..."),
                FieldType.PHONE_NUMBER: self.tr("Enter a phone number..."),
                FieldType.EMAIL: self.tr("Enter an email address..."),
                FieldType.URL: self.tr("Enter a URL (https://...)..."),
                FieldType.COORDINATES: self.tr("Enter latitude, longitude..."),
                FieldType.MEASUREMENT: self.tr("Enter value and unit (e.g. 180 cm)..."),
                FieldType.WEIGHT: self.tr("Enter weight (e.g. 75 kg)..."),
                FieldType.LENGTH_HEIGHT: self.tr("Enter length/height (e.g. 175 cm)..."),
                FieldType.TEMPERATURE: self.tr("Enter temperature (e.g. 37.2 C)..."),
                FieldType.BARCODE: self.tr("Enter or scan barcode value..."),
                FieldType.QR_CODE: self.tr("Enter or scan QR code value..."),
                FieldType.CALCULATED: self.tr("Calculated automatically after formula setup"),
                FieldType.AUTO_NUMBER: self.tr("Generated automatically when saved"),
            }
            widget.setPlaceholderText(placeholders.get(field_type, self.tr("Enter {name}...").format(name=field.name)))
        if isinstance(widget, QComboBox) and widget.count() > 0:
            current_data = widget.currentData()
            widget.setItemText(0, self.tr("-- Select --"))
            if field_type == FieldType.YES_NO and widget.count() >= 3:
                widget.setItemText(1, self.tr("Yes"))
                widget.setItemText(2, self.tr("No"))
            index = widget.findData(current_data)
            if index >= 0:
                widget.setCurrentIndex(index)

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange and hasattr(self, "save_btn"):
            self.retranslate_ui()
        super().changeEvent(event)

    def _collect_form_data(self) -> Dict[int, Any]:
        form_data: Dict[int, Any] = {}
        for field in self.fields:
            widget = self.input_widgets[field.id]
            field_type = FieldType.normalize(field.field_type)
            if field_type == FieldType.DATE and isinstance(widget, QDateEdit):
                value = widget.date().toString("yyyy-MM-dd")
            elif field_type == FieldType.TIME and isinstance(widget, QTimeEdit):
                value = widget.time().toString("HH:mm")
            elif field_type == FieldType.DATE_TIME and isinstance(widget, QDateTimeEdit):
                value = widget.dateTime().toString("yyyy-MM-dd HH:mm")
            elif isinstance(widget, QTextEdit):
                value = widget.toPlainText()
            elif isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, QComboBox):
                value = widget.currentData()
            elif isinstance(widget, QListWidget):
                value = ", ".join(item.data(99) or item.text() for item in widget.selectedItems())
            elif isinstance(widget, RadioChoiceWidget):
                value = widget.value()
            elif isinstance(widget, CheckboxChoiceWidget):
                value = ", ".join(widget.values())
            elif isinstance(widget, FilePickerWidget):
                value = widget.value()
            else:
                value = ""
            if field_type == FieldType.AUTO_NUMBER:
                value = ""
            form_data[field.id] = value if value is not None else ""
        return form_data

    def on_save(self, close_on_success: bool):
        self.clear_field_errors()
        record_id = self.existing_record.id if self.existing_record else None
        success = self.viewmodel.save_record(
            self.project_id,
            self.fields,
            self._collect_form_data(),
            record_id=record_id,
        )
        if not success:
            return
        if close_on_success:
            self.close()
        else:
            self.clear_form()
            if self._keyboard_widgets:
                self._keyboard_widgets[0].setFocus()

    def show_field_error(self, field_id: int, message: str) -> None:
        frame = self.field_frames.get(field_id)
        label = self.error_labels.get(field_id)
        if frame is None or label is None:
            self.show_error(message)
            return
        label.setText(message)
        label.show()
        frame.setProperty("fieldError", True)
        frame.setProperty("card", False)
        AppTheme.repolish(frame)
        widget = self.input_widgets.get(field_id)
        if widget is not None:
            widget.setFocus()

    def clear_field_errors(self) -> None:
        for field_id, frame in self.field_frames.items():
            frame.setProperty("fieldError", False)
            frame.setProperty("card", True)
            AppTheme.repolish(frame)
            label = self.error_labels[field_id]
            label.clear()
            label.hide()

    def _fill_from_record(self, record: Record):
        value_map = {value.field_id: "" if value.value is None else str(value.value) for value in record.values}
        for field in self.fields:
            widget = self.input_widgets.get(field.id)
            if widget is None:
                continue
            field_type = FieldType.normalize(field.field_type)
            value = value_map.get(field.id, "")
            if field_type == FieldType.AUTO_NUMBER and isinstance(widget, QLineEdit):
                widget.setText(str(record.id or ""))
            elif field_type == FieldType.DATE and isinstance(widget, QDateEdit):
                parsed = QDate.fromString(value, "yyyy-MM-dd")
                widget.setDate(parsed if parsed.isValid() else QDate.currentDate())
            elif field_type == FieldType.TIME and isinstance(widget, QTimeEdit):
                parsed = QTime.fromString(value, "HH:mm")
                widget.setTime(parsed if parsed.isValid() else QTime.currentTime())
            elif field_type == FieldType.DATE_TIME and isinstance(widget, QDateTimeEdit):
                parsed = QDateTime.fromString(value, "yyyy-MM-dd HH:mm")
                widget.setDateTime(parsed if parsed.isValid() else QDateTime.currentDateTime())
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(value)
            elif isinstance(widget, QLineEdit):
                widget.setText(value)
            elif isinstance(widget, QComboBox):
                normalized_value = self._normalize_combo_value(field, value)
                index = widget.findData(normalized_value)
                if index < 0:
                    index = widget.findText(value)
                widget.setCurrentIndex(index if index >= 0 else 0)
            elif isinstance(widget, QListWidget):
                chosen = {part.strip() for part in value.split(",") if part.strip()}
                for index in range(widget.count()):
                    item = widget.item(index)
                    item.setSelected((item.data(99) or item.text()) in chosen or item.text() in chosen)
            elif isinstance(widget, RadioChoiceWidget):
                widget.set_value(value)
            elif isinstance(widget, CheckboxChoiceWidget):
                widget.set_values(value.split(","))
            elif isinstance(widget, FilePickerWidget):
                widget.set_value(value)

    def _normalize_combo_value(self, field: Field, value: str) -> str:
        if FieldType.normalize(field.field_type) != FieldType.YES_NO:
            return value
        lowered = value.strip().lower()
        if lowered in {"yes", "نعم", self.YES_VALUE}:
            return self.YES_VALUE
        if lowered in {"no", "لا", self.NO_VALUE}:
            return self.NO_VALUE
        return value

    def clear_form(self):
        self.clear_field_errors()
        for field in self.fields:
            widget = self.input_widgets[field.id]
            field_type = FieldType.normalize(field.field_type)
            if field_type == FieldType.DATE and isinstance(widget, QDateEdit):
                widget.setDate(QDate.currentDate())
            elif field_type == FieldType.TIME and isinstance(widget, QTimeEdit):
                widget.setTime(QTime.currentTime())
            elif field_type == FieldType.DATE_TIME and isinstance(widget, QDateTimeEdit):
                widget.setDateTime(QDateTime.currentDateTime())
            elif isinstance(widget, QTextEdit):
                widget.clear()
            elif isinstance(widget, QLineEdit):
                if field_type not in FieldType.VIRTUAL_TYPES:
                    widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QListWidget):
                widget.clearSelection()
            elif isinstance(widget, RadioChoiceWidget):
                widget.clear_value()
            elif isinstance(widget, CheckboxChoiceWidget):
                widget.clear_values()
            elif isinstance(widget, FilePickerWidget):
                widget.clear_value()

    def show_error(self, message: str):
        QMessageBox.critical(self, self.tr("Error"), message)

    def show_success(self, message: str):
        self.status_label.setText("✓ " + message)
        QTimer.singleShot(2200, self.status_label.clear)
