from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/", response_model=List[schemas.Patient])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список всех пациентов"""
    patients = crud.patient_crud.get_multi(db, skip=skip, limit=limit)
    return patients

@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    """Получить пациента по ID"""
    patient = crud.patient_crud.get(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return patient

@router.post("/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    """Создать нового пациента"""
    return crud.patient_crud.create(db, patient)

@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(patient_id: int, patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    """Обновить данные пациента"""
    db_patient = crud.patient_crud.get(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return crud.patient_crud.update(db, db_patient, patient)

@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Удалить пациента"""
    patient = crud.patient_crud.remove(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return {"message": "Пациент успешно удален"}
