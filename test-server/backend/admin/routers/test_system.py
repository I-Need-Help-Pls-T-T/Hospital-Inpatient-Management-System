import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, MagicMock
import os

from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models

# Базовый URL для тестов (с учетом того, что в main.py может быть префикс /api)
BASE_URL = "http://testserver"

@pytest.fixture
async def admin_headers():
    """Фикстура для создания заголовков авторизации админа (access_level=4)"""
    db = SessionLocal()
    try:
        login = "admin_test_system"
        user = db.query(models.Staff).filter(models.Staff.login == login).first()
        if not user:
            user = crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="System Admin",
                login=login,
                password="123",
                access_level=4
            ))
        else:
            user.access_level = 4
            db.add(user)
            db.commit()

        token = create_access_token({"sub": login})
        return {"Authorization": f"Bearer {token}"}
    finally:
        db.close()

@pytest.fixture
def mock_backup_dir(tmp_path):
    """Создает временную директорию для тестов бэкапа"""
    d = tmp_path / "backups"
    d.mkdir()
    return d

@pytest.mark.asyncio
class TestSystemAdmin:

    # ВАЖНО: Итоговый путь получается из main.py (/api/admin) + system.py (/admin/system)
    # Итого: /api/admin/system/

    # --- ТЕСТЫ BACKUP ---

    @patch("backend.admin.routers.system.create_pg_backup")
    async def test_trigger_full_backup_success(self, mock_create, admin_headers):
        """Успешное создание полного бэкапа"""
        mock_create.return_value = "backups/full_test.sql"

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.post("/api/admin/system/backup", json={}, headers=admin_headers)

        assert response.status_code == 200
        assert response.json()["message"] == "Backup created"
        assert response.json()["type"] == "full"

    @patch("backend.admin.routers.system.create_pg_backup")
    async def test_trigger_selective_backup_success(self, mock_create, admin_headers):
        """Успешное создание селективного бэкапа (конкретные таблицы)"""
        mock_create.return_value = "backups/selective_test.sql"
        tables = ["patient", "department"]

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.post(
                "/api/admin/system/backup",
                json={"tables": tables},
                headers=admin_headers
            )

        assert response.status_code == 200
        assert response.json()["type"] == "selective"
        assert response.json()["tables"] == tables

    @patch("backend.admin.routers.system.create_pg_backup")
    async def test_trigger_backup_script_failure(self, mock_create, admin_headers):
        """Ошибка 500, если скрипт создания бэкапа вернул None (строка 36 в system.py)"""
        mock_create.return_value = None

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.post("/api/admin/system/backup", json={}, headers=admin_headers)

        assert response.status_code == 500
        assert "Ошибка при создании бэкапа" in response.json()["detail"]

    async def test_trigger_backup_forbidden_for_intern(self):
        """Ошибка 403: у стажера нет прав на бэкап"""
        db = SessionLocal()
        try:
            login = "intern_test_system"
            user = db.query(models.Staff).filter(models.Staff.login == login).first()
            if not user:
                crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                    full_name="Intern Staff", login=login, password="123", access_level=1
                ))
            else:
                user.access_level = 1
                db.add(user); db.commit()
        finally:
            db.close()

        token = create_access_token({"sub": "intern_test_system"})
        headers = {"Authorization": f"Bearer {token}"}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.post("/api/admin/system/backup", json={}, headers=headers)

        assert response.status_code == 403

    # --- ТЕСТЫ СКАЧИВАНИЯ (DOWNLOAD) ---

    async def test_download_latest_backup_success(self, mock_backup_dir, monkeypatch, admin_headers):
        """Успешное скачивание последнего файла"""
        latest_file = mock_backup_dir / "latest.sql"
        latest_file.write_text("sql data content")

        monkeypatch.setenv("BACKUP_DIR", str(mock_backup_dir))

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.get("/api/admin/system/backup/latest", headers=admin_headers)

        assert response.status_code == 200
        assert response.content == b"sql data content"

    async def test_download_latest_backup_no_files(self, mock_backup_dir, monkeypatch, admin_headers):
        """Ошибка 404, если в папке нет .sql файлов (строка 58 в system.py)"""
        monkeypatch.setenv("BACKUP_DIR", str(mock_backup_dir))

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.get("/api/admin/system/backup/latest", headers=admin_headers)

        assert response.status_code == 404
        assert "Файлы бэкапа не найдены" in response.json()["detail"]

    # --- ТЕСТЫ RESTORE ---

    @patch("backend.admin.routers.system.restore_pg_backup")
    async def test_trigger_restore_success(self, mock_restore, admin_headers):
        """Успешное восстановление из дампа"""
        mock_restore.return_value = True

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.post(
                "/api/admin/system/restore",
                json={"filename": "test_dump.sql"},
                headers=admin_headers
            )

        assert response.status_code == 200
        assert "successfully restored" in response.json()["message"]

    @patch("backend.admin.routers.system.restore_pg_backup")
    async def test_trigger_restore_failure(self, mock_restore, admin_headers):
        """Ошибка 500 при сбое скрипта восстановления (строка 81 в system.py)"""
        mock_restore.return_value = False

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.post(
                "/api/admin/system/restore",
                json={"filename": "bad.sql"},
                headers=admin_headers
            )

        assert response.status_code == 500

    # --- ТЕСТЫ LIST ---

    async def test_list_backups_empty(self, mock_backup_dir, monkeypatch, admin_headers):
        """Список бэкапов пуст"""
        monkeypatch.setenv("BACKUP_DIR", str(mock_backup_dir))

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.get("/api/admin/system/backups/list", headers=admin_headers)

        assert response.status_code == 200
        assert response.json() == []

    async def test_list_backups_not_found_dir(self, monkeypatch, admin_headers):
        """Тест строки 101: директории не существует — возвращает пустой список"""
        monkeypatch.setenv("BACKUP_DIR", "/non/existent/path/12345")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
            response = await ac.get("/api/admin/system/backups/list", headers=admin_headers)

        assert response.status_code == 200
        assert response.json() == []
