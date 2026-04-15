from pydantic import BaseModel, ConfigDict
from typing import Optional

class RoomBase(BaseModel):
    type: Optional[str] = None
    number: int
    capacity: Optional[int] = None
    department_id: Optional[int] = None

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
