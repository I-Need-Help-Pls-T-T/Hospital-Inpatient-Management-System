from pydantic import BaseModel, ConfigDict, model_validator
from datetime import date
from typing import Optional

class StaffRoleBase(BaseModel):
    staff_id: int
    position_id: int
    appointment_date: date
    end_date: Optional[date] = None

class StaffRoleCreate(StaffRoleBase):
    pass

class StaffRole(StaffRoleBase):
    model_config = ConfigDict(from_attributes=True)