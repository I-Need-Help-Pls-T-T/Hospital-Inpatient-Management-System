from sqlalchemy.orm import Session
from typing import List, Optional, Type, TypeVar, Generic
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

class BaseCRUD(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: any) -> Optional[ModelType]:
        if isinstance(id, dict):
            return db.query(self.model).filter_by(**id).first()
        return db.get(self.model, id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()

        model_attributes = self.model.__mapper__.all_orm_descriptors.keys()

        filtered_data = {
            k: v for k, v in obj_in_data.items()
            if k in model_attributes
        }

        db_obj = self.model(**filtered_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump()
        model_columns = self.model.__table__.columns.keys()
        for field, value in obj_data.items():
            if field in model_columns:
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: any) -> Optional[ModelType]:
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

# Импорты моделей
from backend.models import (
    Department, Position, Room, Ward, Staff, Patient,
    Hospitalization, MedEntry, MedicationOrder,
    Payment, AdmissionTeam, StaffRole, PatientAdmission
)

# Экземпляры CRUD для роутеров
department_crud = BaseCRUD(Department)
position_crud = BaseCRUD(Position)
room_crud = BaseCRUD(Room)
ward_crud = BaseCRUD(Ward)
staff_crud = BaseCRUD(Staff)
patient_crud = BaseCRUD(Patient)
hospitalization_crud = BaseCRUD(Hospitalization)
med_entry_crud = BaseCRUD(MedEntry)
medication_order_crud = BaseCRUD(MedicationOrder)
payment_crud = BaseCRUD(Payment)
admission_team_crud = BaseCRUD(AdmissionTeam)
staff_role_crud = BaseCRUD(StaffRole)
patient_admission_crud = BaseCRUD(PatientAdmission)
