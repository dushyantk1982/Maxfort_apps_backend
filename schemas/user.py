from pydantic import BaseModel
from typing import List, Optional

class AppCredentialInput(BaseModel):
    app_id: int
    username: str
    password: str

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    role: str = "user"
    credentials: List[AppCredentialInput]

# To Notification
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    mobile_number: Optional[str] = None
    employee_code: Optional[str] = None
    admission_no: Optional[str] = None
    class_name: Optional[str] = None
    section: Optional[str] = None

class Config:
        from_attributes = True
