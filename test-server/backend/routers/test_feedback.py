import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.database import SessionLocal
from backend import crud, schemas, models

@pytest.mark.asyncio
async def test_feedback_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        # Админ (уровень 3) - может читать и помечать как прочитанное
        admin_login = "fb_admin"
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Администратор FB", login=admin_login, password="1", access_level=3
            ))

        # Врач (уровень 2) - может только отправлять фидбэк
        doc_login = "fb_doc"
        if not db.query(models.Staff).filter(models.Staff.login == doc_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Врач FB", login=doc_login, password="1", access_level=2
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        # Получаем токены
        admin_auth = await ac.post("/api/auth/login", data={"username": admin_login, "password": "1"})
        admin_headers = {"Authorization": f"Bearer {admin_auth.json()['access_token']}"}

        doc_auth = await ac.post("/api/auth/login", data={"username": doc_login, "password": "1"})
        doc_headers = {"Authorization": f"Bearer {doc_auth.json()['access_token']}"}

        # --- ШАГ 2: СОЗДАНИЕ ОБРАЩЕНИЯ (POST) ---
        fb_payload = {
            "subject": "Тестовая ошибка",
            "description": "Не нажимается кнопка",
            "feedback_type": "Ошибка",
            "section": "Пациенты"
        }

        # Врач может создать обращение
        res_create = await ac.post("/api/feedback/", json=fb_payload, headers=doc_headers)
        assert res_create.status_code == 200
        fb_id = res_create.json()["id"]
        assert res_create.json()["subject"] == "Тестовая ошибка"

        # --- ШАГ 3: ПРОСМОТР СПИСКА (GET) ---
        # 403: Врач не может смотреть список всех фидбэков
        res_list_403 = await ac.get("/api/feedback/", headers=doc_headers)
        assert res_list_403.status_code == 403

        # 200: Админ видит список
        res_list_ok = await ac.get("/api/feedback/", headers=admin_headers)
        assert res_list_ok.status_code == 200
        assert len(res_list_ok.json()) >= 1

        # --- ШАГ 4: ПОМЕТКА КАК ПРОЧИТАННОЕ (PATCH) ---
        # 403: Врач не может менять статус
        res_read_403 = await ac.patch(f"/api/feedback/{fb_id}/read", headers=doc_headers)
        assert res_read_403.status_code == 403

        # 404: Несуществующий ID (тестируем строку 76 в feedback.py)
        res_read_404 = await ac.patch("/api/feedback/99999/read", headers=admin_headers)
        assert res_read_404.status_code == 404

        # 200: Админ успешно помечает
        res_read_ok = await ac.patch(f"/api/feedback/{fb_id}/read", headers=admin_headers)
        assert res_read_ok.status_code == 200
        assert res_read_ok.json()["message"] == "Отмечено как прочитанное"

        # --- ШАГ 5: ТЕСТ ТИПА ПО УМОЛЧАНИЮ (Крайний случай) ---
        # Если прислать неверный тип, должна сработать обработка KeyError (строка 23)
        fb_bad_type = fb_payload.copy()
        fb_bad_type["feedback_type"] = "СтранныйТип"
        res_bad_type = await ac.post("/api/feedback/", json=fb_bad_type, headers=doc_headers)
        assert res_bad_type.status_code == 200
        # Проверяем, что сбросилось на "Ошибка" (как прописано в коде)
        assert res_bad_type.json()["feedback_type"] == "Ошибка"
