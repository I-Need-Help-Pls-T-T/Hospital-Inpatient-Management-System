from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/staff", tags=["staff"])

@router.get("/", response_model=List[schemas.Staff])
def read_staffs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.staff_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{staff_id}", response_model=schemas.Staff)
def read_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получить по id сотрудника"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    staff = crud.staff_crud.get(db, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return staff

@router.post("/", response_model=schemas.Staff)
def create_staff(
    staff: schemas.StaffCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    if staff.access_level > current_user.access_level:
        raise HTTPException(
            status_code=403,
            detail="Вы не можете назначать уровень доступа выше своего"
        )

    return crud.staff_crud.create(db, obj_in=staff)

@router.put("/{staff_id}", response_model=schemas.Staff)
def update_staff(
    staff_id: int,
    staff: schemas.StaffUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования")

    if staff.access_level is not None and staff.access_level > current_user.access_level:
        raise HTTPException(
            status_code=403,
            detail="Вы не можете назначать уровень доступа выше своего"
        )

    db_staff = crud.staff_crud.get(db, staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    return crud.staff_crud.update(db, db_obj=db_staff, obj_in=staff)

@router.delete("/{staff_id}", response_model=schemas.Staff)
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав для удаления")

    deleted_item = crud.staff_crud.remove(db, id=staff_id)

    if not deleted_item:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")

    return deleted_item
