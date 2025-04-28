from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    mobile_number: str
    password: str
    role: Optional[str] = "user"
