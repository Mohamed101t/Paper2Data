import pytest
from unittest.mock import MagicMock
from presentation.viewmodels.project_viewmodel import ProjectViewModel
from domain.entities.project import Project
from core.errors.exceptions import DatabaseException


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    return repo


@pytest.fixture
def viewmodel(mock_repository):
    return ProjectViewModel(mock_repository)


class TestCreateProjectValidation:
    """اختبار قاعدة: اسم المشروع لا يمكن أن يكون فارغًا."""

    def test_empty_name_is_rejected(self, viewmodel, mock_repository):
        errors = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        viewmodel.create_project(name="")

        assert len(errors) == 1
        mock_repository.create_project.assert_not_called()

    def test_whitespace_only_name_is_rejected(self, viewmodel, mock_repository):
        errors = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        viewmodel.create_project(name="   ")

        assert len(errors) == 1
        mock_repository.create_project.assert_not_called()

    def test_valid_name_is_accepted(self, viewmodel, mock_repository):
        viewmodel.create_project(name="أجور موظفين")
        mock_repository.create_project.assert_called_once()


class TestLoadProjects:
    """اختبار جلب المشاريع وإرسالها عبر الإشارة (Signal)."""

    def test_load_projects_emits_projects_loaded(self, viewmodel, mock_repository):
        fake_projects = [Project(id=1, name="أجور موظفين")]
        mock_repository.get_all_projects.return_value = fake_projects

        received = []
        viewmodel.projects_loaded.connect(lambda projects: received.append(projects))

        viewmodel.load_projects()

        assert received == [fake_projects]

    def test_load_projects_handles_database_exception(self, viewmodel, mock_repository):
        mock_repository.get_all_projects.side_effect = DatabaseException("فشل الاتصال")

        errors = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        viewmodel.load_projects()

        assert len(errors) == 1
        assert "فشل الاتصال" in errors[0]


class TestCreateProjectAutoRefresh:
    """اختبار أن إنشاء مشروع بنجاح يُعيد تحميل القائمة تلقائيًا."""

    def test_successful_create_reloads_list(self, viewmodel, mock_repository):
        mock_repository.get_all_projects.return_value = []
        viewmodel.create_project(name="أجور موظفين", description="مشروع تجريبي")

        # يجب أن يُستدعى create_project مرة، و get_all_projects مرة (بسبب load_projects التلقائي)
        mock_repository.create_project.assert_called_once()
        mock_repository.get_all_projects.assert_called_once()


class TestDeleteProject:
    """اختبار حذف مشروع وإعادة تحميل القائمة."""

    def test_delete_project_calls_repository(self, viewmodel, mock_repository):
        mock_repository.get_all_projects.return_value = []
        viewmodel.delete_project(project_id=3)

        mock_repository.delete_project.assert_called_once_with(3)
        mock_repository.get_all_projects.assert_called_once()  # إعادة تحميل تلقائية

    def test_delete_project_handles_exception(self, viewmodel, mock_repository):
        mock_repository.delete_project.side_effect = DatabaseException("فشل الحذف")

        errors = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        viewmodel.delete_project(project_id=99)

        assert len(errors) == 1
        assert "فشل الحذف" in errors[0]