from dataclasses import dataclass, field
from typing import List, Optional

from domain.entities.field_type import FieldType


@dataclass
class FieldOption:
    label: str
    value: str
    id: Optional[int] = None
    field_id: Optional[int] = None
    display_order: int = 0


@dataclass
class Field:
    project_id: int
    name: str
    field_type: str
    is_required: bool = False
    display_order: int = 0
    id: Optional[int] = None
    options: List[FieldOption] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.field_type = FieldType.normalize(self.field_type)
