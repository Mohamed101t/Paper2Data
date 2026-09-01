import pytest
from unittest.mock import MagicMock
from presentation.viewmodels.field_viewmodel import FieldViewModel
from domain.entities.field import Field


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.get_fields_by_project.return_value = []  # لا توجد حقول سابقة افتراضيًا
    return repo


@pytest.fixture
def viewmodel(mock_repository):
    vm = FieldViewModel(mock_repository)
    vm.current_project_id = 1  # محاكاة اختيار مشروع مسبقًا
    return vm


class TestFieldNameValidation:
    """اختبار قاعدة: اسم الحقل لا يمكن أن يكون فارغًا."""

    def test_empty_name_is_rejected(self, viewmodel, mock_repository):
        errors = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        viewmodel.add_field(name="", field_type="Text", is_required=True)

        assert len(errors) == 1
        mock_repository.add_field.assert_not_called()

    def test_whitespace_only_name_is_rejected(self, viewmodel, mock_repository):
        errors = []
        viewmodel.error_occurred.connect(lambda msg: errors.append(msg))

        viewmodel.add_field(name="   ", field_type="Text", is_required=True)

        assert len(errors) == 1
        mock_repository.add_field.assert_not_called()

    def test_valid_name_is_accepted(self, viewmodel, mock_repository):
        viewmodel.add_field(name="القسم", field_type="Text", is_required=True)
        mock_repository.add_field.assert_called_once()


class TestNoProjectSelected:
    """اختبار قاعدة: لا يمكن إضافة حقل بدون تحديد مشروع أولاً."""

    def test_add_field_without_project_fails(self, mock_repository):
        vm = FieldViewModel(mock_repository)  # لم يُستدعَ set_project
        errors = []
        vm.error_occurred.connect(lambda msg: errors.append(msg))

        vm.add_field(name="القسم", field_type="Text", is_required=True)

        assert len(errors) == 1
        mock_repository.add_field.assert_not_called()


class TestOptionsParsing:
    """اختبار قاعدة: تحويل نص الخيارات (مفصول بفواصل) إلى قائمة FieldOption."""

    def test_single_choice_with_options_creates_options(self, viewmodel, mock_repository):
        viewmodel.add_field(
            name="القسم",
            field_type="Single Choice",
            is_required=True,
            raw_options="الإدارة, المبيعات, الإنتاج, المحاسبة"
        )

        saved_field: Field = mock_repository.add_field.call_args[0][0]
        assert len(saved_field.options) == 4
        assert saved_field.options[0].label == "الإدارة"
        assert saved_field.options[3].label == "المحاسبة"

    def test_text_field_ignores_options(self, viewmodel, mock_repository):
        """حقل من نوع Text لا يجب أن يُنشئ خيارات حتى لو كُتب نص في raw_options."""
        viewmodel.add_field(
            name="الاسم",
            field_type="Text",
            is_required=True,
            raw_options="خيار1, خيار2"
        )

        saved_field: Field = mock_repository.add_field.call_args[0][0]
        assert len(saved_field.options) == 0

    def test_empty_options_string_creates_no_options(self, viewmodel, mock_repository):
        viewmodel.add_field(
            name="القسم",
            field_type="Single Choice",
            is_required=True,
            raw_options=""
        )

        saved_field: Field = mock_repository.add_field.call_args[0][0]
        assert len(saved_field.options) == 0

    def test_options_with_extra_whitespace_are_trimmed(self, viewmodel, mock_repository):
        """اختبار أن المسافات الزائدة حول الفواصل تُزال."""
        viewmodel.add_field(
            name="القسم",
            field_type="Single Choice",
            is_required=True,
            raw_options="  الإدارة  ,  المبيعات  "
        )

        saved_field: Field = mock_repository.add_field.call_args[0][0]
        assert saved_field.options[0].label == "الإدارة"
        assert saved_field.options[1].label == "المبيعات"


class TestDeleteField:
    """اختبار حذف حقل."""

    def test_delete_field_calls_repository(self, viewmodel, mock_repository):
        viewmodel.delete_field(field_id=5)
        mock_repository.delete_field.assert_called_once_with(5)