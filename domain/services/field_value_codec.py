from decimal import Decimal
from typing import Any

from domain.entities.field_type import FieldType
from domain.services.number_parser import NumberParser


class FieldValueCodec:
    """Normalize values before persistence without knowing the UI language."""

    TRUE_VALUES = {"yes", "true", "1", "نعم", "oui", "да", "是"}
    FALSE_VALUES = {"no", "false", "0", "لا", "non", "нет", "否"}

    @classmethod
    def normalize_for_storage(cls, field_type: str, value: Any) -> str:
        normalized_type = FieldType.normalize(field_type)
        text = "" if value is None else str(value).strip()
        if not text:
            return ""

        if normalized_type == FieldType.INTEGER:
            return str(int(text))

        if normalized_type == FieldType.DECIMAL:
            return cls._decimal_text(text)

        if normalized_type == FieldType.CURRENCY:
            return cls._decimal_text(text, allow_symbols=True)

        if normalized_type == FieldType.PERCENTAGE:
            return cls._decimal_text(text.rstrip("%").strip())

        if normalized_type in {FieldType.RATING, FieldType.SCALE}:
            return str(int(float(text)))

        if normalized_type == FieldType.YES_NO:
            lowered = text.casefold()
            if lowered in cls.TRUE_VALUES:
                return "yes"
            if lowered in cls.FALSE_VALUES:
                return "no"
            return lowered

        if normalized_type in {
            FieldType.DATE,
            FieldType.TIME,
            FieldType.DATE_TIME,
            FieldType.DURATION,
            FieldType.COORDINATES,
        }:
            return text

        return text

    @staticmethod
    def _decimal_text(value: str, allow_symbols: bool = False) -> str:
        number = NumberParser.to_decimal(value, allow_symbols=allow_symbols)
        if number is None:
            return value.strip()
        normalized = format(number.normalize(), "f")
        if "." in normalized:
            normalized = normalized.rstrip("0").rstrip(".")
        return normalized or "0"
