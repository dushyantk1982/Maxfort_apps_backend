from pydantic import BaseModel, EmailStr

class UserUpdateSchema(BaseModel):
    name: str
    email: EmailStr
    mobile_number: str
    role: str
    is_active: bool

class Config:
        orm_mode = True