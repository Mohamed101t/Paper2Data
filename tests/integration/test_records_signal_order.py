import pytest

from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.project_repository_impl import ProjectRepositoryImpl
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.field import Field
from domain.entities.field_type import FieldType
from domain.entities.project import Project
from domain.entities.record import Record, RecordValue
from presentation.viewmodels.records_list_viewmodel import RecordsListViewModel


pytestmark = pytest.mark.integration


def test_records_list_emits_initial_data_after_listener_is_connected(quality_db_service):
    project_repo = ProjectRepositoryImpl(quality_db_service)
    field_repo = FieldRepositoryImpl(quality_db_service)
    record_repo = RecordRepositoryImpl(quality_db_service)

    project = project_repo.create_project(Project(name="Records signal"))
    field = field_repo.add_field(Field(project_id=project.id, name="Name", field_type=FieldType.SHORT_TEXT))
    record_repo.add_record(Record(project_id=project.id, values=[RecordValue(field_id=field.id, value="Mohamed")]))

    vm = RecordsListViewModel(record_repo, field_repo)
    received = []
    vm.records_loaded.connect(lambda fields, records: received.append((fields, records)))
    vm.set_project(project.id)

    assert len(received) == 1
    assert len(received[0][0]) == 1
    assert len(received[0][1]) == 1
