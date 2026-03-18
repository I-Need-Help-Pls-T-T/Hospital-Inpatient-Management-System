import bcrypt
from sqlalchemy.orm import Session
from typing import Union, List, Optional, Type, TypeVar, Generic, Any, Dict
from pydantic import BaseModel
from passlib.context import CryptContext

# --- МОНКИ-ПАТЧ ДЛЯ BCRYPT (Исправляет ошибку на Windows/Python 3.12) ---
original_hashpw = bcrypt.hashpw
def patched_hashpw(password, salt):
    if isinstance(password, str):
        password = password.encode('utf-8')
    # Bcrypt не принимает более 72 байт, passlib иногда ошибается в проверках
    return original_hashpw(password[:72], salt)
bcrypt.hashpw = patched_hashpw

# Импорты ваших моделей и схем
from backend.models import (
    Department, Position, Room, Ward, Staff, Patient,
    Hospitalization, MedEntry, MedicationOrder,
    Payment, AdmissionTeam, StaffRole, PatientAdmission
)
from backend.schemas import StaffCreate, StaffUpdate

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

# Контекст для хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class BaseCRUD(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        if isinstance(id, dict):
            return db.query(self.model).filter_by(**id).first()
        return db.get(self.model, id)

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: Any) -> ModelType:
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

class StaffCRUD(BaseCRUD[Staff, StaffCreate]):
    def create(self, db: Session, *, obj_in: StaffCreate) -> Staff:
        obj_in_data = obj_in.model_dump()

        if "position_id" in obj_in_data:
            del obj_in_data["position_id"]

        password = obj_in_data.pop("password")
        obj_in_data["password_hash"] = pwd_context.hash(password)

        db_obj = Staff(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, login: str, password: str) -> Optional[Staff]:
        user = db.query(self.model).filter(self.model.login == login).first()
        if not user or not pwd_context.verify(password, user.password_hash):
            return None
        return user

    def update(self, db: Session, *, db_obj: Staff, obj_in: Union[StaffUpdate, Dict[str, Any]]) -> Staff:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["password_hash"] = pwd_context.hash(update_data["password"])
            del update_data["password"]

        return super().update(db, db_obj=db_obj, obj_in=update_data)

# Экземпляры
department_crud = BaseCRUD(Department)
position_crud = BaseCRUD(Position)
room_crud = BaseCRUD(Room)
ward_crud = BaseCRUD(Ward)
staff_crud = StaffCRUD(Staff)
patient_crud = BaseCRUD(Patient)
hospitalization_crud = BaseCRUD(Hospitalization)
med_entry_crud = BaseCRUD(MedEntry)
medication_order_crud = BaseCRUD(MedicationOrder)
payment_crud = BaseCRUD(Payment)
admission_team_crud = BaseCRUD(AdmissionTeam)
staff_role_crud = BaseCRUD(StaffRole)
patient_admission_crud = BaseCRUD(PatientAdmission)
