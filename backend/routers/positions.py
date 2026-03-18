from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
# Импорты для защиты доступа
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/positions", tags=["positions"])

@router.get("/", response_model=List[schemas.Position])
def read_positions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр списка должностей доступен всем авторизованным сотрудникам (1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.position_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{position_id}", response_model=schemas.Position)
def read_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр конкретной должности (1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    position = crud.position_crud.get(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Должность не найдена")
    return position

@router.post("/", response_model=schemas.Position)
def create_position(
    position: schemas.PositionCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Создание новых должностей — только для Администратора (3)"""
    if current_user.access_level < 3:
        raise HTTPException(
            status_code=403,
            detail="Только системный администратор может изменять справочник должностей"
        )
    return crud.position_crud.create(db, position)

@router.put("/{position_id}", response_model=schemas.Position)
def update_position(
    position_id: int,
    position: schemas.PositionCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Редактирование должностей — только для Администратора (3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования")

    db_position = crud.position_crud.get(db, position_id)
    if not db_position:
        raise HTTPException(status_code=404, detail="Должность не найдена")

    return crud.position_crud.update(db, db_obj=db_position, obj_in=position)

@router.delete("/{position_id}")
def delete_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление должности — только для Администратора (3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Удаление запрещено")

    db_position = crud.position_crud.get(db, position_id)
    if not db_position:
        raise HTTPException(status_code=404, detail="Должность не найдена")

    return crud.position_crud.remove(db, id=position_id)
