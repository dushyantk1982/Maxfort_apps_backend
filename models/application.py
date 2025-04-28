from sqlalchemy import Column, String, Integer, Boolean
from db.database import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    app_url = Column(String)
    icon_url = Column(String)
    is_microsoft_oauth = Column(Boolean, default=False)
