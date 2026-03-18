import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_rooms_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ И ДАННЫХ ---
    db = SessionLocal()
    try:
        # Админ (Уровень 4)
        admin_login = "room_admin"
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Завхоз", login=admin_login, password="1", access_level=3
            ))

        # Врач (Уровень 1)
        doc_login = "room_doc"
        if not db.query(models.Staff).filter(models.Staff.login == doc_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Врач", login=doc_login, password="1", access_level=1
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # Токены
        admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': admin_login})}"}
        doc_headers = {"Authorization": f"Bearer {create_access_token({'sub': doc_login})}"}

        # Создаем отделение (необходимо для Foreign Key)
        dep_res = await ac.post("/api/departments/", json={"name": "Тестовое отделение"}, headers=admin_headers)
        dep_id = dep_res.json()["id"]

        # --- 2. ТЕСТ СОЗДАНИЯ (POST) ---
        room_payload = {
            "number": 101,
            "type": "Кабинет",
            "capacity": 2,
            "department_id": dep_id
        }

        # Ошибка 403: Врач не может создавать комнаты
        res_p_403 = await ac.post("/api/rooms/", json=room_payload, headers=doc_headers)
        assert res_p_403.status_code == 403

        # Успех: Админ создает
        res_p_ok = await ac.post("/api/rooms/", json=room_payload, headers=admin_headers)
        assert res_p_ok.status_code == 200
        room_id = res_p_ok.json()["id"]

        # --- 3. ТЕСТ ЧТЕНИЯ (GET) ---
        # Список
        res_list = await ac.get("/api/rooms/", headers=doc_headers)
        assert res_list.status_code == 200
        assert len(res_list.json()) > 0

        # Конкретная комната
        res_one = await ac.get(f"/api/rooms/{room_id}", headers=doc_headers)
        assert res_one.status_code == 200
        assert res_one.json()["number"] == 101

        # Ошибка 404
        res_get_404 = await ac.get("/api/rooms/9999", headers=doc_headers)
        assert res_get_404.status_code == 404

        # --- 4. ТЕСТ ОБНОВЛЕНИЯ (PUT) ---
        update_payload = {**room_payload, "number": 102}

        # Ошибка 404
        res_up_404 = await ac.put("/api/rooms/9999", json=update_payload, headers=admin_headers)
        assert res_up_404.status_code == 404

        # Успех
        res_up_ok = await ac.put(f"/api/rooms/{room_id}", json=update_payload, headers=admin_headers)
        assert res_up_ok.status_code == 200
        assert res_up_ok.json()["number"] == 102

        # --- 5. ТЕСТ УДАЛЕНИЯ (DELETE) ---
        # Ошибка 403: Врач не может удалять
        res_d_403 = await ac.delete(f"/api/rooms/{room_id}", headers=doc_headers)
        assert res_d_403.status_code == 403

        # Успех
        res_d_ok = await ac.delete(f"/api/rooms/{room_id}", headers=admin_headers)
        assert res_d_ok.status_code == 200

        # Повторное удаление (404)
        res_d_404 = await ac.delete(f"/api/rooms/{room_id}", headers=admin_headers)
        assert res_d_404.status_code == 404
