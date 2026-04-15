from pydantic import BaseModel, ConfigDict
from typing import Optional
from backend.app.models.base_models import StaffCondition

class StaffBase(BaseModel):
    login: str
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    condition: Optional[StaffCondition] = StaffCondition.Активен
    room_id: Optional[int] = None
    access_level: int = 0

class StaffCreate(StaffBase):
    password: str 

class StaffUpdate(BaseModel):
    full_name: Optional[str] = None
    login: Optional[str] = None 
    phone: Optional[str] = None
    condition: Optional[StaffCondition] = None
    access_level: Optional[int] = None
    password: Optional[str] = None

class Staff(StaffBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StaffShort(BaseModel):
    full_name: str
    model_config = ConfigDict(from_attributes=True)