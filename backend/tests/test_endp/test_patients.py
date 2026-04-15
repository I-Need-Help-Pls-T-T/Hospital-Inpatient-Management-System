from typing import Any, cast
import base64

ADMIN_PASS_B64 = base64.b64encode(b"admin").decode("utf-8")

HEADERS = {
    "Authorization": "Bearer admin"
}

ADMIN_HEADERS = {
    "Authorization": "Bearer admin",
    "X-Confirm-Password": ADMIN_PASS_B64
}
TEST_PATIENT = {
    "full_name": "Тестовый Пациент",
    "birth_date": "1990-01-01",
    "gender": "Мужской",
    "address": "ул. Тестовая, 1",
    "passport": "MP1234567",
    "phone": "+375291112233"
}

def test_create_patient_success(client):
    response = client.post("/patients/", json=TEST_PATIENT, headers=HEADERS)
    assert response.status_code == 201

def test_create_patient_duplicate_passport(client):
    """Покрытие: Уникальность паспорта (400)"""
    client.post("/patients/", json=TEST_PATIENT, headers=HEADERS)
    response = client.post("/patients/", json=TEST_PATIENT, headers=HEADERS)
    assert response.status_code == 400
    assert "паспортом уже существует" in response.json()["detail"]

def test_read_patient_not_found(client):
    """Покрытие: Поиск несуществующего ID (404)"""
    response = client.get("/patients/9999", headers=HEADERS)
    assert response.status_code == 404

def test_update_patient_not_found(client):
    """Покрытие: Обновление несуществующего (404)"""
    response = client.put("/patients/9999", json=TEST_PATIENT, headers=HEADERS)
    assert response.status_code == 404

def test_delete_patient_success(client):
    res = client.post("/patients/", json=TEST_PATIENT, headers=HEADERS)
    p_id = res.json()["id"]
    
    response = client.delete(f"/patients/{p_id}", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    
    check = client.get(f"/patients/{p_id}", headers=HEADERS)
    assert check.status_code == 404

def test_read_list_empty(client):
    """Покрытие: Список пуст (если база чистая)"""
    response = client.get("/patients/", headers=HEADERS)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_patients_doctor_scope(client, db_session):
    """Покрытие: Логика фильтрации для врачей (level 2)"""  
    from backend.app.models.base_models import Staff, Room, Department

    # 1. Подготовка структуры БД
    dept = Department(name="Тестовое отделение")
    db_session.add(dept)
    db_session.flush()

    room = Room(
        number="101", 
        type="Общий", 
        capacity=2, 
        department_id=dept.id
    )
    db_session.add(room)
    db_session.flush()

    admin = db_session.query(Staff).filter(Staff.login == "admin").first()
    admin.access_level = 2
    admin.room_id = room.id
    db_session.commit()

    response = client.get("/patients/", headers={"Authorization": "Bearer admin"})
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_patient_no_passport(client):
    """Покрытие: raise HTTPException(400, 'Паспорт обязателен')"""
    invalid_patient = cast(dict[str, Any], TEST_PATIENT.copy())
    invalid_patient["passport"] = None 
    
    response = client.post("/patients/", json=invalid_patient, headers=HEADERS)
    
    assert response.status_code == 400
    assert "Паспорт обязателен" in response.json()["detail"]