import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_departments_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- 1. POST (Создание отделения) ---
        dep_data = {
            "name": "Кардиология",
            "phone": "777-111",
            "profile": "Сердечно-сосудистые",
            "category": "Первая"
        }
        create_res = await ac.post("/departments/", json=dep_data)
        assert create_res.status_code == 200
        dep_id = create_res.json()["id"]
        assert create_res.json()["name"] == "Кардиология"

        # --- 2. GET List (Получение списка) ---
        # Покрывает метод read_departments
        list_res = await ac.get("/departments/", params={"limit": 1000})
        assert list_res.status_code == 200
        assert any(d["id"] == dep_id for d in list_res.json())

        # --- 3. GET One (Получение по ID) ---
        # Покрывает метод read_department
        get_one = await ac.get(f"/departments/{dep_id}")
        assert get_one.status_code == 200
        assert get_one.json()["name"] == "Кардиология"

        # --- 4. PUT (Обновление) ---
        # Покрывает метод update_department
        update_data = {
            "name": "Кардиоцентр",
            "phone": "777-222",
            "profile": "Хирургия сердца",
            "category": "Высшая"
        }
        put_res = await ac.put(f"/departments/{dep_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["name"] == "Кардиоцентр"
        assert put_res.json()["category"] == "Высшая"

        # --- 5. ТЕСТЫ ОШИБОК 404 (Закрываем Missing lines) ---
        # Ошибка при получении несуществующего ID
        bad_get = await ac.get("/departments/9999")
        assert bad_get.status_code == 404
        assert bad_get.json()["detail"] == "Отделение не найдено"

        # Ошибка при обновлении несуществующего ID
        bad_put = await ac.put("/departments/9999", json=update_data)
        assert bad_put.status_code == 404
        assert bad_put.json()["detail"] == "Отделение не найдено"

        # --- 6. DELETE (Удаление) ---
        # Покрывает метод delete_department
        del_res = await ac.delete(f"/departments/{dep_id}")
        assert del_res.status_code == 200

        # Проверка удаления (повторный GET должен вернуть 404)
        after_del = await ac.get(f"/departments/{dep_id}")
        assert after_del.status_code == 404

        response = await ac.delete("/departments/99999")
        assert response.status_code == 404
