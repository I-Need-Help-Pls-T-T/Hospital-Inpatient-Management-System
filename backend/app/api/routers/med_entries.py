from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import med_entry_schemas as schemas
from backend.app.crud.med_entry_crud import med_entry_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/med_entries", tags=["Medical Entries"])

@router.get("/", response_model=List[schemas.MedEntry])
def read_med_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Просмотр истории болезни (Уровень 2+: Врачи и медсестры)"""
    return med_entry_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{med_entry_id}", response_model=schemas.MedEntry)
def read_med_entry(
    med_entry_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Просмотр конкретной записи (Уровень 2+)"""
    med_entry = med_entry_crud.get(db, id=med_entry_id)
    if not med_entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return med_entry

@router.post("/", response_model=schemas.MedEntry, status_code=status.HTTP_201_CREATED)
def create_med_entry(
    med_entry_in: schemas.MedEntryCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Добавление записи в историю болезни (Уровень 2+)"""
    return med_entry_crud.create(db, obj_in=med_entry_in)

@router.put("/{med_entry_id}", response_model=schemas.MedEntry)
def update_med_entry(
    med_entry_id: int,
    med_entry_in: schemas.MedEntryCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Редактирование записи (Уровень 2+)"""
    db_obj = med_entry_crud.get(db, id=med_entry_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return med_entry_crud.update(db, db_obj=db_obj, obj_in=med_entry_in)

@router.delete("/{med_entry_id}")
def delete_med_entry(
    med_entry_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удаление записи (Только уровень 3)"""
    success = med_entry_crud.remove(db, id=med_entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "detail": "Запись удалена"}