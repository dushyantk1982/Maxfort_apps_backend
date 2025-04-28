from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from models.user import User
from models.app_credentials import AppCredentials
from schemas.user import UserCreate
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/admin/register-user")
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        role=user_data.role
    )
    db.add(new_user)
    await db.flush()  # So new_user.id is generated

    # Store credentials
    for cred in user_data.credentials:
        enc_password = pwd_context.hash(cred.password)
        db.add(AppCredentials(
            user_id=new_user.id,
            application_id=cred.app_id,
            username=cred.username,
            password=enc_password
        ))

    await db.commit()
    return {"msg": "User registered successfully"}
