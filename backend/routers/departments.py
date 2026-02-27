from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("/", response_model=List[schemas.Department])
def read_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.department_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{department_id}", response_model=schemas.Department)
def read_department(department_id: int, db: Session = Depends(get_db)):
    department = crud.department_crud.get(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Отделение не найдено")
    return department

@router.post("/", response_model=schemas.Department)
def create_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    return crud.department_crud.create(db, department)

@router.put("/{department_id}", response_model=schemas.Department)
def update_department(department_id: int, department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    db_department = crud.department_crud.get(db, department_id)
    if not db_department:
        raise HTTPException(status_code=404, detail="Отделение не найдено")
    return crud.department_crud.update(db, db_department, department)

@router.delete("/{department_id}")
def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = crud.department_crud.remove(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Отделение не найдено")
    return {"message": "Отделение успешно удалено"}
