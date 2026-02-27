import pytest
import asyncio
from backend.database import Base, engine, SessionLocal
from backend.main import app

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

@pytest.fixture(autouse=True)
def clean_tables():
    """Очистка таблиц перед КАЖДЫМ тестом"""
    with SessionLocal() as db:
        # Удаляем в правильном порядке из-за Foreign Keys
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
