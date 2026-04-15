# backend/app/crud/patient_crud.py

from sqlalchemy.orm import Session
from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import Patient, Hospitalization, Ward, Room
from backend.app.schemas.patient_schema import PatientCreate

class CRUDPatient(CRUDBase[Patient, PatientCreate, PatientCreate]):
    
    def get_by_passport(self, db: Session, passport: str):
        return db.query(self.model).filter(self.model.passport == passport).first()

    def get_by_department(self, db: Session, dept_id: int, skip: int = 0, limit: int = 100):
        return (
            db.query(Patient)
            .join(Hospitalization, Hospitalization.patient_id == Patient.id)
            .join(Ward, Hospitalization.ward_id == Ward.id)
            .join(Room, Ward.room_id == Room.id)
            .filter(Room.department_id == dept_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

patient_crud = CRUDPatient(Patient)