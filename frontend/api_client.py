import sys
import os
print("Python path:", sys.executable)
print("Current directory:", os.getcwd())
import requests
from typing import List, Dict, Any
import json

class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def _make_request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}")
            return None

    # --- Пациенты ---
    def get_patients(self, skip=0, limit=100):
        return self._make_request("GET", "/api/patients/", params={"skip": skip, "limit": limit})

    def get_patient(self, patient_id):
        return self._make_request("GET", f"/api/patients/{patient_id}")

    def create_patient(self, patient_data):
        return self._make_request("POST", "/api/patients/", data=patient_data)

    def update_patient(self, patient_id, patient_data):
         return self._make_request("PUT", f"/api/patients/{patient_id}", data=patient_data)

    def delete_patient(self, patient_id):
        return self._make_request("DELETE", f"/api/patients/{patient_id}")

    # --- Отделения ---
    def get_departments(self):
            """Получить список отделений"""
            return self._make_request("GET", "/api/departments/")

    def get_staff(self):
        return self._make_request("GET", "/api/staff/")

    # --- Проверка соединения ---
    def check_connection(self):
            try:
                response = self.session.get(f"{self.base_url}/api/health")
                return response.status_code == 200
            except:
                return False
