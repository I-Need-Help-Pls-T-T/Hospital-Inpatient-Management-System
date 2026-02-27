import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models
from pydantic import BaseModel

router = APIRouter()

class DepartmentBase(BaseModel):
    name: str
    phone: Optional[str] = None
    profile: Optional[str] = None
    category: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[Department])
async def get_departments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    departments = db.query(models.Department).offset(skip).limit(limit).all()
    return departments

@router.get("/{department_id}", response_model=Department)
async def get_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Отделение не найдено")
    return department

@router.post("/", response_model=Department)
async def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    db_department = models.Department(**department.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

@router.put("/{department_id}", response_model=Department)
async def update_department(department_id: int, department: DepartmentCreate, db: Session = Depends(get_db)):
    db_department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if db_department is None:
        raise HTTPException(status_code=404, detail="Отделение не найдено")

    for key, value in department.dict().items():
        setattr(db_department, key, value)

    db.commit()
    db.refresh(db_department)
    return db_department

@router.delete("/{department_id}")
async def delete_department(department_id: int, db: Session = Depends(get_db)):
    db_department = db.query(models.Department).filter(models.Department.id == department_id).first()
    if db_department is None:
        raise HTTPException(status_code=404, detail="Отделение не найдено")

    db.delete(db_department)
    db.commit()
    return {"message": "Отделение удалено"}
