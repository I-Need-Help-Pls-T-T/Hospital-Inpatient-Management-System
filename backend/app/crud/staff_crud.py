from sqlalchemy.orm import Session
from backend.app.models.base_models import Staff
from backend.app.schemas import staff_schema as schemas

class CRUDStaff:
    def get(self, db: Session, id: int):
        return db.query(Staff).filter(Staff.id == id).first()

    def get_by_login(self, db: Session, login: str):
        return db.query(Staff).filter(Staff.login == login).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Staff).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: schemas.StaffCreate):
        data = obj_in.model_dump()
        password = data.pop("password")
        
        db_obj = Staff(**data, password_hash=password) # Здесь можно добавить хеширование
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Staff, obj_in: schemas.StaffUpdate):
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            password = update_data.pop("password")
            db_obj.password_hash = password
            
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int):
        obj = db.get(Staff, id) 
        if obj:
            db.delete(obj)
            db.commit()
        return obj

staff_crud = CRUDStaff()