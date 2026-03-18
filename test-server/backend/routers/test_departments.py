import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_departments_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        # Админ (4) - имеет полные права
        admin_login = "dep_admin"
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Админ", login=admin_login, password="1", access_level=3
            ))

        # Врач (2) - может только читать
        doc_login = "dep_doc"
        if not db.query(models.Staff).filter(models.Staff.login == doc_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Врач", login=doc_login, password="1", access_level=2
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': admin_login})}"}
        doc_headers = {"Authorization": f"Bearer {create_access_token({'sub': doc_login})}"}

        # Данные для тестов
        dep_payload = {
            "name": "Кардиология",
            "phone": "103",
            "profile": "Сердечно-сосудистые",
            "category": "Высшая"
        }

        # --- 2. ТЕСТЫ GET (Список и ID) ---
        # 200: Врач видит список (строка 20)
        assert (await ac.get("/api/departments/", headers=doc_headers)).status_code == 200

        # 404: Отделение не найдено (строка 33)
        assert (await ac.get("/api/departments/9999", headers=doc_headers)).status_code == 404

        # --- 3. ТЕСТЫ POST (Создание) ---
        # 403: Врач не может создать отделение (строка 44)
        res_p_403 = await ac.post("/api/departments/", json=dep_payload, headers=doc_headers)
        assert res_p_403.status_code == 403

        # 200: Админ создает успешно
        res_p_ok = await ac.post("/api/departments/", json=dep_payload, headers=admin_headers)
        assert res_p_ok.status_code == 200
        dep_id = res_p_ok.json()["id"]

        # --- 4. ТЕСТЫ PUT (Обновление) ---
        # 403: Врач не может редактировать (строка 55)
        res_u_403 = await ac.put(f"/api/departments/{dep_id}", json=dep_payload, headers=doc_headers)
        assert res_u_403.status_code == 403

        # 404: Не найдено (строка 58)
        assert (await ac.put("/api/departments/9999", json=dep_payload, headers=admin_headers)).status_code == 404

        # 200: Успех
        res_u_ok = await ac.put(f"/api/departments/{dep_id}",
                                json={**dep_payload, "name": "Обновленная Кардиология"},
                                headers=admin_headers)
        assert res_u_ok.status_code == 200

        # --- 5. ТЕСТЫ DELETE (Удаление) ---
        # 403: Врач не может удалять (строка 69)
        assert (await ac.delete(f"/api/departments/{dep_id}", headers=doc_headers)).status_code == 403

        # 404: Не найдено (строка 72)
        assert (await ac.delete("/api/departments/9999", headers=admin_headers)).status_code == 404

        # 200: Успех (Админ)
        assert (await ac.delete(f"/api/departments/{dep_id}", headers=admin_headers)).status_code == 200
