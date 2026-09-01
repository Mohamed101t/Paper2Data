import pytest

from core.services.export_mapping import ExportMapping
from core.services.spreadsheet_safety import SpreadsheetSafety
from domain.entities.field_type import FieldType


pytestmark = pytest.mark.unit


@pytest.mark.parametrize("value", ["=1+1", "+SUM(A1:A2)", "-2+3", "@SUM(A1:A2)", "  =HYPERLINK(\"x\")"])
def test_formula_like_text_is_detected(value):
    assert SpreadsheetSafety.is_formula_like(value)


@pytest.mark.parametrize("value", ["Mohamed", "00125", "example@example.com", "https://example.com"])
def test_normal_text_is_not_flagged(value):
    assert not SpreadsheetSafety.is_formula_like(value)


def test_csv_text_is_neutralized_but_numeric_values_are_not():
    assert ExportMapping.to_csv(FieldType.SHORT_TEXT, "=1+1").startswith("'")
    assert ExportMapping.to_csv(FieldType.INTEGER, "-25") == "-25"


def test_excel_text_mapping_is_forced_to_string():
    mapped = ExportMapping.to_excel(FieldType.SHORT_TEXT, "=1+1")
    assert mapped.value == "=1+1"
    assert mapped.force_text is True
    assert mapped.number_format == "@"
