import sqlite3
from pathlib import Path

from core.errors.exceptions import DatabaseException
from core.services.runtime_paths import RuntimePaths


class DatabaseService:
    """Owns SQLite connection creation and schema initialization."""

    def __init__(self, db_name: str | Path = "paper2data_local.db"):
        self.db_path = RuntimePaths.database_path(db_name)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as exc:
            raise DatabaseException(f"Database connection failed: {exc}") from exc

    def init_db(self) -> None:
        try:
            with self.get_connection() as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS projects (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

                    CREATE TABLE IF NOT EXISTS fields (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        field_type TEXT NOT NULL,
                        is_required INTEGER DEFAULT 0,
                        display_order INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS field_options (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        field_id INTEGER NOT NULL,
                        label TEXT NOT NULL,
                        value TEXT NOT NULL,
                        display_order INTEGER DEFAULT 0,
                        FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                    );

                    CREATE TABLE IF NOT EXISTS record_values (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        record_id INTEGER NOT NULL,
                        field_id INTEGER NOT NULL,
                        value TEXT,
                        FOREIGN KEY (record_id) REFERENCES records(id) ON DELETE CASCADE,
                        FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
                    );
                    """
                )
                conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseException(f"Database initialization failed: {exc}") from exc
