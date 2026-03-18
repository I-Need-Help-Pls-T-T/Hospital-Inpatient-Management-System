import os
from datetime import datetime, timedelta, timezone  # Добавлен timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from backend.database import get_db
from backend import models

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-if-env-fails")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 600))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def create_access_token(data: dict):
    """Создание JWT токена с использованием актуального datetime.now(timezone.utc)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить личность",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.Staff).filter(models.Staff.login == login).first()
    if user is None:
        raise credentials_exception
    return user

# --- Роутер для дополнительных auth-эндпоинтов ---
from fastapi import APIRouter
from pydantic import BaseModel
from backend.crud import staff_crud

router = APIRouter(prefix="/api/auth", tags=["auth"])

class VerifyPasswordRequest(BaseModel):
    login: str
    password: str

@router.get("/me")
def get_me(current_user: models.Staff = Depends(get_current_user)):
    """Возвращает данные текущего авторизованного пользователя"""
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "login": current_user.login,
        "access_level": current_user.access_level,
    }

@router.post("/verify-password")
def verify_password(
    body: VerifyPasswordRequest,
    db: Session = Depends(get_db),
    current_user: models.Staff = Depends(get_current_user)
):
    """Проверяет пароль текущего пользователя (только своего аккаунта)"""
    # Безопасность: разрешаем проверять только свой логин
    if body.login != current_user.login:
        raise HTTPException(status_code=403, detail="Можно проверять только пароль своего аккаунта")

    user = staff_crud.authenticate(db, login=body.login, password=body.password)
    return {"valid": user is not None}
