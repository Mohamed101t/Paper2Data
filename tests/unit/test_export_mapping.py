import csv
from datetime import date, datetime, time

from openpyxl import load_workbook

from core.services.export_mapping import ExportMapping
from core.services.export_service import ExportService
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.record import Record, RecordValue


def test_excel_mapping_preserves_real_types_and_leading_zero_text():
    assert ExportMapping.to_excel(FieldType.INTEGER, "25").value == 25
    assert ExportMapping.to_excel(FieldType.DECIMAL, "72.5").value == 72.5

    percentage = ExportMapping.to_excel(FieldType.PERCENTAGE, "85")
    assert percentage.value == 0.85
    assert percentage.number_format == "0.00%"

    phone = ExportMapping.to_excel(FieldType.PHONE_NUMBER, "00123456789")
    assert phone.value == "00123456789"
    assert phone.number_format == "@"

    assert ExportMapping.to_excel(FieldType.DATE, "2026-09-01").value == date(2026, 9, 1)
    assert ExportMapping.to_excel(FieldType.TIME, "14:30").value == time(14, 30)
    assert ExportMapping.to_excel(FieldType.DATE_TIME, "2026-09-01 14:30").value == datetime(2026, 9, 1, 14, 30)


def test_csv_mapping_uses_unambiguous_values():
    assert ExportMapping.to_csv(FieldType.DATE, "01/09/2026") == "2026-09-01"
    assert ExportMapping.to_csv(FieldType.DATE_TIME, "2026-09-01 14:30") == "2026-09-01 14:30:00"
    assert ExportMapping.to_csv(FieldType.PHONE_NUMBER, "00125") == "00125"
    assert ExportMapping.to_csv(FieldType.PERCENTAGE, "85%") == "85"


def test_excel_export_writes_true_cell_types(tmp_path):
    fields = [
        Field(id=1, project_id=1, name="Age", field_type=FieldType.INTEGER),
        Field(id=2, project_id=1, name="Birth Date", field_type=FieldType.DATE),
        Field(id=3, project_id=1, name="Phone", field_type=FieldType.PHONE_NUMBER),
        Field(id=4, project_id=1, name="Success", field_type=FieldType.PERCENTAGE),
    ]
    record = Record(
        id=1,
        project_id=1,
        created_at="2026-09-01 14:30:00",
        values=[
            RecordValue(field_id=1, value="25"),
            RecordValue(field_id=2, value="2001-05-10"),
            RecordValue(field_id=3, value="00123456789"),
            RecordValue(field_id=4, value="85"),
        ],
    )

    path = tmp_path / "typed.xlsx"
    ExportService.export_to_excel(fields, [record], str(path))
    workbook = load_workbook(path)
    worksheet = workbook["Data"]

    assert worksheet["C2"].value == 25
    assert worksheet["D2"].value == datetime(2001, 5, 10, 0, 0)
    assert worksheet["E2"].value == "00123456789"
    assert worksheet["E2"].number_format == "@"
    assert worksheet["F2"].value == 0.85
    assert worksheet["F2"].number_format == "0.00%"


def test_csv_export_preserves_identifier_text(tmp_path):
    fields = [Field(id=1, project_id=1, name="Survey ID", field_type=FieldType.IDENTIFIER)]
    record = Record(
        id=1,
        project_id=1,
        created_at="2026-09-01 14:30:00",
        values=[RecordValue(field_id=1, value="00125")],
    )
    path = tmp_path / "data.csv"
    ExportService.export_to_csv(fields, [record], str(path))

    with open(path, encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file))
    assert rows[1][2] == "00125"
