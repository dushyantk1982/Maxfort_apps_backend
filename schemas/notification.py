# # backend/schemas/notification.py
# from pydantic import BaseModel
# from datetime import datetime
# from typing import List, Optional

# class NotificationBase(BaseModel):
#     title: str
#     message: str

# class NotificationCreate(NotificationBase):
#     user_ids: List[int]  # List of user IDs to send notification to

# class NotificationResponse(NotificationBase):
#     id: int
#     created_at: datetime
#     is_active: bool
#     is_read: bool
#     created_by: int
#     user_id: int

#     class Config:
#         from_attributes = True

# schemas.py

from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    message: str

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    is_active: bool
    created_at: datetime

class Config:
    from_attributes = True
