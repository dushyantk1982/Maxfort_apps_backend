from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base

class AppCredentials(Base):
    __tablename__ = "app_credentials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    application_id = Column(Integer, ForeignKey("applications.id"))
    username = Column(String)
    password = Column(String)  # will be encrypted
