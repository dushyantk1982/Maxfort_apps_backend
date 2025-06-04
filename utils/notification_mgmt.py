from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.notification import Notification
from schemas.notification import NotificationCreate

async def create_notification(db: AsyncSession, notification: NotificationCreate):
    db_notification = Notification(**notification.model_dump())
    db.add(db_notification)
    await db.commit()
    await db.refresh(db_notification)
    return db_notification

async def get_active_notifications(db: AsyncSession):
    result = await db.execute(select(Notification).where(Notification.is_active == True))
    return result.scalars().all()

async def deactivate_notification(db: AsyncSession, notification_id: int):
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notif = result.scalar_one_or_none()
    if notif:
        notif.is_active = False
        await db.commit()
        await db.refresh(notif)
    return notif
