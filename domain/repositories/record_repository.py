from abc import ABC, abstractmethod
from typing import List
from domain.entities.record import Record


class RecordRepository(ABC):
    """
    واجهة مجردة لعمليات إدارة السجلات (Interface - DIP).
    """

    @abstractmethod
    def add_record(self, record: Record) -> int:
        """يحفظ سجلًا جديدًا ويعيد الـ ID الخاص به."""
        pass

    @abstractmethod
    def get_records_by_project(self, project_id: int) -> List[Record]:
        """يجلب جميع سجلات مشروع معيّن مع قيمها."""
        pass

    @abstractmethod
    def delete_record(self, record_id: int) -> None:
        """يحذف سجلًا وقيمه المرتبطة به."""
        pass

    @abstractmethod
    def update_record(self, record: Record) -> None:
        """يحدّث قيم سجل موجود دون تغيير معرّفه."""
        pass