from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/", response_model=List[schemas.Patient])
def read_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр списка пациентов (Уровень 1+: Все сотрудники)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.patient_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр данных конкретного пациента (Уровень 1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    patient = crud.patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return patient

@router.post("/", response_model=schemas.Patient)
def create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Регистрация нового пациента (Уровень 2+: Врачи, Регистраторы)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Недостаточно прав для регистрации пациента")
    return crud.patient_crud.create(db, patient)

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(
    patient_id: int,
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Обновление данных пациента (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения данных пациента")

    db_patient = crud.patient_crud.get(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return crud.patient_crud.update(db, db_obj=db_patient, obj_in=patient)

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление карточки пациента (Только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Удаление персональных данных разрешено только администратору")

    patient = crud.patient_crud.remove(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "message": "Карточка пациента удалена"}
