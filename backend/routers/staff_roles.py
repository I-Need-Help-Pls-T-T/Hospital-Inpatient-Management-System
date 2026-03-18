from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from backend.database import get_db
from backend import schemas, crud
# Импорты для защиты
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/staff_roles", tags=["staff_roles"])

@router.get("/", response_model=List[schemas.StaffRole])
def read_staff_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр списка назначений (Уровень 1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.staff_role_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.StaffRole)
def create_staff_role(
    staff_role: schemas.StaffRoleCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Назначить должность (Уровень 3+)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения кадрового состава")
    return crud.staff_role_crud.create(db, staff_role)

@router.get("/detail", response_model=schemas.StaffRole)
def read_staff_role(
    staff_id: int,
    position_id: int,
    appointment_date: date,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получить детали конкретного назначения (Уровень 1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

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
def update_staff_role(
    staff_id: int,
    position_id: int,
    appointment_date: date,
    staff_role_in: schemas.StaffRoleCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Обновить данные назначения (Уровень 3+)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Только HR или руководство могут обновлять должности")

    identity = {
        "staff_id": staff_id,
        "position_id": position_id,
        "appointment_date": appointment_date
    }
    db_staff_role = crud.staff_role_crud.get(db, identity)
    if not db_staff_role:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return crud.staff_role_crud.update(db, db_obj=db_staff_role, obj_in=staff_role_in)

@router.delete("/delete")
def delete_staff_role(
    staff_id: int,
    position_id: int,
    appointment_date: date,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удалить запись о назначении (Уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Удаление архивных записей должностей разрешено только администратору")

    identity = {
        "staff_id": staff_id,
        "position_id": position_id,
        "appointment_date": appointment_date
    }

    db_staff_role = crud.staff_role_crud.get(db, identity)
    if not db_staff_role:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    return crud.staff_role_crud.remove(db, id=identity)
