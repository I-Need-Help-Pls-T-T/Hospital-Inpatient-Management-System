import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_rooms_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА: Создаем отделение (зависимость) ---
        dep_res = await ac.post("/departments/", json={
            "name": "Общая терапия"
        })
        dep_id = dep_res.json()["id"]

        # --- 1. POST (Создание помещения) ---
        # Покрывает метод create_room
        room_data = {
            "type": "Кабинет",
            "number": 105,
            "capacity": 3,
            "department_id": dep_id
        }
        create_res = await ac.post("/rooms/", json=room_data)
        assert create_res.status_code == 200
        room_id = create_res.json()["id"]
        assert create_res.json()["number"] == 105

        # --- 2. GET List (Список всех помещений) ---
        # Покрывает метод read_rooms
        list_res = await ac.get("/rooms/")
        assert list_res.status_code == 200
        assert any(r["id"] == room_id for r in list_res.json())

        # --- 3. GET One (Получение по ID) ---
        # Покрывает метод read_room
        get_one = await ac.get(f"/rooms/{room_id}")
        assert get_one.status_code == 200
        assert get_one.json()["type"] == "Кабинет"

        # --- 4. PUT (Обновление помещения) ---
        # Покрывает метод update_room
        update_data = {
            "type": "Процедурная",
            "number": 106,
            "capacity": 1,
            "department_id": dep_id
        }
        put_res = await ac.put(f"/rooms/{room_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["type"] == "Процедурная"

        # --- 5. ТЕСТЫ ОШИБОК 404 ---
        # Ошибка в GET (несуществующий ID)
        bad_get = await ac.get("/rooms/99999")
        assert bad_get.status_code == 404
        assert bad_get.json()["detail"] == "Помещение не найдено"

        # Ошибка в PUT (несуществующий ID)
        bad_put = await ac.put("/rooms/99999", json=update_data)
        assert bad_put.status_code == 404
        assert bad_put.json()["detail"] == "Помещение не найдено"

        # --- 6. DELETE (Удаление помещения) ---
        # Покрывает метод delete_room
        del_res = await ac.delete(f"/rooms/{room_id}")
        assert del_res.status_code == 200

        # Повторное удаление (404)
        bad_del = await ac.delete(f"/rooms/{room_id}")
        assert bad_del.status_code == 404
        assert bad_del.json()["detail"] == "Помещение не найдено"
