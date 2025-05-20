from pydantic import BaseModel, EmailStr
from typing import Optional

class UserUpdateSchema(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    mobile_number: Optional[str]
    role: Optional[str]
    is_active: Optional[bool] = True
    password: Optional[str] = None

class Config:
        orm_mode = True