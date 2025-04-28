from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.user import User
from db.database import get_db
from models.user_schema import UserRegister
from utils.security import hash_password
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/register")
async def register_user(user: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = User(
        name=user.name,
        email=user.email,
        mobile_number=user.mobile_number,
        password_hash=hash_password(user.password),
        role=user.role
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return {"message": "User registered successfully", "Email": new_user.email}
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email or mobile number already registered")
