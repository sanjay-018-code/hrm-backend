from fastapi import APIRouter
from fastapi import Depends, Query

from constants.enums import SortOrderEnum
from models.employee import EmployeeCreate, EmployeeResponse, EmployeeListResponse, EmployeeUpdate
from app.database import employees_collection
from services.employee_services import create_employee_services, get_all_employees, update_employee_service, delete_employee_service, get_employee_by_id_service
from services.role_dependency import allow_roles

router = APIRouter()

@router.post("/", response_model=EmployeeResponse)
def create_employee(employee:EmployeeCreate):
    return create_employee_services(employee)

@router.get("/",response_model=EmployeeListResponse)
def get_employees(
    page:int=Query(1,ge=1),
    limit:int=Query(10,ge=1,le=50), 
    search:str |None =Query(None),
    sort_by:str=Query("name"),
    order:SortOrderEnum=Query(SortOrderEnum.asc),
    department: str|None=Query(None) ,
    current_user = Depends(allow_roles(["admin","hr","employee"]))
    ):
    return get_all_employees(page, limit, search, sort_by, order,department)

@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str, current_user=Depends(allow_roles(["hr","admin","employee"]))):
    return get_employee_by_id_service(employee_id)

@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: str, emp: EmployeeUpdate, current_user = Depends(allow_roles(["hr","admin"]))):
    return update_employee_service(employee_id, emp)

@router.delete("/{employee_id}")
def delete_employee(employee_id: str, current_user = Depends(allow_roles(["hr","admin"]))):
    return delete_employee_service(employee_id)