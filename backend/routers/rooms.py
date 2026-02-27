from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("/", response_model=List[schemas.Room])
def read_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список помещений"""
    rooms = crud.room_crud.get_multi(db, skip=skip, limit=limit)
    return rooms

@router.get("/{room_id}", response_model=schemas.Room)
def read_room(room_id: int, db: Session = Depends(get_db)):
    """Получить по id помещение"""
    room = crud.room_crud.get(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")
    return room

@router.post("/", response_model=schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    """Создать новое помещение"""
    return crud.room_crud.create(db, room)

@router.put("/{room_id}", response_model=schemas.Room)
def update_room(room_id: int, room: schemas.RoomCreate, db: Session = Depends(get_db)):
    """Обновить помещение"""
    db_room = crud.room_crud.get(db, room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")
    return crud.room_crud.update(db, db_room, room)

@router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    """Удалить помещение"""
    room = crud.room_crud.remove(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Помещение не найдено")
    return {"message": "Помещение успешно удалено"}
