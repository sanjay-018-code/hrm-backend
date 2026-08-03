from fastapi import APIRouter, Depends

from models.department import DepartmentCreate,DepartmentResponse
from models.employee import EmployeeResponse
from services.role_dependency import allow_roles
from services.department_services import create_department_service, get_all_department_service, update_department_by_id_service, get_department_by_id_service, delete_department_service, get_employees_by_department_services

router = APIRouter()

@router.post("/", response_model=DepartmentResponse)
def create_department(department:DepartmentCreate,current_user =Depends(allow_roles(["hr","admin"])) ):
    return create_department_service(department)

@router.get("/", response_model=list[DepartmentResponse])
def get_all_department(current_user =Depends(allow_roles(["hr","admin"]))):
    return get_all_department_service()

@router.get("/{department_id}", response_model=DepartmentResponse)
def  get_department_by_id(department_id:str,current_user =Depends(allow_roles(["hr","admin"]))):
    return  get_department_by_id_service(department_id)

@router.patch("/{department_id}", response_model=DepartmentResponse)
def update_department(department_id:str,name:str,current_user =Depends(allow_roles(["hr","admin"]))):
    return update_department_by_id_service(department_id,name)

@router.delete("/delete/{department_id}")
def delete_department(department_id:str,current_user =Depends(allow_roles(["hr","admin"]))):
    return delete_department_service(department_id)

@router.get("/{department_id}/employees", response_model=list[EmployeeResponse])
def get_employees_by_department(department_id:str,current_user =Depends(allow_roles(["hr","admin"]))):
    return get_employees_by_department_services(department_id)