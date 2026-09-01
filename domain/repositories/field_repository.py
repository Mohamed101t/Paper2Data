from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.field import Field


class FieldRepository(ABC):
    """
    واجهة مجردة لعمليات إدارة حقول النماذج (Interface - DIP).
    تضمن فصل منطق التطبيق الأساسي عن تفاصيل قاعدة البيانات.
    """

    @abstractmethod
    def add_field(self, field: Field) -> Field:
        """إضافة حقل جديد إلى مشروع، مع خياراته (إن وجدت)."""
        pass

    @abstractmethod
    def get_fields_by_project(self, project_id: int) -> List[Field]:
        """جلب جميع الحقول الخاصة بمشروع معين مرتبة حسب display_order."""
        pass

    @abstractmethod
    def update_field(self, field: Field) -> bool:
        """تعديل خصائص حقل موجود."""
        pass

    @abstractmethod
    def delete_field(self, field_id: int) -> bool:
        """حذف حقل من المشروع."""
        pass