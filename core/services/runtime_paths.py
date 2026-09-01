from __future__ import annotations

import os
import sys
from pathlib import Path


class RuntimePaths:
    """Resolve bundled resources and writable application data paths.

    Source runs keep using the project directory for backward compatibility.
    Frozen Windows builds store mutable data under LOCALAPPDATA so updates to
    the application cannot overwrite the user's database.
    """

    APP_NAME = "Paper2Data"

    @classmethod
    def is_frozen(cls) -> bool:
        return bool(getattr(sys, "frozen", False))

    @classmethod
    def project_root(cls) -> Path:
        return Path(__file__).resolve().parents[2]

    @classmethod
    def resource_root(cls) -> Path:
        bundle_root = getattr(sys, "_MEIPASS", None)
        if cls.is_frozen() and bundle_root:
            return Path(bundle_root)
        return cls.project_root()

    @classmethod
    def resource(cls, relative_path: str | Path) -> Path:
        return cls.resource_root() / Path(relative_path)

    @classmethod
    def data_dir(cls) -> Path:
        override = os.environ.get("PAPER2DATA_DATA_DIR")
        if override:
            target = Path(override).expanduser()
        elif cls.is_frozen():
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                target = Path(local_app_data) / cls.APP_NAME
            else:
                target = Path.home() / ".paper2data"
        else:
            # Preserve the existing development workflow and database location.
            target = cls.project_root()

        target.mkdir(parents=True, exist_ok=True)
        return target

    @classmethod
    def database_path(cls, db_name: str | Path = "paper2data_local.db") -> Path:
        requested = Path(db_name).expanduser()
        if requested.is_absolute() or requested.parent != Path("."):
            requested.parent.mkdir(parents=True, exist_ok=True)
            return requested

        override = os.environ.get("PAPER2DATA_DB_PATH")
        if override:
            target = Path(override).expanduser()
            target.parent.mkdir(parents=True, exist_ok=True)
            return target

        return cls.data_dir() / requested.name
