from pydantic import BaseModel
from typing import List
from typing import Optional

# Response schema for Application
class ApplicationOut(BaseModel):
    id: int
    name: str
    app_url: Optional[str] = None
    icon_url: Optional[str] = None
    is_microsoft_oauth: bool

    class Config:
        orm_mode = True

# Response schema for User
class UserOut(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

# Response schema for user credentials
class AppCredentialOut(BaseModel):
    app_name: str
    username: str
    password: str