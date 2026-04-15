from pydantic import BaseModel, ConfigDict
from typing import Optional

class WardBase(BaseModel):
    room_id: Optional[int] = None
    w_place: int = 0
    m_place: int = 0

class WardCreate(WardBase):
    pass

class Ward(WardBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class WardAvailability(BaseModel):
    ward_id: int
    capacity_w: int
    capacity_m: int
    occupied_w: int
    occupied_m: int
    free_w: int
    free_m: int

    model_config = ConfigDict(from_attributes=True)
