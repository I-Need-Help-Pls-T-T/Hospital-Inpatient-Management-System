from __future__ import annotations
from pydantic import BaseModel, ConfigDict, computed_field
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

# TYPE_CHECKING нужен, чтобы избежать циклических импортов во время выполнения
if TYPE_CHECKING:
    from .payment_schema import Payment
    from .patient_schema import PatientShort
    from .admission_schema import PatientAdmission

class HospitalizationBase(BaseModel):
    patient_id: Optional[int] = None
    ward_id: Optional[int] = None
    care_type: Optional[str] = None
    outcome: Optional[str] = None
    treatment_summary: Optional[str] = None

class HospitalizationCreate(HospitalizationBase):
    pass

class Hospitalization(HospitalizationBase):
    id: int
    payments: List["Payment"] = []

    @computed_field
    @property
    def is_paid(self) -> bool:
        return len(self.payments) > 0

    model_config = ConfigDict(from_attributes=True)

class HospitalizationFull(Hospitalization):
    patient: Optional["PatientShort"] = None
    patient_admission: Optional["PatientAdmission"] = None
    model_config = ConfigDict(from_attributes=True)

class HospitalizePatientRequest(BaseModel):
    patient_id: int
    ward_id: int
    arrival_time: datetime
    care_type: Optional[str] = None
    outcome: Optional[str] = None
    treatment_summary: Optional[str] = None

from .payment_schema import Payment
from .patient_schema import PatientShort
from .admission_schema import PatientAdmission

Hospitalization.model_rebuild()
HospitalizationFull.model_rebuild()