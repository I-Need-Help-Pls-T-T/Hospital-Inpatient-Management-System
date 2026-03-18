import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_wards_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ В БД ---
    db = SessionLocal()
    try:
        # Администратор (уровень 4) для создания/удаления
        admin_login = "ward_admin"
        if not db.query(models.Staff).filter(models.Staff.login == admin_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Админ Палат", login=admin_login, password="123", access_level=3
            ))

        # Обычный врач (уровень 1) только для чтения
        doc_login = "ward_doctor"
        if not db.query(models.Staff).filter(models.Staff.login == doc_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Врачи", login=doc_login, password="123", access_level=1
            ))

        # Пользователь без прав (уровень 0)
        zero_login = "ward_zero"
        if not db.query(models.Staff).filter(models.Staff.login == zero_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Никто", login=zero_login, password="123", access_level=0
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- 2. ПОДГОТОВКА ТОКЕНОВ ---
        admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': admin_login})}"}
        doc_headers = {"Authorization": f"Bearer {create_access_token({'sub': doc_login})}"}
        zero_headers = {"Authorization": f"Bearer {create_access_token({'sub': zero_login})}"}

        # --- 3. ПОДГОТОВКА СТРУКТУРЫ (Отделение и Комната) ---
        # Делаем это под админом
        dep_res = await ac.post("/api/departments/", json={"name": "Терапия"}, headers=admin_headers)
        dep_id = dep_res.json()["id"]

        room_res = await ac.post("/api/rooms/", json={
             "number": 303, "type": "Палата", "capacity": 4, "department_id": dep_id
        }, headers=admin_headers)
        room_id = room_res.json()["id"]

        # --- 4. ТЕСТЫ СОЗДАНИЯ (POST) ---
        ward_payload = {"room_id": room_id, "w_place": 2, "m_place": 2}

        # Ошибка: недостаточно прав (уровень 1 < 4)
        res_fail = await ac.post("/api/wards/", json=ward_payload, headers=doc_headers)
        assert res_fail.status_code == 403

        # Успех: админ
        res_ok = await ac.post("/api/wards/", json=ward_payload, headers=admin_headers)
        assert res_ok.status_code == 200
        ward_id = res_ok.json()["id"]

        # --- 5. ТЕСТЫ ЧТЕНИЯ (GET) ---
        # Успех: врач может видеть список
        res_list = await ac.get("/api/wards/", headers=doc_headers)
        assert res_list.status_code == 200

        # Ошибка: уровень 0 не может видеть
        res_zero_list = await ac.get("/api/wards/", headers=zero_headers)
        assert res_zero_list.status_code == 403

        # Получение конкретной палата (успех)
        res_one = await ac.get(f"/api/wards/{ward_id}", headers=doc_headers)
        assert res_one.status_code == 200

        # Ошибка 404
        res_404 = await ac.get("/api/wards/99999", headers=doc_headers)
        assert res_404.status_code == 404

        # --- 6. ТЕСТЫ ОБНОВЛЕНИЯ (PUT) ---
        update_data = {"room_id": room_id, "w_place": 5, "m_place": 0}

        # Ошибка 404 для PUT
        res_put_404 = await ac.put("/api/wards/99999", json=update_data, headers=admin_headers)
        assert res_put_404.status_code == 404

        # Успешное обновление
        res_put_ok = await ac.put(f"/api/wards/{ward_id}", json=update_data, headers=admin_headers)
        assert res_put_ok.status_code == 200
        assert res_put_ok.json()["w_place"] == 5

        # --- 7. ТЕСТЫ УДАЛЕНИЯ (DELETE) ---
        # Ошибка: врач не может удалять
        res_del_fail = await ac.delete(f"/api/wards/{ward_id}", headers=doc_headers)
        assert res_del_fail.status_code == 403

        # Успех: админ удаляет
        res_del_ok = await ac.delete(f"/api/wards/{ward_id}", headers=admin_headers)
        assert res_del_ok.status_code == 200

        # Ошибка 404 при повторном удалении
        res_del_404 = await ac.delete(f"/api/wards/{ward_id}", headers=admin_headers)
        assert res_del_404.status_code == 404
