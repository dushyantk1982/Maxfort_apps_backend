from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db.database import get_db
from utils import notification_mgmt
from schemas.notification import NotificationCreate, NotificationResponse

router = APIRouter()

@router.post("/add_notifications", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate, db: AsyncSession = Depends(get_db)
):
    return await notification_mgmt.create_notification(db, notification)

@router.get("/view_notifications", response_model=List[NotificationResponse])
async def get_active_notifications(db: AsyncSession = Depends(get_db)):
    try:
        return await notification_mgmt.get_active_notifications(db)
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
