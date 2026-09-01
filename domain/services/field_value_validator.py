import re
from dataclasses import dataclass, field as dataclass_field
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.services.number_parser import NumberParser


_PHONE_DIGITS = re.compile(r"\d")
_PHONE_ALLOWED = re.compile(r"^[\d+\-\s()]+$")
_DURATION = re.compile(r"^\d{1,4}:[0-5]\d$")
_MEASUREMENT = re.compile(r"^[+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+)\s*[^\d\s].*$")


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    params: Dict[str, Any] = dataclass_field(default_factory=dict)


class FieldValueValidator:
    """Pure validation rules shared by entry, import and pre-export review."""

    @classmethod
    def validate(cls, field: Field, value: Any) -> Optional[ValidationIssue]:
        text = "" if value is None else str(value).strip()
        field_type = FieldType.normalize(field.field_type)

        if field_type in FieldType.VIRTUAL_TYPES:
            return None
        if field.is_required and not text:
            return ValidationIssue("required", {"name": field.name})
        if not text:
            return None

        if field_type == FieldType.INTEGER:
            try:
                int(text)
            except ValueError:
                return ValidationIssue("integer", {"name": field.name})

        elif field_type == FieldType.DECIMAL:
            if cls._to_number(text) is None:
                return ValidationIssue("decimal", {"name": field.name})

        elif field_type == FieldType.CURRENCY:
            if cls._to_currency_number(text) is None:
                return ValidationIssue("currency", {"name": field.name})

        elif field_type == FieldType.PERCENTAGE:
            number = cls._to_number(text.rstrip("%").strip())
            if number is None or number < 0 or number > 100:
                return ValidationIssue("percentage", {"name": field.name})

        elif field_type == FieldType.DURATION:
            if not _DURATION.fullmatch(text):
                return ValidationIssue("duration", {"name": field.name})

        elif field_type == FieldType.EMAIL:
            local, separator, domain = text.rpartition("@")
            if not separator or not local or "." not in domain:
                return ValidationIssue("email", {"name": field.name})

        elif field_type == FieldType.PHONE_NUMBER:
            if not _PHONE_ALLOWED.fullmatch(text) or len(_PHONE_DIGITS.findall(text)) < 7:
                return ValidationIssue("phone", {"name": field.name})

        elif field_type == FieldType.URL:
            parsed = urlparse(text)
            if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
                return ValidationIssue("url", {"name": field.name})

        elif field_type == FieldType.NATIONAL_ID:
            compact = text.replace(" ", "").replace("-", "").replace("/", "")
            if len(compact) < 4 or not compact.isalnum():
                return ValidationIssue("national_id", {"name": field.name})

        elif field_type == FieldType.COORDINATES:
            if not cls._valid_coordinates(text):
                return ValidationIssue("coordinates", {"name": field.name})

        elif field_type in FieldType.MEASUREMENT_TYPES:
            if not _MEASUREMENT.fullmatch(text):
                return ValidationIssue("measurement", {"name": field.name})

        elif field_type == FieldType.RATING:
            number = cls._to_number(text)
            if number is None or number < 1 or number > 5 or int(number) != number:
                return ValidationIssue("rating", {"name": field.name})

        elif field_type == FieldType.SCALE:
            number = cls._to_number(text)
            if number is None or number < 0 or number > 10:
                return ValidationIssue("scale", {"name": field.name})

        elif field_type in FieldType.FILE_TYPES:
            if text and not Path(text).exists():
                return ValidationIssue("file", {"name": field.name})

        return None

    @staticmethod
    def _to_number(text: str) -> Optional[float]:
        parsed = NumberParser.to_decimal(text)
        return float(parsed) if parsed is not None else None

    @staticmethod
    def _to_currency_number(text: str) -> Optional[float]:
        parsed = NumberParser.to_decimal(text, allow_symbols=True)
        return float(parsed) if parsed is not None else None

    @staticmethod
    def _valid_coordinates(text: str) -> bool:
        try:
            lat_text, lon_text = [part.strip() for part in text.split(",", 1)]
            latitude = float(lat_text)
            longitude = float(lon_text)
            return -90 <= latitude <= 90 and -180 <= longitude <= 180
        except (ValueError, TypeError):
            return False
