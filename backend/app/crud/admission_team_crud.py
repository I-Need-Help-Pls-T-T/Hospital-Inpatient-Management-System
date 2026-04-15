from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import AdmissionTeam
from backend.app.schemas.admission_team_schema import AdmissionTeamCreate

class CRUDAdmissionTeam(CRUDBase[AdmissionTeam, AdmissionTeamCreate, AdmissionTeamCreate]):
    """
    CRUD для управления медицинскими бригадами (приемное отделение).
    """
    pass

admission_team_crud = CRUDAdmissionTeam(AdmissionTeam)