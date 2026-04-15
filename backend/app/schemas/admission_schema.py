from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional

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