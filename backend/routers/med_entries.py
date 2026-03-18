from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/med_entries", tags=["med_entries"])

@router.get("/", response_model=List[schemas.MedEntry])
def read_med_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр истории болезни (Уровень 2+: Врачи и медсестры)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="У вас нет прав для просмотра медицинских записей")
    return crud.med_entry_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{med_entry_id}", response_model=schemas.MedEntry)
def read_med_entry(
    med_entry_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр конкретной записи (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Доступ к медицинской карте ограничен")

    med_entry = crud.med_entry_crud.get(db, med_entry_id)
    if not med_entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return med_entry

@router.post("/", response_model=schemas.MedEntry)
def create_med_entry(
    med_entry: schemas.MedEntryCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Добавление записи в историю болезни (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Только медицинский персонал может вносить записи")
    return crud.med_entry_crud.create(db, med_entry)

@router.put("/{med_entry_id}", response_model=schemas.MedEntry)
def update_med_entry(
    med_entry_id: int,
    med_entry: schemas.MedEntryCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Редактирование записи (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения истории болезни")

    db_med_entry = crud.med_entry_crud.get(db, med_entry_id)
    if not db_med_entry:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return crud.med_entry_crud.update(db, db_obj=db_med_entry, obj_in=med_entry)

@router.delete("/{med_entry_id}")
def delete_med_entry(
    med_entry_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление медицинской записи (Только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Удаление медицинских записей разрешено только администратору")

    result = crud.med_entry_crud.remove(db, med_entry_id)
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "message": "Запись из истории болезни удалена"}
