import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models
from datetime import date

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_payments_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        # Админ (4) - может редактировать и удалять
        admin_login = "pay_admin"
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Бухгалтер-Админ", login=admin_login, password="1", access_level=3
            ))

        # Кассир (3) - может смотреть и создавать
        staff_login = "pay_staff"
        if not db.query(models.Staff).filter(models.Staff.login == staff_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Кассир", login=staff_login, password="1", access_level=2
            ))

        # Врач (1) - доступ запрещен
        doc_login = "pay_doc"
        if not db.query(models.Staff).filter(models.Staff.login == doc_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Врач", login=doc_login, password="1", access_level=1
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': admin_login})}"}
        staff_headers = {"Authorization": f"Bearer {create_access_token({'sub': staff_login})}"}
        doc_headers = {"Authorization": f"Bearer {create_access_token({'sub': doc_login})}"}

        # --- 2. ПОДГОТОВКА ЗАВИСИМОСТЕЙ ---
        # Пациент и госпитализация нужны для создания платежа
        pat = await ac.post("/api/patients/", json={
            "full_name": "Иванов И.И.", "birth_date": "1990-01-01", "gender": "Мужской"
        }, headers=admin_headers)
        pat_id = pat.json()["id"]

        hosp = await ac.post("/api/hospitalizations/", json={
            "patient_id": pat_id, "treatment_summary": "Плановое"
        }, headers=admin_headers)
        hosp_id = hosp.json()["id"]

        payment_payload = {
            "hospitalization_id": hosp_id,
            "amount": 1500.0,
            "method": "Карта",
            "payment_date": str(date.today())
        }

        # --- 3. ТЕСТ GET (Список) ---
        # Строка 21: Доступ запрещен для уровня < 3
        res_list_403 = await ac.get("/api/payments/", headers=doc_headers)
        assert res_list_403.status_code == 403

        # Успешный список
        res_list_ok = await ac.get("/api/payments/", headers=admin_headers)
        assert res_list_ok.status_code == 200

        # --- 4. ТЕСТ POST (Создание) ---
        # Строка 37: Доступ запрещен для уровня < 3
        res_create_403 = await ac.post("/api/payments/", json=payment_payload, headers=doc_headers)
        assert res_create_403.status_code == 403

        # Успешное создание
        res_create_ok = await ac.post("/api/payments/", json=payment_payload, headers=admin_headers)
        assert res_create_ok.status_code == 200
        pay_id = res_create_ok.json()["id"]

        # --- 5. ТЕСТ GET (ID) ---
        # Строка 32: Ошибка 403 при получении по ID
        res_get_403 = await ac.get(f"/api/payments/{pay_id}", headers=doc_headers)
        assert res_get_403.status_code == 403

        # Строка 37 (в контексте get): 404 если не найден
        res_get_404 = await ac.get("/api/payments/99999", headers=admin_headers)
        assert res_get_404.status_code == 404

        # Успешное получение
        res_get_ok = await ac.get(f"/api/payments/{pay_id}", headers=admin_headers)
        assert res_get_ok.status_code == 200

        # --- 6. ТЕСТ PUT (Обновление) ---
        # Строка 63: 403 если уровень < 4 (кассир не может менять)
        res_put_403 = await ac.put(f"/api/payments/{pay_id}", json=payment_payload, headers=staff_headers)
        assert res_put_403.status_code == 403

        # Ошибка 404 (строка 68 в коде роутера)
        res_put_404 = await ac.put("/api/payments/99999", json=payment_payload, headers=admin_headers)
        assert res_put_404.status_code == 404

        # Успешное обновление
        res_put_ok = await ac.put(f"/api/payments/{pay_id}",
                                   json={**payment_payload, "amount": 5000},
                                   headers=admin_headers)
        assert res_put_ok.status_code == 200
        assert res_put_ok.json()["amount"] == 5000

        # --- 7. ТЕСТ DELETE (Удаление) ---
        # Строка 75: 403 если уровень < 4
        res_del_403 = await ac.delete(f"/api/payments/{pay_id}", headers=staff_headers)
        assert res_del_403.status_code == 403

        # Ошибка 404
        res_del_404 = await ac.delete("/api/payments/99999", headers=admin_headers)
        assert res_del_404.status_code == 404

        # Успешное удаление (строка 80+)
        res_del_ok = await ac.delete(f"/api/payments/{pay_id}", headers=admin_headers)
        assert res_del_ok.status_code == 200
