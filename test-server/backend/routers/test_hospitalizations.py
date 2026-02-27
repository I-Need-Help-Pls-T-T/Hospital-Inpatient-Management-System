import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from datetime import date

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_hospitalizations_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА ЗАВИСИМОСТЕЙ ---
        # 1. Отделение -> Помещение -> Палата
        dep = await ac.post("/departments/", json={"name": "Терапия"})
        dep_id = dep.json()["id"]

        room = await ac.post("/rooms/", json={"number": 301, "department_id": dep_id})
        room_id = room.json()["id"]

        ward = await ac.post("/wards/", json={"name": "Палата №1", "room_id": room_id})
        ward_id = ward.json()["id"]

        # 2. Пациент
        patient = await ac.post("/patients/", json={
            "full_name": "Тестовый Пациент",
            "birth_date": "1985-10-10",
            "gender": "Мужской"
        })
        patient_id = patient.json()["id"]

        # --- 1. POST (Создание госпитализации) ---
        hosp_data = {
            "patient_id": patient_id,
            "ward_id": ward_id,
            "care_type": "Стационар",
            "outcome": "В процессе",
            "treatment_summary": "Начальное обследование"
        }
        create_res = await ac.post("/hospitalizations/", json=hosp_data)
        assert create_res.status_code == 200
        hosp_id = create_res.json()["id"]

        # --- 2. GET List (Список) ---
        list_res = await ac.get("/hospitalizations/")
        assert list_res.status_code == 200
        assert any(h["id"] == hosp_id for h in list_res.json())

        # --- 3. GET One (Детально) ---
        get_one = await ac.get(f"/hospitalizations/{hosp_id}")
        assert get_one.status_code == 200
        assert get_one.json()["care_type"] == "Стационар"

        # --- 4. PUT (Обновление) ---
        update_data = hosp_data.copy()
        update_data["outcome"] = "Выписан"
        update_data["treatment_summary"] = "Курс лечения завершен успешно"

        put_res = await ac.put(f"/hospitalizations/{hosp_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["outcome"] == "Выписан"

        # --- 5. ТЕСТЫ ОШИБОК 404 ---
        # Несуществующий ID в GET
        assert (await ac.get("/hospitalizations/999")).status_code == 404

        # Несуществующий ID в PUT
        assert (await ac.put("/hospitalizations/999", json=update_data)).status_code == 404

        # --- 6. DELETE (Удаление) ---
        del_res = await ac.delete(f"/hospitalizations/{hosp_id}")
        assert del_res.status_code == 200

        # Повторное удаление (404)
        assert (await ac.delete(f"/hospitalizations/{hosp_id}")).status_code == 404
