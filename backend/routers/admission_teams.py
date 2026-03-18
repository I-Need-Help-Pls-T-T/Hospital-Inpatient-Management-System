from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import schemas, crud
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/admission_teams", tags=["admission_teams"])

@router.get("/", response_model=List[schemas.AdmissionTeam])
def read_admission_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Просмотр состава бригад (Уровень 2+: Врачи и медсестры)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Доступ к данным медицинских бригад ограничен")
    return crud.admission_team_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{admission_team_id}", response_model=schemas.AdmissionTeam)
def read_admission_team(
    admission_team_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Получить информацию о конкретной бригаде (Уровень 2+)"""
    if current_user.access_level < 2:
        raise HTTPException(status_code=403, detail="Недостаточно прав для просмотра")

    admission_team = crud.admission_team_crud.get(db, admission_team_id)
    if not admission_team:
        raise HTTPException(status_code=404, detail="Запись о медицинской бригаде не найдена")
    return admission_team

@router.post("/", response_model=schemas.AdmissionTeam)
def create_admission_team(
    admission_team: schemas.AdmissionTeamCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Назначение сотрудника в бригаду (Уровень 3+)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Только медицинский персонал может формировать бригады")
    return crud.admission_team_crud.create(db, admission_team)

@router.put("/{admission_team_id}", response_model=schemas.AdmissionTeam)
def update_admission_team(
    admission_team_id: int,
    admission_team: schemas.AdmissionTeamCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Изменение данных бригады (Только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Редактирование архивных записей бригад разрешено только администратору")

    db_admission_team = crud.admission_team_crud.get(db, admission_team_id)
    if not db_admission_team:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return crud.admission_team_crud.update(db, db_obj=db_admission_team, obj_in=admission_team)

@router.delete("/{admission_team_id}")
def delete_admission_team(
    admission_team_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(get_current_user)
):
    """Удаление записи о бригаде (Только уровень 3)"""
    if current_user.access_level < 3:
        raise HTTPException(status_code=403, detail="Удаление записей о персонале госпитализации разрешено только администратору")

    result = crud.admission_team_crud.remove(db, admission_team_id)
    if not result:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "message": "Запись о медицинской бригаде удалена"}
