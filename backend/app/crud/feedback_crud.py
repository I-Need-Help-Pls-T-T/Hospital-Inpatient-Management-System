from sqlalchemy.orm import Session
from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import Feedback, FeedbackType
from backend.app.schemas.feedback_schema import FeedbackCreate

class CRUDFeedback(CRUDBase[Feedback, FeedbackCreate, FeedbackCreate]):
    def create_feedback(self, db: Session, *, obj_in: FeedbackCreate, staff_id: int) -> Feedback:
        try:
            f_type = FeedbackType[obj_in.feedback_type]
        except KeyError:
            f_type = FeedbackType.Ошибка

        db_obj = Feedback(
            staff_id=staff_id,
            subject=obj_in.subject,
            description=obj_in.description,
            feedback_type=f_type,
            section=obj_in.section,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def mark_read(self, db: Session, db_obj: Feedback) -> Feedback:
        setattr(db_obj, "is_read", True) 
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_unread_count(self, db: Session) -> int:
        return db.query(Feedback).filter(Feedback.is_read == False).count()

feedback_crud = CRUDFeedback(Feedback)