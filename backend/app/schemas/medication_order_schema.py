from pydantic import BaseModel, ConfigDict, model_validator
from datetime import date
from typing import Optional

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