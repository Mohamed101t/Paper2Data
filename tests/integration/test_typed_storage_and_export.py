import csv
from datetime import date

import pytest
from openpyxl import load_workbook

from core.services.export_service import ExportService
from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.project_repository_impl import ProjectRepositoryImpl
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.project import Project
from domain.entities.record import Record, RecordValue
from domain.services.field_value_codec import FieldValueCodec


pytestmark = pytest.mark.integration


def test_typed_values_survive_sqlite_and_export(quality_db_service, tmp_path):
    project_repo = ProjectRepositoryImpl(quality_db_service)
    field_repo = FieldRepositoryImpl(quality_db_service)
    record_repo = RecordRepositoryImpl(quality_db_service)

    project = project_repo.create_project(Project(name="Typed export"))
    fields = [
        field_repo.add_field(Field(project_id=project.id, name="Age", field_type=FieldType.INTEGER, is_required=True, display_order=1)),
        field_repo.add_field(Field(project_id=project.id, name="Salary", field_type=FieldType.CURRENCY, display_order=2)),
        field_repo.add_field(Field(project_id=project.id, name="Birth date", field_type=FieldType.DATE, display_order=3)),
        field_repo.add_field(Field(project_id=project.id, name="Survey ID", field_type=FieldType.IDENTIFIER, display_order=4)),
        field_repo.add_field(Field(project_id=project.id, name="Success", field_type=FieldType.PERCENTAGE, display_order=5)),
        field_repo.add_field(Field(project_id=project.id, name="Active", field_type=FieldType.YES_NO, display_order=6)),
    ]

    raw_values = ["25", "15000.50", "2001-05-10", "00125", "85%", "نعم"]
    record_repo.add_record(
        Record(
            project_id=project.id,
            values=[
                RecordValue(field_id=field.id, value=FieldValueCodec.normalize_for_storage(field.field_type, raw))
                for field, raw in zip(fields, raw_values)
            ],
        )
    )

    records = record_repo.get_records_by_project(project.id)
    assert len(records) == 1
    stored = {value.field_id: value.value for value in records[0].values}
    assert stored[fields[3].id] == "00125"
    assert stored[fields[4].id] == "85"
    assert stored[fields[5].id] == "yes"

    xlsx_path = tmp_path / "typed.xlsx"
    csv_path = tmp_path / "typed.csv"
    ExportService.export_to_excel(fields, records, str(xlsx_path))
    ExportService.export_to_csv(fields, records, str(csv_path))

    workbook = load_workbook(xlsx_path, data_only=False)
    sheet = workbook["Data"]
    assert sheet["C2"].value == 25
    assert isinstance(sheet["E2"].value, date)
    assert sheet["F2"].value == "00125"
    assert sheet["F2"].data_type == "s"
    assert sheet["G2"].value == pytest.approx(0.85)
    assert sheet["H2"].value is True

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[1][2] == "25"
    assert rows[1][4] == "2001-05-10"
    assert rows[1][5] == "00125"
    assert rows[1][6] == "85"
    assert rows[1][7] == "yes"
