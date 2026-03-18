from __future__ import annotations
from pydantic import BaseModel, ConfigDict, computed_field, model_validator
from datetime import date, datetime
from typing import Optional, List
from enum import Enum

class GenderEnum(str, Enum):
    Мужской = "Мужской"
    Женский = "Женский"

class StaffConditionEnum(str, Enum):
    Активен = "Активен"
    На_больничном = "На больничном"
    Отпуск = "Отпуск"
    Уволен = "Уволен"

class PaymentMethodEnum(str, Enum):
    Наличные = "Наличные"
    Карта = "Карта"
    Страховка = "Страховка"

# ----- Базовые схемы -----
# ----- Department -----
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

# ----- Position -----
class PositionBase(BaseModel):
    name: str
    med_education: bool = True
    description: Optional[str] = None

class PositionCreate(PositionBase):
    pass

class Position(PositionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ----- Room -----
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

# ----- Ward -----
class WardBase(BaseModel):
    room_id: Optional[int] = None
    w_place: int = 0
    m_place: int = 0

class WardCreate(WardBase):
    pass

class Ward(WardBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ----- Staff -----
class StaffBase(BaseModel):
    full_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    condition: Optional[StaffConditionEnum] = StaffConditionEnum.Активен
    room_id: Optional[int] = None
    login: Optional[str] = None
    access_level: int = 0

class StaffCreate(StaffBase):
    password: str

class Staff(StaffBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class StaffUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    condition: Optional[StaffConditionEnum] = None
    access_level: Optional[int] = None
    password: Optional[str] = None

class StaffShort(BaseModel):
    full_name: str
    model_config = ConfigDict(from_attributes=True)

# ----- Patient -----
class PatientBase(BaseModel):
    full_name: str
    birth_date: date
    gender: Optional[GenderEnum] = None
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

# ----- Hospitalization -----
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
    payments: List[Payment] = []
    @computed_field
    @property
    def is_paid(self) -> bool:
        # Логика Pydantic для отображения в JSON
        return len(self.payments) > 0

    model_config = ConfigDict(from_attributes=True)

class HospitalizationFull(Hospitalization):
    patient: Optional[PatientShort] = None
    patient_admission: Optional[PatientAdmission] = None
    model_config = ConfigDict(from_attributes=True)

# ----- PatientAdmission -----
class PatientAdmissionBase(BaseModel):
    hospitalization_id: int
    arrival_time: datetime
    end_time: Optional[datetime] = None

    @model_validator(mode='after')
    def check_dates(self):
        if self.end_time and self.arrival_time:
            if self.end_time < self.arrival_time:
                raise ValueError("Дата отмены не может быть раньше даты назначения")
        return self

class PatientAdmissionCreate(PatientAdmissionBase):
    pass

class PatientAdmission(PatientAdmissionBase):
    model_config = ConfigDict(from_attributes=True)

# ----- MedEntry -----
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

# ----- MedicationOrder -----
class MedicationOrderBase(BaseModel):
    med_entry_id: Optional[int] = None
    name: str
    dose: Optional[str] = None
    rules_taking: Optional[str] = None
    begin_date: Optional[date] = None
    end_date: Optional[date] = None

    @model_validator(mode='after')
    def check_dates(self):
        if self.end_date and self.begin_date:
            if self.end_date < self.begin_date:
                raise ValueError("Дата отмены не может быть раньше даты назначения")
        return self

class MedicationOrderCreate(MedicationOrderBase):
    pass

class MedicationOrder(MedicationOrderBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ----- Payment -----
class PaymentBase(BaseModel):
    hospitalization_id: Optional[int] = None
    payment_date: Optional[date] = None
    amount: float
    method: Optional[PaymentMethodEnum] = None

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ----- AdmissionTeam -----
class AdmissionTeamBase(BaseModel):
    hospitalization_id: Optional[int] = None
    staff_id: Optional[int] = None
    begin_time: datetime
    end_time: Optional[datetime] = None
    role: Optional[str] = None

    @model_validator(mode='after')
    def check_dates(self):
        if self.end_time and self.begin_time:
            if self.end_time < self.begin_time:
                raise ValueError("Дата отмены не может быть раньше даты назначения")
        return self

class AdmissionTeamCreate(AdmissionTeamBase):
    pass

class AdmissionTeam(AdmissionTeamBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ----- StaffRole -----
class StaffRoleBase(BaseModel):
    staff_id: int
    position_id: int
    appointment_date: date
    end_date: Optional[date] = None

class StaffRoleCreate(StaffRoleBase):
    pass

class StaffRole(StaffRoleBase):
    model_config = ConfigDict(from_attributes=True)

# Фидбэк
class FeedbackCreate(BaseModel):
    subject: str
    description: str
    feedback_type: str = "Ошибка"
    section: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    staff_id: Optional[int]
    subject: str
    description: str
    feedback_type: str
    section: Optional[str]
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True
