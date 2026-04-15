from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
