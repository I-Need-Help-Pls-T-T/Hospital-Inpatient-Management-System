import os
import glob
from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel

from backend.app.database import engine
from backend.app.utils.create_dump import create_pg_backup, restore_pg_backup
from backend.app.models.base_models import Staff
from backend.app.api.dependencies import get_current_user

router = APIRouter(prefix="/system", tags=["system"])

class BackupRequest(BaseModel):
    tables: Optional[List[str]] = None

def check_admin_access(user: Staff):
    access_level = getattr(user, "access_level", 0)
    if int(access_level) < 3:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещен: уровень администратора ниже 3"
        )

@router.post("/backup")
async def trigger_backup(
    request: BackupRequest = Body(default=BackupRequest()),
    current_user: Staff = Depends(get_current_user)
):
    check_admin_access(current_user)
    path = create_pg_backup(tables=request.tables)
    if not path:
        raise HTTPException(status_code=500, detail="Ошибка при создании бэкапа")
    return {"message": "Backup created", "path": path}

@router.get("/backups/list")
async def list_available_backups(current_user: Staff = Depends(get_current_user)):
    check_admin_access(current_user)
    backup_dir = os.getenv("BACKUP_DIR", "backups")
    if not os.path.exists(backup_dir):
        return []
    files = [os.path.basename(f) for f in glob.glob(os.path.join(backup_dir, "*.sql"))]
    return sorted(files, reverse=True)

class RestoreRequest(BaseModel):
    filename: str

@router.post("/restore")
async def trigger_restore(
    request: RestoreRequest,
    current_user: Staff = Depends(get_current_user)
):
    check_admin_access(current_user)
    
    engine.dispose()
    
    success = restore_pg_backup(request.filename)
    if not success:
        raise HTTPException(status_code=500, detail="Ошибка при восстановлении")
    
    return {"message": f"Database successfully restored from {request.filename}"}