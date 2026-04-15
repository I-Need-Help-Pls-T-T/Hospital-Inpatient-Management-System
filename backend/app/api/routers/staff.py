from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import staff_schema as schemas
from backend.app.crud.staff_crud import staff_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/staff", tags=["Staff"])

@router.get("/", response_model=List[schemas.Staff])
def read_staff_list(
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Список всех сотрудников (доступно от уровня 1)"""
    return staff_crud.get_multi(db)

@router.post("/", response_model=schemas.Staff)
def create_staff(
    staff_in: schemas.StaffCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Создание сотрудника (только для уровня 3)"""
    current_level = int(getattr(current_user, "access_level", 0))

    if staff_crud.get_by_login(db, login=staff_in.login):
        raise HTTPException(status_code=400, detail="Логин уже занят")
    
    if staff_in.access_level > current_level:
        raise HTTPException(
            status_code=403, 
            detail=f"Нельзя назначить уровень {staff_in.access_level}, ваш уровень {current_level}"
        )
    
    return staff_crud.create(db, obj_in=staff_in)

@router.put("/{staff_id}", response_model=schemas.Staff)
def update_staff(
    staff_id: int,
    staff_in: schemas.StaffUpdate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Обновление данных сотрудника"""
    db_obj = staff_crud.get(db, id=staff_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
        
    current_level = int(getattr(current_user, "access_level", 0))

    if staff_in.access_level is not None:
        if int(staff_in.access_level) > current_level:
            raise HTTPException(status_code=403, detail="Недостаточно прав для назначения такого уровня")

    return staff_crud.update(db, db_obj=db_obj, obj_in=staff_in)

@router.delete("/{staff_id}")
def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удаление сотрудника (только уровень 3)"""
    staff_to_delete = staff_crud.get(db, id=staff_id)
    if not staff_to_delete:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    
    curr_id = int(getattr(current_user, "id", 0))
    target_id = int(getattr(staff_to_delete, "id", 0))

    if target_id == curr_id:
        raise HTTPException(status_code=400, detail="Нельзя удалить свою учетную запись")

    staff_crud.remove(db, id=staff_id)
    return {"status": "success", "detail": "Сотрудник удален"}