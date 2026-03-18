from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import crud, auth
from backend.models import Staff

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.staff_crud.authenticate(
        db,
        login=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.login})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "login": user.login,
            "access_level": user.access_level,
            "full_name": user.full_name
        }
    }

@router.get("/me")
def get_me(current_user: Staff = Depends(auth.get_current_user)):
    """Возвращает данные текущего авторизованного пользователя"""
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "login": current_user.login,
        "access_level": current_user.access_level,
    }

class VerifyPasswordRequest(BaseModel):
    login: str
    password: str

@router.post("/verify-password")
def verify_password(
    body: VerifyPasswordRequest,
    db: Session = Depends(get_db),
    current_user: Staff = Depends(auth.get_current_user)
):
    """Проверяет пароль текущего пользователя"""
    if body.login != current_user.login:
        raise HTTPException(status_code=403, detail="Можно проверять только пароль своего аккаунта")

    user = crud.staff_crud.authenticate(db, login=body.login, password=body.password)
    return {"valid": user is not None}
