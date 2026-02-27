from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/hospitalizations", tags=["hospitalizations"])

@router.get("/", response_model=List[schemas.Hospitalization])
def read_hospitalizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить весь список госпитализаций"""
    hospitalizations = crud.hospitalization_crud.get_multi(db, skip=skip, limit=limit)
    return hospitalizations

@router.get("/{hospitalization_id}", response_model=schemas.Hospitalization)
def read_hospitalization(hospitalization_id: int, db: Session = Depends(get_db)):
    """Получить госпитализацию id"""
    hospitalization = crud.hospitalization_crud.get(db, hospitalization_id)
    if not hospitalization:
        raise HTTPException(status_code=404, detail="Госпитализации не найдено")
    return hospitalization

@router.post("/", response_model=schemas.Hospitalization)
def create_hospitalization(hospitalization: schemas.HospitalizationCreate, db: Session = Depends(get_db)):
    """Создать новую госпитализацию"""
    return crud.hospitalization_crud.create(db, hospitalization)

@router.put("/{hospitalization_id}", response_model=schemas.Hospitalization)
def update_hospitalization(hospitalization_id: int, hospitalization: schemas.HospitalizationCreate, db: Session = Depends(get_db)):
    """Обновить данные госпитализации"""
    db_hospitalization = crud.hospitalization_crud.get(db, hospitalization_id)
    if not db_hospitalization:
        raise HTTPException(status_code=404, detail="Госпитализация не найдена")
    return crud.hospitalization_crud.update(db, db_hospitalization, hospitalization)

@router.delete("/{hospitalization_id}")
def delete_hospitalization(hospitalization_id: int, db: Session = Depends(get_db)):
    """Удалить госпитализацию"""
    hospitalization = crud.hospitalization_crud.remove(db, hospitalization_id)
    if not hospitalization:
        raise HTTPException(status_code=404, detail="Госпитаоизация не найдена")
    return {"message": "Госпитализация успешно удалена"}
