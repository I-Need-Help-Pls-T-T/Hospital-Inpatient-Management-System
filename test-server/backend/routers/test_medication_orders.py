import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from datetime import date, timedelta

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_medication_orders_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА ---
        # 1. Создаем пациента
        patient = await ac.post("/patients/", json={
            "full_name": "Тестовый Пациент",
            "birth_date": "1990-01-01",
            "gender": "Мужской"
        })
        p_id = patient.json()["id"]

        # 2. Создаем сотрудника (врача)
        staff = await ac.post("/staff/", json={
            "full_name": "Тестовый Врач",
            "phone": "911"
        })
        s_id = staff.json()["id"]

        # 3. Создаем запись в истории болезни (к ней привязываются назначения)
        med_entry = await ac.post("/med_entries/", json={
            "patient_id": p_id,
            "staff_id": s_id,
            "description": "Первичный осмотр"
        })
        e_id = med_entry.json()["id"]

        # --- 1. POST (Создание назначения) ---
        today = date.today()
        next_week = today + timedelta(days=7)

        order_data = {
            "med_entry_id": e_id,
            "name": "Аспирин",
            "dose": "500 мг",
            "rules_taking": "1 таблетка после еды",
            "begin_date": str(today),
            "end_date": str(next_week)
        }
        create_res = await ac.post("/medication_orders/", json=order_data)
        assert create_res.status_code == 200
        order_id = create_res.json()["id"]
        assert create_res.json()["name"] == "Аспирин"

        # --- 2. GET List (Получение списка) ---
        list_res = await ac.get("/medication_orders/")
        assert list_res.status_code == 200
        assert any(o["id"] == order_id for o in list_res.json())

        # --- 3. GET One (Получение по ID) ---
        get_one = await ac.get(f"/medication_orders/{order_id}")
        assert get_one.status_code == 200
        assert get_one.json()["dose"] == "500 мг"

        # --- 4. PUT (Обновление) ---
        update_data = order_data.copy()
        update_data["dose"] = "1000 мг"
        put_res = await ac.put(f"/medication_orders/{order_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["dose"] == "1000 мг"

        # --- 5. ТЕСТ ВАЛИДАЦИИ ДАТ ---
        # Проверяем @model_validator(mode='after') check_dates
        invalid_dates = order_data.copy()
        invalid_dates["begin_date"] = str(next_week)
        invalid_dates["end_date"] = str(today) # Конец раньше начала

        bad_res = await ac.post("/medication_orders/", json=invalid_dates)
        assert bad_res.status_code == 422 # Unprocessable Entity
        assert "Дата отмены не может быть раньше даты назначения" in bad_res.text

        # --- 6. ТЕСТЫ ОШИБОК 404 ---
        assert (await ac.get("/medication_orders/9999")).status_code == 404
        assert (await ac.put("/medication_orders/9999", json=order_data)).status_code == 404
        assert (await ac.delete("/medication_orders/9999")).status_code == 404

        # --- 7. DELETE (Удаление) ---
        del_res = await ac.delete(f"/medication_orders/{order_id}")
        assert del_res.status_code == 200
        assert del_res.json()["message"] == "Лист назначения успешно удален"

        # Проверка удаления
        final_check = await ac.get(f"/medication_orders/{order_id}")
        assert final_check.status_code == 404
