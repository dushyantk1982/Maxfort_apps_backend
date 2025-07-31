from sqlalchemy import Column, String, Boolean, Integer, DateTime
from db.database import Base
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import relationship
from models.notification_user import notification_user

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    password_hash = Column(String, nullable=False)
    otp_code = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    employee_code = Column(String, nullable=True)
    admission_no = Column(String, nullable=True)
    class_name = Column(String, nullable=True)   # 'class' is a reserved keyword, so use 'class_name'
    section = Column(String, nullable=True)
    notifications = relationship("Notification", secondary=notification_user, back_populates="users")
    # notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    # Many-to-many with notifications
    # notifications = relationship(
    #     "Notification",
    #     secondary="notification_user",
    #     back_populates="users"
    # )