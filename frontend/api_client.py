import requests
from typing import List, Dict, Any, Optional

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def login(self, username, password):
        """Авторизация и сохранение JWT токена"""
        url = f"{self.base_url}/api/auth/login"
        try:
            response = self.session.post(url, data={
                "username": username,
                "password": password
            })
            response.raise_for_status()
            self.token = response.json()["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            self._username = username
            self._password = password
            return True
        except Exception as e:
            print(f"Ошибка входа: {e}")
            return False

    def relogin(self):
        """Повторная авторизация с сохранёнными учётными данными"""
        if hasattr(self, '_username') and hasattr(self, '_password'):
            return self.login(self._username, self._password)
        return False

    def check_connection(self):
        """Проверка доступности сервера"""
        try:
            return self.session.get(f"{self.base_url}/health", timeout=2).status_code == 200
        except:
            return False

    def _make_request(self, method, endpoint, params=None, json_data=None):
        """Универсальный внутренний метод для запросов"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method,
                url,
                params=params,
                json=json_data,
                timeout=60
            )
            if response.status_code == 204:
                return True

            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка запроса {method} {endpoint}: {e}")
            return None

    def verify_password(self, login: str, password: str) -> bool:
        """Проверяет правильность пароля текущего пользователя через сервер"""
        result = self._make_request("POST", "/api/auth/verify-password", json_data={
            "login": login,
            "password": password
        })
        return result is not None and result.get("valid", False)

    def get_current_user_info(self):
        """Получить данные текущего авторизованного пользователя"""
        return self._make_request("GET", "/api/auth/me")

    # --- МЕТОДЫ ДЛЯ ОПЕРАЦИЙ (CRUD) ---

    def get_by_id(self, section: str, item_id: int):
        """Получить одну запись по ID из любой таблицы"""
        return self._make_request("GET", f"/api/{section}/{item_id}")

    def delete_record(self, section: str, item_id: int):
        """Удалить запись по ID"""
        return self._make_request("DELETE", f"/api/{section}/{item_id}")

    def create_patient(self, patient_data):
        """Создание нового пациента"""
        if not self.check_connection():
            print("Нет соединения с сервером")
            return None

        result = self._make_request("POST", "/api/patients/", json_data=patient_data)

        if result is None:
            print(f"Не удалось создать пациента. Данные: {patient_data}")
            try:
                url = f"{self.base_url}/api/patients/"
                response = self.session.post(url, json=patient_data)
                print(f"Статус ответа: {response.status_code}")
                print(f"Текст ответа: {response.text}")
            except Exception as e:
                print(f"Ошибка при прямой отправке: {e}")

        return result

    def update_patient(self, patient_id: int, patient_data: dict):
        """Обновление данных пациента"""
        return self._make_request("PUT", f"/api/patients/{patient_id}", json_data=patient_data)

    def create_backup(self):
        """Создать резервную копию БД"""
        return self._make_request("POST", "/api/admin/system/backup")

    def get_backups_list(self):
        """Получить список всех .sql бэкапов с сервера"""
        return self._make_request("GET", "/api/admin/system/backups/list") or []

    def restore_backup(self, filename: str):
        """Отправить запрос на восстановление БД через JSON Body"""
        url = "/api/admin/system/restore"
        payload = {"filename": filename}

        return self._make_request(
            "POST",
            url,
            json_data=payload
        )

    # --- МЕНЮ "ВВОД" (ОСНОВНЫЕ ТАБЛИЦЫ) ---

    def get_patients(self):
        return self._make_request("GET", "/api/patients/")

    def get_staff(self):
        return self._make_request("GET", "/api/staff/")

    def get_hospitalizations(self):
        return self._make_request("GET", "/api/hospitalizations/")

    def get_med_entries(self):
        return self._make_request("GET", "/api/med_entries/")

    def get_medication_orders(self):
        return self._make_request("GET", "/api/medication_orders/")

    def get_payments(self):
        return self._make_request("GET", "/api/payments/")

    def get_admissions(self):
        return self._make_request("GET", "/api/admissions/")

    def get_admission_teams(self):
        return self._make_request("GET", "/api/admission_teams/")

    # --- МЕНЮ "СПРАВОЧНИКИ" ---

    def get_departments(self):
        return self._make_request("GET", "/api/departments/")

    def get_positions(self):
        return self._make_request("GET", "/api/positions/")

    def get_rooms(self):
        return self._make_request("GET", "/api/rooms/")

    def get_wards(self):
        return self._make_request("GET", "/api/wards/")

    def get_staff_roles(self):
        return self._make_request("GET", "/api/staff_roles/")

    # --- ОБРАТНАЯ СВЯЗЬ ---

    def get_feedback(self):
        """Получить все обращения (для администратора — все, для остальных — свои)"""
        return self._make_request("GET", "/api/feedback/") or []

    def get_unread_feedback_count(self):
        """Получить количество непрочитанных обращений (только для администратора)"""
        result = self._make_request("GET", "/api/feedback/unread-count")
        if result is None:
            return 0
        return result.get("count", 0)

    def mark_feedback_read(self, feedback_id: int):
        """Отметить обращение как прочитанное"""
        return self._make_request("PATCH", f"/api/feedback/{feedback_id}/read")
