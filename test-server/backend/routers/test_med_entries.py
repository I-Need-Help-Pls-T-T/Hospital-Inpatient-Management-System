import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from datetime import datetime

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_med_entries_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА: Создаем пациента и сотрудника ---
        patient = await ac.post("/patients/", json={
            "full_name": "Иванов Иван Иванович",
            "birth_date": "1975-03-20",
            "gender": "Мужской"
        })
        patient_id = patient.json()["id"]

        staff = await ac.post("/staff/", json={
            "full_name": "Др. Смирнова",
            "phone": "103"
        })
        staff_id = staff.json()["id"]

        # --- 1. POST (Создание записи) ---
        # Покрывает метод create_med_entry
        entry_data = {
            "patient_id": patient_id,
            "staff_id": staff_id,
            "description": "Жалобы на головную боль. Температура 36.6."
        }
        create_res = await ac.post("/med_entries/", json=entry_data)
        assert create_res.status_code == 200
        entry_id = create_res.json()["id"]
        assert "головную боль" in create_res.json()["description"]

        # --- 2. GET List (Список всех записей) ---
        # Покрывает метод read_med_entries
        list_res = await ac.get("/med_entries/")
        assert list_res.status_code == 200
        assert any(e["id"] == entry_id for e in list_res.json())

        # --- 3. GET One (Получение по ID) ---
        # Покрывает метод read_med_entry
        get_one = await ac.get(f"/med_entries/{entry_id}")
        assert get_one.status_code == 200
        assert get_one.json()["staff_id"] == staff_id

        # --- 4. PUT (Обновление записи) ---
        # Покрывает метод update_med_entry
        update_data = {
            "patient_id": patient_id,
            "staff_id": staff_id,
            "description": "Диагноз: Мигрень. Рекомендован покой."
        }
        put_res = await ac.put(f"/med_entries/{entry_id}", json=update_data)
        assert put_res.status_code == 200
        assert "Мигрень" in put_res.json()["description"]

        # --- 5. ТЕСТЫ ОШИБОК 404 (Закрываем Missing lines) ---
        # Ошибка в GET
        bad_get = await ac.get("/med_entries/99999")
        assert bad_get.status_code == 404
        assert bad_get.json()["detail"] == "Запись в истории болезни не найдена"

        # Ошибка в PUT
        bad_put = await ac.put("/med_entries/99999", json=update_data)
        assert bad_put.status_code == 404

        # --- 6. DELETE (Удаление записи) ---
        # Покрывает метод delete_med_entry
        del_res = await ac.delete(f"/med_entries/{entry_id}")
        assert del_res.status_code == 200
        assert del_res.json()["message"] == "Запись в истории болезни успешно удалена"

        # Повторное удаление (404)
        bad_del = await ac.delete(f"/med_entries/{entry_id}")
        assert bad_del.status_code == 404
