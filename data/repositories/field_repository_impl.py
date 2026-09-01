import sqlite3
from typing import List

from core.database.database_service import DatabaseService
from core.errors.exceptions import DatabaseException
from domain.entities.field import Field, FieldOption
from domain.entities.field_type import FieldType
from domain.repositories.field_repository import FieldRepository


class FieldRepositoryImpl(FieldRepository):
    """SQLite implementation of FieldRepository."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def add_field(self, field: Field) -> Field:
        try:
            with self.db_service.get_connection() as conn:
                cursor = conn.cursor()
                field.field_type = FieldType.normalize(field.field_type)
                cursor.execute(
                    """
                    INSERT INTO fields (project_id, name, field_type, is_required, display_order)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        field.project_id,
                        field.name,
                        field.field_type,
                        int(field.is_required),
                        field.display_order,
                    ),
                )
                field.id = cursor.lastrowid

                if field.options:
                    options_data = [
                        (field.id, opt.label, opt.value, opt.display_order)
                        for opt in field.options
                    ]
                    cursor.executemany(
                        """
                        INSERT INTO field_options (field_id, label, value, display_order)
                        VALUES (?, ?, ?, ?);
                        """,
                        options_data,
                    )
                    cursor.execute(
                        "SELECT id FROM field_options WHERE field_id = ? ORDER BY id",
                        (field.id,),
                    )
                    for idx, row in enumerate(cursor.fetchall()):
                        field.options[idx].id = row["id"]
                        field.options[idx].field_id = field.id

                conn.commit()
                return field
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to add field: {e}")

    def get_fields_by_project(self, project_id: int) -> List[Field]:
        try:
            with self.db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM fields WHERE project_id = ? ORDER BY display_order ASC;",
                    (project_id,),
                )
                fields_rows = cursor.fetchall()

                fields = []
                for row in fields_rows:
                    field = Field(
                        id=row["id"],
                        project_id=row["project_id"],
                        name=row["name"],
                        field_type=row["field_type"],
                        is_required=bool(row["is_required"]),
                        display_order=row["display_order"],
                    )
                    cursor.execute(
                        "SELECT * FROM field_options WHERE field_id = ? ORDER BY display_order ASC;",
                        (field.id,),
                    )
                    field.options = [
                        FieldOption(
                            id=opt_row["id"],
                            field_id=opt_row["field_id"],
                            label=opt_row["label"],
                            value=opt_row["value"],
                            display_order=opt_row["display_order"],
                        )
                        for opt_row in cursor.fetchall()
                    ]
                    fields.append(field)

                return fields
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to load project fields: {e}")

    def update_field(self, field: Field) -> bool:
        if not field.id:
            raise DatabaseException("Cannot update a field without an ID.")
        try:
            with self.db_service.get_connection() as conn:
                cursor = conn.cursor()
                field.field_type = FieldType.normalize(field.field_type)
                cursor.execute(
                    """
                    UPDATE fields
                    SET name = ?, field_type = ?, is_required = ?, display_order = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?;
                    """,
                    (
                        field.name,
                        field.field_type,
                        int(field.is_required),
                        field.display_order,
                        field.id,
                    ),
                )
                updated = cursor.rowcount > 0
                cursor.execute("DELETE FROM field_options WHERE field_id = ?;", (field.id,))
                if field.options:
                    cursor.executemany(
                        """
                        INSERT INTO field_options (field_id, label, value, display_order)
                        VALUES (?, ?, ?, ?);
                        """,
                        [
                            (field.id, opt.label, opt.value, opt.display_order)
                            for opt in field.options
                        ],
                    )
                conn.commit()
                return updated
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to update field: {e}")

    def delete_field(self, field_id: int) -> bool:
        try:
            with self.db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM fields WHERE id = ?;", (field_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to delete field: {e}")
