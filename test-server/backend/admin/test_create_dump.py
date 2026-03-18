import pytest
from unittest.mock import patch, MagicMock
import os
import subprocess
from backend.admin.create_dump import create_pg_backup, restore_pg_backup

@pytest.fixture
def mock_env(monkeypatch):
    """Подменяем переменные окружения для теста"""
    monkeypatch.setenv("DB_NAME", "Hospital")
    monkeypatch.setenv("DB_USER", "postgres")
    monkeypatch.setenv("DB_PASSWORD", "testpass")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("BACKUP_DIR", "test_backups")

@patch("subprocess.run")
@patch("os.makedirs")
@patch("os.path.exists")
def test_create_pg_backup_full_success(mock_exists, mock_makedirs, mock_run, mock_env):
    """Тест 1: Успешное создание ПОЛНОГО бэкапа"""
    mock_exists.return_value = False
    mock_run.return_value = MagicMock(returncode=0)

    result = create_pg_backup(tables=None)

    # Проверка создания папки
    mock_makedirs.assert_called_once_with("test_backups")

    # Проверка аргументов команды
    args, kwargs = mock_run.call_args
    command = args[0]
    assert "pg_dump" in command
    assert "--clean" in command
    assert "--if-exists" in command
    assert "full_system_" in result
    assert kwargs["env"]["PGPASSWORD"] == "testpass"

@patch("subprocess.run")
@patch("os.path.exists")
def test_create_pg_backup_selective_success(mock_exists, mock_run, mock_env):
    """Тест 2: Успешное создание СЕЛЕКТИВНОГО бэкапа (только данные)"""
    mock_exists.return_value = True
    mock_run.return_value = MagicMock(returncode=0)

    tables = ["patient", "hospitalization"]
    result = create_pg_backup(tables=tables)

    args, _ = mock_run.call_args
    command = args[0]

    assert "--data-only" in command
    assert "--column-inserts" in command
    assert "-t" in command
    assert "patient" in command
    assert "selective_data_" in result

@patch("subprocess.run")
def test_create_pg_backup_failure(mock_run, mock_env):
    """Тест 3: Обработка ошибки pg_dump"""
    mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd="pg_dump")

    result = create_pg_backup()
    assert result is None

@patch("subprocess.run")
@patch("os.path.exists")
def test_restore_pg_backup_full(mock_exists, mock_run, mock_env):
    """Тест 4: Восстановление из ПОЛНОГО бэкапа (без TRUNCATE)"""
    mock_exists.return_value = True
    mock_run.return_value = MagicMock(returncode=0)

    filename = "full_system_20240101.sql"
    success = restore_pg_backup(filename)

    assert success is True
    # Проверяем, что в командах НЕТ truncate для полного бэкапа
    all_calls = [call.args[0] for call in mock_run.call_args_list]
    flattened_commands = [item for sublist in all_calls for item in sublist]
    assert not any("TRUNCATE TABLE" in str(cmd) for cmd in flattened_commands)

@patch("subprocess.run")
@patch("os.path.exists")
def test_restore_pg_backup_selective(mock_exists, mock_run, mock_env):
    """Тест 5: Восстановление из СЕЛЕКТИВНОГО бэкапа (с TRUNCATE CASCADE)"""
    mock_exists.return_value = True
    mock_run.return_value = MagicMock(returncode=0)

    filename = "selective_data_20240101.sql"
    success = restore_pg_backup(filename)

    assert success is True

    # Проверяем наличие команды TRUNCATE в вызовах subprocess
    all_calls_args = [call.args[0] for call in mock_run.call_args_list]
    # Собираем все строки команд в одну
    combined_commands = " ".join([str(arg) for sublist in all_calls_args for arg in sublist])

    assert "TRUNCATE TABLE patient CASCADE;" in combined_commands
    assert "SET session_replication_role = 'replica';" in combined_commands

@patch("os.path.exists")
def test_restore_pg_backup_file_not_found(mock_exists, mock_env):
    """Тест 6: Файл бэкапа не найден"""
    mock_exists.return_value = False
    success = restore_pg_backup("non_existent.sql")
    assert success is False
