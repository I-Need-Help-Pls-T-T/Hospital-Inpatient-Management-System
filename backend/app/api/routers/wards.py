from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import ward_schema as schemas
from backend.app.crud.ward_crud import ward_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/wards", tags=["Wards"])

# --- READ LIST ---
@router.get("/", response_model=List[schemas.Ward])
def read_wards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Список палат доступен всем сотрудникам (уровень 1+)"""
    return ward_crud.get_multi(db, skip=skip, limit=limit)

# --- READ SINGLE ---
@router.get("/{ward_id}", response_model=schemas.Ward)
def read_ward(
    ward_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Просмотр конкретной палаты (уровень 1+)"""
    ward = ward_crud.get(db, id=ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Палата не найдена")
    return ward

# --- CREATE ---
@router.post("/", response_model=schemas.Ward, status_code=status.HTTP_201_CREATED)
def create_ward(
    ward_in: schemas.WardCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Создание палат — только для Администратора (уровень 3)"""
    return ward_crud.create(db, obj_in=ward_in)

# --- UPDATE ---
@router.put("/{ward_id}", response_model=schemas.Ward)
def update_ward(
    ward_id: int,
    ward_in: schemas.WardCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Редактирование палат — только для Администратора (уровень 3)"""
    db_ward = ward_crud.get(db, id=ward_id)
    if not db_ward:
        raise HTTPException(status_code=404, detail="Палата не найдена")
    return ward_crud.update(db, db_obj=db_ward, obj_in=ward_in)

# --- DELETE ---
@router.delete("/{ward_id}")
def delete_ward(
    ward_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удаление палат — только для Администратора (уровень 3)"""
    db_ward = ward_crud.get(db, id=ward_id)
    if not db_ward:
        raise HTTPException(status_code=404, detail="Палата не найдена")

    ward_crud.remove(db, id=ward_id)
    return {"status": "success", "detail": "Палата удалена"}