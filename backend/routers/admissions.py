from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/admissions", tags=["admissions"])

@router.get("/", response_model=List[schemas.PatientAdmission])
def read_admissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить полный список времени поступления и выбытия"""
    admissions = crud.patient_admission_crud.get_multi(db, skip=skip, limit=limit)
    return admissions

@router.get("/{hospitalization_id}", response_model=schemas.PatientAdmission)
def read_admission(hospitalization_id: int, db: Session = Depends(get_db)):
    admission = crud.patient_admission_crud.get(db, {"hospitalization_id": hospitalization_id})
    if not admission:
        raise HTTPException(status_code=404, detail="Запись о поступлении не найдена")
    return admission

@router.post("/", response_model=schemas.PatientAdmission)
def create_admission(admission: schemas.PatientAdmissionCreate, db: Session = Depends(get_db)):
    """Создать нового времени поступления и выбытия"""
    return crud.patient_admission_crud.create(db, admission)

@router.put("/{hospitalization_id}", response_model=schemas.PatientAdmission)
def update_admission(hospitalization_id: int, admission: schemas.PatientAdmissionCreate, db: Session = Depends(get_db)):
    """Обновить данные времени поступления и выбытия"""
    db_admission = crud.patient_admission_crud.get(db, {"hospitalization_id": hospitalization_id})
    if not db_admission:
        raise HTTPException(status_code=404, detail="Такого времени поступления не найдено")
    return crud.patient_admission_crud.update(db, db_admission, admission)

@router.delete("/{hospitalization_id}")
def delete_admission(hospitalization_id: int, db: Session = Depends(get_db)):
    admission = crud.patient_admission_crud.remove(db, {"hospitalization_id": hospitalization_id})
    if not admission:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"message": "Успешно удалено"}
