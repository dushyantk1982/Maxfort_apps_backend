# # backend/models/notification.py
# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
# from sqlalchemy.orm import relationship
# from datetime import datetime, timezone
# from db.database import Base

# class Notification(Base):
#     __tablename__ = "notifications"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, nullable=False)
#     message = Column(String, nullable=False)
#     created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
#     is_active = Column(Boolean, default=True)
#     created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # The user this notification is for
#     is_read = Column(Boolean, default=False)  # Track if the user has read this notification

#     # Relationships
#     creator = relationship("User", foreign_keys=[created_by])
#     user = relationship("User", foreign_keys=[user_id])

# models.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

