from typing import List
from domain.entities.record import Record, RecordValue
from domain.repositories.record_repository import RecordRepository
from core.database.database_service import DatabaseService
from core.errors.exceptions import DatabaseException


class RecordRepositoryImpl(RecordRepository):
    """
    التنفيذ الفعلي لعمليات السجلات عبر SQLite.
    ملاحظة: إنشاء الجداول (schema) هو مسؤولية DatabaseService حصريًا (SRP) —
    لا تُضف هنا أي CREATE TABLE.
    """

    def __init__(self, db_service: DatabaseService):
        self._db_service = db_service

    def add_record(self, record: Record) -> int:
        try:
            with self._db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO records (project_id) VALUES (?)",
                    (record.project_id,)
                )
                record_id = cursor.lastrowid

                if record.values:
                    cursor.executemany(
                        "INSERT INTO record_values (record_id, field_id, value) VALUES (?, ?, ?)",
                        [(record_id, val.field_id, str(val.value)) for val in record.values]
                    )

                conn.commit()
                return record_id
        except Exception as e:
            raise DatabaseException(f"فشل في حفظ السجل: {e}")

    def get_records_by_project(self, project_id: int) -> List[Record]:
        """
        استعلام واحد بـ LEFT JOIN بدل N+1 query.
        """
        try:
            with self._db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT r.id, r.project_id, r.created_at, rv.field_id, rv.value
                    FROM records r
                    LEFT JOIN record_values rv ON rv.record_id = r.id
                    WHERE r.project_id = ?
                    ORDER BY r.id DESC
                    """,
                    (project_id,)
                )
                rows = cursor.fetchall()

                records_map = {}
                for row in rows:
                    rec_id = row["id"]
                    if rec_id not in records_map:
                        records_map[rec_id] = Record(
                            project_id=row["project_id"],
                            id=rec_id,
                            created_at=row["created_at"],
                            values=[]
                        )
                    if row["field_id"] is not None:
                        records_map[rec_id].values.append(
                            RecordValue(field_id=row["field_id"], value=row["value"])
                        )

                return list(records_map.values())
        except Exception as e:
            raise DatabaseException(f"فشل في جلب السجلات: {e}")

    def delete_record(self, record_id: int) -> None:
        try:
            with self._db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
                conn.commit()
        except Exception as e:
            raise DatabaseException(f"فشل في حذف السجل: {e}")

    def update_record(self, record: Record) -> None:
        if not record.id:
            raise DatabaseException("لا يمكن تعديل سجل بدون معرف (ID).")
        try:
            with self._db_service.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE records SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (record.id,),
                )
                if cursor.rowcount == 0:
                    raise DatabaseException("السجل غير موجود.")
                cursor.execute(
                    "DELETE FROM record_values WHERE record_id = ?",
                    (record.id,),
                )
                if record.values:
                    cursor.executemany(
                        "INSERT INTO record_values (record_id, field_id, value) VALUES (?, ?, ?)",
                        [(record.id, val.field_id, str(val.value)) for val in record.values],
                    )
                conn.commit()
        except DatabaseException:
            raise
        except Exception as e:
            raise DatabaseException(f"فشل في تعديل السجل: {e}")