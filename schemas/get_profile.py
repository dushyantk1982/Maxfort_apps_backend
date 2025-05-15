from pydantic import BaseModel

class UserProfile(BaseModel):
    name: str
    email: str
    mobile_number: str | None = None
    role: str
    # add more fields if needed

    class Config:
        # orm_mode = True
        from_attributes = True
    # model_config = {
    #     "from_attributes": True
    # }