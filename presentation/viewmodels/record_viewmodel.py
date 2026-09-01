from typing import Any, Dict, Optional

from PySide6.QtCore import QObject, Signal

from core.errors.exceptions import DatabaseException
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.record import Record, RecordValue
from domain.repositories.record_repository import RecordRepository
from domain.services.field_value_codec import FieldValueCodec
from domain.services.field_value_validator import FieldValueValidator, ValidationIssue


class RecordViewModel(QObject):
    error_occurred = Signal(str)
    operation_success = Signal(str)
    validation_failed = Signal(int, str)

    def __init__(self, record_repository: RecordRepository):
        super().__init__()
        self._repository = record_repository

    def save_record(
        self,
        project_id: int,
        fields: list[Field],
        form_data: Dict[int, Any],
        record_id: Optional[int] = None,
    ) -> bool:
        record_values = []
        for field in fields:
            value = form_data.get(field.id)
            issue = FieldValueValidator.validate(field, value)
            if issue:
                self.validation_failed.emit(field.id or 0, self._translate_validation_issue(issue))
                return False
            if FieldType.is_virtual(field.field_type):
                continue
            record_values.append(
                RecordValue(
                    field_id=field.id,
                    value=FieldValueCodec.normalize_for_storage(field.field_type, value),
                )
            )

        try:
            record = Record(project_id=project_id, id=record_id, values=record_values)
            if record_id:
                self._repository.update_record(record)
                self.operation_success.emit(self.tr("Record updated successfully."))
            else:
                self._repository.add_record(record)
                self.operation_success.emit(self.tr("Record saved successfully."))
            return True
        except DatabaseException as error:
            self.error_occurred.emit(
                self.tr("Database operation failed: {error}").format(error=error)
            )
            return False

    def _translate_validation_issue(self, issue: ValidationIssue) -> str:
        name = issue.params.get("name", "")
        messages = {
            "required": self.tr("Field '{name}' is required."),
            "integer": self.tr("Field '{name}' must contain a valid integer."),
            "decimal": self.tr("Field '{name}' must contain a valid decimal number."),
            "currency": self.tr("Field '{name}' must contain a valid amount."),
            "percentage": self.tr("Field '{name}' must be a percentage from 0 to 100."),
            "duration": self.tr("Field '{name}' must use HH:MM duration format."),
            "email": self.tr("Field '{name}' contains an invalid email address."),
            "phone": self.tr("Field '{name}' contains an invalid phone number."),
            "url": self.tr("Field '{name}' contains an invalid URL."),
            "national_id": self.tr("Field '{name}' contains an invalid national ID."),
            "coordinates": self.tr(
                "Field '{name}' must contain latitude and longitude, e.g. 15.5007, 32.5599."
            ),
            "measurement": self.tr(
                "Field '{name}' must contain a numeric value followed by a unit."
            ),
            "rating": self.tr("Field '{name}' must be a rating from 1 to 5."),
            "scale": self.tr("Field '{name}' must be a scale from 0 to 10."),
            "file": self.tr("The selected file for '{name}' does not exist."),
        }
        template = messages.get(issue.code, self.tr("Field '{name}' contains an invalid value."))
        return template.format(name=name)
