from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
# Импорты для защиты
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/hospitalizations", tags=["hospitalizations"])

@router.get("/", response_model=List[schemas.Hospitalization])
def read_hospitalizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получить весь список госпитализаций (Уровень 1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.hospitalization_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{hospitalization_id}", response_model=schemas.Hospitalization)
def read_hospitalization(
    hospitalization_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получить госпитализацию по id (Уровень 1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    hospitalization = crud.hospitalization_crud.get(db, hospitalization_id)
    if not hospitalization:
        raise HTTPException(status_code=404, detail="Госпитализация не найдена")
    return hospitalization

@router.post("/", response_model=schemas.Hospitalization)
def create_hospitalization(
    hospitalization: schemas.HospitalizationCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Создать новую госпитализацию (Уровень 2+: Врачи, Регистраторы)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Недостаточно прав для оформления госпитализации")
    return crud.hospitalization_crud.create(db, hospitalization)

@router.put("/{hospitalization_id}", response_model=schemas.Hospitalization)
def update_hospitalization(
    hospitalization_id: int,
    hospitalization: schemas.HospitalizationCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Обновить данные госпитализации (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения данных")

    db_hospitalization = crud.hospitalization_crud.get(db, hospitalization_id)
    if not db_hospitalization:
        raise HTTPException(status_code=404, detail="Госпитализация не найдена")
    return crud.hospitalization_crud.update(db, db_obj=db_hospitalization, obj_in=hospitalization)

@router.delete("/{hospitalization_id}")
def delete_hospitalization(
    hospitalization_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удалить госпитализацию (Только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Только администратор может удалять записи о госпитализации")

    hospitalization = crud.hospitalization_crud.remove(db, hospitalization_id)
    if not hospitalization:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"message": "Запись успешно удалена"}
