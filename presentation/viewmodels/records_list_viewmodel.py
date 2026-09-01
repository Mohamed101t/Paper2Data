from typing import Optional

from PySide6.QtCore import QObject, Signal

from core.errors.exceptions import DatabaseException
from domain.repositories.field_repository import FieldRepository
from domain.repositories.record_repository import RecordRepository


class RecordsListViewModel(QObject):
    records_loaded = Signal(list, list)
    error_occurred = Signal(str)
    operation_success = Signal(str)

    def __init__(self, record_repo: RecordRepository, field_repo: FieldRepository):
        super().__init__()
        self._record_repo = record_repo
        self._field_repo = field_repo
        self.current_project_id: Optional[int] = None

    def set_project(self, project_id: int):
        self.current_project_id = project_id
        self.load_data()

    def load_data(self):
        if not self.current_project_id:
            return
        try:
            fields = self._field_repo.get_fields_by_project(self.current_project_id)
            records = self._record_repo.get_records_by_project(self.current_project_id)
            self.records_loaded.emit(fields, records)
        except DatabaseException as e:
            self.error_occurred.emit(
                self.tr("Database operation failed: {error}").format(error=e)
            )

    def delete_record(self, record_id: int):
        try:
            self._record_repo.delete_record(record_id)
            self.operation_success.emit(self.tr("Record deleted successfully."))
            self.load_data()
        except DatabaseException as e:
            self.error_occurred.emit(
                self.tr("Database operation failed: {error}").format(error=e)
            )
