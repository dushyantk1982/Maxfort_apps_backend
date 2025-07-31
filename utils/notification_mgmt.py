from sqlalchemy import insert, desc
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.notification import Notification
from models.notification_user import notification_user
from schemas.notification import NotificationCreate
from models.user import User

# async def create_notification(db: AsyncSession, notification: NotificationCreate):
#     db_notification = Notification(**notification.model_dump())
#     db.add(db_notification)
#     await db.commit()
#     await db.refresh(db_notification)
#     return db_notification

# async def create_notification(db: AsyncSession, notification: NotificationCreate):
#     # Step 1: Create the notification
#     db_notification = Notification(message=notification.message)

#     # Fetch and attach users
#     users = await db.execute(select(User).where(User.id.in_(notification.user_ids)))
#     db_notification.users = users.scalars().all()

#     db.add(db_notification)
#     await db.flush()  # ensure notification.id is available

#     # Step 2: Add relationships
#     # for user_id in notification.user_ids:
#     #     db.execute(
#     #         NotificationUser.__table__.insert().values(
#     #             notification_id=db_notification.id,
#     #             user_id=user_id
#     #         )
#     #     )

#     await db.commit()
#     await db.refresh(db_notification)
#     return db_notification

async def create_notification(db: AsyncSession, notification: NotificationCreate):
    try:
        db_notification = Notification(message = notification.message)
        db.add(db_notification)
        await db.commit()
        await db.refresh(db_notification)

        print(f"Created Notification with id:{db_notification.id}")

        for user_id in notification.user_ids:
            # if notification.user_ids:
            # values = [{"notification_id": db_notification.id, "user_id": uid}
            #              for uid in notification.user_ids ]
            # stmt = insert (notification_user).values(values)
            print("Notification ID:", db_notification.id)
            stmt = notification_user.insert().values(notification_id=db_notification.id,user_id=user_id)
            await db.execute(stmt)
            # await db.commit()
            print(f"Associated users {notification.user_ids} with notification")
        await db.commit()
        await db.refresh(db_notification)
        return db_notification
    except Exception as e:
        await db.rollback()
        print(f"Error occured: {e}")
        raise
            
    
    # for user_id in notification.user_ids:
    #     print("User IDs to notify:", notification.user_ids)
    #     # link = notification_user(notification_id=db_notification.id, user_id=user_id)
    #     # db.add(link)
    #     stmt = notification_user.insert().values(notification_id=db_notification.id, user_id=user_id)
    #     await db.execute(stmt)
    # print("User IDs to insert:", notification.user_ids)
    # for user_id in notification.user_ids:
    #     print(f"Inserting notification_user row for user_id={user_id}")
    #     stmt = notification_user.insert().values(
    #         notification_id=db_notification.id,
    #         user_id=user_id
    #     )
    #     await db.execute(stmt)

    # await db.commit()
    # print("Created notification ID:", db_notification.id)

    # return db_notification

# async def get_active_notifications(db: AsyncSession):
#     result = await db.execute(select(Notification).where(Notification.is_active == True))
#     return result.scalars().all()

async def get_active_notifications(db: AsyncSession, user_id: int = None, user_role = None):
    if user_role == "admin":
        result = await db.execute(select(Notification).where(Notification.is_active == True).order_by(desc(Notification.created_at)))
    else:
        if user_id is None:
            raise ValueError("user_id is required for non - admin users")
        result = await db.execute(select(Notification).join(notification_user).where(Notification.is_active == True,notification_user.c.user_id == user_id).order_by(desc(Notification.created_at)))
    return result.scalars().all()

async def deactivate_notification(db: AsyncSession, notification_id: int):
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notif = result.scalar_one_or_none()
    if notif:
        notif.is_active = False
        await db.commit()
        await db.refresh(notif)
    return notif
