import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

# Импортируем app из вашего основного файла
from backend.main import app

client = TestClient(app)

@pytest.fixture
def mock_backup_dir(tmp_path):
    """Создает временную директорию для тестов бэкапа"""
    d = tmp_path / "backups"
    d.mkdir()
    return d

### Тест 1: Успешный запуск бэкапа (POST /admin/system/backup)
@patch("backend.admin.routers.system.create_pg_backup")
def test_trigger_backup_success(mock_create):
    # Настраиваем мок так, будто бэкап успешно создался и вернул путь
    mock_create.return_value = "backups/test_backup.sql"

    response = client.post("/admin/system/backup")

    assert response.status_code == 200
    assert response.json()["message"] == "Backup created"
    assert response.json()["path"] == "backups/test_backup.sql"
    mock_create.assert_called_once()

### Тест 2: Ошибка при создании бэкапа (POST /admin/system/backup)
@patch("backend.admin.routers.system.create_pg_backup")
def test_trigger_backup_error(mock_create):
    # Настраиваем мок на возврат None (имитация ошибки в скрипте)
    mock_create.return_value = None

    response = client.post("/admin/system/backup")

    assert response.status_code == 500
    assert response.json()["detail"] == "Ошибка при создании бэкапа"

### Тест 3: Скачивание последнего бэкапа (GET /admin/system/backup/latest)
def test_download_latest_backup_success(mock_backup_dir, monkeypatch):
    # Создаем тестовые файлы во временной папке
    file1 = mock_backup_dir / "old_backup.sql"
    file1.write_text("old data")

    file2 = mock_backup_dir / "latest_backup.sql"
    file2.write_text("latest data")

    # Подменяем переменную окружения, чтобы роутер смотрел во временную папку
    monkeypatch.setenv("BACKUP_DIR", str(mock_backup_dir))

    response = client.get("/admin/system/backup/latest")

    assert response.status_code == 200
    assert response.content == b"latest data"
    assert "latest_backup.sql" in response.headers["content-disposition"]

### Тест 4: Ошибка, если файлов бэкапа нет (GET /admin/system/backup/latest)
def test_download_latest_backup_no_files(mock_backup_dir, monkeypatch):
    monkeypatch.setenv("BACKUP_DIR", str(mock_backup_dir))

    response = client.get("/admin/system/backup/latest")

    assert response.status_code == 404
    assert response.json()["detail"] == "Файлы бэкапа не найдены"
