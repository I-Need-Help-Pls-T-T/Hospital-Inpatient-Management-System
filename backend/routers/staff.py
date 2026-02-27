from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/staff", tags=["staff"])

@router.get("/", response_model=List[schemas.Staff])
def read_staffs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список сотрудников"""
    staffs = crud.staff_crud.get_multi(db, skip=skip, limit=limit)
    return staffs

@router.get("/{staff_id}", response_model=schemas.Staff)
def read_staff(staff_id: int, db: Session = Depends(get_db)):
    """Получить по id сотрудника"""
    staff = crud.staff_crud.get(db, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return staff

@router.post("/", response_model=schemas.Staff)
def create_staff(staff: schemas.StaffCreate, db: Session = Depends(get_db)):
    """Создать нового сотрудника"""
    return crud.staff_crud.create(db, staff)

@router.put("/{staff_id}", response_model=schemas.Staff)
def update_staff(staff_id: int, staff: schemas.StaffCreate, db: Session = Depends(get_db)):
    """Обновить сотрудника"""
    db_staff = crud.staff_crud.get(db, staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return crud.staff_crud.update(db, db_staff, staff)

@router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    """Удалить сотрудника"""
    staff = crud.staff_crud.remove(db, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return {"message": "Сотрудник успешно удален"}
