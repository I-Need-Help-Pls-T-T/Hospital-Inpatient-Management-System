from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/", response_model=List[schemas.Payment])
def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить весь список финансовых транзакций"""
    payments = crud.payment_crud.get_multi(db, skip=skip, limit=limit)
    return payments

@router.get("/{payment_id}", response_model=schemas.Payment)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    """Получить по id финансовую транзакцию"""
    payment = crud.payment_crud.get(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Финансовая трнзакция не найдена")
    return payment

@router.post("/", response_model=schemas.Payment)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    """Создать новую финансовую транзакцию"""
    return crud.payment_crud.create(db, payment)

@router.put("/{payment_id}", response_model=schemas.Payment)
def update_payment(payment_id: int, payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    """Обновить финансовую транзакцию"""
    db_payment = crud.payment_crud.get(db, payment_id)
    if not db_payment:
        raise HTTPException(status_code=404, detail="Финансовая транзакция не найдена")
    return crud.payment_crud.update(db, db_payment, payment)

@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    """Удалить финансовую транзакцию"""
    payment = crud.payment_crud.remove(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Финансовая транзакция не найдена")
    return {"message": "Финансовая транзакция успешно удалена"}
