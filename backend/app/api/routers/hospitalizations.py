from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import hospitalization_schema as schemas
from backend.app.crud.hospitalization_crud import hospitalization_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/hospitalizations", tags=["Hospitalizations"])

@router.get("/", response_model=List[schemas.Hospitalization])
def read_hospitalizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Список госпитализаций (Уровень 1+)"""
    return hospitalization_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{hospitalization_id}", response_model=schemas.Hospitalization)
def read_hospitalization(
    hospitalization_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Получить по ID (Уровень 1+)"""
    hospitalization = hospitalization_crud.get(db, id=hospitalization_id)
    if not hospitalization:
        raise HTTPException(status_code=404, detail="Госпитализация не найдена")
    return hospitalization

@router.post("/", response_model=schemas.Hospitalization, status_code=status.HTTP_201_CREATED)
def create_hospitalization(
    hospitalization_in: schemas.HospitalizationCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Создать запись (Уровень 2+)"""
    return hospitalization_crud.create(db, obj_in=hospitalization_in)

@router.put("/{hospitalization_id}", response_model=schemas.Hospitalization)
def update_hospitalization(
    hospitalization_id: int,
    hospitalization_in: schemas.HospitalizationCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Обновить запись (Уровень 2+)"""
    db_hosp = hospitalization_crud.get(db, id=hospitalization_id)
    if not db_hosp:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return hospitalization_crud.update(db, db_obj=db_hosp, obj_in=hospitalization_in)

@router.delete("/{hospitalization_id}")
def delete_hospitalization(
    hospitalization_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удалить запись (Уровень 3)"""
    success = hospitalization_crud.remove(db, id=hospitalization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "detail": "Удалено"}