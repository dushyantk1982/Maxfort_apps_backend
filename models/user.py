from sqlalchemy import Column, String, Boolean, Integer, DateTime
from db.database import Base
from datetime import datetime, timedelta, timezone

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