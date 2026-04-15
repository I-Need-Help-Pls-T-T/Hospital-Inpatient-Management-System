import base64
import requests

class ApiClient:
    BASE_URL = "http://localhost:8000"
    TOKEN = None
    
    _session = requests.Session()

    _url_cache: dict[str, str] = {}

    @classmethod
    def _headers(cls):
        if cls.TOKEN:
            return {"Authorization": f"Bearer {cls.TOKEN}"}
        return {}
    
    @classmethod
    def login(cls, username: str, password: str):
        """Авторизация и получение токена"""
        data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(f"{cls.BASE_URL}/auth/login", data=data)
        
        if response.status_code != 200:
            raise Exception("Неверный логин или пароль")
            
        token_data = response.json()
        cls.TOKEN = token_data.get("access_token")
        return cls.TOKEN

    @classmethod
    def _normalize_endpoint(cls, name: str) -> str:
        name = name.lower().replace("get_", "")
        return name.replace(" ", "-").replace("_", "-")

    @classmethod
    def _resolve_url(cls, endpoint: str) -> str:
        """
        Возвращает рабочий URL для эндпоинта.
        При первом вызове пробует дефис, потом нижнее подчёркивание,
        запоминает результат — повторного 404 больше не будет.
        """
        if endpoint in cls._url_cache:
            return cls._url_cache[endpoint]

        base = cls._normalize_endpoint(endpoint)
        url_dash = f"{cls.BASE_URL}/{base}/"
        url_underscore = f"{cls.BASE_URL}/{base.replace('-', '_')}/"

        r = cls._session.get(url_dash, headers=cls._headers())
        if r.status_code != 404:
            cls._url_cache[endpoint] = url_dash
            return url_dash

        cls._url_cache[endpoint] = url_underscore
        return url_underscore

    @classmethod
    def get_all(cls, endpoint: str):
        url = cls._resolve_url(endpoint)
        response = cls._session.get(url, headers=cls._headers())
        response.raise_for_status()
        return response.json()

    @classmethod
    def delete_any(cls, endpoint: str, item_id: int, password: str):
        base_url = cls._resolve_url(endpoint).rstrip("/")
        headers = cls._headers()
        encoded_pw = base64.b64encode(password.strip().encode('utf-8')).decode('utf-8')
        headers["X-Confirm-Password"] = encoded_pw
        response = cls._session.delete(f"{base_url}/{item_id}", headers=headers)
        response.raise_for_status()
        return response.json()

    @classmethod
    def create_any(cls, endpoint: str, data: dict):
        url = cls._resolve_url(endpoint)
        response = cls._session.post(url, json=data, headers=cls._headers())
        response.raise_for_status()
        return response.json()

    @classmethod
    def create_patient(cls, patient_data: dict):
        response = cls._session.post(f"{cls.BASE_URL}/patients/", json=patient_data, headers=cls._headers())
        response.raise_for_status()
        return response.json()

    @classmethod
    def update_any(cls, endpoint: str, item_id: int, data: dict):
        base_url = cls._resolve_url(endpoint).rstrip("/")
        response = cls._session.put(f"{base_url}/{item_id}", json=data, headers=cls._headers())
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_backups(cls):
        response = cls._session.get(f"{cls.BASE_URL}/system/backups/list", headers=cls._headers())
        response.raise_for_status()
        return response.json()

    @classmethod
    def create_backup(cls):
        response = cls._session.post(f"{cls.BASE_URL}/system/backup", json={}, headers=cls._headers())
        response.raise_for_status()
        return response.json()

    @classmethod
    def restore_backup(cls, filename: str):
        response = cls._session.post(f"{cls.BASE_URL}/system/restore", json={"filename": filename}, headers=cls._headers())
        response.raise_for_status()
        return response.json()

    @classmethod
    def search_patients_by_name(cls, name: str):
        all_patients = cls.get_all("patients")
        search_query = name.lower()
        return [
            p for p in all_patients
            if search_query in str(p.get("full_name", "")).lower()
            or search_query in str(p.get("name", "")).lower()
        ]
    
    @classmethod
    def get_unread_feedback_count(cls) -> int:
        """Получает количество непрочитанных обращений (Только для админов)"""
        try:
            response = requests.get(f"{cls.BASE_URL}/feedback/unread-count", headers=cls._headers())
            if response.status_code == 200:
                return response.json().get("count", 0)
            return 0
        except Exception:
            return 0

    @classmethod
    def submit_feedback(cls, data: dict):
        """Отправляет новый фидбэк"""
        response = requests.post(f"{cls.BASE_URL}/feedback/", json=data, headers=cls._headers())
        response.raise_for_status()
        return response.json()