from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional
from backend.app.models.base_models import PaymentMethod

class PaymentBase(BaseModel):
    hospitalization_id: Optional[int] = None
    payment_date: Optional[date] = None
    amount: float
    method: Optional[PaymentMethod] = None

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)