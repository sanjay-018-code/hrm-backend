from fastapi import APIRouter,Depends

from models.dashboard import DashboardResponse
from services.role_dependency import allow_roles
from services.dashboard_services import get_dashboard_details, get_attendance_chart_service

router = APIRouter()

@router.get("/",response_model=DashboardResponse)
def get_dashboard_data(current_user=Depends(allow_roles(["hr","admin"]))):
    return get_dashboard_details()

@router.get("/chart")
def get_attendance_chart(current_user=Depends(allow_roles(["hr","admin"]))):
    return get_attendance_chart_service()