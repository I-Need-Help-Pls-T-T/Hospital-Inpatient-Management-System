from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import room_schema as schemas
from backend.app.crud.room_crud import room_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff

router = APIRouter(prefix="/rooms", tags=["Rooms"])

# --- READ LIST ---
@router.get("/", response_model=List[schemas.Room])
def read_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Просмотр списка помещений доступен персоналу (уровень 1+)"""
    return room_crud.get_multi(db, skip=skip, limit=limit)

# --- READ SINGLE ---
@router.get("/{room_id}", response_model=schemas.Room)
def read_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(1))
):
    """Просмотр помещения по ID (уровень 1+)"""
    room = room_crud.get(db, id=room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Помещение не найдено"
        )
    return room

# --- CREATE ---
@router.post("/", response_model=schemas.Room, status_code=status.HTTP_201_CREATED)
def create_room(
    room_in: schemas.RoomCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Создание помещений — только Администратор (уровень 3)"""
    return room_crud.create(db, obj_in=room_in)

# --- UPDATE ---
@router.put("/{room_id}", response_model=schemas.Room)
def update_room(
    room_id: int,
    room_in: schemas.RoomCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Редактирование помещений — только Администратор (уровень 3)"""
    db_room = room_crud.get(db, id=room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")
    
    return room_crud.update(db, db_obj=db_room, obj_in=room_in)

# --- DELETE ---
@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удаление помещений — только Администратор (уровень 3)"""
    room = room_crud.get(db, id=room_id)
    if not room:
         raise HTTPException(status_code=404, detail="Запись не найдена")
         
    room_crud.remove(db, id=room_id)
    return {"status": "success", "detail": "Помещение удалено"}