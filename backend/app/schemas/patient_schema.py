from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from backend.app.models.base_models import GenderType

class PatientBase(BaseModel):
    full_name: str
    birth_date: date
    gender: Optional[GenderType] = None
    address: Optional[str] = None
    passport: Optional[str] = None
    phone: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class PatientShort(BaseModel):
    id: int
    full_name: str
    model_config = ConfigDict(from_attributes=True)