from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Staff, Feedback, FeedbackType
from backend.auth import get_current_user
from backend.schemas import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse)
def create_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Отправить сообщение об ошибке / обратную связь"""
    try:
        feedback_type = FeedbackType[data.feedback_type]
    except KeyError:
        feedback_type = FeedbackType.Ошибка

    feedback = Feedback(
        staff_id=current_user.id,
        subject=data.subject,
        description=data.description,
        feedback_type=feedback_type,
        section=data.section,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/", response_model=List[FeedbackResponse])
def list_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр всех обращений (только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    return db.query(Feedback).order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()


@router.patch("/{feedback_id}/read")
def mark_as_read(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Отметить обращение как прочитанное (только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Доступ запрещён")
    feedback = db.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    feedback.is_read = True
    db.commit()
    return {"message": "Отмечено как прочитанное"}


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Количество непрочитанных обращений (только уровень 3)"""
    if current_user.access_level < 3:
        return {"count": 0}
    count = db.query(Feedback).filter(Feedback.is_read == False).count()
    return {"count": count}
