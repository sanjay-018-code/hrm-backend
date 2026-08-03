from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class AttendanceCreate(BaseModel):
    employee_id:str
    date: date
    status: str
    check_in:time
    check_out:time

class AttendanceResponse(BaseModel):
    id:str
    employee_id:str
    date: date
    status: str
    check_in:time
    check_out:time
    is_deleted:bool=False

class AttendanceUpdate(BaseModel):
    status: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None