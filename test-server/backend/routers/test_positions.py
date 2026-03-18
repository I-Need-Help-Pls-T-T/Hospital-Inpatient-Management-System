import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_positions_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        admin_login = "pos_admin" # Уровень 4
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Админ Должностей", login=admin_login, password="1", access_level=3
            ))

        user_login = "pos_user" # Уровень 1
        if not db.query(models.Staff).filter(models.Staff.login == user_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Врач", login=user_login, password="1", access_level=1
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': admin_login})}"}
        user_headers = {"Authorization": f"Bearer {create_access_token({'sub': user_login})}"}

        # --- 2. POST (Создание) ---
        pos_data = {"name": "Хирург", "med_education": True}

        # 403: Обычный юзер не может создавать
        res_p_403 = await ac.post("/api/positions/", json=pos_data, headers=user_headers)
        assert res_p_403.status_code == 403

        # 200: Админ может
        res_p_ok = await ac.post("/api/positions/", json=pos_data, headers=admin_headers)
        assert res_p_ok.status_code == 200
        pos_id = res_p_ok.json()["id"]

        # --- 3. GET (Чтение) ---
        # Список
        res_list = await ac.get("/api/positions/", headers=user_headers)
        assert res_list.status_code == 200

        # Детально
        res_one = await ac.get(f"/api/positions/{pos_id}", headers=user_headers)
        assert res_one.status_code == 200

        # 404: Несуществующая
        res_get_404 = await ac.get("/api/positions/9999", headers=user_headers)
        assert res_get_404.status_code == 404

        # --- 4. PUT (Обновление) ---
        update_data = {"name": "Старший Хирург", "med_education": True}

        # 403: Недостаточно прав
        res_up_403 = await ac.put(f"/api/positions/{pos_id}", json=update_data, headers=user_headers)
        assert res_up_403.status_code == 403

        # 404: Не найдена
        res_up_404 = await ac.put("/api/positions/9999", json=update_data, headers=admin_headers)
        assert res_up_404.status_code == 404

        # 200: Успех
        res_up_ok = await ac.put(f"/api/positions/{pos_id}", json=update_data, headers=admin_headers)
        assert res_up_ok.status_code == 200

        # --- 5. DELETE (Удаление) ---
        # 403: Ошибка прав
        res_d_403 = await ac.delete(f"/api/positions/{pos_id}", headers=user_headers)
        assert res_d_403.status_code == 403

        # 200: Удаление админом
        res_d_ok = await ac.delete(f"/api/positions/{pos_id}", headers=admin_headers)
        assert res_d_ok.status_code == 200

        # 404: Повторное удаление
        res_d_404 = await ac.delete(f"/api/positions/{pos_id}", headers=admin_headers)
        assert res_d_404.status_code == 404
