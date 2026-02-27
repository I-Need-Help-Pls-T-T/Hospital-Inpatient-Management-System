from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/positions", tags=["positions"])

@router.get("/", response_model=List[schemas.Position])
def read_positions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список справочника должностей"""
    positions = crud.position_crud.get_multi(db, skip=skip, limit=limit)
    return positions

@router.get("/{position_id}", response_model=schemas.Position)
def read_position(position_id: int, db: Session = Depends(get_db)):
    """Получить по id должность"""
    position = crud.position_crud.get(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Должность не найдена")
    return position

@router.post("/", response_model=schemas.Position)
def create_position(position: schemas.PositionCreate, db: Session = Depends(get_db)):
    """Создать новую должность"""
    return crud.position_crud.create(db, position)

@router.put("/{position_id}", response_model=schemas.Position)
def update_position(position_id: int, position: schemas.PositionCreate, db: Session = Depends(get_db)):
    """Обновить должность"""
    db_position = crud.position_crud.get(db, position_id)
    if not db_position:
        raise HTTPException(status_code=404, detail="Должность не найдена")
    return crud.position_crud.update(db, db_position, position)

@router.delete("/{position_id}")
def delete_position(position_id: int, db: Session = Depends(get_db)):
    """Удалить должность"""
    position = crud.position_crud.remove(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Должность не найдена")
    return {"message": "Должность успешно удалена"}
