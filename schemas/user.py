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
