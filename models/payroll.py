from pydantic import BaseModel

class PayrollCreate(BaseModel):
    employee_id:str
    month:int
    year:int

class PayrollResponse(BaseModel):
    id:str
    employee_id:str
    month:int
    year:int
    base_salary:float
    present_days:int
    leave_days:int
    ot_amount:float
    deduction:float
    final:float
    is_deleted:bool = False