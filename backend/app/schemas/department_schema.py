from pydantic import BaseModel, ConfigDict
from typing import Optional

class DepartmentBase(BaseModel):
    name: str
    phone: Optional[str] = None
    profile: Optional[str] = None
    category: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)