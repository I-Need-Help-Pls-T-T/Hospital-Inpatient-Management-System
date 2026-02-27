from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/wards", tags=["wards"])

@router.get("/", response_model=List[schemas.Ward])
def read_wards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список палат"""
    wards = crud.ward_crud.get_multi(db, skip=skip, limit=limit)
    return wards

@router.get("/{ward_id}", response_model=schemas.Ward)
def read_ward(ward_id: int, db: Session = Depends(get_db)):
    """Получить по id палату"""
    ward = crud.ward_crud.get(db, ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Палата не найдена")
    return ward

@router.post("/", response_model=schemas.Ward)
def create_ward(ward: schemas.WardCreate, db: Session = Depends(get_db)):
    """Создать палату"""
    return crud.ward_crud.create(db, ward)

@router.put("/{ward_id}", response_model=schemas.Ward)
def update_ward(ward_id: int, ward: schemas.WardCreate, db: Session = Depends(get_db)):
    """Обновить палату"""
    db_ward = crud.ward_crud.get(db, ward_id)
    if not db_ward:
        raise HTTPException(status_code=404, detail="Палата не найдена")
    return crud.ward_crud.update(db, db_ward, ward)

@router.delete("/{ward_id}")
def delete_ward(ward_id: int, db: Session = Depends(get_db)):
    """Удалить палату"""
    ward = crud.ward_crud.remove(db, ward_id)
    if not ward:
        raise HTTPException(status_code=404, detail="Палата не найдена")
    return {"message": "Палата успешно удалена"}
