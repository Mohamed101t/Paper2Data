import pytest

from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.project_repository_impl import ProjectRepositoryImpl
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.project import Project
from domain.entities.record import Record, RecordValue


pytestmark = pytest.mark.security


def test_foreign_keys_are_enabled(quality_db_service):
    with quality_db_service.get_connection() as connection:
        enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]
    assert enabled == 1


def test_project_delete_cascades_sensitive_child_data(quality_db_service):
    project_repo = ProjectRepositoryImpl(quality_db_service)
    field_repo = FieldRepositoryImpl(quality_db_service)
    record_repo = RecordRepositoryImpl(quality_db_service)

    project = project_repo.create_project(Project(name="Sensitive survey"))
    field = field_repo.add_field(Field(project_id=project.id, name="Secret", field_type=FieldType.SHORT_TEXT))
    record_repo.add_record(
        Record(project_id=project.id, values=[RecordValue(field_id=field.id, value="private-value")])
    )

    project_repo.delete_project(project.id)

    with quality_db_service.get_connection() as connection:
        assert connection.execute("SELECT COUNT(*) FROM fields WHERE project_id = ?", (project.id,)).fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM records WHERE project_id = ?", (project.id,)).fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM record_values").fetchone()[0] == 0
