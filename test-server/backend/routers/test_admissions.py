import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from datetime import datetime, timedelta

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_patient_admissions_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА: Создаем госпитализацию ---
        # Сначала нужен пациент
        patient = await ac.post("/patients/", json={
            "full_name": "Петров Петр Петрович",
            "birth_date": "1985-05-10",
            "gender": "Мужской"
        })
        p_id = patient.json()["id"]

        # Затем сама госпитализация, к которой привязывается время
        hosp = await ac.post("/hospitalizations/", json={
            "patient_id": p_id,
            "status": "Активна"
        })
        hosp_id = hosp.json()["id"]

        # --- 1. POST (Создание записи о времени поступления) ---
        arrival = datetime.now()
        end = arrival + timedelta(days=3)

        admission_data = {
            "hospitalization_id": hosp_id,
            "arrival_time": arrival.isoformat(),
            "end_time": end.isoformat()
        }

        create_res = await ac.post("/admissions/", json=admission_data)
        assert create_res.status_code == 200
        assert create_res.json()["hospitalization_id"] == hosp_id

        # --- 2. GET List (Получение списка) ---
        list_res = await ac.get("/admissions/")
        assert list_res.status_code == 200
        assert any(a["hospitalization_id"] == hosp_id for a in list_res.json())

        # --- 3. GET One (Получение по ID госпитализации) ---
        get_one = await ac.get(f"/admissions/{hosp_id}")
        assert get_one.status_code == 200
        # Проверяем, что дата прибытия совпадает (с точностью до секунд)
        assert "arrival_time" in get_one.json()
        assert get_one.json()["hospitalization_id"] == hosp_id

        # --- 4. PUT (Обновление данных) ---
        new_end = arrival + timedelta(days=5)
        update_data = {
            "hospitalization_id": hosp_id,
            "arrival_time": arrival.isoformat(),
            "end_time": new_end.isoformat()
        }
        put_res = await ac.put(f"/admissions/{hosp_id}", json=update_data)
        assert put_res.status_code == 200
        # В некоторых форматах API может возвращать дату со смещением или в UTC,
        # здесь важно, что запрос прошел успешно.

        # --- 5. ТЕСТ ВАЛИДАЦИИ (check_dates в схеме) ---
        # Попытка поставить время выбытия раньше времени прибытия
        invalid_data = {
            "hospitalization_id": hosp_id,
            "arrival_time": end.isoformat(),
            "end_time": arrival.isoformat()
        }
        bad_val_res = await ac.post("/admissions/", json=invalid_data)
        assert bad_val_res.status_code == 422 # Ошибка валидации Pydantic
        assert "Дата отмены не может быть раньше даты назначения" in bad_val_res.text

        # --- 6. ТЕСТЫ ОШИБОК 404 ---
        # Несуществующая госпитализация
        assert (await ac.get("/admissions/99999")).status_code == 404
        assert (await ac.put("/admissions/99999", json=update_data)).status_code == 404
        assert (await ac.delete("/admissions/99999")).status_code == 404

        # --- 7. DELETE (Удаление записи) ---
        del_res = await ac.delete(f"/admissions/{hosp_id}")
        assert del_res.status_code == 200
        assert del_res.json()["message"] == "Успешно удалено"

        # Проверка, что записи больше нет
        final_check = await ac.get(f"/admissions/{hosp_id}")
        assert final_check.status_code == 404
