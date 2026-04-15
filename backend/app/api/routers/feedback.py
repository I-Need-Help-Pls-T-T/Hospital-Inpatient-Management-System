from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, cast

from backend.app.database import get_db
from backend.app.schemas import feedback_schema as schemas
from backend.app.crud.feedback_crud import feedback_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff, Feedback

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/", response_model=schemas.FeedbackResponse)
def create_feedback(
    data: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    user_id = cast(int, current_user.id) 
    return feedback_crud.create_feedback(db, obj_in=data, staff_id=user_id)

@router.get("/", response_model=List[schemas.FeedbackResponse])
def list_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3)) # Только админы
):
    """Просмотр всех обращений (Только уровень 3)"""
    # Используем query напрямую для кастомной сортировки по дате
    return db.query(Feedback).order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Количество непрочитанных обращений (Только уровень 3)"""
    count = feedback_crud.get_unread_count(db)
    return {"count": count}

@router.patch("/{feedback_id}/read")
def mark_as_read(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Отметить обращение как прочитанное (Только уровень 3)"""
    feedback = feedback_crud.get(db, id=feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Обращение не найдено")
    
    return feedback_crud.mark_read(db, db_obj=feedback)

@router.delete("/{id}")
def delete_feedback(
    id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удалить обращение (Только уровень 3)"""
    success = feedback_crud.remove(db, id=id)
    
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=f"Обращение с ID {id} не найдено"
        )
        
    return {"message": "Обращение успешно удалено", "id": id}