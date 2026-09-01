from PySide6.QtCore import QObject, Signal

from core.errors.exceptions import DatabaseException
from domain.entities.project import Project
from domain.repositories.project_repository import ProjectRepository


class ProjectViewModel(QObject):
    projects_loaded = Signal(list)
    error_occurred = Signal(str)
    operation_success = Signal(str)

    def __init__(self, repository: ProjectRepository):
        super().__init__()
        self._repository = repository

    def load_projects(self):
        try:
            self.projects_loaded.emit(self._repository.get_all_projects())
        except DatabaseException as e:
            self._emit_database_error(e)

    def create_project(self, name: str, description: str = ""):
        if not name.strip():
            self.error_occurred.emit(self.tr("Project name is required."))
            return
        try:
            self._repository.create_project(Project(name=name.strip(), description=description))
            self.operation_success.emit(self.tr("Project created successfully."))
            self.load_projects()
        except DatabaseException as e:
            self._emit_database_error(e)

    def delete_project(self, project_id: int):
        try:
            self._repository.delete_project(project_id)
            self.operation_success.emit(self.tr("Project deleted successfully."))
            self.load_projects()
        except DatabaseException as e:
            self._emit_database_error(e)

    def rename_project(self, project_id: int, name: str):
        if not name.strip():
            self.error_occurred.emit(self.tr("Project name is required."))
            return
        try:
            project = self._repository.get_project_by_id(project_id)
            if project is None:
                self.error_occurred.emit(self.tr("Project not found."))
                return
            project.name = name.strip()
            self._repository.update_project(project)
            self.operation_success.emit(self.tr("Project name updated successfully."))
            self.load_projects()
        except DatabaseException as e:
            self._emit_database_error(e)

    def _emit_database_error(self, error: DatabaseException) -> None:
        self.error_occurred.emit(
            self.tr("Database operation failed: {error}").format(error=error)
        )
