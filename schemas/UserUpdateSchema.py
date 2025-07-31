from pydantic import BaseModel, EmailStr
from typing import Optional

class UserUpdateSchema(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    mobile_number: Optional[str]
    role: Optional[str]
    is_active: Optional[bool] = True
    employee_code: Optional[str]
    admission_no: Optional[str]
    class_name: Optional[str]
    section: Optional[str]
    password: Optional[str] = None

class Config:
        orm_mode = True