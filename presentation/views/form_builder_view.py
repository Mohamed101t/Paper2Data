from typing import Optional

from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from core.database.database_service import DatabaseService
from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.field_type import FieldType
from domain.services.field_type_suggester import FieldTypeSuggester
from presentation.components.app_button import AppButton
from presentation.components.field_type_picker import FieldTypePickerDialog
from presentation.viewmodels.field_viewmodel import FieldViewModel
from presentation.viewmodels.record_viewmodel import RecordViewModel
from presentation.viewmodels.records_list_viewmodel import RecordsListViewModel
from presentation.views.data_entry_view import DataEntryView
from presentation.views.records_view import RecordsView


class FormBuilderView(QWidget):
    def __init__(
        self,
        viewmodel: FieldViewModel,
        project_id: int,
        project_name: str,
        db_service: DatabaseService,
    ):
        super().__init__()
        self.viewmodel = viewmodel
        self.project_id = project_id
        self.project_name = project_name
        self.db_service = db_service
        self.data_entry_window: Optional[QWidget] = None
        self.records_window: Optional[QWidget] = None
        self.suggested_type: Optional[str] = None

        self.setup_ui()
        self.setup_connections()
        self.viewmodel.set_project(self.project_id)

    def setup_ui(self):
        self.setObjectName("AppRoot")
        self.resize(1040, 760)
        self.setMinimumSize(860, 650)
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 28)
        root.setSpacing(20)

        header = QHBoxLayout()
        self.back_btn = AppButton(variant=AppButton.GHOST)
        header.addWidget(self.back_btn)
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        self.title_label = QLabel()
        self.title_label.setProperty("role", "pageTitle")
        self.subtitle_label = QLabel()
        self.subtitle_label.setProperty("role", "muted")
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.subtitle_label)
        header.addLayout(title_box, 1)
        root.addLayout(header)

        self.editor_card = QFrame()
        self.editor_card.setProperty("card", True)
        editor = QVBoxLayout(self.editor_card)
        editor.setContentsMargins(22, 20, 22, 20)
        editor.setSpacing(14)

        self.editor_title = QLabel()
        self.editor_title.setProperty("role", "sectionTitle")
        editor.addWidget(self.editor_title)

        name_row = QHBoxLayout()
        self.name_label = QLabel()
        self.name_label.setMinimumWidth(95)
        self.name_input = QLineEdit()
        name_row.addWidget(self.name_label)
        name_row.addWidget(self.name_input, 1)
        editor.addLayout(name_row)

        type_row = QHBoxLayout()
        self.type_label = QLabel()
        self.type_label.setMinimumWidth(95)
        self.type_combo = QComboBox()
        self.type_combo.setMinimumWidth(220)
        self.more_types_btn = AppButton(variant=AppButton.SOFT)
        self.required_check = QCheckBox()
        type_row.addWidget(self.type_label)
        type_row.addWidget(self.type_combo, 1)
        type_row.addWidget(self.more_types_btn)
        type_row.addWidget(self.required_check)
        editor.addLayout(type_row)

        smart_row = QHBoxLayout()
        self.type_info_label = QLabel()
        self.type_info_label.setWordWrap(True)
        self.type_info_label.setProperty("role", "helper")
        self.suggestion_label = QLabel()
        self.suggestion_label.setProperty("role", "body")
        self.use_suggestion_btn = AppButton(variant=AppButton.SOFT)
        self.use_suggestion_btn.setVisible(False)
        smart_row.addWidget(self.type_info_label, 1)
        smart_row.addWidget(self.suggestion_label)
        smart_row.addWidget(self.use_suggestion_btn)
        editor.addLayout(smart_row)

        options_row = QHBoxLayout()
        self.options_label = QLabel()
        self.options_label.setMinimumWidth(95)
        self.options_input = QLineEdit()
        self.options_input.setEnabled(False)
        options_row.addWidget(self.options_label)
        options_row.addWidget(self.options_input, 1)
        editor.addLayout(options_row)

        editor_actions = QHBoxLayout()
        editor_actions.addStretch()
        self.update_field_btn = AppButton(variant=AppButton.SOFT)
        self.add_btn = AppButton(variant=AppButton.PRIMARY)
        editor_actions.addWidget(self.update_field_btn)
        editor_actions.addWidget(self.add_btn)
        editor.addLayout(editor_actions)
        root.addWidget(self.editor_card)

        fields_head = QHBoxLayout()
        self.fields_title = QLabel()
        self.fields_title.setProperty("role", "sectionTitle")
        self.fields_hint = QLabel()
        self.fields_hint.setProperty("role", "muted")
        fields_head.addWidget(self.fields_title)
        fields_head.addWidget(self.fields_hint)
        fields_head.addStretch()
        self.move_up_btn = AppButton("↑", AppButton.GHOST)
        self.move_down_btn = AppButton("↓", AppButton.GHOST)
        self.delete_btn = AppButton(variant=AppButton.DANGER)
        fields_head.addWidget(self.move_up_btn)
        fields_head.addWidget(self.move_down_btn)
        fields_head.addWidget(self.delete_btn)
        root.addLayout(fields_head)

        self.fields_list = QListWidget()
        root.addWidget(self.fields_list, 1)
        self.no_fields_label = QLabel()
        self.no_fields_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_fields_label.setProperty("role", "muted")
        self.no_fields_label.setWordWrap(True)
        root.addWidget(self.no_fields_label)

        bottom = QHBoxLayout()
        self.view_records_btn = AppButton(variant=AppButton.SOFT)
        self.start_entry_btn = AppButton(variant=AppButton.PRIMARY)
        self.start_entry_btn.setMinimumWidth(220)
        bottom.addWidget(self.view_records_btn)
        bottom.addStretch()
        bottom.addWidget(self.start_entry_btn)
        root.addLayout(bottom)

        self.retranslate_ui()

    def setup_connections(self):
        self.name_input.textChanged.connect(self.on_name_changed)
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        self.more_types_btn.clicked.connect(self.on_more_types_clicked)
        self.use_suggestion_btn.clicked.connect(self.apply_suggestion)
        self.add_btn.clicked.connect(self.on_add_clicked)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        self.move_up_btn.clicked.connect(lambda: self.on_move(-1))
        self.move_down_btn.clicked.connect(lambda: self.on_move(1))
        self.update_field_btn.clicked.connect(self.on_update_clicked)
        self.fields_list.currentItemChanged.connect(self.on_field_selected)
        self.back_btn.clicked.connect(self.close)
        self.start_entry_btn.clicked.connect(self.open_data_entry)
        self.view_records_btn.clicked.connect(self.open_records_view)
        self.viewmodel.fields_loaded.connect(self.update_fields_list)
        self.viewmodel.error_occurred.connect(self.show_error)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Paper2Data - Form Builder: {name}").format(name=self.project_name))
        self.back_btn.setText(self.tr("← Projects"))
        self.title_label.setText(self.project_name)
        self.subtitle_label.setText(self.tr("Tell Paper2Data what information appears on your paper form."))
        self.editor_title.setText(self.tr("Add a field"))
        self.name_label.setText(self.tr("Field name"))
        self.name_input.setPlaceholderText(self.tr("Example: Age, phone number, birth date..."))
        self.type_label.setText(self.tr("Data type"))
        self.more_types_btn.setText(self.tr("Browse all types"))
        self.required_check.setText(self.tr("Required"))
        self.options_label.setText(self.tr("Options"))
        self.options_input.setPlaceholderText(self.tr("Separate options with commas, e.g. Male, Female"))
        self.use_suggestion_btn.setText(self.tr("Use suggestion"))
        self.add_btn.setText(self.tr("＋ Add Field"))
        self.update_field_btn.setText(self.tr("Update selected"))
        self.fields_title.setText(self.tr("Fields in this form"))
        self.fields_hint.setText(self.tr("Select a field to edit or reorder it."))
        self.delete_btn.setText(self.tr("Delete"))
        self.view_records_btn.setText(self.tr("View records"))
        self.start_entry_btn.setText(self.tr("Start data entry →"))
        self.no_fields_label.setText(self.tr("No fields yet. Add the first piece of information that appears on your paper form."))
        self._rebuild_type_combo()
        self._update_suggestion_ui()
        self._update_type_info()

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange and hasattr(self, "type_combo"):
            self.retranslate_ui()
            self.viewmodel.load_fields()
        super().changeEvent(event)

    def _field_type_labels(self):
        return {
            FieldType.SHORT_TEXT: self.tr("Short Text"),
            FieldType.LONG_TEXT: self.tr("Long Text"),
            FieldType.INTEGER: self.tr("Integer"),
            FieldType.DECIMAL: self.tr("Decimal"),
            FieldType.CURRENCY: self.tr("Currency"),
            FieldType.PERCENTAGE: self.tr("Percentage"),
            FieldType.DATE: self.tr("Date"),
            FieldType.TIME: self.tr("Time"),
            FieldType.DATE_TIME: self.tr("Date & Time"),
            FieldType.DURATION: self.tr("Duration"),
            FieldType.YES_NO: self.tr("Yes / No"),
            FieldType.SINGLE_CHOICE: self.tr("Single Choice"),
            FieldType.MULTIPLE_CHOICE: self.tr("Multiple Choice"),
            FieldType.DROPDOWN: self.tr("Dropdown"),
            FieldType.RADIO_BUTTONS: self.tr("Radio Buttons"),
            FieldType.CHECKBOXES: self.tr("Checkboxes"),
            FieldType.RATING: self.tr("Rating"),
            FieldType.SCALE: self.tr("Scale"),
            FieldType.PHONE_NUMBER: self.tr("Phone Number"),
            FieldType.EMAIL: self.tr("Email"),
            FieldType.URL: self.tr("URL"),
            FieldType.IDENTIFIER: self.tr("Identifier / ID"),
            FieldType.NATIONAL_ID: self.tr("National ID"),
            FieldType.CODE: self.tr("Code"),
            FieldType.POSTAL_CODE: self.tr("Postal Code"),
            FieldType.ADDRESS: self.tr("Address"),
            FieldType.COUNTRY: self.tr("Country"),
            FieldType.STATE_PROVINCE: self.tr("State / Province"),
            FieldType.CITY: self.tr("City"),
            FieldType.COORDINATES: self.tr("Latitude / Longitude"),
            FieldType.MEASUREMENT: self.tr("Measurement"),
            FieldType.WEIGHT: self.tr("Weight"),
            FieldType.LENGTH_HEIGHT: self.tr("Length / Height"),
            FieldType.TEMPERATURE: self.tr("Temperature"),
            FieldType.FILE_ATTACHMENT: self.tr("File Attachment"),
            FieldType.IMAGE: self.tr("Image"),
            FieldType.SIGNATURE: self.tr("Signature"),
            FieldType.BARCODE: self.tr("Barcode"),
            FieldType.QR_CODE: self.tr("QR Code"),
            FieldType.CALCULATED: self.tr("Calculated Field"),
            FieldType.AUTO_NUMBER: self.tr("Auto Number"),
        }

    def _category_labels(self):
        return {
            FieldType.CATEGORY_TEXT: self.tr("Text"),
            FieldType.CATEGORY_NUMBERS: self.tr("Numbers"),
            FieldType.CATEGORY_DATE_TIME: self.tr("Date & Time"),
            FieldType.CATEGORY_CHOICES: self.tr("Choices"),
            FieldType.CATEGORY_CONTACT: self.tr("Contact"),
            FieldType.CATEGORY_LOCATION: self.tr("Location"),
            FieldType.CATEGORY_MEASUREMENT: self.tr("Measurements"),
            FieldType.CATEGORY_FILES: self.tr("Files"),
            FieldType.CATEGORY_IDENTIFIERS: self.tr("Identifiers & Codes"),
            FieldType.CATEGORY_ADVANCED: self.tr("Advanced"),
        }

    def _field_type_label(self, field_type: str) -> str:
        normalized = FieldType.normalize(field_type)
        return self._field_type_labels().get(normalized, FieldType.source_label(normalized))

    def _category_label(self, category: str) -> str:
        return self._category_labels().get(category, category)

    def _rebuild_type_combo(self):
        selected_type = FieldType.normalize(self.type_combo.currentData())
        self.type_combo.blockSignals(True)
        self.type_combo.clear()
        labels = self._field_type_labels()
        for field_type in FieldType.BASIC_TYPES:
            self.type_combo.addItem(labels[field_type], field_type)
        if selected_type in FieldType.ALL and self.type_combo.findData(selected_type) < 0:
            self.type_combo.addItem(labels[selected_type], selected_type)
        index = self.type_combo.findData(selected_type)
        self.type_combo.setCurrentIndex(index if index >= 0 else 0)
        self.type_combo.blockSignals(False)
        self.on_type_changed()

    def _select_field_type(self, field_type: str) -> None:
        normalized = FieldType.normalize(field_type)
        index = self.type_combo.findData(normalized)
        if index < 0:
            self.type_combo.addItem(self._field_type_label(normalized), normalized)
            index = self.type_combo.findData(normalized)
        self.type_combo.setCurrentIndex(index)

    def on_more_types_clicked(self):
        dialog = FieldTypePickerDialog(self._field_type_label, self._category_label, self)
        if dialog.exec() and dialog.selected_type:
            self._select_field_type(dialog.selected_type)

    def on_name_changed(self, name: str) -> None:
        self.suggested_type = FieldTypeSuggester.suggest(name)
        self._update_suggestion_ui()

    def _update_suggestion_ui(self) -> None:
        if not self.suggested_type:
            self.suggestion_label.clear()
            self.use_suggestion_btn.setVisible(False)
            return
        self.suggestion_label.setText(
            self.tr("Suggested: {type}").format(type=self._field_type_label(self.suggested_type))
        )
        self.use_suggestion_btn.setVisible(
            FieldType.normalize(self.type_combo.currentData()) != self.suggested_type
        )

    def apply_suggestion(self) -> None:
        if self.suggested_type:
            self._select_field_type(self.suggested_type)

    def _update_type_info(self) -> None:
        field_type = self.type_combo.currentData()
        if not field_type:
            self.type_info_label.clear()
            return
        self.type_info_label.setText(
            self.tr("Example: {example}").format(example=FieldType.source_example(field_type))
        )

    def on_type_changed(self, _index=None):
        field_type = self.type_combo.currentData()
        enabled = FieldType.uses_options(field_type)
        self.options_input.setEnabled(enabled)
        if not enabled:
            self.options_input.clear()
        self._update_type_info()
        self._update_suggestion_ui()

    def on_add_clicked(self):
        self.viewmodel.add_field(
            self.name_input.text(),
            self.type_combo.currentData(),
            self.required_check.isChecked(),
            self.options_input.text(),
        )
        self.name_input.clear()
        self.options_input.clear()
        self.required_check.setChecked(False)

    def on_delete_clicked(self):
        field_id = self._selected_field_id()
        if field_id is None:
            self.show_error(self.tr("Please select a field to delete."))
            return
        self.viewmodel.delete_field(field_id)

    def _selected_field_id(self):
        selected_item = self.fields_list.currentItem()
        return None if selected_item is None else selected_item.data(99)

    def on_move(self, direction: int):
        field_id = self._selected_field_id()
        if field_id is None:
            self.show_error(self.tr("Please select a field first."))
            return
        self.viewmodel.move_field(field_id, direction)

    def on_update_clicked(self):
        field_id = self._selected_field_id()
        if field_id is None:
            self.show_error(self.tr("Please select a field first."))
            return
        self.viewmodel.update_field(
            field_id,
            self.name_input.text(),
            self.type_combo.currentData(),
            self.required_check.isChecked(),
            self.options_input.text(),
        )

    def on_field_selected(self, current, _previous):
        if current is None:
            return
        field_id = current.data(99)
        fields = self._get_current_fields_objects()
        field = next((item for item in fields if item.id == field_id), None)
        if field is None:
            return
        self.name_input.setText(field.name)
        self._select_field_type(field.field_type)
        self.required_check.setChecked(field.is_required)
        self.options_input.setText(", ".join(option.label for option in field.options))

    def open_data_entry(self):
        fields = self._get_current_fields_objects()
        if not fields:
            self.show_error(self.tr("Please add fields to the form before starting data entry."))
            return
        record_vm = RecordViewModel(RecordRepositoryImpl(self.db_service))
        self.data_entry_window = DataEntryView(record_vm, self.project_id, self.project_name, fields)
        self.data_entry_window.show()

    def open_records_view(self):
        records_vm = RecordsListViewModel(
            RecordRepositoryImpl(self.db_service),
            FieldRepositoryImpl(self.db_service),
        )
        # Connect the view before loading data so the first records_loaded signal
        # cannot be lost. This is covered by the E2E GUI smoke test.
        self.records_window = RecordsView(records_vm, self.project_name, self.db_service)
        records_vm.set_project(self.project_id)
        self.records_window.show()

    def _get_current_fields_objects(self):
        return FieldRepositoryImpl(self.db_service).get_fields_by_project(self.project_id)

    def update_fields_list(self, fields):
        self.fields_list.clear()
        for field in fields:
            required_text = self.tr("Required") if field.is_required else self.tr("Optional")
            options_text = ""
            if field.options:
                options_text = self.tr(" • Options: {options}").format(
                    options=", ".join(option.label for option in field.options)
                )
            item_text = (
                f"{field.display_order}.  {field.name}\n"
                f"{self._field_type_label(field.field_type)}  •  {required_text}{options_text}"
            )
            self.fields_list.addItem(item_text)
            item = self.fields_list.item(self.fields_list.count() - 1)
            item.setData(99, field.id)
            item.setSizeHint(QSize(100, 62))
        has_fields = bool(fields)
        self.fields_list.setVisible(has_fields)
        self.no_fields_label.setVisible(not has_fields)

    def show_error(self, message: str):
        QMessageBox.critical(self, self.tr("Error"), message)
