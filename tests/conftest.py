import os

import pytest


@pytest.fixture
def quality_db_service(tmp_path):
    """A real SQLite database isolated to one test."""
    from core.database.database_service import DatabaseService

    return DatabaseService(db_name=str(tmp_path / "paper2data_quality.db"))


@pytest.fixture(scope="session")
def qapp():
    """Offscreen QApplication for GUI smoke tests on CI and developer machines."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    qt_widgets = pytest.importorskip("PySide6.QtWidgets")
    app = qt_widgets.QApplication.instance() or qt_widgets.QApplication([])
    return app
