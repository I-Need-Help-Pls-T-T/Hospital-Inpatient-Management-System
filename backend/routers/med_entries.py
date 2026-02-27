from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/med_entries", tags=["med_entries"])

@router.get("/", response_model=List[schemas.MedEntry])
def read_med_entries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить весь список записей в истории болезни"""
    med_entries = crud.med_entry_crud.get_multi(db, skip=skip, limit=limit)
    return med_entries

@router.get("/{med_entry_id}", response_model=schemas.MedEntry)
def read_med_entry(med_entry_id: int, db: Session = Depends(get_db)):
    """Получить по id запись в истории болезни"""
    med_entry = crud.med_entry_crud.get(db, med_entry_id)
    if not med_entry:
        raise HTTPException(status_code=404, detail="Запись в истории болезни не найдена")
    return med_entry

@router.post("/", response_model=schemas.MedEntry)
def create_med_entry(med_entry: schemas.MedEntryCreate, db: Session = Depends(get_db)):
    """Создать новую запись в истории болезни"""
    return crud.med_entry_crud.create(db, med_entry)

@router.put("/{med_entry_id}", response_model=schemas.MedEntry)
def update_med_entry(med_entry_id: int, med_entry: schemas.MedEntryCreate, db: Session = Depends(get_db)):
    """Обновить запись в истории болезни"""
    db_med_entry = crud.med_entry_crud.get(db, med_entry_id)
    if not db_med_entry:
        raise HTTPException(status_code=404, detail="Запись в истории болезни не найдена")
    return crud.med_entry_crud.update(db, db_med_entry, med_entry)

@router.delete("/{med_entry_id}")
def delete_med_entry(med_entry_id: int, db: Session = Depends(get_db)):
    """Удалить запись в истории болезни"""
    med_entry = crud.med_entry_crud.remove(db, med_entry_id)
    if not med_entry:
        raise HTTPException(status_code=404, detail="Запись в истории болезни не найдена")
    return {"message": "Запись в истории болезни успешно удалена"}
