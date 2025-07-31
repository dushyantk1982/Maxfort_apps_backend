from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.database import get_db, SessionLocal
from models.user import User
from fastapi.middleware.cors import CORSMiddleware
from utils.otp_store import generate_otp, verify_otp, save_otp
from models.otps import OTP
from sqlalchemy.future import select
from pydantic import BaseModel
import random
import bcrypt
from datetime import datetime, timedelta, timezone
import traceback
from auth.auth_jwt import create_access_token, create_refresh_access_token
from jose import jwt, JWTError
import os
from dotenv import load_dotenv


load_dotenv()


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 43200


router = APIRouter()


async def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# async def create_jwt_token(user_id):
#     payload = {"sub": str(user_id), "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
#     return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def create_jwt_token(user):
    # payload = {"sub": str(user.email), "role": user.role, "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
    payload = {"sub": str(user.email), "role": user.role, "exp": datetime.now(timezone.utc) + timedelta(minutes=43200)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def create_refresh_token(user):
    payload = {"sub": str(user.email), "role": user.role, "exp": datetime.now(timezone.utc) + timedelta(days=7)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Send OTP logic 

class OTPRequest(BaseModel):
    username: str
    # password: str

@router.post("/send-otp")
async def send_otp(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    username = data.username
    # password = data.password

    result = await db.execute(select(User).where(User.email == username))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    # if not user or not await verify_password(password, user.password_hash):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    
    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=5)
    user.otp_expiry = otp_expiry.replace(tzinfo=None)

    # Simulate sending SMS
    print(f"Sent OTP {otp} to {user.mobile_number}")

    await db.commit()
    return {"success": True,
            "otp":otp}


#  Verigy OTP Logic

class VerifyOTPSchema(BaseModel):
    username: str
    otp: str

@router.post("/verify-otp")
async def verify_user_otp(data: VerifyOTPSchema, db: AsyncSession = Depends(get_db)):
    username = data.username
    otp = data.otp

    result = await db.execute(select(User).where(User.email == username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    otp_expiry_aware = user.otp_expiry.replace(tzinfo=timezone.utc)
    print(f"Expected OTP: {user.otp_code}, Provided OTP: {data.otp}")

    if not user or user.otp_code != otp or otp_expiry_aware < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    print("OTP Verified")

    user.otp_code = None
    user.otp_expiry = None
    await db.commit()
    token = await create_jwt_token(user)
    refresh_token = await create_refresh_token(user)
    # token = await create_jwt_token(user.email)
    print("Access Token:", token)
    return {"access_token": token, "referesh_token": refresh_token, "token_type": "bearer"}

  

@router.post("/login-with-otp")
async def login_with_otp(payload: VerifyOTPSchema, db: AsyncSession = Depends(get_db)):
    phone = payload.phone
    otp = payload.otp

    try:
        await verify_otp(db, phone, otp)
        
        # Get user from DB
        result = await db.execute(select(User).where(User.phone == phone))
        user = result.scalars().first()

        # Create JWT token
        token_data = {"sub": user.email, "role": user.role}
        # token_data = {"sub": str(user.id), "role": user.role}
        access_token = create_access_token(token_data)
        refresh_access_token = create_refresh_access_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "role": user.role
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Something went wrong")


# Login with Password Logic

class PasswordLoginSchema(BaseModel):
    username: str
    password: str

@router.post("/auth/token")
async def login_with_password(data: PasswordLoginSchema, db: AsyncSession = Depends(get_db)):
    # username = data.username
    # password = data.password
    result = await db.execute(select(User).where(User.email == data.username))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    if not await verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # if not user or not await verify_password(data.password, user.password_hash):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = await create_jwt_token(user)
    refresh_token = await create_refresh_token(user)
    return {"access_token": token, "referesh_token": refresh_token, "token_type": "bearer"}

# Check email before login method

@router.post("/check-email")
async def check_email_exists(data: dict, db: AsyncSession = Depends(get_db)):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account is disabled. Please contact Admin.")
    
    return {"exists": True}


# To refresh JWT token


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        new_access_token = create_access_token({
            "sub": payload["sub"],
            "role": payload["role"]
        })
        return {"access_token": new_access_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")