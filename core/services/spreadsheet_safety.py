from __future__ import annotations


class SpreadsheetSafety:
    """Guards text exports against spreadsheet formula injection.

    Spreadsheet programs may interpret text beginning with =, +, -, or @ as a
    formula/command when a CSV is opened. Paper2Data treats user-entered text as
    data, never as executable spreadsheet content.
    """

    DANGEROUS_PREFIXES = ("=", "+", "-", "@")

    @classmethod
    def is_formula_like(cls, value: object) -> bool:
        text = "" if value is None else str(value)
        normalized = text.lstrip(" \t\r\n")
        return bool(normalized) and normalized.startswith(cls.DANGEROUS_PREFIXES)

    @classmethod
    def safe_csv_text(cls, value: object) -> str:
        text = "" if value is None else str(value)
        if cls.is_formula_like(text):
            return "'" + text
        return text
