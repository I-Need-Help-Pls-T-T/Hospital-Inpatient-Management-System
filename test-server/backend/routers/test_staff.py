import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_staff_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА: Создаем кабинет (зависимость) ---
        # Сначала нужно отделение для кабинета
        dep_res = await ac.post("/departments/", json={"name": "Тестовое отделение"})
        dep_id = dep_res.json()["id"]

        room_res = await ac.post("/rooms/", json={
            "number": 202,
            "type": "Ординаторская",
            "department_id": dep_id
        })
        room_id = room_res.json()["id"]

        # --- 1. POST (Создание сотрудника) ---
        # Покрывает метод create_staff
        staff_data = {
            "full_name": "Петров Петр Петрович",
            "phone": "8-800-555-3535",
            "email": "petrov@hospital.ru",
            "condition": "Активен",
            "room_id": room_id
        }
        create_res = await ac.post("/staff/", json=staff_data)
        assert create_res.status_code == 200
        staff_id = create_res.json()["id"]
        assert create_res.json()["full_name"] == "Петров Петр Петрович"

        # --- 2. GET List (Список сотрудников) ---
        # Покрывает метод read_staffs
        list_res = await ac.get("/staff/")
        assert list_res.status_code == 200
        assert any(s["id"] == staff_id for s in list_res.json())

        # --- 3. GET One (Получение по ID) ---
        # Покрывает метод read_staff
        get_one = await ac.get(f"/staff/{staff_id}")
        assert get_one.status_code == 200
        assert get_one.json()["email"] == "petrov@hospital.ru"

        # --- 4. PUT (Обновление данных сотрудника) ---
        # Покрывает метод update_staff
        update_data = staff_data.copy()
        update_data["condition"] = "Отпуск"
        update_data["full_name"] = "Петров Петр (в отпуске)"

        put_res = await ac.put(f"/staff/{staff_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["condition"] == "Отпуск"

        # --- 5. ТЕСТЫ ОШИБОК 404 (Закрываем Missing lines) ---
        # Ошибка в GET
        bad_get = await ac.get("/staff/99999")
        assert bad_get.status_code == 404
        assert bad_get.json()["detail"] == "Сотрудник не найден"

        # Ошибка в PUT
        bad_put = await ac.put("/staff/99999", json=update_data)
        assert bad_put.status_code == 404

        # --- 6. DELETE (Удаление сотрудника) ---
        # Покрывает метод delete_staff
        del_res = await ac.delete(f"/staff/{staff_id}")
        assert del_res.status_code == 200
        assert del_res.json()["message"] == "Сотрудник успешно удален"

        # Повторный DELETE (404)
        bad_del = await ac.delete(f"/staff/{staff_id}")
        assert bad_del.status_code == 404
