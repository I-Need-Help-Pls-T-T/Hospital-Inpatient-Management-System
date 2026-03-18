from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
# Импорты для авторизации
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/wards", tags=["wards"])

@router.get("/", response_model=List[schemas.Ward])
def read_wards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Список палат доступен всем сотрудникам (1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.ward_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{ward_id}", response_model=schemas.Ward)
def read_ward(
    ward_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр конкретной палаты (1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    ward = crud.ward_crud.get(db, ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Палата не найдена")
    return ward

@router.post("/", response_model=schemas.Ward)
def create_ward(
    ward: schemas.WardCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Создание палат — только для Администратора (3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Только администратор может изменять структуру корпуса")
    return crud.ward_crud.create(db, ward)

@router.put("/{ward_id}", response_model=schemas.Ward)
def update_ward(
    ward_id: int,
    ward: schemas.WardCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Редактирование палат — только для Администратора (3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения справочника палат")

    db_ward = crud.ward_crud.get(db, ward_id)
    if not db_ward:
        raise HTTPException(status_code=404, detail="Палата не найдена")
    return crud.ward_crud.update(db, db_obj=db_ward, obj_in=ward)

@router.delete("/{ward_id}")
def delete_ward(
    ward_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление палат — только для Администратора (3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    db_ward = crud.ward_crud.get(db, ward_id)
    if not db_ward:
        raise HTTPException(status_code=404, detail="Палата не найдена")

    return crud.ward_crud.remove(db, id=ward_id)
