import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_patients_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА БД ---
    db = SessionLocal()
    try:
        # Админ (4) - может удалять
        admin_login = "pat_admin"
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Главный Врач", login=admin_login, password="1", access_level=3
            ))

        # Регистратор (2) - может создавать и править, но не удалять
        staff_login = "pat_staff"
        if not db.query(models.Staff).filter(models.Staff.login == staff_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Регистратор", login=staff_login, password="1", access_level=2
            ))

        # Стажер (1) - может только смотреть
        user_login = "pat_user"
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

        patient_payload = {
            "full_name": "Тестовый Пациент",
            "birth_date": "1985-10-10",
            "gender": "Мужской",
            "passport": "0000 111222"
        }

        # --- 2. ТЕСТЫ GET (Список) ---
        # Успешно (1+)
        res = await ac.get("/api/patients/", headers=user_headers)
        assert res.status_code == 200

        # --- 3. ТЕСТЫ POST (Создание) ---
        # 403: Уровень 1 не может создавать (строка 47)
        res_p_403 = await ac.post("/api/patients/", json=patient_payload, headers=user_headers)
        assert res_p_403.status_code == 403

        # 200: Успех для регистратора
        res_p_ok = await ac.post("/api/patients/", json=patient_payload, headers=staff_headers)
        assert res_p_ok.status_code == 200
        patient_id = res_p_ok.json()["id"]

        # --- 4. ТЕСТЫ GET (ID) ---
        # 404: Не найден (строка 37)
        res_g_404 = await ac.get("/api/patients/99999", headers=user_headers)
        assert res_g_404.status_code == 404

        # 200: Успех
        res_g_ok = await ac.get(f"/api/patients/{patient_id}", headers=user_headers)
        assert res_g_ok.status_code == 200

        # --- 5. ТЕСТЫ PUT (Обновление) ---
        # 403: Уровень 1 не может менять (строка 59)
        res_u_403 = await ac.put(f"/api/patients/{patient_id}", json=patient_payload, headers=user_headers)
        assert res_u_403.status_code == 403

        # 404: Пациент не найден
        res_u_404 = await ac.put("/api/patients/99999", json=patient_payload, headers=staff_headers)
        assert res_u_404.status_code == 404

        # 200: Успех
        res_u_ok = await ac.put(f"/api/patients/{patient_id}",
                                json={**patient_payload, "full_name": "Обновлен"},
                                headers=staff_headers)
        assert res_u_ok.status_code == 200

        # --- 6. ТЕСТЫ DELETE (Удаление) ---
        # 403: Регистратор (уровень 2) не может удалять (строка 74)
        res_d_403 = await ac.delete(f"/api/patients/{patient_id}", headers=staff_headers)
        assert res_d_403.status_code == 403

        # 404: Не найден
        res_d_404 = await ac.delete("/api/patients/99999", headers=admin_headers)
        assert res_d_404.status_code == 404

        # 200: Успех админом
        res_d_ok = await ac.delete(f"/api/patients/{patient_id}", headers=admin_headers)
        assert res_d_ok.status_code == 200
