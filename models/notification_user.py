
from sqlalchemy import Column, Integer, ForeignKey, Table
from db.database import Base
notification_user = Table(
    "notification_user",
    Base.metadata,
    Column("notification_id", Integer, ForeignKey("notifications.id"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True)
    # UniqueConstraint("notification_id", "user_id", name="uq_notification_user")
)
