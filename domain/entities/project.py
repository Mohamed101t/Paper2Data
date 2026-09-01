from dataclasses import dataclass
from typing import Optional

@dataclass
class Project:
    name: str
    description: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    record_count: int = 0