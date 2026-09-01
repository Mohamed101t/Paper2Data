from pathlib import Path

from core.services.runtime_paths import RuntimePaths


def test_explicit_database_path_is_preserved(tmp_path):
    expected = tmp_path / "isolated.db"
    assert RuntimePaths.database_path(expected) == expected


def test_database_override_is_respected(monkeypatch, tmp_path):
    expected = tmp_path / "override" / "paper2data.db"
    monkeypatch.setenv("PAPER2DATA_DB_PATH", str(expected))
    assert RuntimePaths.database_path() == expected
    assert expected.parent.is_dir()


def test_data_directory_override_is_respected(monkeypatch, tmp_path):
    expected = tmp_path / "app_data"
    monkeypatch.setenv("PAPER2DATA_DATA_DIR", str(expected))
    assert RuntimePaths.data_dir() == expected
    assert expected.is_dir()


def test_resource_path_is_inside_resource_root():
    result = RuntimePaths.resource(Path("presentation") / "translations")
    assert result == RuntimePaths.resource_root() / "presentation" / "translations"


def test_frozen_data_dir_uses_local_app_data(monkeypatch, tmp_path):
    import sys

    monkeypatch.delenv("PAPER2DATA_DATA_DIR", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    assert RuntimePaths.data_dir() == tmp_path / "Paper2Data"


def test_frozen_resource_root_uses_meipass(monkeypatch, tmp_path):
    import sys

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert RuntimePaths.resource_root() == tmp_path
