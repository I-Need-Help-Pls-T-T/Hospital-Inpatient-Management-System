import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.database import SessionLocal
from backend import crud, schemas, models

BASE_URL = "http://testserver/api"

@pytest.mark.asyncio
async def test_auth_login_flow():
    # 1. Подготовка: создаем пользователя в БД
    db = SessionLocal()
    try:
        login = "auth_test_user"
        password = "testpassword"
        user = db.query(models.Staff).filter(models.Staff.login == login).first()
        if not user:
            # Используем crud для корректного хеширования пароля
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Auth Tester",
                login=login,
                password=password,
                access_level=1
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # 2. ТЕСТ: Успешный вход
        # OAuth2PasswordRequestForm ожидает данные в формате form-data
        login_data = {
            "username": login,
            "password": password
        }
        response = await ac.post("/auth/login", data=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["login"] == login

        # 3. ТЕСТ: Неверный пароль (Ошибка 401)
        bad_data = {
            "username": login,
            "password": "wrong_password"
        }
        response_bad = await ac.post("/auth/login", data=bad_data)
        assert response_bad.status_code == 401
        assert "Неверный логин или пароль" in response_bad.json()["detail"]

        # 4. ТЕСТ: Несуществующий пользователь
        fake_data = {
            "username": "non_existent_user",
            "password": "some_password"
        }
        response_fake = await ac.post("/auth/login", data=fake_data)
        assert response_fake.status_code == 401
