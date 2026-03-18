from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/", response_model=List[schemas.Payment])
def read_payments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получить список транзакций (Уровень 3+)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Доступ к финансовой отчетности запрещен")
    return crud.payment_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{payment_id}", response_model=schemas.Payment)
def read_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получить транзакцию по id (Уровень 3+)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    payment = crud.payment_crud.get(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    return payment

@router.post("/", response_model=schemas.Payment)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Регистрация оплаты (Уровень 3+)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав для регистрации оплаты")
    return crud.payment_crud.create(db, payment)

@router.put("/{payment_id}", response_model=schemas.Payment)
def update_payment(
    payment_id: int,
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Изменение транзакции (Только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Редактирование финансовых записей разрешено только администратору")

    db_payment = crud.payment_crud.get(db, payment_id)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")

    return crud.payment_crud.update(db, db_obj=db_payment, obj_in=payment)

@router.delete("/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление транзакции (Только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Удаление финансовых данных запрещено")

    payment = crud.payment_crud.remove(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "message": "Транзакция удалена"}
