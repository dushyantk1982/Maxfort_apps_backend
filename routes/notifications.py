from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.database import get_db
from utils import notification_mgmt
from schemas.notification import NotificationCreate, NotificationResponse
from models.user import User
from sqlalchemy.future import select
from auth.auth_jwt import get_current_user
# from utils.notification_mgmt import get_active_notifications as fetch_user_notifications

router = APIRouter()

@router.post("/add_notifications", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate, db: AsyncSession = Depends(get_db)
):
    return await notification_mgmt.create_notification(db, notification)

@router.get("/view_notifications", response_model=List[NotificationResponse])
async def get_active_notifications(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        user_email = current_user.get("email")
        # user_role = current_user.get("role")
        # if user_role == "admin":
        #     return await notification_mgmt.get_active_notifications(db, user_email, user_role)
        
        user = await db.execute(select(User).where(User.email == user_email))
        user_obj = user.scalar_one_or_none()
        print(f"Fetching notifications for user ID: {user_obj.id}")
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        return await notification_mgmt.get_active_notifications(db, user_obj.id, user_obj.role)
    except Exception as e:
        import logging
        logging.exception("Failed to get notifications")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_notifications/{notification_id}", response_model=NotificationResponse)
async def remove_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    notif = await notification_mgmt.deactivate_notification(db, notification_id)
    if notif is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notif


