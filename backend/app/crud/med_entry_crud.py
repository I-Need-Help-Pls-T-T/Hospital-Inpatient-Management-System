from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import MedEntry
from backend.app.schemas.med_entry_schemas import MedEntryCreate

class CRUDMedEntry(CRUDBase[MedEntry, MedEntryCreate, MedEntryCreate]):
    pass

med_entry_crud = CRUDMedEntry(MedEntry)