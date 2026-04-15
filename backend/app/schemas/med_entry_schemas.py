from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .staff_schema import StaffShort

class MedEntryBase(BaseModel):
    patient_id: Optional[int] = None
    entry_date: Optional[datetime] = None
    description: Optional[str] = None
    staff_id: Optional[int] = None

class MedEntryCreate(MedEntryBase):
    pass

class MedEntry(MedEntryBase):
    id: int
    staff: Optional[StaffShort] = None
    model_config = ConfigDict(from_attributes=True)

from .staff_schema import StaffShort
MedEntry.model_rebuild()