from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import position_schema as schemas
from backend.app.crud.position_crud import position_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/positions", tags=["Positions"])

# --- READ LIST ---
@router.get("/", response_model=List[schemas.Position])
def read_positions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Просмотр списка должностей доступен всем сотрудникам (уровень 1+)"""
    return position_crud.get_multi(db, skip=skip, limit=limit)

# --- READ SINGLE ---
@router.get("/{position_id}", response_model=schemas.Position)
def read_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Просмотр конкретной должности (уровень 1+)"""
    position = position_crud.get(db, id=position_id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Должность не найдена"
        )
    return position

# --- CREATE ---
@router.post("/", response_model=schemas.Position, status_code=status.HTTP_201_CREATED)
def create_position(
    position_in: schemas.PositionCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Создание новых должностей — только для Администратора (уровень 3)"""
    return position_crud.create(db, obj_in=position_in)

# --- UPDATE ---
@router.put("/{position_id}", response_model=schemas.Position)
def update_position(
    position_id: int,
    position_in: schemas.PositionCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Редактирование должностей — только для Администратора (уровень 3)"""
    db_position = position_crud.get(db, id=position_id)
    if not db_position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Должность не найдена"
        )
    return position_crud.update(db, db_obj=db_position, obj_in=position_in)

# --- DELETE ---
@router.delete("/{position_id}")
def delete_position(
    position_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удаление должности — только для Администратора (уровень 3)"""
    db_position = position_crud.get(db, id=position_id)
    if not db_position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Должность не найдена"
        )
    
    position_crud.remove(db, id=position_id)
    return {"status": "success", "detail": "Должность удалена из справочника"}