from typing import Optional, Literal
from pydantic import BaseModel, Field

class UserRegister(BaseModel):
    username:str
    password : str = Field(min_length=8, max_length=72)
    role: str
    employee_id: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class ForgotUsernameRequest(BaseModel):
    employee_id: str
    new_username: str = Field(min_length=3, max_length=50)
    reason: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str = Field(min_length=8, max_length=72)
    reason: Optional[str] = None

class RecoveryRequestUpdate(BaseModel):
    status: Literal["approved", "rejected"]
    review_note: Optional[str] = None