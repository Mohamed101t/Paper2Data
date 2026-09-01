import pytest

from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.project_repository_impl import ProjectRepositoryImpl
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.project import Project
from domain.entities.record import Record, RecordValue


pytestmark = pytest.mark.security


def test_record_values_are_not_printed_to_console(quality_db_service, capsys):
    secret = "P2D-VERY-SENSITIVE-VALUE"
    project_repo = ProjectRepositoryImpl(quality_db_service)
    field_repo = FieldRepositoryImpl(quality_db_service)
    record_repo = RecordRepositoryImpl(quality_db_service)

    project = project_repo.create_project(Project(name="Security test"))
    field = field_repo.add_field(Field(project_id=project.id, name="Secret", field_type=FieldType.SHORT_TEXT))
    record_repo.add_record(Record(project_id=project.id, values=[RecordValue(field_id=field.id, value=secret)]))
    record_repo.get_records_by_project(project.id)

    captured = capsys.readouterr()
    assert secret not in captured.out
    assert secret not in captured.err
