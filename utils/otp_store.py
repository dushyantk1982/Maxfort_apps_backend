import random
from fastapi import APIRouter, Depends, HTTPException
from db.database import get_db
from sqlalchemy.future import select
from models.user import User
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import delete
from models.otps import OTP
from sqlalchemy.ext.asyncio import AsyncSession
import traceback
from sqlalchemy.sql import func

# This will act as a mock OTP store
otp_storage = {}

def generate_otp(phone: str):
    otp = str(random.randint(100000, 999999))
    expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
    otp_storage[phone] = {"otp": otp, "expires_at": expiry}
    print(f"DEBUG: Sending OTP {otp} to {phone}")
    return otp

async def save_otp(db: AsyncSession, user_id: int, otp: str):
    print(f"Saving OTP: {otp} for user id: {user_id}")
    
    # Delete previous OTPs for this user (optional cleanup)
    try:
        await db.execute(delete(OTP).where(OTP.user_id == user_id))
        # db.query(OTP).filter(OTP.user_id == user_id).delete()

        new_otp = OTP(user_id=user_id, otp=otp)
        db.add(new_otp)
        await db.commit()
        print(f" OTP {otp} saved for user ID {user_id}")
    except Exception as e:
        await db.rollback
        # print(f"Error in saving otp:{e}")
        print("Error saving OTP:", e)


async def verify_otp(db: AsyncSession, phone: str, input_otp: str):

    try:
        result = await db.execute(select(User).where(User.phone == phone))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        otp_result = await db.execute(select(OTP).where(OTP.user_id == user.id, OTP.otp==input_otp))

        otp_record = otp_result.scalars().first()

        if not otp_record:
            raise HTTPException(status_code=401, detail="Invalid OTP")
        
        # Check OTP expiration
        created_at_aware = otp_record.created_at.replace(tzinfo=timezone.utc)
        if created_at_aware + timedelta(minutes=5) < datetime.now(timezone.utc):
        # if otp_record.created_at + timedelta(minutes=5) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="OTP Expired")
        
        # Delete OTP after successful verification
        await db.delete(otp_record)
        await db.commit()
        return {"msg": "OTP verified"}
    except Exception as e:
        traceback.print_exc()
        print(f"Error during OTP verification: {e}")
        raise HTTPException(status_code=500, detail="Internal server error: {str(e)}")

   
