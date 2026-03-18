import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models
from datetime import date

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_hospitalizations_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        admin_login = "hosp_admin"
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Админ", login=admin_login, password="1", access_level=3
            ))

        staff_login = "hosp_staff" # Регистратор (2)
        if not db.query(models.Staff).filter(models.Staff.login == staff_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Регистратор", login=staff_login, password="1", access_level=2
            ))

        user_login = "hosp_user" # Стажер (1)
        if not db.query(models.Staff).filter(models.Staff.login == user_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Стажер", login=user_login, password="1", access_level=1
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': admin_login})}"}
        staff_headers = {"Authorization": f"Bearer {create_access_token({'sub': staff_login})}"}
        user_headers = {"Authorization": f"Bearer {create_access_token({'sub': user_login})}"}

        # Подготовка данных (Отделение -> Палата -> Пациент)
        dep = await ac.post("/api/departments/", json={"name": "Терапия"}, headers=admin_headers)
        dep_id = dep.json()["id"]
        room = await ac.post("/api/rooms/", json={"number": 101, "department_id": dep_id}, headers=admin_headers)
        room_id = room.json()["id"]
        ward = await ac.post("/api/wards/", json={"room_id": room_id, "w_place": 1, "m_place": 1}, headers=admin_headers)
        ward_id = ward.json()["id"]
        pat = await ac.post("/api/patients/", json={"full_name": "Иванов", "birth_date": "1990-01-01", "gender": "Мужской"}, headers=admin_headers)
        patient_id = pat.json()["id"]

        hosp_payload = {
            "patient_id": patient_id,
            "ward_id": ward_id,
            "admission_date": str(date.today()),
            "care_type": "Стационар"
        }

        # --- 2. ТЕСТЫ GET (Список) ---
        # 200: Стажер может видеть список (строка 23)
        assert (await ac.get("/api/hospitalizations/", headers=user_headers)).status_code == 200

        # --- 3. ТЕСТЫ POST (Создание) ---
        # 403: Стажер (1) не может оформлять (строка 48)
        assert (await ac.post("/api/hospitalizations/", json=hosp_payload, headers=user_headers)).status_code == 403

        # 200: Регистратор (2) может
        res_p_ok = await ac.post("/api/hospitalizations/", json=hosp_payload, headers=staff_headers)
        assert res_p_ok.status_code == 200
        hosp_id = res_p_ok.json()["id"]

        # --- 4. ТЕСТЫ GET (ID) ---
        # 404: Не найдена (строка 38)
        assert (await ac.get("/api/hospitalizations/9999", headers=user_headers)).status_code == 404

        # --- 5. ТЕСТЫ PUT (Обновление) ---
        # 403: Уровень 1 не может менять (строка 59)
        assert (await ac.put(f"/api/hospitalizations/{hosp_id}", json=hosp_payload, headers=user_headers)).status_code == 403

        # 404: Не найдена
        assert (await ac.put("/api/hospitalizations/9999", json=hosp_payload, headers=staff_headers)).status_code == 404

        # 200: Успех
        res_u_ok = await ac.put(f"/api/hospitalizations/{hosp_id}",
                                json={**hosp_payload, "outcome": "Выписан"},
                                headers=staff_headers)
        assert res_u_ok.status_code == 200

        # --- 6. ТЕСТЫ DELETE (Удаление) ---
        # 403: Регистратор (2) не может удалять (строка 74)
        assert (await ac.delete(f"/api/hospitalizations/{hosp_id}", headers=staff_headers)).status_code == 403

        # 404: Не найдена
        assert (await ac.delete("/api/hospitalizations/9999", headers=admin_headers)).status_code == 404

        # 200: Успех (Админ)
        assert (await ac.delete(f"/api/hospitalizations/{hosp_id}", headers=admin_headers)).status_code == 200
