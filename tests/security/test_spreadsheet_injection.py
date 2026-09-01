import csv

import pytest
from openpyxl import load_workbook

from core.services.export_service import ExportService
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.record import Record, RecordValue


pytestmark = pytest.mark.security


@pytest.mark.parametrize(
    "payload",
    [
        '=HYPERLINK("https://example.invalid","click")',
        "+SUM(1,1)",
        "-2+3",
        "@SUM(A1:A2)",
        "  =1+1",
    ],
)
def test_text_cannot_become_csv_formula(tmp_path, payload):
    field = Field(project_id=1, id=1, name="Comment", field_type=FieldType.SHORT_TEXT)
    record = Record(project_id=1, id=1, values=[RecordValue(field_id=1, value=payload)])
    path = tmp_path / "safe.csv"

    ExportService.export_to_csv([field], [record], str(path))

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        row = list(csv.reader(handle))[1]
    exported = row[2]
    assert exported.startswith("'")
    assert exported[1:] == payload.strip()


def test_equal_prefixed_text_is_stored_as_string_in_xlsx(tmp_path):
    payload = '=HYPERLINK("https://example.invalid","click")'
    field = Field(project_id=1, id=1, name="Comment", field_type=FieldType.SHORT_TEXT)
    record = Record(project_id=1, id=1, values=[RecordValue(field_id=1, value=payload)])
    path = tmp_path / "safe.xlsx"

    ExportService.export_to_excel([field], [record], str(path))

    workbook = load_workbook(path, data_only=False)
    cell = workbook["Data"]["C2"]
    assert cell.value == payload
    assert cell.data_type == "s"
