import os
import glob
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

# Импортируем вашу функцию из соседнего файла create_dump.py
# В зависимости от вашей структуры используйте правильный путь:
from backend.admin.create_dump import create_pg_backup

router = APIRouter(prefix="/admin/system", tags=["system"])

@router.post("/backup")
async def trigger_backup():
    """Создать резервную копию базы данных"""
    path = create_pg_backup()
    if not path:
        raise HTTPException(status_code=500, detail="Ошибка при создании бэкапа")
    return {"message": "Backup created", "path": path}

@router.get("/backup/latest")
async def download_latest_backup():
    """Скачать последний файл бэкапа"""
    # Теперь 'os' будет определен благодаря импорту в начале файла
    backup_dir = os.getenv("BACKUP_DIR", "backups")

    if not os.path.exists(backup_dir):
        raise HTTPException(status_code=404, detail="Директория бэкапов не найдена")

    files = glob.glob(os.path.join(backup_dir, "*.sql"))
    if not files:
        raise HTTPException(status_code=404, detail="Файлы бэкапа не найдены")

    # Находим самый новый файл
    latest_file = max(files, key=os.path.getmtime)

    return FileResponse(
        path=latest_file,
        filename=os.path.basename(latest_file),
        media_type='application/sql'
    )
