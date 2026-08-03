from pydantic import BaseModel

class DepartmentCreate(BaseModel):
    name : str

class DepartmentResponse(DepartmentCreate):
    id : str
    name : str
    total_employees: int
    is_deleted : bool = False