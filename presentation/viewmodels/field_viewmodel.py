from typing import List, Optional

from PySide6.QtCore import QObject, Signal

from core.errors.exceptions import DatabaseException
from domain.entities.field import Field, FieldOption
from domain.entities.field_type import FieldType
from domain.repositories.field_repository import FieldRepository


class FieldViewModel(QObject):
    fields_loaded = Signal(list)
    error_occurred = Signal(str)
    operation_success = Signal(str)

    def __init__(self, repository: FieldRepository):
        super().__init__()
        self._repository = repository
        self.current_project_id: Optional[int] = None

    def set_project(self, project_id: int):
        self.current_project_id = project_id
        self.load_fields()

    def load_fields(self):
        if not self.current_project_id:
            return
        try:
            self.fields_loaded.emit(
                self._repository.get_fields_by_project(self.current_project_id)
            )
        except DatabaseException as e:
            self._emit_database_error(e)

    def _parse_options(self, field_type: str, raw_options: str) -> List[FieldOption]:
        if not FieldType.uses_options(field_type) or not raw_options.strip():
            return []
        items = [option.strip() for option in raw_options.split(",") if option.strip()]
        return [
            FieldOption(label=item, value=item, display_order=index)
            for index, item in enumerate(items)
        ]

    def add_field(
        self,
        name: str,
        field_type: str,
        is_required: bool,
        raw_options: str = "",
    ):
        if not self.current_project_id:
            self.error_occurred.emit(self.tr("No project is selected."))
            return
        if not name.strip():
            self.error_occurred.emit(self.tr("Field name is required."))
            return

        normalized_type = FieldType.normalize(field_type)
        try:
            current_fields = self._repository.get_fields_by_project(self.current_project_id)
            new_field = Field(
                project_id=self.current_project_id,
                name=name.strip(),
                field_type=normalized_type,
                is_required=is_required,
                display_order=len(current_fields) + 1,
                options=self._parse_options(normalized_type, raw_options),
            )
            self._repository.add_field(new_field)
            self.operation_success.emit(self.tr("Field added successfully."))
            self.load_fields()
        except DatabaseException as e:
            self._emit_database_error(e)

    def update_field(
        self,
        field_id: int,
        name: str,
        field_type: str,
        is_required: bool,
        raw_options: str = "",
    ):
        if not self.current_project_id:
            self.error_occurred.emit(self.tr("No project is selected."))
            return
        if not name.strip():
            self.error_occurred.emit(self.tr("Field name is required."))
            return

        try:
            current = self._repository.get_fields_by_project(self.current_project_id)
            existing = next((field for field in current if field.id == field_id), None)
            if existing is None:
                self.error_occurred.emit(self.tr("Field not found."))
                return

            normalized_type = FieldType.normalize(field_type)
            existing.name = name.strip()
            existing.field_type = normalized_type
            existing.is_required = is_required
            existing.options = self._parse_options(normalized_type, raw_options)
            self._repository.update_field(existing)
            self.operation_success.emit(self.tr("Field updated successfully."))
            self.load_fields()
        except DatabaseException as e:
            self._emit_database_error(e)

    def move_field(self, field_id: int, direction: int):
        if not self.current_project_id:
            return
        try:
            fields = self._repository.get_fields_by_project(self.current_project_id)
            index = next((i for i, field in enumerate(fields) if field.id == field_id), None)
            if index is None:
                self.error_occurred.emit(self.tr("Field not found."))
                return

            new_index = index + direction
            if new_index < 0 or new_index >= len(fields):
                return

            fields[index], fields[new_index] = fields[new_index], fields[index]
            for order, field in enumerate(fields, start=1):
                field.display_order = order
                self._repository.update_field(field)
            self.load_fields()
        except DatabaseException as e:
            self._emit_database_error(e)

    def delete_field(self, field_id: int):
        try:
            self._repository.delete_field(field_id)
            self.operation_success.emit(self.tr("Field deleted successfully."))
            self.load_fields()
        except DatabaseException as e:
            self._emit_database_error(e)

    def _emit_database_error(self, error: DatabaseException) -> None:
        self.error_occurred.emit(
            self.tr("Database operation failed: {error}").format(error=error)
        )
