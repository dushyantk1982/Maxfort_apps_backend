from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from models.user import User
from schemas.get_profile import UserProfile
from fastapi.security import OAuth2PasswordBearer
from auth.auth_jwt import get_current_user  # use this to validate JWT

router = APIRouter()

@router.get("/user/profile")
async def get_user_profile(email: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return {"error": "User not found"}
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "contact": user.mobile_number,
        "role": user.role,
        "status": user.is_active,
    }

@router.put("/user/profile/update")
async def update_profile(updated_data: dict, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == updated_data['email']))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.name = updated_data['name']
    user.mobile_number = updated_data['contact']
    # user.role = updated_data['role']
    await db.commit()
    return {"message": "Profile updated successfully"}
