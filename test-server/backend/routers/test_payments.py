import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
from datetime import date

BASE_URL = "http://testserver"

@pytest.mark.asyncio
async def test_payments_full_coverage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url=BASE_URL) as ac:

        # --- ПОДГОТОВКА ЦЕПОЧКИ ЗАВИСИМОСТЕЙ ---
        # 1. Отделение и Палата
        dep = await ac.post("/departments/", json={"name": "Платное отделение"})
        dep_id = dep.json()["id"]
        room = await ac.post("/rooms/", json={"number": 777, "department_id": dep_id})
        room_id = room.json()["id"]
        ward = await ac.post("/wards/", json={"name": "VIP", "room_id": room_id})
        ward_id = ward.json()["id"]

        # 2. Пациент
        patient = await ac.post("/patients/", json={
            "full_name": "Богатый Клиент",
            "birth_date": "1980-01-01",
            "gender": "Мужской"
        })
        patient_id = patient.json()["id"]

        # 3. Госпитализация
        hosp = await ac.post("/hospitalizations/", json={
            "patient_id": patient_id,
            "ward_id": ward_id,
            "admission_date": str(date.today())
        })
        hosp_id = hosp.json()["id"]

        # --- 1. POST (Создание оплаты) ---
        payment_data = {
            "hospitalization_id": hosp_id,
            "payment_date": str(date.today()),
            "amount": 50000.00,
            "method": "Карта"
        }
        create_res = await ac.post("/payments/", json=payment_data)
        assert create_res.status_code == 200
        pay_id = create_res.json()["id"]

        # --- 2. GET List ---
        list_res = await ac.get("/payments/")
        assert list_res.status_code == 200
        assert any(p["id"] == pay_id for p in list_res.json())

        # --- 3. GET One ---
        get_one = await ac.get(f"/payments/{pay_id}")
        assert get_one.status_code == 200
        assert float(get_one.json()["amount"]) == 50000.00

        # --- 4. PUT (Обновление) ---
        update_data = payment_data.copy()
        update_data["amount"] = 55000.50
        update_data["method"] = "Наличные"

        put_res = await ac.put(f"/payments/{pay_id}", json=update_data)
        assert put_res.status_code == 200
        assert float(put_res.json()["amount"]) == 55000.50

        # --- 5. ТЕСТЫ ОШИБОК 404 ---
        bad_get = await ac.get("/payments/9999")
        assert bad_get.status_code == 404

        bad_put = await ac.put("/payments/9999", json=update_data)
        assert bad_put.status_code == 404

        # --- 6. DELETE ---
        del_res = await ac.delete(f"/payments/{pay_id}")
        assert del_res.status_code == 200

        # Повторное удаление для 404
        bad_del = await ac.delete(f"/payments/{pay_id}")
        assert bad_del.status_code == 404
