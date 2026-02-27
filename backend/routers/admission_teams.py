from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud

router = APIRouter(prefix="/admission_teams", tags=["admission_teams"])

@router.get("/", response_model=List[schemas.AdmissionTeam])
def read_admission_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить все списки состав медицинских бригад"""
    admission_teams = crud.admission_team_crud.get_multi(db, skip=skip, limit=limit)
    return admission_teams

@router.get("/{admission_team_id}", response_model=schemas.AdmissionTeam)
def read_admission_team(admission_team_id: int, db: Session = Depends(get_db)):
    """Получить время поступления и выбытия по id"""
    admission_team = crud.admission_team_crud.get(db, admission_team_id)
    if not admission_team:
        raise HTTPException(status_code=404, detail="Такой медиццинской бригады не было")
    return admission_team

@router.post("/", response_model=schemas.AdmissionTeam)
def create_admission_team(admission_team: schemas.AdmissionTeamCreate, db: Session = Depends(get_db)):
    """Создать новую медицинскую бригаду"""
    return crud.admission_team_crud.create(db, admission_team)

@router.put("/{admission_team_id}", response_model=schemas.AdmissionTeam)
def update_admission(admission_team_id: int, admission_team: schemas.AdmissionTeamCreate, db: Session = Depends(get_db)):
    """Обновить данные медицинских бригад"""
    db_admission_team = crud.admission_team_crud.get(db, admission_team_id)
    if not db_admission_team:
        raise HTTPException(status_code=404, detail="Такой медицинской бригады не было")
    return crud.admission_team_crud.update(db, db_admission_team, admission_team)

@router.delete("/{admission_team_id}")
def delete_admission_team(admission_team_id: int, db: Session = Depends(get_db)):
    """Удалить медицинскую бригаду"""
    admission_team = crud.admission_team_crud.remove(db, admission_team_id)
    if not admission_team:
        raise HTTPException(status_code=404, detail="Медицинская бригада не найдена")
    return {"message": "Медицинская бригада успешно удалена"}
