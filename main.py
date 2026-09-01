from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from core.database.database_service import DatabaseService
from core.services.language_service import LanguageService
from core.services.runtime_paths import RuntimePaths
from data.repositories.field_repository_impl import FieldRepositoryImpl
from data.repositories.project_repository_impl import ProjectRepositoryImpl
from presentation.theme.theme_service import ThemeService
from presentation.viewmodels.field_viewmodel import FieldViewModel
from presentation.viewmodels.project_viewmodel import ProjectViewModel
from presentation.views.project_list_view import ProjectListView


APP_NAME = "Paper2Data"
APP_VERSION = "1.0.0"


def _create_main_window(app: QApplication, db_service: DatabaseService) -> ProjectListView:
    theme_service = ThemeService(app)
    theme_service.initialize()

    language_service = LanguageService(app)
    language_service.initialize()

    project_repo = ProjectRepositoryImpl(db_service)
    field_repo = FieldRepositoryImpl(db_service)
    project_viewmodel = ProjectViewModel(project_repo)
    field_viewmodel = FieldViewModel(field_repo)

    return ProjectListView(
        project_viewmodel,
        field_viewmodel,
        db_service,
        language_service,
        theme_service,
    )


def _configure_application(app: QApplication) -> None:
    app.setStyle("Fusion")
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_NAME)

    icon_path = RuntimePaths.resource("presentation/resources/app_icon.ico")
    if icon_path.is_file():
        app.setWindowIcon(QIcon(str(icon_path)))


def _run_smoke_test(app: QApplication) -> int:
    """Initialize the frozen application against a temporary database and exit."""
    with tempfile.TemporaryDirectory(prefix="paper2data_smoke_") as temp_dir:
        db_service = DatabaseService(Path(temp_dir) / "smoke.db")
        main_window = _create_main_window(app, db_service)
        main_window.show()
        app.processEvents()
        main_window.close()
        app.processEvents()
    return 0


def main() -> int:
    app = QApplication(sys.argv)
    _configure_application(app)

    if "--smoke-test" in sys.argv:
        return _run_smoke_test(app)

    db_service = DatabaseService()
    main_window = _create_main_window(app, db_service)
    main_window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
