from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import MedicationOrder  # Проверьте имя модели в base_models
from backend.app.schemas.medication_order_schema import MedicationOrderCreate

class CRUDMedicationOrder(CRUDBase[MedicationOrder, MedicationOrderCreate, MedicationOrderCreate]):
    pass

medication_order_crud = CRUDMedicationOrder(MedicationOrder)