import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models
from datetime import date, timedelta

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_staff_roles_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        admin_login = "sr_admin" # Уровень 4
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="HR Директор", login=admin_login, password="1", access_level=3
            ))

        hr_login = "sr_hr" # Уровень 3
        if not db.query(models.Staff).filter(models.Staff.login == hr_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="HR Менеджер", login=hr_login, password="1", access_level=2
            ))

        doc_login = "sr_doc" # Уровень 1
        if not db.query(models.Staff).filter(models.Staff.login == doc_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Врач", login=doc_login, password="1", access_level=1
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # Токены
        admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': admin_login})}"}
        hr_headers = {"Authorization": f"Bearer {create_access_token({'sub': hr_login})}"}
        doc_headers = {"Authorization": f"Bearer {create_access_token({'sub': doc_login})}"}

        # --- 2. ПОДГОТОВКА ДАННЫХ (Сотрудник и Должность) ---
        pos_res = await ac.post("/api/positions/", json={"name": "Хирург-тест"}, headers=admin_headers)
        pos_id = pos_res.json()["id"]

        staff_res = await ac.post("/api/staff/", json={
            "full_name": "Тестовый Работник", "login": "test_work", "password": "1", "access_level": 1
        }, headers=admin_headers)
        staff_id = staff_res.json()["id"]

        today = str(date.today())

        # --- 3. ТЕСТЫ СОЗДАНИЯ (POST) ---
        role_payload = {
            "staff_id": staff_id,
            "position_id": pos_id,
            "appointment_date": today
        }

        # Ошибка 403: Врач (1) не может назначать роли
        res_p_403 = await ac.post("/api/staff_roles/", json=role_payload, headers=doc_headers)
        assert res_p_403.status_code == 403

        # Успех: admin (3) может
        res_p_ok = await ac.post("/api/staff_roles/", json=role_payload, headers=admin_headers)
        assert res_p_ok.status_code == 200

        # --- 4. ТЕСТЫ ЧТЕНИЯ (GET) ---
        # Список
        res_list = await ac.get("/api/staff_roles/", headers=doc_headers)
        assert res_list.status_code == 200

        # Детально (с параметрами)
        params = {"staff_id": staff_id, "position_id": pos_id, "appointment_date": today}
        res_det = await ac.get("/api/staff_roles/detail", params=params, headers=doc_headers)
        assert res_det.status_code == 200

        # Ошибка 404
        bad_params = {"staff_id": 999, "position_id": pos_id, "appointment_date": today}
        res_det_404 = await ac.get("/api/staff_roles/detail", params=bad_params, headers=doc_headers)
        assert res_det_404.status_code == 404

        # --- 5. ТЕСТЫ ОБНОВЛЕНИЯ (PUT) ---
        update_json = {"staff_id": staff_id, "position_id": pos_id, "appointment_date": today, "end_date": today}

        # Ошибка 404
        res_up_404 = await ac.put("/api/staff_roles/update", params=bad_params, json=update_json, headers=admin_headers)
        assert res_up_404.status_code == 404

        # Успех
        res_up_ok = await ac.put("/api/staff_roles/update", params=params, json=update_json, headers=admin_headers)
        assert res_up_ok.status_code == 200

        # --- 6. ТЕСТЫ УДАЛЕНИЯ (DELETE) ---
        # Ошибка 403: HR (3) не может удалять, нужен Админ (4)
        res_d_403 = await ac.delete("/api/staff_roles/delete", params=params, headers=hr_headers)
        assert res_d_403.status_code == 403

        # Успех: Админ (4)
        res_d_ok = await ac.delete("/api/staff_roles/delete", params=params, headers=admin_headers)
        assert res_d_ok.status_code == 200

        # Ошибка 404 при повторном удалении
        res_d_404 = await ac.delete("/api/staff_roles/delete", params=params, headers=admin_headers)
        assert res_d_404.status_code == 404
