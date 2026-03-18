import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from backend.auth import create_access_token
from backend.database import SessionLocal
from backend import crud, schemas, models
from datetime import datetime, timedelta

BASE_URL = "http://testserver/api"

@pytest.mark.asyncio
async def test_admissions_full_coverage():
    # --- 1. ПОДГОТОВКА ПОЛЬЗОВАТЕЛЕЙ ---
    db = SessionLocal()
    try:
        for login, level in [("adm_adm", 3), ("doc_doc", 2), ("intern_1", 1)]:
            user = db.query(models.Staff).filter(models.Staff.login == login).first()
            if not user:
                crud.staff_crud.create(db, obj_in=schemas.StaffCreate(
                    full_name=login, login=login, password="1", access_level=level
                ))
            else:
                user.access_level = level
                db.add(user)
        db.commit()
    finally:
        db.close()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:
        # Токены для разных уровней доступа
        adm_h = {"Authorization": f"Bearer {create_access_token({'sub': 'adm_adm'})}"}
        doc_h = {"Authorization": f"Bearer {create_access_token({'sub': 'doc_doc'})}"}
        int_h = {"Authorization": f"Bearer {create_access_token({'sub': 'intern_1'})}"}

        # --- 2. СОЗДАНИЕ ЗАВИСИМОСТЕЙ ---
        # Создаем пациента
        p_res = await ac.post("/patients/",
                             json={"full_name": "Тест Поступления", "birth_date": "1990-01-01", "gender": "Мужской"},
                             headers=adm_h)
        p_id = p_res.json()["id"]

        # Создаем госпитализацию
        h_res = await ac.post("/hospitalizations/",
                             json={"patient_id": p_id, "status": "Активна"},
                             headers=adm_h)
        hosp_id = h_res.json()["id"]

        # Данные для поступления
        arrival = datetime.now()
        departure = arrival + timedelta(days=5)
        adm_payload = {
            "hospitalization_id": hosp_id,
            "arrival_time": arrival.isoformat(),
            "end_time": departure.isoformat()
        }

        # --- 3. ТЕСТЫ ПРАВ ДОСТУПА (403 Forbidden) ---
        # Чтение: уровень 0 (без токена) -> 401/403
        no_auth = await ac.get("/admissions/")
        assert no_auth.status_code in [401, 403]

        # Создание: уровень 1 (интерн) не может (нужен 2+)
        forb_post = await ac.post("/admissions/", json=adm_payload, headers=int_h)
        assert forb_post.status_code == 403

        # --- 4. ТЕСТЫ СОЗДАНИЯ И ВАЛИДАЦИИ (POST) ---
        # Ошибка валидации (время выбытия раньше прибытия)
        bad_time = {**adm_payload, "end_time": (arrival - timedelta(hours=1)).isoformat()}
        val_res = await ac.post("/admissions/", json=bad_time, headers=doc_h)
        assert val_res.status_code == 422
        assert "Дата отмены не может быть раньше даты назначения" in val_res.text

        # Успешное создание (Врач)
        res_ok = await ac.post("/admissions/", json=adm_payload, headers=doc_h)
        assert res_ok.status_code == 200

        # --- 5. ТЕСТЫ ПОЛУЧЕНИЯ ДАННЫХ (GET) ---
        # Список
        list_res = await ac.get("/admissions/", headers=int_h)
        assert list_res.status_code == 200
        assert any(item["hospitalization_id"] == hosp_id for item in list_res.json())

        # Конкретная запись
        get_one = await ac.get(f"/admissions/{hosp_id}", headers=int_h)
        assert get_one.status_code == 200
        assert get_one.json()["hospitalization_id"] == hosp_id

        # --- 6. ТЕСТЫ ОБНОВЛЕНИЯ (PUT) ---
        new_departure = arrival + timedelta(days=10)
        update_payload = {**adm_payload, "end_time": new_departure.isoformat()}

        # Успешное обновление
        put_res = await ac.put(f"/admissions/{hosp_id}", json=update_payload, headers=doc_h)
        assert put_res.status_code == 200

        # Обновление несуществующего (404)
        bad_put = await ac.put("/admissions/9999", json=update_payload, headers=doc_h)
        assert bad_put.status_code == 404

        # --- 7. ТЕСТЫ УДАЛЕНИЯ (DELETE) ---
        # Врач (2) не может удалять (нужен 4)
        forb_del = await ac.delete(f"/admissions/{hosp_id}", headers=doc_h)
        assert forb_del.status_code == 403

        # Удаление несуществующего администратором (404)
        bad_del = await ac.delete("/admissions/9999", headers=adm_h)
        assert bad_del.status_code == 404

        # Успешное удаление (Админ)
        del_res = await ac.delete(f"/admissions/{hosp_id}", headers=adm_h)
        assert del_res.status_code == 200

        # Проверка, что после удаления GET выдает 404
        final_check = await ac.get(f"/admissions/{hosp_id}", headers=doc_h)
        assert final_check.status_code == 404
