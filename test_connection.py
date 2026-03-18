import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
# Загружаем .env
load_dotenv()

# Получаем параметры
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

print(f"Параметры подключения:")
print(f"  USER: {DB_USER}")
print(f"  DATABASE: {DB_NAME}")
print(f"  HOST: {DB_HOST}")
print(f"  PORT: {DB_PORT}")

# Формируем URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"URL: postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    # Пробуем подключиться
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.scalar()
        print("\n✅ ПОДКЛЮЧЕНИЕ УСПЕШНО!")
        print(f"Версия PostgreSQL: {version}")
        
        # Проверяем существующие таблицы
        result = conn.execute(text("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname='public'
        """))
        tables = result.fetchall()
        if tables:
            print("\nСуществующие таблицы:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("\nТаблицы ещё не созданы")
            
except Exception as e:
    print(f"\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
