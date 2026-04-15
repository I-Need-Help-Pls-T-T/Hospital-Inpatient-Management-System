from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import PatientAdmission
from backend.app.schemas.admission_schema import PatientAdmissionCreate

class CRUDPatientAdmission(CRUDBase[PatientAdmission, PatientAdmissionCreate, PatientAdmissionCreate]):
    pass

patient_admission_crud = CRUDPatientAdmission(PatientAdmission)