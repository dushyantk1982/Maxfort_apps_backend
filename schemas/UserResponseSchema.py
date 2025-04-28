from pydantic import BaseModel, EmailStr

class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: EmailStr
    mobile_number: str
    role: str

    class Config:
        from_attributes = True  # For Pydantic v2
