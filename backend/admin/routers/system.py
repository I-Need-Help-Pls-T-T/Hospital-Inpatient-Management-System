import os
import glob
from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from pydantic import BaseModel

from backend.database import engine
from backend.admin.create_dump import create_pg_backup, restore_pg_backup
from backend.models import Staff
from backend.auth import get_current_user

router = APIRouter(prefix="/system", tags=["system"])

class BackupRequest(BaseModel):
    tables: Optional[List[str]] = None

def check_admin_access(user: Staff):
    """Вспомогательная функция для проверки прав уровня 3+"""
    if user.access_level < 3:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещен: требуются права администратора (уровень 3)"
        )

@router.post("/backup")
async def trigger_backup(
    request: BackupRequest = Body(default=BackupRequest()),
    current_user: Staff = Depends(get_current_user) # Защита
):
    """Создать резервную копию базы данных (Уровень 3+)"""
    check_admin_access(current_user)

    path = create_pg_backup(tables=request.tables)
    if not path:
        raise HTTPException(status_code=500, detail="Ошибка при создании бэкапа")

    return {
        "message": "Backup created",
        "path": path,
        "type": "selective" if request.tables else "full",
        "tables": request.tables
    }

@router.get("/backup/latest")
async def download_latest_backup(
    current_user: Staff = Depends(get_current_user) # Защита
):
    """Скачать последний бэкап (Уровень 3+)"""
    check_admin_access(current_user)

    backup_dir = os.getenv("BACKUP_DIR", "backups")
    if not os.path.exists(backup_dir):
        raise HTTPException(status_code=404, detail="Директория бэкапов не найдена")

    files = glob.glob(os.path.join(backup_dir, "*.sql"))
    if not files:
        raise HTTPException(status_code=404, detail="Файлы бэкапа не найдены")

    latest_file = max(files, key=os.path.getmtime)

    return FileResponse(
        path=latest_file,
        filename=os.path.basename(latest_file),
        media_type='application/sql'
    )

class RestoreRequest(BaseModel):
    filename: str

@router.post("/restore")
async def trigger_restore(
    request: RestoreRequest,
    current_user: Staff = Depends(get_current_user)
):
    """Восстановить БД из файла (Уровень 3+)"""
    check_admin_access(current_user)

    filename = request.filename
    if not filename.endswith(".sql"):
        filename += ".sql"

    success = restore_pg_backup(filename)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Ошибка при восстановлении базы данных."
        )
    engine.dispose()
    return {"message": f"Database successfully restored from {request.filename}"}

@router.get("/backups/list")
async def list_available_backups(
    current_user: Staff = Depends(get_current_user) # Защита
):
    """Список всех доступных бэкапов (Уровень 3+)"""
    check_admin_access(current_user)

    backup_dir = os.getenv("BACKUP_DIR", "backups")
    if not os.path.exists(backup_dir):
        return []

    files = glob.glob(os.path.join(backup_dir, "*.sql"))
    result = []
    for f in files:
        result.append({
            "filename": os.path.basename(f),
            "size": os.path.getsize(f),
            "created_at": os.path.getmtime(f)
        })
    return sorted(result, key=lambda x: x['created_at'], reverse=True)
