import pytest

from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.project_repository_impl import ProjectRepositoryImpl
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.project import Project
from domain.entities.record import Record, RecordValue


pytestmark = pytest.mark.security


def test_sql_injection_payloads_are_stored_as_data(quality_db_service):
    project_repo = ProjectRepositoryImpl(quality_db_service)
    field_repo = FieldRepositoryImpl(quality_db_service)
    record_repo = RecordRepositoryImpl(quality_db_service)

    project_payload = "survey'); DROP TABLE projects; --"
    field_payload = "name'); DROP TABLE fields; --"
    value_payload = "x'); DROP TABLE records; --"

    project = project_repo.create_project(Project(name=project_payload))
    field = field_repo.add_field(
        Field(project_id=project.id, name=field_payload, field_type=FieldType.SHORT_TEXT)
    )
    record_repo.add_record(
        Record(project_id=project.id, values=[RecordValue(field_id=field.id, value=value_payload)])
    )

    projects = project_repo.get_all_projects()
    fields = field_repo.get_fields_by_project(project.id)
    records = record_repo.get_records_by_project(project.id)

    assert projects[0].name == project_payload
    assert fields[0].name == field_payload
    assert records[0].values[0].value == value_payload

    # Tables still exist and remain usable after the malicious-looking strings.
    second = project_repo.create_project(Project(name="Still alive"))
    assert second.id is not None
