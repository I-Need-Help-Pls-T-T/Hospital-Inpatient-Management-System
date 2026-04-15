from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import medication_order_schema as schemas
from backend.app.crud.medication_order_crud import medication_order_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/medication_orders", tags=["Medication Orders"])

@router.get("/", response_model=List[schemas.MedicationOrder])
def read_medication_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Просмотр всех листов назначения (Уровень 2+)"""
    return medication_order_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{medication_order_id}", response_model=schemas.MedicationOrder)
def read_medication_order(
    medication_order_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Просмотр конкретного назначения (Уровень 2+)"""
    medication_order = medication_order_crud.get(db, id=medication_order_id)
    if not medication_order:
        raise HTTPException(status_code=404, detail="Лист назначения не найден")
    return medication_order

@router.post("/", response_model=schemas.MedicationOrder, status_code=status.HTTP_201_CREATED)
def create_medication_order(
    medication_order_in: schemas.MedicationOrderCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Создание назначения (Уровень 2+)"""
    return medication_order_crud.create(db, obj_in=medication_order_in)

@router.put("/{medication_order_id}", response_model=schemas.MedicationOrder)
def update_medication_order(
    medication_order_id: int,
    medication_order_in: schemas.MedicationOrderCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Обновление назначения (Уровень 2+)"""
    db_obj = medication_order_crud.get(db, id=medication_order_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Лист назначения не найден")
    return medication_order_crud.update(db, db_obj=db_obj, obj_in=medication_order_in)

@router.delete("/{medication_order_id}")
def delete_medication_order(
    medication_order_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удаление назначения (Только уровень 3)"""
    success = medication_order_crud.remove(db, id=medication_order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Лист назначения не найден")
    return {"status": "success", "detail": "Назначение успешно удалено"}