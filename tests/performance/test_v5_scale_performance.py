import os
import time

import pytest

from core.services.export_service import ExportService
from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.project_repository_impl import ProjectRepositoryImpl
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.project import Project


pytestmark = [pytest.mark.performance, pytest.mark.slow]


PERF_MULTIPLIER = float(os.getenv("P2D_PERF_MULTIPLIER", "1.0"))


def _seed_records(db_service, project_id: int, fields, count: int) -> None:
    """Seed a large realistic dataset in one transaction.

    This intentionally isolates read/export performance from per-record commit
    cost. The existing repository performance tests continue to cover normal
    insertion speed.
    """
    with db_service.get_connection() as connection:
        cursor = connection.cursor()
        values = []
        for index in range(count):
            cursor.execute("INSERT INTO records (project_id) VALUES (?)", (project_id,))
            record_id = cursor.lastrowid
            values.extend(
                [
                    (record_id, fields[0].id, f"Person {index}"),
                    (record_id, fields[1].id, str(18 + index % 70)),
                    (record_id, fields[2].id, f"ID-{index:06d}"),
                    (record_id, fields[3].id, str(index % 101)),
                    (record_id, fields[4].id, "yes" if index % 2 == 0 else "no"),
                ]
            )
        cursor.executemany(
            "INSERT INTO record_values (record_id, field_id, value) VALUES (?, ?, ?)",
            values,
        )
        connection.commit()


def _setup_large_project(db_service, count: int):
    project_repo = ProjectRepositoryImpl(db_service)
    field_repo = FieldRepositoryImpl(db_service)
    project = project_repo.create_project(Project(name=f"Performance {count}"))
    fields = [
        field_repo.add_field(Field(project_id=project.id, name="Name", field_type=FieldType.SHORT_TEXT, display_order=1)),
        field_repo.add_field(Field(project_id=project.id, name="Age", field_type=FieldType.INTEGER, display_order=2)),
        field_repo.add_field(Field(project_id=project.id, name="ID", field_type=FieldType.IDENTIFIER, display_order=3)),
        field_repo.add_field(Field(project_id=project.id, name="Percent", field_type=FieldType.PERCENTAGE, display_order=4)),
        field_repo.add_field(Field(project_id=project.id, name="Active", field_type=FieldType.YES_NO, display_order=5)),
    ]
    _seed_records(db_service, project.id, fields, count)
    return project, fields


def test_retrieve_10000_records_is_usable(quality_db_service):
    project, _fields = _setup_large_project(quality_db_service, 10_000)
    repo = RecordRepositoryImpl(quality_db_service)

    started = time.perf_counter()
    records = repo.get_records_by_project(project.id)
    elapsed = time.perf_counter() - started

    assert len(records) == 10_000
    assert all(len(record.values) == 5 for record in records)
    assert elapsed < 12.0 * PERF_MULTIPLIER, f"10,000 record retrieval took {elapsed:.2f}s"


def test_export_10000_records_to_csv_is_usable(quality_db_service, tmp_path):
    project, fields = _setup_large_project(quality_db_service, 10_000)
    records = RecordRepositoryImpl(quality_db_service).get_records_by_project(project.id)
    output = tmp_path / "10k.csv"

    started = time.perf_counter()
    ExportService.export_to_csv(fields, records, str(output))
    elapsed = time.perf_counter() - started

    assert output.exists()
    assert output.stat().st_size > 100_000
    assert elapsed < 12.0 * PERF_MULTIPLIER, f"10,000 record CSV export took {elapsed:.2f}s"


def test_export_5000_records_to_excel_is_usable(quality_db_service, tmp_path):
    project, fields = _setup_large_project(quality_db_service, 5_000)
    records = RecordRepositoryImpl(quality_db_service).get_records_by_project(project.id)
    output = tmp_path / "5k.xlsx"

    started = time.perf_counter()
    ExportService.export_to_excel(fields, records, str(output))
    elapsed = time.perf_counter() - started

    assert output.exists()
    assert output.stat().st_size > 50_000
    assert elapsed < 20.0 * PERF_MULTIPLIER, f"5,000 record Excel export took {elapsed:.2f}s"
