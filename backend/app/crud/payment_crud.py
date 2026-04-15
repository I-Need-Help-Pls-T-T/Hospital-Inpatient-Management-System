from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import Payment
from backend.app.schemas.payment_schema import PaymentCreate

class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentCreate]):
    pass

payment_crud = CRUDPayment(Payment)