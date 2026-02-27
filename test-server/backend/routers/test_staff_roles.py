import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from datetime import date, timedelta

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_staff_roles_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА ---
        pos_res = await ac.post("/positions/", json={
            "name": "Хирург", "med_education": True, "lvl_responsibility": 5
        })
        pos_id = pos_res.json()["id"]

        staff_res = await ac.post("/staff/", json={
            "full_name": "Иванов Иван", "position_id": pos_id, "status": "Активен"
        })
        staff_id = staff_res.json()["id"]

        today = str(date.today())
        tomorrow = str(date.today() + timedelta(days=1))

        # --- 1. POST (Создание) ---
        role_data = {
            "staff_id": staff_id,
            "position_id": pos_id,
            "appointment_date": today,
            "end_date": None  # Поля 'role' нет в модели, используем end_date
        }
        create_res = await ac.post("/staff_roles/", json=role_data)
        assert create_res.status_code == 200

        # --- 2. GET List ---
        list_res = await ac.get("/staff_roles/")
        assert list_res.status_code == 200
        assert len(list_res.json()) > 0

        # --- 3. GET /detail ---
        detail_res = await ac.get("/staff_roles/detail", params={
            "staff_id": staff_id,
            "position_id": pos_id,
            "appointment_date": today
        })
        assert detail_res.status_code == 200
        # Проверяем по staff_id, так как поля role нет
        assert detail_res.json()["staff_id"] == staff_id

        # --- 4. PUT /update ---
        update_data = {
            "staff_id": staff_id,
            "position_id": pos_id,
            "appointment_date": today,
            "end_date": tomorrow # Обновляем дату окончания
        }
        put_res = await ac.put("/staff_roles/update", params={
            "staff_id": staff_id,
            "position_id": pos_id,
            "appointment_date": today
        }, json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["end_date"] == tomorrow

        # --- 5. ТЕСТ ОШИБОК 404 ---
        # Ошибка в GET detail
        bad_detail = await ac.get("/staff_roles/detail", params={
            "staff_id": 9999, "position_id": pos_id, "appointment_date": today
        })
        assert bad_detail.status_code == 404

        # Ошибка в PUT update
        bad_put = await ac.put("/staff_roles/update", params={
            "staff_id": 9999, "position_id": pos_id, "appointment_date": today
        }, json=update_data)
        assert bad_put.status_code == 404

        # --- 6. DELETE ---
        del_res = await ac.delete("/staff_roles/delete", params={
            "staff_id": staff_id,
            "position_id": pos_id,
            "appointment_date": today
        })
        assert del_res.status_code == 200

        # Ошибка в DELETE (уже удалено)
        bad_del = await ac.delete("/staff_roles/delete", params={
            "staff_id": staff_id, "position_id": pos_id, "appointment_date": today
        })
        assert bad_del.status_code == 404
