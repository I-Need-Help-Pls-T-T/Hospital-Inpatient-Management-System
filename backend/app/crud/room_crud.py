from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import Room
from backend.app.schemas.room_schema import RoomCreate

class CRUDRoom(CRUDBase[Room, RoomCreate, RoomCreate]):
    pass

room_crud = CRUDRoom(Room)