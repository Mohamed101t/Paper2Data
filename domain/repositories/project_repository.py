from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.project import Project


class ProjectRepository(ABC):
    """
    واجهة مجردة لعمليات إدارة المشاريع (Interface - DIP).
    """

    @abstractmethod
    def create_project(self, project: Project) -> Project:
        """إنشاء مشروع جديد وحفظه."""
        pass

    @abstractmethod
    def get_all_projects(self) -> List[Project]:
        """جلب جميع المشاريع."""
        pass

    @abstractmethod
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """جلب مشروع محدد بواسطة الرقم التعريفي."""
        pass

    @abstractmethod
    def update_project(self, project: Project) -> bool:
        """تعديل بيانات مشروع موجود."""
        pass

    @abstractmethod
    def delete_project(self, project_id: int) -> bool:
        """حذف مشروع بواسطة الرقم التعريفي."""
        pass