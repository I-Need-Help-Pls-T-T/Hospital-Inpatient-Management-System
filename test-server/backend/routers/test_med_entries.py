import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_med_entries_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        # Админ (4) - для удаления
        admin_login = "med_admin_ent"
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Главврач", login=admin_login, password="1", access_level=3
            ))

        # Врач (2) - для создания и чтения
        doc_login = "med_doc_ent"
        if not db.query(models.Staff).filter(models.Staff.login == doc_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Врач", login=doc_login, password="1", access_level=2
            ))

        # Стажер (1) - НЕТ прав на мед. записи
        intern_login = "med_intern_ent"
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

        # Создаем пациента для тестов
        pat = await ac.post("/api/patients/", json={"full_name": "Пациент Х", "birth_date": "1990-01-01", "gender": "Мужской"}, headers=admin_headers)
        patient_id = pat.json()["id"]

        entry_payload = {
            "patient_id": patient_id,
            "description": "Первичный осмотр, жалоб нет."
        }

        # --- 2. ТЕСТЫ GET (Список) ---
        # 403: Стажер (1) не имеет доступа (строка 21)
        res_l_403 = await ac.get("/api/med_entries/", headers=intern_headers)
        assert res_l_403.status_code == 403

        # 200: Врач имеет доступ
        res_l_ok = await ac.get("/api/med_entries/", headers=doc_headers)
        assert res_l_ok.status_code == 200

        # --- 3. ТЕСТЫ POST (Создание) ---
        # 403: Стажер не может создавать записи (строка 47)
        res_p_403 = await ac.post("/api/med_entries/", json=entry_payload, headers=intern_headers)
        assert res_p_403.status_code == 403

        # 200: Врач создает запись
        res_p_ok = await ac.post("/api/med_entries/", json=entry_payload, headers=doc_headers)
        assert res_p_ok.status_code == 200
        entry_id = res_p_ok.json()["id"]

        # --- 4. ТЕСТЫ GET (ID) ---
        # 404: Запись не найдена (строка 37)
        res_g_404 = await ac.get("/api/med_entries/99999", headers=doc_headers)
        assert res_g_404.status_code == 404

        # --- 5. ТЕСТЫ PUT (Обновление) ---
        # 403: Недостаточно прав (строка 59)
        res_u_403 = await ac.put(f"/api/med_entries/{entry_id}", json=entry_payload, headers=intern_headers)
        assert res_u_403.status_code == 403

        # 404: Не найдена
        res_u_404 = await ac.put("/api/med_entries/99999", json=entry_payload, headers=doc_headers)
        assert res_u_404.status_code == 404

        # 200: Успех
        res_u_ok = await ac.put(f"/api/med_entries/{entry_id}",
                                json={"patient_id": patient_id, "description": "Обновлено"},
                                headers=doc_headers)
        assert res_u_ok.status_code == 200

        # --- 6. ТЕСТЫ DELETE (Удаление) ---
        # 403: Врач (2) не может удалять (строка 74)
        res_d_403 = await ac.delete(f"/api/med_entries/{entry_id}", headers=doc_headers)
        assert res_d_403.status_code == 403

        # 404: Не найдена
        res_d_404 = await ac.delete("/api/med_entries/99999", headers=admin_headers)
        assert res_d_404.status_code == 404

        # 200: Успех (Админ)
        res_d_ok = await ac.delete(f"/api/med_entries/{entry_id}", headers=admin_headers)
        assert res_d_ok.status_code == 200
