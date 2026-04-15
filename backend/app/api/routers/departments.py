from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import department_schema as schemas
from backend.app.crud.department_crud import department_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/departments", tags=["Departments"])

# --- READ LIST ---
@router.get("/", response_model=List[schemas.Department])
def read_departments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # Уровень 1: просмотр доступен персоналу
    current_user: Staff = Depends(check_access_level(1))
):
    return department_crud.get_multi(db, skip=skip, limit=limit)

# --- READ SINGLE ---
@router.get("/{department_id}", response_model=schemas.Department)
def read_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    department = department_crud.get(db, id=department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Отделение не найдено"
        )
    return department

# --- CREATE ---
@router.post("/", response_model=schemas.Department, status_code=status.HTTP_201_CREATED)
def create_department(
    department_in: schemas.DepartmentCreate,
    db: Session = Depends(get_db),
    # Уровень 3: только администратор
    current_user: Staff = Depends(check_access_level(3))
):
    return department_crud.create(db, obj_in=department_in)

# --- UPDATE ---
@router.put("/{department_id}", response_model=schemas.Department)
def update_department(
    department_id: int,
    department_in: schemas.DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    db_obj = department_crud.get(db, id=department_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Отделение не найдено")
    
    return department_crud.update(db, db_obj=db_obj, obj_in=department_in)

# --- DELETE ---
@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    department = department_crud.get(db, id=department_id)
    if not department:
         raise HTTPException(status_code=404, detail="Отделение не найдено")
         
    department_crud.remove(db, id=department_id)
    return {"status": "success", "detail": "Отделение удалено"}