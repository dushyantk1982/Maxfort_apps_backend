from pydantic import BaseModel
from typing import List
from typing import Optional

class AppCredentialInput(BaseModel):
    application_id: int
    username: str
    password: str  # optional: hash or encrypt before storing

class AppCredentialsRequest(BaseModel):
    user_id: int
    credentials: List[AppCredentialInput]


# To update app credentials
class CredentialUpdateRequest(BaseModel):
    # user_id: int
    # application_id: int
    username: str
    password: str