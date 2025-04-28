# routes/user_route.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.UserUpdateSchema import UserUpdateSchema
from models import User
from db.database import get_db, SessionLocal

router = APIRouter()

@router.put("/users/{user_id}")
async def update_user(user_id: int, updated_user: UserUpdateSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = updated_user.name
    user.email = updated_user.email
    user.mobile_number = updated_user.mobile_number
    user.role = updated_user.role
    user.is_active = updated_user.is_active

    try:
        await db.commit()
        await db.refresh(user)
        return {
                "message": "User updated successfully",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "mobile_number": user.mobile_number,
                    "role": user.role,
                    "is_active": user.is_active
                }
            }
    except Exception as e:
        await db.rollback()
        print("Error during user update:", str(e))
        raise HTTPException(status_code=500, detail="Failed to update user")