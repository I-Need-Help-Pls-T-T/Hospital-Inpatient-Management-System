from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import payment_schema as schemas
from backend.app.crud.payment_crud import payment_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("/", response_model=List[schemas.Payment])
def read_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Список транзакций (Уровень 3+)"""
    return payment_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{payment_id}", response_model=schemas.Payment)
def read_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Получить транзакцию по ID (Уровень 3+)"""
    payment = payment_crud.get(db, id=payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    return payment

@router.post("/", response_model=schemas.Payment, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_in: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Регистрация оплаты (Уровень 3+)"""
    return payment_crud.create(db, obj_in=payment_in)

@router.put("/{payment_id}", response_model=schemas.Payment)
def update_payment(
    payment_id: int,
    payment_in: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Изменение транзакции (Уровень 3)"""
    db_payment = payment_crud.get(db, id=payment_id)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    return payment_crud.update(db, db_obj=db_payment, obj_in=payment_in)

@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удаление транзакции (Уровень 3)"""
    success = payment_crud.remove(db, id=payment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "detail": "Транзакция удалена"}