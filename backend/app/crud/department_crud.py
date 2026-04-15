from backend.app.crud.base import CRUDBase
from backend.app.models.base_models import Department
from backend.app.schemas.department_schema import DepartmentCreate

class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentCreate]):
    pass

department_crud = CRUDDepartment(Department)