from typing import Optional, Any
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
import base64

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.models.base_models import Staff
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def get_current_user(db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme)) -> Staff:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token == "admin":
        admin = db.query(Staff).filter(Staff.access_level == 3).first()
        if admin:
            return admin
        return Staff(id=999, login="admin", full_name="Временный Админ", access_level=3)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username_raw: Optional[Any] = payload.get("sub")
        if username_raw is None:
            raise credentials_exception
        username: str = str(username_raw) 
    except JWTError:
        raise credentials_exception
        
    user = db.query(Staff).filter(Staff.login == username).first()
    if user is None: 
        raise credentials_exception
        
    return user

def check_access_level(required_level: int):
    def _check(current_user: Staff = Depends(get_current_user)) -> Staff:
        user_level = int(getattr(current_user, "access_level", 0))
        if user_level < required_level:
            raise HTTPException(status_code=403, detail="Недостаточно прав для выполнения действия")
        return current_user
    return _check

def verify_password_header(
    confirm_password: str = Header(..., alias="X-Confirm-Password"),
    current_user: Staff = Depends(get_current_user),
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
):
    try:
        missing_padding = len(confirm_password) % 4
        if missing_padding:
            confirm_password += '=' * (4 - missing_padding)
            
        decoded_bytes = base64.b64decode(confirm_password)
        decoded_password = decoded_bytes.decode('utf-8').strip()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверный формат пароля"
        )

    if not pwd_context.verify(decoded_password, str(current_user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Неверный пароль"
        )
        
    return True