import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models

BASE_URL = "http://testserver/api"

@pytest.mark.asyncio
async def test_staff_full_coverage():
    # --- ШАГ 1: ПОДГОТОВКА БД ---
    db = SessionLocal()
    try:
        # Супер-админ (уровень 4 для DELETE)
        admin_login = "super_admin"
        admin = db.query(models.Staff).filter(models.Staff.login == admin_login).first()
        if not admin:
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Главный Админ", login=admin_login, password="123", access_level=3
            ))

        # Модератор (уровень 3 для POST/PUT)
        mod_login = "mod_user"
        if not db.query(models.Staff).filter(models.Staff.login == mod_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Модератор", login=mod_login, password="123", access_level=2
            ))

        # Обычный пользователь (уровень 1 для GET)
        read_login = "read_user"
        if not db.query(models.Staff).filter(models.Staff.login == read_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Читатель", login=read_login, password="123", access_level=1
            ))

        # Пользователь без прав (уровень 0)
        zero_login = "zero_user"
        if not db.query(models.Staff).filter(models.Staff.login == zero_login).first():
            crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                full_name="Без прав", login=zero_login, password="123", access_level=0
            ))
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # Токены
        admin_headers = {"Authorization": f"Bearer {create_access_token({'sub': admin_login})}"}
        mod_headers = {"Authorization": f"Bearer {create_access_token({'sub': mod_login})}"}
        read_headers = {"Authorization": f"Bearer {create_access_token({'sub': read_login})}"}
        zero_headers = {"Authorization": f"Bearer {create_access_token({'sub': zero_login})}"}

        # --- ТЕСТЫ GET (ЧТЕНИЕ) ---
        # Покрываем строку 21 (уровень 0)
        res = await ac.get("/staff/", headers=zero_headers)
        assert res.status_code == 403

        # Покрываем строки 32 и 37 (несуществующий ID)
        res_404 = await ac.get("/staff/99999", headers=read_headers)
        assert res_404.status_code == 404

        # --- ТЕСТЫ POST (СОЗДАНИЕ) ---
        # Покрываем строку 46 (недостаточно прав, уровень 1 < 3)
        res_fail_level = await ac.post("/staff/", headers=read_headers, json={
            "full_name": "Тест", "login": "t1", "password": "1", "access_level": 1
        })
        assert res_fail_level.status_code == 403

        # Покрываем строку 49 (уровень выше своего: 3 пытается создать 4)
        res_above = await ac.post("/staff/", headers=mod_headers, json={
            "full_name": "Тест", "login": "t2", "password": "1", "access_level": 4
        })
        assert res_above.status_code == 403

        # Успешное создание для дальнейших тестов
        res_created = await ac.post("/staff/", headers=admin_headers, json={
            "full_name": "Временный", "login": "temp_user", "password": "1", "access_level": 1
        })
        assert res_created.status_code == 200
        temp_id = res_created.json()["id"]

        # --- ТЕСТЫ PUT (ОБНОВЛЕНИЕ) ---
        # Покрываем строку 64 (обновление несуществующего ID)
        res_put_404 = await ac.put("/staff/99999", headers=admin_headers, json={"full_name": "Ghost"})
        assert res_put_404.status_code == 404

        # Покрываем проверку прав (3 < 4) при попытке выставить уровень выше своего
        res_put_above = await ac.put(f"/staff/{temp_id}", headers=mod_headers, json={"access_level": 4})
        assert res_put_above.status_code == 403

        # Успешное обновление
        res_put_ok = await ac.put(f"/staff/{temp_id}", headers=admin_headers, json={"full_name": "Обновлен"})
        assert res_put_ok.status_code == 200

        # --- ТЕСТЫ DELETE (УДАЛЕНИЕ) ---
        # Покрываем строку 74 (недостаточно прав, уровень 3 < 4)
        res_del_fail = await ac.delete(f"/staff/{temp_id}", headers=mod_headers)
        assert res_del_fail.status_code == 403

        # Покрываем строку 77 (удаление несуществующего)
        res_del_404 = await ac.delete("/staff/99999", headers=admin_headers)
        assert res_del_404.status_code == 404

        # Успешное удаление
        res_del_ok = await ac.delete(f"/staff/{temp_id}", headers=admin_headers)
        assert res_del_ok.status_code == 200
