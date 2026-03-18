from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/admissions", tags=["admissions"])

@router.get("/", response_model=List[schemas.PatientAdmission])
def read_admissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр списка госпитализаций (Уровень 1+: Все сотрудники)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.patient_admission_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{hospitalization_id}", response_model=schemas.PatientAdmission)
def read_admission(
    hospitalization_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр данных о конкретном поступлении (Уровень 1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    admission = crud.patient_admission_crud.get(db, {"hospitalization_id": hospitalization_id})
    if not admission:
        raise HTTPException(status_code=404, detail="Запись о поступлении не найдена")
    return admission

@router.post("/", response_model=schemas.PatientAdmission)
def create_admission(
    admission: schemas.PatientAdmissionCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Регистрация поступления/выбытия (Уровень 2+: Врачи, Регистраторы)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Недостаточно прав для регистрации пациента")
    return crud.patient_admission_crud.create(db, admission)

@router.put("/{hospitalization_id}", response_model=schemas.PatientAdmission)
def update_admission(
    hospitalization_id: int,
    admission: schemas.PatientAdmissionCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Обновление данных о поступлении (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Недостаточно прав для изменения данных")

    db_admission = crud.patient_admission_crud.get(db, {"hospitalization_id": hospitalization_id})
    if not db_admission:
        raise HTTPException(status_code=404, detail="Такого времени поступления не найдено")
    return crud.patient_admission_crud.update(db, db_obj=db_admission, obj_in=admission)

@router.delete("/{hospitalization_id}")
def delete_admission(
    hospitalization_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Удаление записей разрешено только администратору")

    db_admission = crud.patient_admission_crud.get(db, {"hospitalization_id": hospitalization_id})
    if not db_admission:
        raise HTTPException(status_code=404, detail="Запись о поступлении не найдена")

    return crud.patient_admission_crud.remove(db, id=hospitalization_id)
