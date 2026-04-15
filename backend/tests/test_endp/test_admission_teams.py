import pytest
import base64
from datetime import date, datetime
from backend.app.models.base_models import Patient, Hospitalization, PatientAdmission

ADMIN_PASS_B64 = base64.b64encode(b"admin").decode("utf-8")
HEADERS = {"Authorization": "Bearer admin"}
DELETE_HEADERS = {
    "Authorization": "Bearer admin",
    "X-Confirm-Password": ADMIN_PASS_B64
}

def test_create_admission_team_success(client, db_session):
    """Покрытие: Создание записи в бригаде"""
    patient = Patient(full_name="Иванов", passport="123456", birth_date=date(1990, 1, 1))
    db_session.add(patient)
    db_session.flush()

    hosp = Hospitalization(patient_id=patient.id, care_type="Стационар")
    db_session.add(hosp)
    db_session.flush()

    adm = PatientAdmission(hospitalization_id=hosp.id, arrival_time=datetime.now())
    db_session.add(adm)
    db_session.commit()

    valid_data = {
        "staff_id": 1, 
        "admission_id": hosp.id, 
        "role": "Врач"
    }
    
    response = client.post("/admission-teams/", json=valid_data, headers=HEADERS)
    assert response.status_code == 201

def test_update_admission_team_not_found(client):
    """Покрытие: 404 при обновлении несуществующей связи в бригаде"""
    update_data = {
        "staff_id": 1,
        "admission_id": 1, 
        "role": "Медсестра"
    }
    response = client.put("/admission-teams/9999", json=update_data, headers=HEADERS)
    assert response.status_code == 404

def test_delete_admission_team_success(client, db_session):
    """Покрытие: Удаление записи из бригады"""
    patient = Patient(full_name="Петров", passport="654321", birth_date=date(1985, 5, 5))
    db_session.add(patient)
    db_session.flush()
    
    hosp = Hospitalization(patient_id=patient.id)
    db_session.add(hosp)
    db_session.commit()

    create_data = {"staff_id": 1, "admission_id": hosp.id, "role": "Врач"}
    res = client.post("/admission-teams/", json=create_data, headers=HEADERS)
    assert res.status_code == 201
    team_entry_id = res.json()["id"]

    response = client.delete(f"/admission-teams/{team_entry_id}", headers=DELETE_HEADERS)
    assert response.status_code == 200