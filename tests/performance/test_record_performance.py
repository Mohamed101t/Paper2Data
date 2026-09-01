import pytest
import time
from core.database.database_service import DatabaseService
from data.repositories.project_repository_impl import ProjectRepositoryImpl
from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.record_repository_impl import RecordRepositoryImpl
from domain.entities.project import Project
from domain.entities.field import Field
from domain.entities.record import Record, RecordValue


@pytest.fixture
def db_service(tmp_path):
    path = str(tmp_path / "perf_test.db")
    return DatabaseService(db_name=path)


@pytest.fixture
def setup_project_with_fields(db_service):
    """
    يُنشئ مشروعًا بحقول مشابهة لسيناريو 'أجور موظفين' الحقيقي،
    ويعيد (project_id, fields, record_repo) جاهزة للاستخدام في اختبارات الأداء.
    """
    project_repo = ProjectRepositoryImpl(db_service)
    field_repo = FieldRepositoryImpl(db_service)
    record_repo = RecordRepositoryImpl(db_service)

    project = project_repo.create_project(Project(name="اختبار أداء"))

    fields = [
        field_repo.add_field(Field(project_id=project.id, name="اسم الموظف", field_type="Text", is_required=True)),
        field_repo.add_field(Field(project_id=project.id, name="الرقم الوظيفي", field_type="Number", is_required=True)),
        field_repo.add_field(Field(project_id=project.id, name="الراتب الأساسي", field_type="Number", is_required=True)),
        field_repo.add_field(Field(project_id=project.id, name="البريد الإلكتروني", field_type="Email", is_required=False)),
    ]

    return project.id, fields, record_repo


def _insert_records(record_repo, project_id, fields, count: int):
    """يُدرج عددًا محددًا من السجلات، ويعيد الزمن المستغرق بالثواني."""
    start = time.perf_counter()
    for i in range(count):
        record_repo.add_record(Record(
            project_id=project_id,
            values=[
                RecordValue(field_id=fields[0].id, value=f"موظف رقم {i}"),
                RecordValue(field_id=fields[1].id, value=str(1000 + i)),
                RecordValue(field_id=fields[2].id, value=str(5000 + (i % 3000))),
                RecordValue(field_id=fields[3].id, value=f"emp{i}@company.com"),
            ]
        ))
    return time.perf_counter() - start


class TestInsertPerformance:
    """اختبار زمن إدخال السجلات دفعة واحدة."""

    def test_insert_1000_records(self, setup_project_with_fields):
        project_id, fields, record_repo = setup_project_with_fields
        elapsed = _insert_records(record_repo, project_id, fields, 1000)

        print(f"\n⏱ إدخال 1000 سجل: {elapsed:.2f} ثانية")
        # هدف Spec: أداء ممتاز — نضع سقفًا متساهلاً معقولاً كإنذار مبكر
        assert elapsed < 10, f"إدخال 1000 سجل استغرق {elapsed:.2f}s — أبطأ من المتوقع"

    def test_insert_5000_records(self, setup_project_with_fields):
        project_id, fields, record_repo = setup_project_with_fields
        elapsed = _insert_records(record_repo, project_id, fields, 5000)

        print(f"\n⏱ إدخال 5000 سجل: {elapsed:.2f} ثانية")
        assert elapsed < 40, f"إدخال 5000 سجل استغرق {elapsed:.2f}s — أبطأ من المتوقع"


class TestRetrievalPerformance:
    """
    اختبار زمن جلب السجلات مع الـ JOIN — هذا يختبر تحديدًا
    إصلاح N+1 query الذي طبّقناه في RecordRepositoryImpl.
    """

    def test_retrieve_1000_records_is_fast(self, setup_project_with_fields):
        project_id, fields, record_repo = setup_project_with_fields
        _insert_records(record_repo, project_id, fields, 1000)

        start = time.perf_counter()
        records = record_repo.get_records_by_project(project_id)
        elapsed = time.perf_counter() - start

        print(f"\n⏱ جلب 1000 سجل (JOIN واحد): {elapsed:.3f} ثانية")
        assert len(records) == 1000
        # استعلام واحد بـ JOIN يجب أن يكون سريعًا جدًا حتى مع آلاف السجلات
        assert elapsed < 2, f"جلب 1000 سجل استغرق {elapsed:.3f}s — تحقق من عدم رجوع N+1 query"

    def test_retrieve_5000_records_is_fast(self, setup_project_with_fields):
        project_id, fields, record_repo = setup_project_with_fields
        _insert_records(record_repo, project_id, fields, 5000)

        start = time.perf_counter()
        records = record_repo.get_records_by_project(project_id)
        elapsed = time.perf_counter() - start

        print(f"\n⏱ جلب 5000 سجل (JOIN واحد): {elapsed:.3f} ثانية")
        assert len(records) == 5000
        assert elapsed < 5, f"جلب 5000 سجل استغرق {elapsed:.3f}s — أبطأ من المتوقع"

    def test_retrieved_data_integrity_at_scale(self, setup_project_with_fields):
        """يتأكد أن كل سجل من بين 1000 يحتفظ بقيمه الأربع دون خلط أو فقدان."""
        project_id, fields, record_repo = setup_project_with_fields
        _insert_records(record_repo, project_id, fields, 1000)

        records = record_repo.get_records_by_project(project_id)

        for record in records:
            assert len(record.values) == 4  # كل سجل يجب أن يحتفظ بـ 4 قيم بالضبط