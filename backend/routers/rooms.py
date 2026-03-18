from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("/", response_model=List[schemas.Room])
def read_rooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр списка помещений доступен всем (1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    return crud.room_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{room_id}", response_model=schemas.Room)
def read_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр помещения по ID (1+)"""
    if current_user.access_level < 1:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    room = crud.room_crud.get(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")
    return room

@router.post("/", response_model=schemas.Room)
def create_room(
    room: schemas.RoomCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Создание помещений — только Администратор (3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Только администратор может добавлять новые помещения")
    return crud.room_crud.create(db, room)

@router.put("/{room_id}", response_model=schemas.Room)
def update_room(
    room_id: int,
    room: schemas.RoomCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Редактирование помещений — только Администратор (3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Недостаточно прав для редактирования справочника помещений")

    db_room = crud.room_crud.get(db, room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")
    return crud.room_crud.update(db, db_obj=db_room, obj_in=room)

@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление помещений — только Администратор (3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Удаление помещений разрешено только администратору")

    result = crud.room_crud.remove(db, room_id)
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "message": "Помещение удалено"}
