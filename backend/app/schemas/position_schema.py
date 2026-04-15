from pydantic import BaseModel, ConfigDict
from typing import Optional

class PositionBase(BaseModel):
    name: str
    med_education: bool = True
    description: Optional[str] = None

class PositionCreate(PositionBase):
    pass

class Position(PositionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
