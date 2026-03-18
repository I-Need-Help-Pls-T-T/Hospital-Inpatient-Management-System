import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models
from datetime import datetime, timedelta

BASE_URL = "http://testserver/api"

@pytest.mark.asyncio
async def test_admission_teams_full_100_percent():
    # --- 1. ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        # Создаем/обновляем пользователей с разными уровнями доступа
        for login, level in [("adm_adm", 3), ("doc_doc", 2), ("intern_1", 1)]:
            user = db.query(models.Staff).filter(models.Staff.login == login).first()
            if not user:
                crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                    full_name=login, login=login, password="1", access_level=level
                ))
            else:
                user.access_level = level
                db.add(user)
        db.commit()
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        # Заголовки авторизации
        adm_h = {"Authorization": f"Bearer {create_access_token({'sub': 'adm_adm'})}"}
        doc_h = {"Authorization": f"Bearer {create_access_token({'sub': 'doc_doc'})}"}
        int_h = {"Authorization": f"Bearer {create_access_token({'sub': 'intern_1'})}"}

        # --- 2. ПОДГОТОВКА ДАННЫХ ---
        # Пациент и госпитализация (нужны для внешних ключей)
        p_res = await ac.post("/patients/", json={"full_name": "Бригада Тест", "birth_date": "1990-01-01", "gender": "Мужской"}, headers=adm_h)
        p_id = p_res.json()["id"]
        h_res = await ac.post("/hospitalizations/", json={"patient_id": p_id, "status": "Активна"}, headers=adm_h)
        hosp_id = h_res.json()["id"]

        # Сотрудник для бригады
        s_res = await ac.post("/staff/", json={"full_name": "Врач Тест", "login": "t_doc", "password": "1", "access_level": 2}, headers=adm_h)
        staff_id = s_res.json()["id"]

        team_payload = {
            "hospitalization_id": hosp_id,
            "staff_id": staff_id,
            "begin_time": datetime.now().isoformat(),
            "role": "Хирург"
        }

        # --- 3. ТЕСТЫ ПРАВ ДОСТУПА (403 Forbidden) ---
        # Строка 32: Чтение списка интерном (нужен уровень 2+)
        res_32 = await ac.get("/admission_teams/", headers=int_h)
        assert res_32.status_code == 403

        # Строка 47: Создание интерном (нужен уровень 2+)
        res_47 = await ac.post("/admission_teams/", json=team_payload, headers=int_h)
        assert res_47.status_code == 403

        # --- 4. ТЕСТЫ СОЗДАНИЯ И ОШИБОК 404 ---
        # Успешное создание врачом
        res_ok = await ac.post("/admission_teams/", json=team_payload, headers=adm_h)
        assert res_ok.status_code == 200
        team_id = res_ok.json()["id"]

        # Строка 37: Чтение несуществующей записи
        res_37 = await ac.get("/admission_teams/99999", headers=doc_h)
        assert res_37.status_code == 404

        # --- 5. ТЕСТЫ ОБНОВЛЕНИЯ (PUT) ---
        update_data = {**team_payload, "role": "Ассистент"}

        # Строка 63: Врач пытается обновить (в роутере стоит уровень 4 для PUT)
        res_63 = await ac.put(f"/admission_teams/{team_id}", json=update_data, headers=doc_h)
        assert res_63.status_code == 403

        # Обновление несуществующей записи админом (404)
        res_put_404 = await ac.put("/admission_teams/99999", json=update_data, headers=adm_h)
        assert res_put_404.status_code == 404

        # Успешное обновление админом
        res_put_ok = await ac.put(f"/admission_teams/{team_id}", json=update_data, headers=adm_h)
        assert res_put_ok.status_code == 200

        # --- 6. ТЕСТЫ УДАЛЕНИЯ (DELETE) ---
        # Строка 78: Врач пытается удалить (нужен уровень 4)
        res_78 = await ac.delete(f"/admission_teams/{team_id}", headers=doc_h)
        assert res_78.status_code == 403

        # Удаление админом
        res_del_ok = await ac.delete(f"/admission_teams/{team_id}", headers=adm_h)
        assert res_del_ok.status_code == 200

        # Удаление уже удаленной записи (404)
        res_del_404 = await ac.delete(f"/admission_teams/{team_id}", headers=adm_h)
        assert res_del_404.status_code == 404
