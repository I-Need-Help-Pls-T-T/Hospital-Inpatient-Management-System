import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_patients_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- 1. POST (Создание пациента) ---
        patient_data = {
            "full_name": "Сидоров Сидор Сидорович",
            "birth_date": "1990-05-15",
            "gender": "Мужской",
            "address": "ул. Пушкина, д. Колотушкина",
            "passport": "1234 567890",
            "phone": "8-999-000-11-22"
        }
        create_res = await ac.post("/patients/", json=patient_data)
        assert create_res.status_code == 200
        patient_id = create_res.json()["id"]
        assert create_res.json()["full_name"] == "Сидоров Сидор Сидорович"

        # --- 2. GET List (Список пациентов) ---
        list_res = await ac.get("/patients/")
        assert list_res.status_code == 200
        assert len(list_res.json()) > 0
        assert any(p["id"] == patient_id for p in list_res.json())

        # --- 3. GET One (Получение по ID) ---
        get_one = await ac.get(f"/patients/{patient_id}")
        assert get_one.status_code == 200
        assert get_one.json()["passport"] == "1234 567890"

        # --- 4. PUT (Обновление данных) ---
        update_data = patient_data.copy()
        update_data["full_name"] = "Сидоров Сидор (изменено)"
        update_data["address"] = "Новый адрес"

        put_res = await ac.put(f"/patients/{patient_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["full_name"] == "Сидоров Сидор (изменено)"

        # --- 5. ТЕСТЫ ОШИБОК 404 ---
        # Ошибка в GET
        bad_get = await ac.get("/patients/99999")
        assert bad_get.status_code == 404
        assert bad_get.json()["detail"] == "Пациент не найден"

        # Ошибка в PUT
        bad_put = await ac.put("/patients/99999", json=update_data)
        assert bad_put.status_code == 404

        # --- 6. DELETE (Удаление) ---
        del_res = await ac.delete(f"/patients/{patient_id}")
        assert del_res.status_code == 200

        # Повторный DELETE (404)
        bad_del = await ac.delete(f"/patients/{patient_id}")
        assert bad_del.status_code == 404
