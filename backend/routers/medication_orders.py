from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/medication_orders", tags=["medication_orders"])

@router.get("/", response_model=List[schemas.MedicationOrder])
def read_medication_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить все листы назначения"""
    medication_orders = crud.medication_order_crud.get_multi(db, skip=skip, limit=limit)
    return medication_orders

@router.get("/{medication_order_id}", response_model=schemas.MedicationOrder)
def read_medication_order(medication_order_id: int, db: Session = Depends(get_db)):
    """Получить по id лист назначения"""
    medication_order = crud.medication_order_crud.get(db, medication_order_id)
    if not medication_order:
        raise HTTPException(status_code=404, detail="Лист назначений не найден")
    return medication_order

@router.post("/", response_model=schemas.MedicationOrder)
def create_medication_order(medication_order: schemas.MedicationOrderCreate, db: Session = Depends(get_db)):
    """Создать новый лист назначения"""
    return crud.medication_order_crud.create(db, medication_order)

@router.put("/{medication_order_id}", response_model=schemas.MedicationOrder)
def update_medication_order(medication_order_id: int, medication_order: schemas.MedicationOrderCreate, db: Session = Depends(get_db)):
    """Обновить лист назначения"""
    db_medication_order = crud.medication_order_crud.get(db, medication_order_id)
    if not db_medication_order:
        raise HTTPException(status_code=404, detail="Лист назначения не найден")
    return crud.medication_order_crud.update(db, db_medication_order, medication_order)

@router.delete("/{medication_order_id}")
def delete_medication_order(medication_order_id: int, db: Session = Depends(get_db)):
    """Удалить лист назначения"""
    medication_order = crud.medication_order_crud.remove(db, medication_order_id)
    if not medication_order:
        raise HTTPException(status_code=404, detail="Лист назначения не найден")
    return {"message": "Лист назначения успешно удален"}
