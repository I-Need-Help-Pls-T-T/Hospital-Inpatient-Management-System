import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from datetime import datetime, timedelta

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_admission_teams_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА ---
        # 1. Создаем пациента и госпитализацию
        patient = await ac.post("/patients/", json={
            "full_name": "Сидоров Сидор",
            "birth_date": "1995-05-05",
            "gender": "Мужской"
        })
        p_id = patient.json()["id"]

        hosp = await ac.post("/hospitalizations/", json={
            "patient_id": p_id,
            "status": "Активна"
        })
        hosp_id = hosp.json()["id"]

        # 2. Создаем сотрудника
        staff = await ac.post("/staff/", json={
            "full_name": "Медсестра Петрова",
            "phone": "03"
        })
        s_id = staff.json()["id"]

        # --- 1. POST (Создание записи о бригаде) ---
        begin = datetime.now()
        end = begin + timedelta(hours=8)

        team_data = {
            "hospitalization_id": hosp_id,
            "staff_id": s_id,
            "begin_time": begin.isoformat(),
            "end_time": end.isoformat(),
            "role": "Лечащий врач"
        }

        create_res = await ac.post("/admission_teams/", json=team_data)
        assert create_res.status_code == 200
        team_id = create_res.json()["id"]
        assert create_res.json()["role"] == "Лечащий врач"

        # --- 2. GET List (Получение списка) ---
        list_res = await ac.get("/admission_teams/")
        assert list_res.status_code == 200
        assert any(t["id"] == team_id for t in list_res.json())

        # --- 3. GET One (Получение по ID) ---
        get_one = await ac.get(f"/admission_teams/{team_id}")
        assert get_one.status_code == 200
        assert get_one.json()["staff_id"] == s_id

        # --- 4. PUT (Обновление роли) ---
        update_data = team_data.copy()
        update_data["role"] = "Заведующий отделением"
        put_res = await ac.put(f"/admission_teams/{team_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["role"] == "Заведующий отделением"

        # --- 5. ТЕСТ ВАЛИДАЦИИ ДАТ ---
        invalid_dates = team_data.copy()
        invalid_dates["begin_time"] = end.isoformat()
        invalid_dates["end_time"] = begin.isoformat() # Конец раньше начала

        bad_val = await ac.post("/admission_teams/", json=invalid_dates)
        assert bad_val.status_code == 422
        assert "Дата отмены не может быть раньше даты назначения" in bad_val.text

        # --- 6. ТЕСТЫ ОШИБОК 404 ---
        # Проверка сообщений, указанных в вашем роутере
        bad_get = await ac.get("/admission_teams/9999")
        assert bad_get.status_code == 404
        assert bad_get.json()["detail"] == "Такой медиццинской бригады не было"

        bad_put = await ac.put("/admission_teams/9999", json=update_data)
        assert bad_put.status_code == 404
        assert bad_put.json()["detail"] == "Такой медицинской бригады не было"

        # --- 7. DELETE (Удаление) ---
        del_res = await ac.delete(f"/admission_teams/{team_id}")
        assert del_res.status_code == 200
        assert del_res.json()["message"] == "Медицинская бригада успешно удалена"

        # Проверка удаления несуществующей записи для покрытия 404 в delete
        bad_del = await ac.delete("/admission_teams/9999")
        assert bad_del.status_code == 404
        assert bad_del.json()["detail"] == "Медицинская бригада не найдена"
