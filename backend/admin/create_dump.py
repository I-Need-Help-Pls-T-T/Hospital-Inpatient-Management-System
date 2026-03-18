import subprocess
import datetime
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

def create_pg_backup(tables: Optional[List[str]] = None):
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    backup_dir = os.getenv("BACKUP_DIR", "backups")

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    env = os.environ.copy()
    env["PGPASSWORD"] = db_password
    env["PGCLIENTENCODING"] = "UTF8"

    command = ["pg_dump", "-U", db_user, "-d", db_name, "-h", db_host]

    if tables:
        # СЕЛЕКТИВНЫЙ РЕЖИМ
        filename = os.path.join(backup_dir, f"selective_data_{timestamp}.sql")
        # Используем --data-only и --column-inserts для чистых данных
        command.extend(["--data-only", "--column-inserts"])
        for table in tables:
            command.extend(["-t", table])
    else:
        # ПОЛНЫЙ РЕЖИМ
        filename = os.path.join(backup_dir, f"full_system_{timestamp}.sql")
        command.extend(["--clean", "--if-exists"])

    command.extend(["-f", filename])

    try:
        subprocess.run(command, check=True, env=env)
        return filename
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании бэкапа: {e}")
        return None


def restore_pg_backup(filename: str) -> bool:
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    backup_dir = os.getenv("BACKUP_DIR", "backups")

    file_path = os.path.join(backup_dir, filename)
    if not os.path.exists(file_path):
        return False

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password
    env["PGCLIENTENCODING"] = "UTF8"

    # Определяем, селективный это бэкап или полный, по имени файла
    is_selective = "selective_data" in filename

    kill_sessions_cmd = [
        "psql", "-U", db_user, "-d", "postgres", "-h", db_host,
        "-c", f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}' AND pid <> pg_backend_pid();"
    ]

    restore_command = [
        "psql", "-U", db_user, "-d", db_name, "-h", db_host,
        "-c", "SET session_replication_role = 'replica';",
    ]

    # Если это селективный бэкап, мы можем попробовать сделать TRUNCATE
    # для таблицы patient (или других), чтобы избежать Duplicate Key
    if is_selective:
        # Пытаемся очистить таблицу перед вставкой, чтобы не было конфликтов ID
        # Это сработает для вашего случая с пациентами
        restore_command.extend(["-c", "TRUNCATE TABLE patient CASCADE;"])

    restore_command.extend(["-f", file_path])
    restore_command.extend(["-c", "SET session_replication_role = 'origin';"])

    try:
        # 1. Сначала выкидываем всех (включая наше же приложение)
        subprocess.run(kill_sessions_cmd, check=True, env=env)
        # 2. Теперь база свободна для psql
        subprocess.run(restore_command, check=True, env=env)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при восстановлении: {e}")
        return False
