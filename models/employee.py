from pydantic import BaseModel
from typing import Optional

class EmployeeCreate(BaseModel):
    name: str
    department: str
    designation: str
    joining_date: str
    salary: int
    phone: str
    email: str

class EmployeeResponse(BaseModel):
    id:str
    name:str
    department:str
    designation: str
    joining_date: str
    salary:int
    phone: str
    email: str

class EmployeeListResponse(BaseModel):
    employees: list[EmployeeResponse]
    page: int
    limit: int
    total: int
    has_more : bool

class EmployeeUpdate(BaseModel):
    name: Optional[str]= None
    department: Optional[str]= None
    designation: Optional[str] = None
    joining_date: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    salary: Optional[int]= None