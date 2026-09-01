import re
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from domain.entities.field_type import FieldType
from core.services.spreadsheet_safety import SpreadsheetSafety
from domain.services.number_parser import NumberParser


@dataclass(frozen=True)
class ExcelCellValue:
    value: Any
    number_format: str | None = None
    force_text: bool = False


class ExportMapping:
    """Convert stable Paper2Data values to target-format values."""

    TEXT_FORMAT = "@"
    INTEGER_FORMAT = "0"
    DECIMAL_FORMAT = "0.00########"
    CURRENCY_FORMAT = "#,##0.00"
    PERCENTAGE_FORMAT = "0.00%"
    DATE_FORMAT = "dd/mm/yyyy"
    TIME_FORMAT = "hh:mm"
    DATETIME_FORMAT = "dd/mm/yyyy hh:mm"

    @classmethod
    def to_excel(cls, field_type: str, raw_value: Any) -> ExcelCellValue:
        normalized_type = FieldType.normalize(field_type)
        text = "" if raw_value is None else str(raw_value).strip()
        if text == "":
            return ExcelCellValue(None)

        if normalized_type in {
            FieldType.PHONE_NUMBER,
            FieldType.IDENTIFIER,
            FieldType.NATIONAL_ID,
            FieldType.CODE,
            FieldType.POSTAL_CODE,
            FieldType.BARCODE,
            FieldType.QR_CODE,
        }:
            return ExcelCellValue(text, cls.TEXT_FORMAT, True)

        if normalized_type in {FieldType.INTEGER, FieldType.RATING, FieldType.SCALE, FieldType.AUTO_NUMBER}:
            try:
                return ExcelCellValue(int(float(text)), cls.INTEGER_FORMAT)
            except ValueError:
                return ExcelCellValue(text, cls.TEXT_FORMAT, True)

        if normalized_type == FieldType.DECIMAL:
            number = cls._decimal(text)
            return ExcelCellValue(float(number), cls.DECIMAL_FORMAT) if number is not None else ExcelCellValue(text, cls.TEXT_FORMAT, True)

        if normalized_type == FieldType.CURRENCY:
            number = cls._currency_decimal(text)
            return ExcelCellValue(float(number), cls.CURRENCY_FORMAT) if number is not None else ExcelCellValue(text, cls.TEXT_FORMAT, True)

        if normalized_type == FieldType.PERCENTAGE:
            number = cls._decimal(text.rstrip("%").strip())
            return ExcelCellValue(float(number / Decimal("100")), cls.PERCENTAGE_FORMAT) if number is not None else ExcelCellValue(text, cls.TEXT_FORMAT, True)

        if normalized_type == FieldType.DATE:
            parsed = cls._date(text)
            return ExcelCellValue(parsed, cls.DATE_FORMAT) if parsed else ExcelCellValue(text, cls.TEXT_FORMAT, True)

        if normalized_type == FieldType.TIME:
            parsed = cls._time(text)
            return ExcelCellValue(parsed, cls.TIME_FORMAT) if parsed else ExcelCellValue(text, cls.TEXT_FORMAT, True)

        if normalized_type == FieldType.DATE_TIME:
            parsed = cls._datetime(text)
            return ExcelCellValue(parsed, cls.DATETIME_FORMAT) if parsed else ExcelCellValue(text, cls.TEXT_FORMAT, True)

        if normalized_type == FieldType.YES_NO:
            lowered = text.casefold()
            if lowered in {"yes", "true", "1", "نعم", "oui", "да", "是"}:
                return ExcelCellValue(True)
            if lowered in {"no", "false", "0", "لا", "non", "нет", "否"}:
                return ExcelCellValue(False)

        definition = FieldType.definition(normalized_type)
        if definition.excel_kind == "text":
            return ExcelCellValue(text, cls.TEXT_FORMAT, True)
        return ExcelCellValue(text)

    @classmethod
    def to_csv(cls, field_type: str, raw_value: Any) -> str:
        normalized_type = FieldType.normalize(field_type)
        text = "" if raw_value is None else str(raw_value).strip()
        if not text:
            return ""

        if normalized_type == FieldType.DATE:
            parsed = cls._date(text)
            return parsed.isoformat() if parsed else text

        if normalized_type == FieldType.TIME:
            parsed = cls._time(text)
            return parsed.strftime("%H:%M:%S") if parsed else text

        if normalized_type == FieldType.DATE_TIME:
            parsed = cls._datetime(text)
            return parsed.strftime("%Y-%m-%d %H:%M:%S") if parsed else text

        if normalized_type == FieldType.PERCENTAGE:
            number = cls._decimal(text.rstrip("%").strip())
            if number is not None:
                return cls._plain_decimal(number)

        if normalized_type in {FieldType.DECIMAL, FieldType.CURRENCY}:
            number = cls._currency_decimal(text) if normalized_type == FieldType.CURRENCY else cls._decimal(text)
            if number is not None:
                return cls._plain_decimal(number)

        if normalized_type == FieldType.YES_NO:
            excel_value = cls.to_excel(normalized_type, text).value
            if excel_value is True:
                return "yes"
            if excel_value is False:
                return "no"

        definition = FieldType.definition(normalized_type)
        if definition.csv_kind == "text":
            return SpreadsheetSafety.safe_csv_text(text)
        return text

    @staticmethod
    def _decimal(text: str) -> Decimal | None:
        return NumberParser.to_decimal(text)

    @classmethod
    def _currency_decimal(cls, text: str) -> Decimal | None:
        return NumberParser.to_decimal(text, allow_symbols=True)

    @staticmethod
    def _plain_decimal(value: Decimal) -> str:
        result = format(value.normalize(), "f")
        if "." in result:
            result = result.rstrip("0").rstrip(".")
        return result or "0"

    @staticmethod
    def _date(text: str) -> date | None:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _time(text: str) -> time | None:
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(text, fmt).time()
            except ValueError:
                continue
        return None

    @staticmethod
    def _datetime(text: str) -> datetime | None:
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
        ):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue
        return None
