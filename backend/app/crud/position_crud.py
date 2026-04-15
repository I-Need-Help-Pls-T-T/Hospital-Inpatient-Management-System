from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import Position
from backend.app.schemas.position_schema import PositionCreate 

class CRUDPosition(CRUDBase[Position, PositionCreate, PositionCreate]):
    pass

position_crud = CRUDPosition(Position)