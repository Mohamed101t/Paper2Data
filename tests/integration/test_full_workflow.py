import pytest
import tempfile
import os
from core.database.database_service import DatabaseService
from data.repositories.project_repository_impl import ProjectRepositoryImpl
from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.project import Project
from domain.entities.field import Field, FieldOption
from domain.entities.record import Record, RecordValue


@pytest.fixture
def db_service(tmp_path):
    """
    قاعدة بيانات SQLite حقيقية في ملف مؤقت (وليست Mock).
    نستخدم tmp_path (من pytest نفسه) بدل tempfile.mkstemp، لأن pytest
    يدير حذف هذه الملفات بشكل آمن يتوافق مع قيود نظام الملفات في Windows.
    """
    path = str(tmp_path / "test_paper2data.db")
    service = DatabaseService(db_name=path)
    yield service
    # لا حاجة لحذف يدوي — pytest ينظف مجلد tmp_path تلقائيًا بعد الجلسة

@pytest.fixture
def project_repo(db_service):
    return ProjectRepositoryImpl(db_service)


@pytest.fixture
def field_repo(db_service):
    return FieldRepositoryImpl(db_service)


@pytest.fixture
def record_repo(db_service):
    return RecordRepositoryImpl(db_service)


class TestFullWorkflow:
    """
    اختبار السيناريو الكامل: إنشاء مشروع → إضافة حقول →
    حفظ سجل → جلب السجلات → التحقق من القيم → الحذف.
    يطابق مسار UC-01 إلى UC-14 في الـ Spec.
    """

    def test_create_project_and_retrieve_it(self, project_repo):
        project = Project(name="أجور موظفين", description="مشروع اختباري")
        created = project_repo.create_project(project)

        assert created.id is not None

        all_projects = project_repo.get_all_projects()
        assert len(all_projects) == 1
        assert all_projects[0].name == "أجور موظفين"

    def test_add_field_with_options_and_retrieve(self, project_repo, field_repo):
        project = project_repo.create_project(Project(name="أجور موظفين"))

        field = Field(
            project_id=project.id,
            name="القسم",
            field_type="Single Choice",
            is_required=True,
            options=[
                FieldOption(label="الإدارة", value="الإدارة", display_order=0),
                FieldOption(label="المبيعات", value="المبيعات", display_order=1),
            ]
        )
        field_repo.add_field(field)

        fields = field_repo.get_fields_by_project(project.id)
        assert len(fields) == 1
        assert fields[0].name == "القسم"
        assert len(fields[0].options) == 2
        assert fields[0].options[0].label == "الإدارة"

    def test_full_record_lifecycle(self, project_repo, field_repo, record_repo):
        """السيناريو الكامل من إنشاء المشروع حتى حذف السجل."""
        # 1. إنشاء مشروع
        project = project_repo.create_project(Project(name="أجور موظفين"))

        # 2. إضافة حقلين
        name_field = field_repo.add_field(
            Field(project_id=project.id, name="اسم الموظف", field_type="Text", is_required=True)
        )
        salary_field = field_repo.add_field(
            Field(project_id=project.id, name="الراتب", field_type="Number", is_required=True)
        )

        # 3. حفظ سجل
        record = Record(
            project_id=project.id,
            values=[
                RecordValue(field_id=name_field.id, value="محمد أحمد"),
                RecordValue(field_id=salary_field.id, value="8500"),
            ]
        )
        record_id = record_repo.add_record(record)
        assert record_id is not None

        # 4. جلب السجلات والتحقق من القيم (يختبر الـ JOIN بشكل حقيقي)
        records = record_repo.get_records_by_project(project.id)
        assert len(records) == 1
        assert len(records[0].values) == 2

        values_by_field = {v.field_id: v.value for v in records[0].values}
        assert values_by_field[name_field.id] == "محمد أحمد"
        assert values_by_field[salary_field.id] == "8500"

        # 5. حذف السجل والتأكد أن CASCADE يعمل فعليًا
        record_repo.delete_record(record_id)
        remaining = record_repo.get_records_by_project(project.id)
        assert len(remaining) == 0

    def test_multiple_records_are_retrieved_correctly(self, project_repo, field_repo, record_repo):
        """اختبار أن JOIN لا يخلط بيانات السجلات ببعضها عند وجود أكثر من سجل."""
        project = project_repo.create_project(Project(name="أجور موظفين"))
        name_field = field_repo.add_field(
            Field(project_id=project.id, name="اسم الموظف", field_type="Text", is_required=True)
        )

        for name in ["محمد", "سارة", "خالد"]:
            record_repo.add_record(
                Record(project_id=project.id, values=[RecordValue(field_id=name_field.id, value=name)])
            )

        records = record_repo.get_records_by_project(project.id)
        assert len(records) == 3

        names = {r.values[0].value for r in records}
        assert names == {"محمد", "سارة", "خالد"}

    def test_delete_project_cascades_to_fields(self, project_repo, field_repo):
        """
        اختبار حرج: حذف المشروع يجب أن يحذف حقوله تلقائيًا (ON DELETE CASCADE).
        هذا يتحقق تحديدًا من أن PRAGMA foreign_keys = ON يعمل فعليًا.
        """
        project = project_repo.create_project(Project(name="أجور موظفين"))
        field_repo.add_field(
            Field(project_id=project.id, name="القسم", field_type="Text", is_required=False)
        )

        assert len(field_repo.get_fields_by_project(project.id)) == 1

        project_repo.delete_project(project.id)

        # الحقل يجب أن يختفي تلقائيًا بسبب CASCADE
        assert len(field_repo.get_fields_by_project(project.id)) == 0

    def test_field_without_options_has_empty_list(self, field_repo, project_repo):
        project = project_repo.create_project(Project(name="أجور موظفين"))
        field_repo.add_field(
            Field(project_id=project.id, name="ملاحظات", field_type="Text", is_required=False)
        )

        fields = field_repo.get_fields_by_project(project.id)
        assert fields[0].options == []