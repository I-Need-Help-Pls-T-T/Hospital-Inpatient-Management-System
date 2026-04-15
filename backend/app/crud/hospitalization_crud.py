from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import Hospitalization
from backend.app.schemas.hospitalization_schema import HospitalizationCreate

class CRUDHospitalization(CRUDBase[Hospitalization, HospitalizationCreate, HospitalizationCreate]):
    pass

hospitalization_crud = CRUDHospitalization(Hospitalization)