import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models
from datetime import date, timedelta

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_medication_orders_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        # Админ (4)
        admin_login = "med_admin"
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Админ", login=admin_login, password="1", access_level=3
            ))
        # Врач (2)
        doc_login = "med_doc"
        if not db.query(models.Staff).filter(models.Staff.login == doc_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Врач", login=doc_login, password="1", access_level=2
            ))
        # Стажер (1) - НЕТ прав на назначения
        intern_login = "med_intern"
        if not db.query(models.Staff).filter(models.Staff.login == intern_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Стажер", login=intern_login, password="1", access_level=1
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': admin_login})}"}
        doc_headers = {"Authorization": f"Bearer {create_access_token({'sub': doc_login})}"}
        intern_headers = {"Authorization": f"Bearer {create_access_token({'sub': intern_login})}"}

        # --- ШАГ 2: ПОДГОТОВКА ЗАВИСИМОСТЕЙ ---
        # Назначение привязано к MedEntry (записи в истории)
        pat = await ac.post("/api/patients/", json={"full_name": "П", "birth_date": "1990-01-01", "gender": "Мужской"}, headers=admin_headers)
        pat_id = pat.json()["id"]

        entry = await ac.post("/api/med_entries/", json={"patient_id": pat_id, "description": "Осмотр"}, headers=admin_headers)
        entry_id = entry.json()["id"]

        order_payload = {
            "med_entry_id": entry_id,
            "name": "Аспирин",
            "dose": "100мг",
            "begin_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=5))
        }

        # --- 3. ТЕСТЫ GET (Список) ---
        # 403: Стажер не видит назначения
        assert (await ac.get("/api/medication_orders/", headers=intern_headers)).status_code == 403
        # 200: Врач видит
        assert (await ac.get("/api/medication_orders/", headers=doc_headers)).status_code == 200

        # --- 4. ТЕСТЫ POST (Создание) ---
        # 403: Стажер не может назначать
        assert (await ac.post("/api/medication_orders/", json=order_payload, headers=intern_headers)).status_code == 403
        # 200: Врач может
        res_ok = await ac.post("/api/medication_orders/", json=order_payload, headers=doc_headers)
        assert res_ok.status_code == 200
        order_id = res_ok.json()["id"]

        # --- 5. ТЕСТЫ GET (ID) ---
        # 404: Не найдено
        assert (await ac.get("/api/medication_orders/9999", headers=doc_headers)).status_code == 404
        # 200: Успех
        assert (await ac.get(f"/api/medication_orders/{order_id}", headers=doc_headers)).status_code == 200

        # --- 6. ТЕСТЫ PUT (Обновление) ---
        # 403: Уровень 1 запрещен
        assert (await ac.put(f"/api/medication_orders/{order_id}", json=order_payload, headers=intern_headers)).status_code == 403
        # 404: Не найден
        assert (await ac.put("/api/medication_orders/9999", json=order_payload, headers=doc_headers)).status_code == 404
        # 200: Успех
        res_upd = await ac.put(f"/api/medication_orders/{order_id}", json={**order_payload, "dose": "200мг"}, headers=doc_headers)
        assert res_upd.status_code == 200

        # --- 7. ТЕСТЫ DELETE (Удаление) ---
        # 403: Врач (2) не может удалять, только Админ (4)
        assert (await ac.delete(f"/api/medication_orders/{order_id}", headers=doc_headers)).status_code == 403
        # 404: Не найден
        assert (await ac.delete("/api/medication_orders/9999", headers=admin_headers)).status_code == 404
        # 200: Успех
        assert (await ac.delete(f"/api/medication_orders/{order_id}", headers=admin_headers)).status_code == 200
