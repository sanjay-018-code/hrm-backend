from fastapi import APIRouter, Depends

from models.attendance import AttendanceCreate, AttendanceResponse, AttendanceUpdate
from services.attendance_services import create_attendance, get_all_attendance_service, update_attendance_services, delete_attendance_services
from services.role_dependency import allow_roles

router = APIRouter()

@router.post("/", response_model=AttendanceResponse)
def mark_attendance(attendance:AttendanceCreate , current_user=Depends(allow_roles(["hr","admin"]))):
    return create_attendance(attendance)

@router.get("/", response_model=list[AttendanceResponse])
def get_attendance(page:int=1,limit:int=10, employee_id:str|None=None,order:str="desc",current_user = Depends(allow_roles(["hr","admin","employee"]))):
    return get_all_attendance_service(page, limit,employee_id,order)

@router.patch("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id:str, attendance:AttendanceUpdate, current_user=Depends(allow_roles(["hr","admin"]))):
    return update_attendance_services(attendance_id, attendance)

@router.delete("/{attendance_id}")
def delete_attendance(attendance_id:str, current_user=Depends(allow_roles(["hr","admin"]))):
    return delete_attendance_services(attendance_id, )
