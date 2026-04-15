from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from backend.app.database import get_db
from backend.app.schemas import staff_role_schema as schemas
from backend.app.crud.staff_role_crud import staff_role_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/staff_roles", tags=["Staff Roles"])

@router.get("/", response_model=List[schemas.StaffRole])
def read_staff_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Просмотр списка всех назначений (Уровень 1+)"""
    return staff_role_crud.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.StaffRole, status_code=status.HTTP_201_CREATED)
def create_staff_role(
    staff_role_in: schemas.StaffRoleCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Назначить должность сотруднику (Уровень 3: Админ/HR)"""
    return staff_role_crud.create(db, obj_in=staff_role_in)

@router.get("/detail", response_model=schemas.StaffRole)
def read_staff_role(
    staff_id: int,
    position_id: int,
    appointment_date: date,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Получить детали конкретного назначения по составному ключу (Уровень 1+)"""
    staff_role = staff_role_crud.get_by_identity(
        db, 
        staff_id=staff_id, 
        position_id=position_id, 
        appointment_date=appointment_date
    )
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
    current_user: Staff = Depends(check_access_level(3))
):
    """Обновить данные назначения (Уровень 3+)"""
    db_staff_role = staff_role_crud.get_by_identity(
        db, 
        staff_id=staff_id, 
        position_id=position_id, 
        appointment_date=appointment_date
    )
    if not db_staff_role:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return staff_role_crud.update(db, db_obj=db_staff_role, obj_in=staff_role_in)

@router.delete("/delete")
def delete_staff_role(
    staff_id: int,
    position_id: int,
    appointment_date: date,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удалить запись о назначении (Уровень 3: Админ)"""
    deleted_obj = staff_role_crud.remove_by_identity(
        db, 
        staff_id=staff_id, 
        position_id=position_id, 
        appointment_date=appointment_date
    )
    if not deleted_obj:
        raise HTTPException(status_code=404, detail="Запись для удаления не найдена")
    
    return {"status": "success", "detail": "Запись о назначении удалена"}