from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.schemas import admission_team_schema as schemas
from backend.app.crud.admission_team_crud import admission_team_crud
from backend.app.api.dependencies import check_access_level, verify_password_header
from backend.app.models.base_models import Staff, AdmissionTeam

router = APIRouter(prefix="/admission-teams", tags=["Admission Teams"])

@router.get("/", response_model=List[schemas.AdmissionTeam])
def read_admission_teams(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # Уровень 2+: Врачи и медсестры могут видеть составы
    current_user: Staff = Depends(check_access_level(2))
):
    """Просмотр состава бригад"""
    return admission_team_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/{admission_team_id}", response_model=schemas.AdmissionTeam)
def read_admission_team(
    admission_team_id: int,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(2))
):
    """Получить информацию о конкретной бригаде"""
    team = admission_team_crud.get(db, id=admission_team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Запись о медицинской бригаде не найдена"
        )
    return team


@router.post("/", response_model=schemas.AdmissionTeam, status_code=status.HTTP_201_CREATED)
def create_admission_team(
    team_in: schemas.AdmissionTeamCreate,
    db: Session = Depends(get_db),
    # Уровень 3: Только администраторы формируют бригады
    current_user: Staff = Depends(check_access_level(3))
):
    """Назначение сотрудника в бригаду"""
    return admission_team_crud.create(db, obj_in=team_in)


@router.put("/{admission_team_id}", response_model=schemas.AdmissionTeam)
def update_admission_team(
    admission_team_id: int,
    team_in: schemas.AdmissionTeamCreate,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(check_access_level(3))
):
    """Изменение данных бригады"""
    db_obj = admission_team_crud.get(db, id=admission_team_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return admission_team_crud.update(db, db_obj=db_obj, obj_in=team_in)


@router.delete("/{admission_team_id}")
def delete_admission_team(
    admission_team_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_password_header),
    current_user: Staff = Depends(check_access_level(3))
):
    """Удаление записи о бригаде"""
    success = admission_team_crud.remove(db, id=admission_team_id)
    if not success:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return {"status": "success", "detail": "Запись о медицинской бригаде удалена"}