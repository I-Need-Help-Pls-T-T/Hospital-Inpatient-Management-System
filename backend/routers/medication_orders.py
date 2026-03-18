from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/medication_orders", tags=["medication_orders"])

@router.get("/", response_model=List[schemas.MedicationOrder])
def read_medication_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр всех листов назначения (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="У вас нет прав для просмотра листов назначения")
    return crud.medication_order_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{medication_order_id}", response_model=schemas.MedicationOrder)
def read_medication_order(
    medication_order_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр конкретного назначения (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Доступ к листу назначений ограничен")

    medication_order = crud.medication_order_crud.get(db, medication_order_id)
    if not medication_order:
        raise HTTPException(status_code=404, detail="Лист назначения не найден")
    return medication_order

@router.post("/", response_model=schemas.MedicationOrder)
def create_medication_order(
    medication_order: schemas.MedicationOrderCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Создание назначения (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Только медицинский персонал может создавать назначения")
    return crud.medication_order_crud.create(db, medication_order)

@router.put("/{medication_order_id}", response_model=schemas.MedicationOrder)
def update_medication_order(
    medication_order_id: int,
    medication_order: schemas.MedicationOrderCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Обновление назначения (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения назначений")

    db_medication_order = crud.medication_order_crud.get(db, medication_order_id)
    if not db_medication_order:
        raise HTTPException(status_code=404, detail="Лист назначения не найден")
    return crud.medication_order_crud.update(db, db_obj=db_medication_order, obj_in=medication_order)

@router.delete("/{medication_order_id}")
def delete_medication_order(
    medication_order_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление назначения (Только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Удаление записей назначений разрешено только администратору")

    result = crud.medication_order_crud.remove(db, medication_order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Лист назначения не найден")
    return {"status": "success", "message": "Назначение успешно удалено из базы данных"}
