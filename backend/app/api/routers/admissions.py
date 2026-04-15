from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import admission_schema as schemas
from backend.app.crud.patient_admission_crud import patient_admission_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/admissions", tags=["Admissions"])

# --- READ LIST ---
@router.get("/", response_model=List[schemas.PatientAdmission])
def read_admissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Просмотр списка госпитализаций (Уровень 1+)"""
    return patient_admission_crud.get_multi(db, skip=skip, limit=limit)

# --- READ SINGLE ---
@router.get("/{hospitalization_id}", response_model=schemas.PatientAdmission)
def read_admission(
    hospitalization_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Просмотр данных о конкретном поступлении (Уровень 1+)"""
    # В CRUDBase поиск обычно идет по полю id
    admission = patient_admission_crud.get(db, id=hospitalization_id)
    if not admission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Запись о поступлении не найдена"
        )
    return admission

# --- CREATE ---
@router.post("/", response_model=schemas.PatientAdmission, status_code=status.HTTP_201_CREATED)
def create_admission(
    admission_in: schemas.PatientAdmissionCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Регистрация поступления (Уровень 2+)"""
    return patient_admission_crud.create(db, obj_in=admission_in)

# --- UPDATE ---
@router.put("/{hospitalization_id}", response_model=schemas.PatientAdmission)
def update_admission(
    hospitalization_id: int,
    admission_in: schemas.PatientAdmissionCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Обновление данных о поступлении (Уровень 2+)"""
    db_admission = patient_admission_crud.get(db, id=hospitalization_id)
    if not db_admission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Такого времени поступления не найдено"
        )
    return patient_admission_crud.update(db, db_obj=db_admission, obj_in=admission_in)

# --- DELETE ---
@router.delete("/{hospitalization_id}")
def delete_admission(
    hospitalization_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удаление записей (Уровень 3: Администратор)"""
    db_admission = patient_admission_crud.get(db, id=hospitalization_id)
    if not db_admission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Запись о поступлении не найдена"
        )

    patient_admission_crud.remove(db, id=hospitalization_id)
    return {"status": "success", "detail": "Запись о поступлении удалена"}