from pydantic import BaseModel
from datetime import date
from typing import Literal, Optional

class LeaveCreate(BaseModel):
    employee_id:str
    leave_type:str
    start_date:date
    end_date:date
    reason:Optional[str] = None

class LeaveResponse(BaseModel):
    id:str
    employee_id:str
    leave_type:str
    start_date:date
    end_date:date
    reason:Optional[str] = None
    status:str
    paid_status:Optional[str] = None

class LeaveUpdate(BaseModel):
    status:Optional[Literal["pending", "approved", "rejected"]]=None
    paid_status:Optional[Literal["paid", "unpaid"]]=None
    leave_type:Optional[str]=None
