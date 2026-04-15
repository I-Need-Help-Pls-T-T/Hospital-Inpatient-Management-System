from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Optional

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