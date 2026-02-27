import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_positions_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- 1. POST (Создание должности) ---
        # Покрывает метод create_position
        pos_data = {
            "name": "Главный врач",
            "med_education": True,
            "lvl_responsibility": 10,
            "description": "Руководитель медицинского учреждения"
        }
        create_res = await ac.post("/positions/", json=pos_data)
        assert create_res.status_code == 200
        pos_id = create_res.json()["id"]
        assert create_res.json()["name"] == "Главный врач"

        # --- 2. GET List (Список должностей) ---
        # Покрывает метод read_positions
        list_res = await ac.get("/positions/")
        assert list_res.status_code == 200
        assert len(list_res.json()) > 0
        assert any(p["id"] == pos_id for p in list_res.json())

        # --- 3. GET One (Получение по ID) ---
        # Покрывает метод read_position
        get_one = await ac.get(f"/positions/{pos_id}")
        assert get_one.status_code == 200
        assert get_one.json()["lvl_responsibility"] == 10

        # --- 4. PUT (Обновление должности) ---
        # Покрывает метод update_position
        update_data = {
            "name": "Главврач (и.о.)",
            "med_education": True,
            "lvl_responsibility": 9,
            "description": "Временно исполняющий обязанности"
        }
        put_res = await ac.put(f"/positions/{pos_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["name"] == "Главврач (и.о.)"

        # --- 5. ТЕСТЫ ОШИБОК 404 ---
        # Ошибка в GET
        bad_get = await ac.get("/positions/9999")
        assert bad_get.status_code == 404
        assert bad_get.json()["detail"] == "Должность не найдена"

        # Ошибка в PUT
        bad_put = await ac.put("/positions/9999", json=update_data)
        assert bad_put.status_code == 404

        # --- 6. DELETE (Удаление должности) ---
        # Покрывает метод delete_position
        del_res = await ac.delete(f"/positions/{pos_id}")
        assert del_res.status_code == 200
        assert del_res.json()["message"] == "Должность успешно удалена"

        # Ошибка в DELETE (уже удалено)
        bad_del = await ac.delete(f"/positions/{pos_id}")
        assert bad_del.status_code == 404
