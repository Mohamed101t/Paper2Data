from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class RecordValue:
    field_id: int
    value: Any


@dataclass
class Record:
    project_id: int
    id: Optional[int] = None
    created_at: Optional[str] = None
    values: List[RecordValue] = field(default_factory=list)
