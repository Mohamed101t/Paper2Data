from typing import List, Optional

from PySide6.QtCore import QEvent
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.database.database_service import DatabaseService
from core.services.export_service import ExportService
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.record import Record
from presentation.components.app_button import AppButton
from presentation.components.app_empty_state import AppEmptyState
from presentation.viewmodels.record_viewmodel import RecordViewModel
from presentation.viewmodels.records_list_viewmodel import RecordsListViewModel
from presentation.views.data_entry_view import DataEntryView


class RecordsView(QWidget):
    def __init__(
        self,
        viewmodel: RecordsListViewModel,
        project_name: str,
        db_service: DatabaseService,
    ):
        super().__init__()
        self.viewmodel = viewmodel
        self.project_name = project_name
        self.db_service = db_service
        self.fields: List[Field] = []
        self.records: List[Record] = []
        self.edit_window: Optional[QWidget] = None

        self.setup_ui()
        self.setup_connections()
        self.setup_shortcuts()

    def setup_ui(self):
        self.setObjectName("AppRoot")
        self.resize(1050, 680)
        self.setMinimumSize(820, 560)
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 26)
        root.setSpacing(16)

        head = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        self.title_label = QLabel()
        self.title_label.setProperty("role", "pageTitle")
        self.count_label = QLabel()
        self.count_label.setProperty("role", "muted")
        title_box.addWidget(self.title_label)
        title_box.addWidget(self.count_label)
        head.addLayout(title_box)
        head.addStretch()
        self.refresh_btn = AppButton(variant=AppButton.GHOST)
        head.addWidget(self.refresh_btn)
        root.addLayout(head)

        search_card = QFrame()
        search_card.setProperty("softCard", True)
        search_layout = QHBoxLayout(search_card)
        search_layout.setContentsMargins(12, 9, 12, 9)
        self.search_input = QLineEdit()
        self.search_input.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_input)
        root.addWidget(search_card)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        root.addWidget(self.table, 1)

        self.empty_state = AppEmptyState()
        self.empty_state.setProperty("card", True)
        root.addWidget(self.empty_state, 1)
        self.empty_state.hide()

        actions = QHBoxLayout()
        self.export_csv_btn = AppButton(variant=AppButton.GHOST)
        self.export_excel_btn = AppButton(variant=AppButton.SOFT)
        actions.addWidget(self.export_csv_btn)
        actions.addWidget(self.export_excel_btn)
        actions.addStretch()
        self.delete_btn = AppButton(variant=AppButton.DANGER)
        self.edit_btn = AppButton(variant=AppButton.PRIMARY)
        actions.addWidget(self.delete_btn)
        actions.addWidget(self.edit_btn)
        root.addLayout(actions)
        self.retranslate_ui()

    def setup_connections(self):
        self.search_input.textChanged.connect(self.filter_table)
        self.refresh_btn.clicked.connect(self.viewmodel.load_data)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        self.edit_btn.clicked.connect(self.on_edit_clicked)
        self.table.doubleClicked.connect(lambda: self.on_edit_clicked())
        self.export_excel_btn.clicked.connect(self.on_export_excel)
        self.export_csv_btn.clicked.connect(self.on_export_csv)
        self.viewmodel.records_loaded.connect(self.populate_table)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.viewmodel.operation_success.connect(lambda _message: None)
        self.empty_state.action_clicked.connect(self.viewmodel.load_data)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self, self.search_input.setFocus)
        QShortcut(QKeySequence("Ctrl+E"), self, self.on_export_excel)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Paper2Data - Records: {name}").format(name=self.project_name))
        self.title_label.setText(self.project_name)
        self.search_input.setPlaceholderText(self.tr("Search across all fields..."))
        self.edit_btn.setText(self.tr("Edit selected"))
        self.delete_btn.setText(self.tr("Delete"))
        self.refresh_btn.setText(self.tr("Refresh"))
        self.export_excel_btn.setText(self.tr("Open in Excel (.xlsx)"))
        self.export_csv_btn.setText(self.tr("Save CSV"))
        self.empty_state.set_content(
            self.tr("No records yet"),
            self.tr("Enter the first paper form and it will appear here automatically."),
            self.tr("Refresh"),
        )
        if self.fields or self.records:
            self.populate_table(self.fields, self.records)
        else:
            self.count_label.setText(self.tr("0 records"))

    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange and hasattr(self, "search_input"):
            self.retranslate_ui()
        super().changeEvent(event)

    def populate_table(self, fields: List[Field], records: List[Record]):
        self.fields = fields
        self.records = records
        self.count_label.setText(self.tr("{count} records").format(count=len(records)))
        headers = [self.tr("ID"), self.tr("Created At")] + [field.name for field in fields]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(records))

        for row_index, record in enumerate(records):
            id_item = QTableWidgetItem(str(record.id))
            id_item.setData(99, record.id)
            self.table.setItem(row_index, 0, id_item)
            self.table.setItem(row_index, 1, QTableWidgetItem(str(record.created_at)))
            value_map = {value.field_id: value.value for value in record.values}
            for column_index, field in enumerate(fields, start=2):
                display_value = self._display_field_value(field, value_map.get(field.id, ""), record)
                self.table.setItem(row_index, column_index, QTableWidgetItem(display_value))

        has_records = bool(records)
        self.table.setVisible(has_records)
        self.empty_state.setVisible(not has_records)
        self.edit_btn.setVisible(has_records)
        self.delete_btn.setVisible(has_records)
        self.export_excel_btn.setVisible(has_records)
        self.export_csv_btn.setVisible(has_records)
        if self.search_input.text() and has_records:
            self.filter_table(self.search_input.text())

    def _display_field_value(self, field: Field, value, record: Record) -> str:
        field_type = FieldType.normalize(field.field_type)
        if field_type == FieldType.AUTO_NUMBER:
            return str(record.id or "")
        if field_type == FieldType.YES_NO:
            normalized = str(value or "").strip().lower()
            if normalized in {"yes", "نعم"}:
                return self.tr("Yes")
            if normalized in {"no", "لا"}:
                return self.tr("No")
        return str(value or "")

    def filter_table(self, text: str):
        visible = 0
        for row in range(self.table.rowCount()):
            match = any(
                self.table.item(row, column)
                and text.casefold() in self.table.item(row, column).text().casefold()
                for column in range(self.table.columnCount())
            )
            self.table.setRowHidden(row, not match)
            visible += int(match)
        self.count_label.setText(self.tr("{count} records").format(count=visible))

    def _selected_record(self) -> Optional[Record]:
        selected_items = self.table.selectedItems()
        if not selected_items:
            return None
        row = selected_items[0].row()
        record_id = self.table.item(row, 0).data(99)
        return next((record for record in self.records if record.id == record_id), None)

    def on_edit_clicked(self):
        record = self._selected_record()
        if record is None:
            self.show_error(self.tr("Please select a record to edit."))
            return
        record_vm = RecordViewModel(RecordRepositoryImpl(self.db_service))
        self.edit_window = DataEntryView(
            record_vm,
            record.project_id,
            self.project_name,
            self.fields,
            existing_record=record,
        )
        self.edit_window.destroyed.connect(self.viewmodel.load_data)
        self.edit_window.show()

    def on_delete_clicked(self):
        record = self._selected_record()
        if record is None:
            self.show_error(self.tr("Please select a record to delete."))
            return
        confirm = QMessageBox.question(
            self,
            self.tr("Confirm Deletion"),
            self.tr("Are you sure you want to delete this record?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.viewmodel.delete_record(record.id)

    def on_export_excel(self):
        if not self.records:
            self.show_error(self.tr("There are no records to export."))
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save Excel File"),
            f"{self.project_name}_data.xlsx",
            self.tr("Excel Files (*.xlsx)"),
        )
        if file_path:
            try:
                ExportService.export_to_excel(self.fields, self.records, file_path)
                QMessageBox.information(self, self.tr("Success"), self.tr("Data exported to Excel successfully."))
            except Exception as error:
                self.show_error(self.tr("Export failed: {error}").format(error=error))

    def on_export_csv(self):
        if not self.records:
            self.show_error(self.tr("There are no records to export."))
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Save CSV File"),
            f"{self.project_name}_data.csv",
            self.tr("CSV Files (*.csv)"),
        )
        if file_path:
            try:
                ExportService.export_to_csv(self.fields, self.records, file_path)
                QMessageBox.information(self, self.tr("Success"), self.tr("Data exported to CSV successfully."))
            except Exception as error:
                self.show_error(self.tr("Export failed: {error}").format(error=error))

    def show_error(self, message: str):
        QMessageBox.critical(self, self.tr("Error"), message)
