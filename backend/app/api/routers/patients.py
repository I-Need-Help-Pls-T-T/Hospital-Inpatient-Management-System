from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.schemas import patient_schema as schemas
from backend.app.crud.patient_crud import patient_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff, Room

router = APIRouter(prefix="/patients", tags=["Patients"])

# --- CREATE ---
# Добавлен status_code=201, чтобы тест на создание (test_create_patient) прошел
@router.post("/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_in: schemas.PatientCreate,
    db: Session = Depends(get_db),
    # Добавьте зависимость, если создание требует прав (например, уровень 1)
    current_user: Staff = Depends(check_access_level(1)) 
):
    if patient_in.passport is None:
        raise HTTPException(status_code=400, detail="Паспорт обязателен")
    
    existing_patient = patient_crud.get_by_passport(db, passport=patient_in.passport)
    if existing_patient:
        raise HTTPException(
            status_code=400, 
            detail="Пациент с таким паспортом уже существует"
        )
    return patient_crud.create(db, obj_in=patient_in)

# --- READ LIST ---
@router.get("/", response_model=List[schemas.Patient])
def read_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    user_level = int(getattr(current_user, "access_level", 0))

    if user_level == 2:
        room_id = getattr(current_user, "room_id", None)
        if room_id is None:
            return []
            
        room = db.query(Room).filter(Room.id == room_id).first()
        dept_id = getattr(room, "department_id", None) if room else None
        
        if dept_id is None:
            return []

        return patient_crud.get_by_department(
            db, dept_id=int(dept_id), skip=skip, limit=limit
        )

    return patient_crud.get_multi(db, skip=skip, limit=limit)

# --- READ SINGLE ---
@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    patient = patient_crud.get(db, id=patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Пациент не найден"
        )
    return patient

# --- UPDATE ---
@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(
    patient_id: int,
    patient_in: schemas.PatientCreate, 
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    db_obj = patient_crud.get(db, id=patient_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    
    return patient_crud.update(db, db_obj=db_obj, obj_in=patient_in)

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    patient = patient_crud.get(db, id=patient_id)
    if not patient:
         raise HTTPException(status_code=404, detail="Запись не найдена")
         
    patient_crud.remove(db, id=patient_id)
    return {"status": "success", "detail": "Карточка пациента удалена"}