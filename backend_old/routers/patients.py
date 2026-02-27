from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
from pydantic import BaseModel
from datetime import date
import enum

router = APIRouter()

class GenderEnum(str, enum.Enum):
    Мужской = "Мужской"
    Женский = "Женский"

class PatientBase(BaseModel):
    full_name: str
    birth_date: date
    gender: GenderEnum
    address: str = None
    passport: str = None
    phone: str = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[Patient])
async def get_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    patients = db.query(models.Patient).offset(skip).limit(limit).all()
    return patients

@router.get("/{patient_id}", response_model=Patient)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return patient

@router.post("/", response_model=Patient)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.put("/{patient_id}", response_model=Patient)
async def update_patient(patient_id: int, patient: PatientCreate, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Пациент не найден")

    for key, value in patient.dict().items():
        setattr(db_patient, key, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.delete("/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Пациент не найден")

    db.delete(db_patient)
    db.commit()
    return {"message": "Пациент удален"}
