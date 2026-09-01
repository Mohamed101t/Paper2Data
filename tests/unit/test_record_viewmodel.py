import pytest
from unittest.mock import MagicMock
from presentation.viewmodels.record_viewmodel import RecordViewModel
from domain.entities.field import Field


@pytest.fixture
def mock_repository():
    """مستودع وهمي (Mock) لا يتصل بقاعدة بيانات حقيقية."""
    repo = MagicMock()
    repo.add_record.return_value = 1
    return repo


@pytest.fixture
def viewmodel(mock_repository):
    return RecordViewModel(mock_repository)


@pytest.fixture
def sample_fields():
    """حقول تمثل مشروع 'أجور موظفين' المصغّر."""
    return [
        Field(id=1, project_id=1, name="اسم الموظف", field_type="Text", is_required=True),
        Field(id=2, project_id=1, name="الراتب الأساسي", field_type="Number", is_required=True),
        Field(id=3, project_id=1, name="البريد الإلكتروني", field_type="Email", is_required=False),
    ]


class TestRequiredFieldValidation:
    """اختبار قاعدة: الحقل الإجباري لا يمكن أن يكون فارغًا (قسم 15 من الـ Spec)."""

    def test_empty_required_field_fails(self, viewmodel, sample_fields):
        form_data = {1: "", 2: "5000", 3: ""}
        result = viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        assert result is False

    def test_whitespace_only_required_field_fails(self, viewmodel, sample_fields):
        """مسافات فارغة فقط يجب أن تُعامل كحقل فارغ."""
        form_data = {1: "   ", 2: "5000", 3: ""}
        result = viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        assert result is False

    def test_filled_required_field_passes(self, viewmodel, sample_fields):
        form_data = {1: "محمد أحمد", 2: "5000", 3: ""}
        result = viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        assert result is True


class TestNumberFieldValidation:
    """اختبار قاعدة: حقل النوع Number يجب أن يحتوي رقمًا صحيحًا فقط."""

    def test_non_numeric_value_fails(self, viewmodel, sample_fields):
        form_data = {1: "محمد", 2: "خمسة آلاف", 3: ""}
        result = viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        assert result is False

    def test_decimal_number_passes(self, viewmodel, sample_fields):
        """الأرقام العشرية يجب أن تُقبل (مثل 9800.5)."""
        form_data = {1: "سارة", 2: "9800.5", 3: ""}
        result = viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        assert result is True

    def test_integer_number_passes(self, viewmodel, sample_fields):
        form_data = {1: "خالد", 2: "6200", 3: ""}
        result = viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        assert result is True


class TestEmailFieldValidation:
    """اختبار قاعدة: حقل Email يجب أن يحتوي @ ونقطة."""

    def test_invalid_email_without_at_fails(self, viewmodel, sample_fields):
        form_data = {1: "خالد", 2: "6200", 3: "khaled-invalid"}
        result = viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        assert result is False

    def test_valid_email_passes(self, viewmodel, sample_fields):
        form_data = {1: "سارة", 2: "9800", 3: "sara@company.com"}
        result = viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        assert result is True

    def test_empty_optional_email_passes(self, viewmodel, sample_fields):
        """البريد الإلكتروني هنا غير إجباري، فالحقل الفارغ يجب أن يمر."""
        form_data = {1: "محمد", 2: "5000", 3: ""}
        result = viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        assert result is True


class TestRepositoryInteraction:
    """اختبار أن الـ ViewModel يستدعي المستودع بشكل صحيح عند النجاح."""

    def test_successful_save_calls_repository_once(self, viewmodel, mock_repository, sample_fields):
        form_data = {1: "محمد", 2: "5000", 3: ""}
        viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        mock_repository.add_record.assert_called_once()

    def test_failed_validation_never_calls_repository(self, viewmodel, mock_repository, sample_fields):
        """أهم اختبار: التحقق يجب أن يمنع الوصول لقاعدة البيانات أصلًا عند الفشل."""
        form_data = {1: "", 2: "5000", 3: ""}
        viewmodel.save_record(project_id=1, fields=sample_fields, form_data=form_data)
        mock_repository.add_record.assert_not_called()