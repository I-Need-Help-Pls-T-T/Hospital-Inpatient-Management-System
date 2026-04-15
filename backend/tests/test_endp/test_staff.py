import base64

ADMIN_PASS_B64 = base64.b64encode(b"admin").decode("utf-8")

HEADERS = {
    "Authorization": "Bearer admin"
}

ADMIN_HEADERS = {
    "Authorization": "Bearer admin",
    "X-Confirm-Password": ADMIN_PASS_B64
}
USER_DATA = {
    "full_name": "Иван Иванов",
    "login": "ivan_test",
    "password": "securepassword",
    "access_level": 1,
    "phone": "123456789",
    "email": "ivan@hospital.com"
}

def test_create_staff_success(client):
    response = client.post("/staff/", json=USER_DATA, headers=ADMIN_HEADERS)
    assert response.status_code in [200, 201]
    assert response.json()["login"] == USER_DATA["login"]

def test_update_staff_success(client):
    created_res = client.post("/staff/", json=USER_DATA, headers=ADMIN_HEADERS)
    staff_id = created_res.json()["id"]
    
    update_data = {"full_name": "Иван Обновленный", "access_level": 2}
    response = client.put(f"/staff/{staff_id}", json=update_data, headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Иван Обновленный"

def test_create_staff_duplicate_login(client):
    """Покрытие: raise HTTPException(400, 'Логин уже занят')"""
    client.post("/staff/", json=USER_DATA, headers=ADMIN_HEADERS)
    response = client.post("/staff/", json=USER_DATA, headers=ADMIN_HEADERS)
    assert response.status_code == 400
    assert "Логин уже занят" in response.json()["detail"]

def test_create_staff_forbidden_level(client):
    """Покрытие: Нельзя назначить уровень выше своего (403)"""
    high_level_user = {**USER_DATA, "access_level": 5} # Админ имеет 3
    response = client.post("/staff/", json=high_level_user, headers=ADMIN_HEADERS)
    assert response.status_code == 403

def test_delete_self_forbidden(client):
    """Покрытие: Запрет на удаление своей учетной записи (400)"""
    staff_list = client.get("/staff/", headers=ADMIN_HEADERS).json()
    admin_id = next(s["id"] for s in staff_list if s["login"] == "admin")
    
    response = client.delete(f"/staff/{admin_id}", headers=ADMIN_HEADERS)
    assert response.status_code == 400
    assert "Нельзя удалить свою учетную запись" in response.json()["detail"]

def test_delete_staff_not_found(client):
    """Покрытие: Удаление несуществующего (404)"""
    response = client.delete("/staff/9999", headers=ADMIN_HEADERS)
    assert response.status_code == 404

def test_unauthorized_access(client):
    """Покрытие: Доступ без токена (401/403)"""
    response = client.get("/staff/")
    assert response.status_code in [401, 403]

def test_update_staff_not_found(client):
    """Покрытие: Обновление несуществующего сотрудника (404)"""
    response = client.put("/staff/9999", json={"full_name": "Ghost"}, headers=ADMIN_HEADERS)
    assert response.status_code == 404

def test_update_staff_forbidden_level(client):
    """Покрытие: Недостаточно прав для назначения уровня (403 в PUT)"""
    res = client.post("/staff/", json=USER_DATA, headers=ADMIN_HEADERS)
    s_id = res.json()["id"]
    
    response = client.put(f"/staff/{s_id}", json={"access_level": 5}, headers=ADMIN_HEADERS)
    assert response.status_code == 403