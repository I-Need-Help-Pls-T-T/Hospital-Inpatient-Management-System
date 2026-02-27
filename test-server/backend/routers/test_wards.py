import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from datetime import datetime

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_wards_full_coverage():
    # Используем ASGITransport для обращения к нашему FastAPI приложению
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА ---
        # Палата (Ward) в вашей схеме данных зависит от Room, а та от Department.
        # Создаем их, чтобы не зависеть от состояния БД
        dep_res = await ac.post("/departments/", json={"name": "Хирургия"})
        dep_id = dep_res.json()["id"]

        room_res = await ac.post("/rooms/", json={
             "number": 202,
             "type": "Палата",
             "capacity": 2,
             "department_id": dep_id
        })
        room_id = room_res.json()["id"]

        # --- 1. POST (Создание) ---
        # ВНИМАНИЕ: убедитесь, что в WardCreate нет поля id (как мы исправляли ранее)
        ward_data = {
            "room_id": room_id,
            "w_place": 2,
            "m_place": 0
        }
        create_res = await ac.post("/wards/", json=ward_data)
        assert create_res.status_code == 200
        ward_id = create_res.json()["id"]

        # --- 2. GET List (Список) ---
        list_res = await ac.get("/wards/")
        assert list_res.status_code == 200
        assert any(w["id"] == ward_id for w in list_res.json())

        # --- 3. GET One (Получение по ID) ---
        get_one = await ac.get(f"/wards/{ward_id}")
        assert get_one.status_code == 200
        assert get_one.json()["room_id"] == room_id

        # --- 4. PUT (Обновление) ---
        update_data = {
            "room_id": room_id,
            "w_place": 1,
            "m_place": 1
        }
        put_res = await ac.put(f"/wards/{ward_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["m_place"] == 1

        # --- 5. GET 404 (Ошибка: не найдено) ---
        bad_get = await ac.get("/wards/99999")
        assert bad_get.status_code == 404
        assert bad_get.json()["detail"] == "Палата не найдена"

        # --- 6. DELETE (Удаление) ---
        del_res = await ac.delete(f"/wards/{ward_id}")
        assert del_res.status_code == 200

        # Проверка удаления
        after_del = await ac.get(f"/wards/{ward_id}")
        assert after_del.status_code == 404

        # --- 7. PUT 404 (Ошибка обновления несуществующей палаты) ---
        bad_put = await ac.put("/wards/99999", json=update_data)
        assert bad_put.status_code == 404
        assert bad_put.json()["detail"] == "Палата не найдена"

        # --- 8. DELETE 404 (Ошибка удаления несуществующей палаты) ---
        bad_del = await ac.delete("/wards/99999")
        assert bad_del.status_code == 404
        assert bad_del.json()["detail"] == "Палата не найдена"
