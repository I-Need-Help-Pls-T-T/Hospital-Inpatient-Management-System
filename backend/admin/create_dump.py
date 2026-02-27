import subprocess
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def create_pg_backup():
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    backup_dir = os.getenv("BACKUP_DIR", "backups")

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(backup_dir, f"hospital_backup_{timestamp}.sql")

    env = os.environ.copy()
    env["PGPASSWORD"] = db_password

    command = [
        "pg_dump",
        "-U", db_user,
        "-d", db_name,
        "-f", filename,
        "-h", "localhost"
    ]

    try:
        subprocess.run(command, check=True, env=env)
        print(f"Бэкап успешно создан: {filename}")
        return filename
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании бэкапа: {e}")
        return None
