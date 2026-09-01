import sqlite3
from typing import List, Optional
from domain.entities.project import Project
from domain.repositories.project_repository import ProjectRepository
from core.database.database_service import DatabaseService
from core.errors.exceptions import DatabaseException

class ProjectRepositoryImpl(ProjectRepository):
    """
    التنفيذ الفعلي لواجهة ProjectRepository باستخدام SQLite.
    """
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create_project(self, project: Project) -> Project:
        try:
            with self.db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO projects (name, description) VALUES (?, ?);",
                    (project.name, project.description)
                )
                conn.commit()
                project.id = cursor.lastrowid
                return project
        except sqlite3.Error as e:
            raise DatabaseException(f"فشل في إنشاء المشروع: {str(e)}")

    def get_all_projects(self) -> List[Project]:
        try:
            with self.db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT p.id, p.name, p.description, p.created_at, p.updated_at,
                           COUNT(r.id) AS record_count
                    FROM projects p
                    LEFT JOIN records r ON r.project_id = p.id
                    GROUP BY p.id
                    ORDER BY p.updated_at DESC;
                    """
                )
                rows = cursor.fetchall()
                return [
                    Project(
                        id=row["id"],
                        name=row["name"],
                        description=row["description"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        record_count=int(row["record_count"] or 0),
                    )
                    for row in rows
                ]
        except sqlite3.Error as e:
            raise DatabaseException(f"فشل في جلب المشاريع: {str(e)}")

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        try:
            with self.db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, description, created_at, updated_at FROM projects WHERE id = ?;",
                    (project_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return Project(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
        except sqlite3.Error as e:
            raise DatabaseException(f"فشل في جلب تفاصيل المشروع: {str(e)}")

    def update_project(self, project: Project) -> bool:
        if not project.id:
            raise DatabaseException("لا يمكن تعديل مشروع بدون معرف (ID).")
        try:
            with self.db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE projects 
                    SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?;
                    """,
                    (project.name, project.description, project.id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseException(f"فشل في تحديث بيانات المشروع: {str(e)}")

    def delete_project(self, project_id: int) -> bool:
        try:
            with self.db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM projects WHERE id = ?;", (project_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseException(f"فشل في حذف المشروع: {str(e)}")