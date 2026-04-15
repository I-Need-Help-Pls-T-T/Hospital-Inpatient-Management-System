from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import StaffRole
from backend.app.schemas.staff_role_schema import StaffRoleCreate

class CRUDStaffRole(CRUDBase[StaffRole, StaffRoleCreate, StaffRoleCreate]):
    
    def get_by_identity(
        self, db: Session, *, staff_id: int, position_id: int, appointment_date: Any
    ) -> Optional[StaffRole]:
        return db.query(StaffRole).filter(
            StaffRole.staff_id == staff_id,
            StaffRole.position_id == position_id,
            StaffRole.appointment_date == appointment_date
        ).first()

    def remove_by_identity(
        self, db: Session, *, staff_id: int, position_id: int, appointment_date: Any
    ) -> Optional[StaffRole]:
        obj = self.get_by_identity(
            db, 
            staff_id=staff_id, 
            position_id=position_id, 
            appointment_date=appointment_date
        )
        if obj:
            db.delete(obj)
            db.commit()
        return obj

staff_role_crud = CRUDStaffRole(StaffRole)