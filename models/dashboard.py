from pydantic import BaseModel

class DashboardResponse(BaseModel):
    total_employees:int
    total_departments:int
    present_today:int
    absent_today : int
    pending_leaves : int
