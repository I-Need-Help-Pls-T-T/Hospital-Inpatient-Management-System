from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/staff_roles", tags=["staff_roles"])

@router.get("/", response_model=List[schemas.StaffRole])
def read_staff_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить общий список всех назначений должностей"""
    return crud.staff_role_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.StaffRole)
def create_staff_role(staff_role: schemas.StaffRoleCreate, db: Session = Depends(get_db)):
    """Назначить сотруднику должность"""
    return crud.staff_role_crud.create(db, staff_role)

@router.get("/detail", response_model=schemas.StaffRole)
def read_staff_role(staff_id: int, position_id: int, appointment_date: date, db: Session = Depends(get_db)):
    """Получить конкретную запись назначения по составному ключу"""
    identity = {
        "staff_id": staff_id,
        "position_id": position_id,
        "appointment_date": appointment_date
    }
    staff_role = crud.staff_role_crud.get(db, identity)
    if not staff_role:
        raise HTTPException(status_code=404, detail="Запись о назначении не найдена")
    return staff_role

@router.put("/update", response_model=schemas.StaffRole)
def update_staff_role(staff_id: int, position_id: int, appointment_date: date, staff_role_in: schemas.StaffRoleCreate, db: Session = Depends(get_db)):
    """Обновить данные о назначении"""
    identity = {
        "staff_id": staff_id,
        "position_id": position_id,
        "appointment_date": appointment_date
    }
    db_staff_role = crud.staff_role_crud.get(db, identity)
    if not db_staff_role:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return crud.staff_role_crud.update(db, db_staff_role, staff_role_in)

@router.delete("/delete")
def delete_staff_role(staff_id: int, position_id: int, appointment_date: date, db: Session = Depends(get_db)):
    """Удалить запись о назначении"""
    identity = {
        "staff_id": staff_id,
        "position_id": position_id,
        "appointment_date": appointment_date
    }
    staff_role = crud.staff_role_crud.remove(db, identity)
    if not staff_role:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"message": "Запись успешно удалена"}
