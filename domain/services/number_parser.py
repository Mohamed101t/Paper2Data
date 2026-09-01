from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Optional


class NumberParser:
    """Locale-tolerant decimal parsing shared across Paper2Data layers.

    Supports decimal comma/dot and common grouped values such as 1,500.50 or
    1.500,50. The last separator is treated as the decimal separator when both
    styles are present.
    """

    @classmethod
    def to_decimal(cls, value: object, allow_symbols: bool = False) -> Optional[Decimal]:
        text = "" if value is None else str(value).strip()
        if not text:
            return None

        if allow_symbols:
            text = re.sub(r"[^\d+\-.,]", "", text)
        else:
            text = text.replace(" ", "")
        if not text:
            return None

        normalized = cls._normalize_separators(text)
        try:
            return Decimal(normalized)
        except InvalidOperation:
            return None

    @staticmethod
    def _normalize_separators(text: str) -> str:
        comma_count = text.count(",")
        dot_count = text.count(".")

        if comma_count and dot_count:
            decimal_sep = "," if text.rfind(",") > text.rfind(".") else "."
            thousands_sep = "." if decimal_sep == "," else ","
            return text.replace(thousands_sep, "").replace(decimal_sep, ".")

        separator = "," if comma_count else "." if dot_count else None
        if separator is None:
            return text

        count = text.count(separator)
        if count == 1:
            return text.replace(separator, ".")

        # Multiple equal separators are normally grouping separators. If the
        # final group is not 3 digits, keep the final separator as decimal.
        parts = text.split(separator)
        if all(len(part) == 3 for part in parts[1:]):
            return "".join(parts)
        return "".join(parts[:-1]) + "." + parts[-1]
