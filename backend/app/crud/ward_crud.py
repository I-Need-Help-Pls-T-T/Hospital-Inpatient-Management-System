from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import Ward
from backend.app.schemas.ward_schema import WardCreate # Предполагается наличие этой схемы

class CRUDWard(CRUDBase[Ward, WardCreate, WardCreate]):
    pass

ward_crud = CRUDWard(Ward)