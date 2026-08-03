from fastapi import APIRouter,Depends

from services.payroll_services import generate_payroll_services, get_all_payroll_service, get_employee_payroll_service, get_payroll_by_id_service, delete_payroll_service
from models.payroll import PayrollResponse,PayrollCreate
from services.role_dependency import allow_roles

router = APIRouter()

@router.post("/", response_model=PayrollResponse)
def generate_payroll(payroll:PayrollCreate,current_user = Depends(allow_roles(["hr","admin"]))):
    return generate_payroll_services(payroll)

@router.get("/", response_model=list[PayrollResponse])
def get_all_payroll(current_user = Depends(allow_roles(["hr","admin"]))):
    return get_all_payroll_service()

@router.get("/employee/{employee_id}", response_model=list[PayrollResponse])
def get_employee_payroll(employee_id:str, current_user = Depends(allow_roles(["hr","admin","employee"]))):
    return get_employee_payroll_service(employee_id)

@router.get("/details/{payroll_id}",response_model=PayrollResponse)
def get_payroll_by_id(payroll_id:str, current_user=Depends(allow_roles(["hr","admin"]))):
    return get_payroll_by_id_service(payroll_id)

@router.delete("/{payroll_id}")
def delete_payroll(payroll_id:str,current_user = Depends(allow_roles(["hr","admin"]))):
    return delete_payroll_service(payroll_id)