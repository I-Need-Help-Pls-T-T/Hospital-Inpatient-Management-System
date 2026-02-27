import pytest
from unittest.mock import patch, MagicMock
import os
import subprocess
from backend.admin.create_dump import create_pg_backup

@pytest.fixture
def mock_env(monkeypatch):
    """Подменяем переменные окружения для теста"""
    monkeypatch.setenv("DB_NAME", "Hospital")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "testpass")
    monkeypatch.setenv("BACKUP_DIR", "test_backups")

### Тест 1: Успешное создание бэкапа
@patch("subprocess.run")
@patch("os.makedirs")
@patch("os.path.exists")
def test_create_pg_backup_success(mock_exists, mock_makedirs, mock_run, mock_env):
    # Настраиваем моки
    mock_exists.return_value = False # Имитируем, что папки нет
    mock_run.return_value = MagicMock(returncode=0)

    result = create_pg_backup()

    # Проверяем, что папка создалась
    mock_makedirs.assert_called_once_with("test_backups")

    # Проверяем, что subprocess.run вызван с правильными аргументами
    args, kwargs = mock_run.call_args
    command = args[0]

    assert command[0] == "pg_dump"
    assert "-d" in command and "Hospital" in command
    assert "-U" in command and "postgres" in command
    assert kwargs["env"]["PGPASSWORD"] == "testpass"
    assert result is not None
    assert "test_backups" in result

### Тест 2: Ошибка при выполнении команды (pg_dump упал)
@patch("subprocess.run")
@patch("os.path.exists")
def test_create_pg_backup_failure(mock_exists, mock_run, mock_env):
    mock_exists.return_value = True
    # Имитируем ошибку процесса
    mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd="pg_dump")

    result = create_pg_backup()

    assert result is None

### Тест 3: Проверка корректности формата имени файла
def test_backup_filename_format(mock_env):
    with patch("subprocess.run"), patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        result = create_pg_backup()

        # Проверяем, что имя файла содержит дату (8 цифр) и расширение .sql
        filename = os.path.basename(result)
        assert filename.startswith("hospital_backup_")
        assert filename.endswith(".sql")
        assert len(filename) > 25 # Проверка на наличие таймстампа
